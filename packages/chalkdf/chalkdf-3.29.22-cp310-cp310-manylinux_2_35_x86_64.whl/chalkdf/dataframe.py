"""Lightweight DataFrame wrapper around Chalk's execution engine.

The :class:`DataFrame` class constructs query plans backed by ``libchalk`` and
can materialize them into Arrow tables.  It offers a minimal API similar to
other DataFrame libraries while delegating heavy lifting to the underlying
engine.
"""

from __future__ import annotations

import typing
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Dict, TypeAlias

import pyarrow
from frozendict import frozendict

from chalkdf._chalk_import import (
    _get_base_sql_source_cls,
    _get_expr_pb,
    _get_underscore_attr_and_root,
    _get_underscore_cls,
)
from chalkdf._display import (
    format_materialized_table,
    format_materialized_table_html,
    format_plan_summary,
    normalize_materialized_tables,
)
from chalkdf.config import CompilationConfig, resolve_config
from chalkdf.debug import chalk_dataframe_debug_context_ob
from chalkdf.schema import Schema
from chalkdf.util import get_unique_item
from libchalk.chalktable import (
    AggExpr,
    AsOfJoinStrategy,
    ChalkTable,
    CompilationOptions,
    CompiledPlan,
    Expr,
    JoinKind,
    PlanRunContext,
    SchemaDescriptor,
    SortMethod,
    WindowExpr,
    string_to_join_kind,
    string_to_sort_method,
)
from libchalk.metrics import InMemoryMetricsEventCollector
from libchalk.utils import InMemoryErrorCollector

if TYPE_CHECKING:
    from chalk._gen.chalk.expression.v1 import expression_pb2 as expr_pb
    from chalk.features import Underscore
    from chalk.sql._internal.sql_source import BaseSQLSource

    from chalkdf.sql import CompatibleFrameType
    from libchalk.chalksql import ChalkSqlCatalog


MaterializedTable: TypeAlias = pyarrow.RecordBatch | pyarrow.Table


_empty_table_dict = frozendict()


def _generate_table_name(prefix: str = "") -> str:
    """Generate a unique table name with an optional ``prefix``."""

    return prefix + str(uuid.uuid4())


def _process_sort_cols(columns: typing.Sequence[str | tuple[str, str]]) -> list[tuple[str, SortMethod]]:
    sort_cols: list[tuple[str, SortMethod]] = []
    for col in columns:
        if isinstance(col, str):
            sort_cols.append((col, SortMethod.ASCENDING))
        else:
            sort_cols.append((col[0], string_to_sort_method(col[1])))
    return sort_cols


class DataFrame:
    """Logical representation of tabular data for query operations.

    DataFrame provides a lazy evaluation model where operations build up a query
    plan that executes only when materialized. Most users should use the class
    methods like ``from_dict``, ``from_arrow``, or ``scan`` to create
    DataFrames rather than calling the constructor directly.

    Examples
    --------
    >>> from chalkdf import DataFrame
    >>> from chalk.features import _
    >>> # Create from a dictionary
    >>> df = DataFrame({"x": [1, 2, 3], "y": ["a", "b", "c"]})
    >>> # Apply operations
    >>> filtered = df.filter(_.x > 1)
    >>> result = filtered.run()
    """

    def __init__(
        self,
        root: ChalkTable | MaterializedTable | dict,
        tables: Dict[str, MaterializedTable] | None = None,
    ):
        """Create a DataFrame from a dictionary, Arrow table, or query plan.

        For most use cases, prefer using class methods like `from_dict`,
        `from_arrow`, or `scan` instead of calling this constructor directly.

        Parameters
        ----------
        root
            Data source for the DataFrame. Can be:
            - dict: Dictionary mapping column names to lists of values
            - PyArrow Table or RecordBatch: In-memory Arrow data
            - ChalkTable: Query plan (advanced usage)
        tables
            Optional mapping of additional table names to Arrow data. Used internally
            for query execution with multiple tables.

        Examples
        --------
        >>> from chalkdf import DataFrame
        >>> # Simple dictionary input
        >>> df = DataFrame({"x": [1, 2, 3], "y": [4, 5, 6]})
        >>> # Or use the explicit class method (recommended)
        >>> df = DataFrame.from_dict({"x": [1, 2, 3], "y": [4, 5, 6]})
        """

        super().__init__()

        self._show_materialized_preview = False
        self._materialized_plan: typing.Optional[ChalkTable] = None

        if isinstance(root, dict):
            root = pyarrow.table(root)
        if isinstance(root, MaterializedTable):
            if isinstance(root, pyarrow.RecordBatch):
                materialized_table = pyarrow.Table.from_batches([root])
            else:
                materialized_table = root
            generated_name = _generate_table_name()
            self._plan: ChalkTable = ChalkTable.named_table(
                generated_name,
                SchemaDescriptor(schema=materialized_table.schema, sorted_by=[], partitioned_by="single_threaded"),
            )
            self._tables = {generated_name: materialized_table}
            self._show_materialized_preview = True
            self._materialized_plan = self._plan
        elif isinstance(root, ChalkTable):
            self._plan: ChalkTable = root
            self._tables = normalize_materialized_tables(tables) if tables else {}
            self._materialized_plan = None
        else:
            raise TypeError(f"Expected a ChalkTable or MaterializedTable, got {type(root)}")
        self._compiled_plan: typing.Optional[CompiledPlan] = None

    def _maybe_materialized(self) -> pyarrow.Table | None:
        if self._materialized_plan is None or self._plan is not self._materialized_plan or len(self._tables) != 1:
            return None

        only_table = get_unique_item(self._tables.values(), "tables")
        if isinstance(only_table, pyarrow.Table):
            return only_table
        return None

    def __repr__(self) -> str:
        table: pyarrow.Table | None = None
        if self._show_materialized_preview:
            table = self._maybe_materialized()
            if table is None and len(self._tables) == 1:
                only_table = get_unique_item(self._tables.values(), "tables")
                if isinstance(only_table, pyarrow.RecordBatch):
                    table = pyarrow.Table.from_batches([only_table])
        if table is not None:
            return format_materialized_table(table)
        return format_plan_summary(self._plan.schema_dict, len(self._tables))

    __str__ = __repr__

    def _repr_html_(self) -> str:
        import html

        table: pyarrow.Table | None = None
        if self._show_materialized_preview:
            table = self._maybe_materialized()
            if table is None and len(self._tables) == 1:
                only_table = get_unique_item(self._tables.values(), "tables")
                if isinstance(only_table, pyarrow.RecordBatch):
                    table = pyarrow.Table.from_batches([only_table])
        if table is not None:
            return format_materialized_table_html(table)
        return f"<pre>{html.escape(format_plan_summary(self._plan.schema_dict, len(self._tables)))}</pre>"

    def __len__(self) -> int:
        """
        Return the number of rows if this DataFrame has already been materialized.

        Raising ``TypeError`` for non-materialized frames matches Python's default
        behavior while avoiding implicitly executing the plan.
        """

        table = self._maybe_materialized()
        if table is None:
            raise TypeError("len() is only supported on materialized DataFrames; call run() or to_arrow() first")
        return table.num_rows

    def _to_proto(self) -> expr_pb.LogicalExprNode:
        expr_pb = _get_expr_pb()
        return expr_pb.LogicalExprNode(
            call=expr_pb.ExprCall(
                func=expr_pb.LogicalExprNode(identifier=expr_pb.Identifier(name="chalk_data_frame")),
                args=[],
                kwargs={},
            )
        )

    @classmethod
    def named_table(cls, name: str, schema: pyarrow.Schema) -> DataFrame:
        """Create a ``DataFrame`` for a named table.

        Parameters
        ----------
        name
            Table identifier.
        schema
            Arrow schema describing the table.

        Returns
        -------
        DataFrame referencing the named table.
        """

        return cls(
            ChalkTable.named_table(
                name, SchemaDescriptor(schema=schema, sorted_by=[], partitioned_by="single_threaded")
            )
        )

    @classmethod
    def from_arrow(cls, data: MaterializedTable):
        """Construct a DataFrame from an in-memory Arrow object.

        Parameters
        ----------
        data
            PyArrow Table or RecordBatch to convert into a DataFrame.

        Returns
        -------
        DataFrame backed by the provided Arrow data.

        Examples
        --------
        >>> import pyarrow as pa
        >>> from chalkdf import DataFrame
        >>> table = pa.table({"x": [1, 2, 3], "y": ["a", "b", "c"]})
        >>> df = DataFrame.from_arrow(table)
        """

        return cls(data)

    @classmethod
    def from_dict(cls, data: dict):
        """Construct a DataFrame from a Python dictionary.

        Parameters
        ----------
        data
            Dictionary mapping column names to lists of values.

        Returns
        -------
        DataFrame backed by the provided dictionary data.

        Examples
        --------
        >>> from chalkdf import DataFrame
        >>> df = DataFrame.from_dict({"x": [1, 2, 3], "y": ["a", "b", "c"]})
        """

        return cls(data)

    @classmethod
    def scan(
        cls,
        input_uris: typing.Sequence[str | Path],
        *,
        name: typing.Optional[str] = None,
        schema: pyarrow.Schema | None = None,
    ) -> DataFrame:
        """Scan files and return a DataFrame.

        Currently supports CSV (with headers) and Parquet file formats.

        Parameters
        ----------
        input_uris
            List of file paths or URIs to scan. Supports local paths and file:// URIs.
        name
            Optional name to assign to the table being scanned.
        schema
            Schema of the data. Required for CSV files, optional for Parquet.

        Returns
        -------
        DataFrame that reads data from the specified files.

        Examples
        --------
        >>> from chalkdf import DataFrame
        >>> # Scan Parquet files
        >>> df = DataFrame.scan(["data/sales_2024.parquet"], name="sales_data")
        >>> # Scan CSV with explicit schema
        >>> import pyarrow as pa
        >>> schema = pa.schema([("id", pa.int64()), ("name", pa.string())])
        >>> df = DataFrame.scan(["data/users.csv"], schema=schema)
        """
        # import uuid

        # if not name:
        #    name = str(uuid.uuid4())

        # Accept filesystem paths or URIs; construct file:// URIs manually for
        # local paths to avoid percent-encoding partition tokens like '='.
        # normalized: list[str] = []
        # for p in input_uris:
        #    s = p if isinstance(p, str) else str(p)
        #    if "://" in s:
        #        normalized.append(s)
        #    else:
        #        abs_path = str(Path(s).resolve())
        #        if not abs_path.startswith("/"):
        #            normalized.append(Path(s).resolve().as_uri())
        #        else:
        #            normalized.append("file://" + abs_path)
        # plan = ChalkTable.table_scan(name, normalized, schema)
        # return cls(plan, {})

        normalized: list[str] = []
        for p in input_uris:
            s = p if isinstance(p, str) else str(p)
            if "://" in s:
                normalized.append(s)
                continue
            # Detect hive/glob patterns
            if any(token in s for token in ("*", "?", "[", "=:")):
                # Keep as absolute POSIX path without scheme
                normalized.append(str(Path(s).resolve()))
                continue
            # Plain path -> file:// URI without percent-encoding
            abs_path = str(Path(s).resolve())
            if not abs_path.startswith("/"):
                normalized.append(Path(s).resolve().as_uri())
            else:
                normalized.append("file://" + abs_path)
        plan = ChalkTable.scan_parquet(
            normalized,
            schema,
            16,
            256,
            1024**2,
            None,
        )
        return cls(plan, {})

    @classmethod
    def scan_glue_iceberg(
        cls,
        glue_table_name: str,
        schema: typing.Mapping[str, pyarrow.DataType],
        *,
        batch_row_count: int = 1_000,
        aws_catalog_account_id: typing.Optional[str] = None,
        aws_catalog_region: typing.Optional[str] = None,
        aws_role_arn: typing.Optional[str] = None,
        filter_predicate: typing.Optional[Expr] = None,
        parquet_scan_range_column: typing.Optional[str] = None,
        custom_partitions: typing.Optional[dict[str, tuple[typing.Literal["date_trunc(day)"], str]]] = None,
        partition_column: typing.Optional[str] = None,
    ) -> DataFrame:
        """Load data from an AWS Glue Iceberg table.

        Parameters
        ----------
        glue_table_name
            Fully qualified ``database.table`` name.
        schema
            Mapping of column names to Arrow types.
        batch_row_count
            Number of rows per batch.
        aws_catalog_account_id
            AWS account hosting the Glue catalog.
        aws_catalog_region
            Region of the Glue catalog.
        aws_role_arn
            IAM role to assume for access.
        filter_predicate
            Optional filter applied during scan.
        parquet_scan_range_column
            Column used for range-based reads.
        custom_partitions
            Additional partition definitions.
        partition_column
            Column name representing partitions.

        Returns
        -------
        DataFrame backed by the Glue table.
        """

        custom_partitions = {} if custom_partitions is None else custom_partitions
        custom_partitions = {
            partition_column: tuple(partition_definition)  # pyright: ignore
            for partition_column, partition_definition in custom_partitions.items()
        }
        filter_predicate = (
            Expr.lit(pyarrow.scalar(True, type=pyarrow.bool_())) if filter_predicate is None else filter_predicate
        )

        plan = ChalkTable.load_glue_table(
            aws_catalog_account_id=aws_catalog_account_id,
            aws_catalog_region=aws_catalog_region,
            aws_role_arn=aws_role_arn,
            table_name=list(glue_table_name.split(".")),
            schema=pyarrow.schema(schema),
            batch_row_count=batch_row_count,
            filter_predicate=filter_predicate,
            parquet_scan_range_column=parquet_scan_range_column or partition_column,
            custom_partitions=custom_partitions or {},
        )

        return cls(plan, {})

    @classmethod
    def from_catalog_table(
        cls,
        table_name: str,
        *,
        catalog: ChalkSqlCatalog,
    ) -> DataFrame:
        """Create a DataFrame from a Chalk SQL catalog table.

        Parameters
        ----------
        table_name
            Name of the table in the catalog.
        catalog
            ChalkSqlCatalog instance containing the table.

        Returns
        -------
        DataFrame referencing the catalog table.

        Examples
        --------
        >>> from chalkdf import DataFrame
        >>> from libchalk.chalksql import ChalkSqlCatalog
        >>> catalog = ChalkSqlCatalog()
        >>> df = DataFrame.from_catalog_table("users", catalog=catalog)
        """

        plan = ChalkTable.from_catalog_table(
            table_name,
            catalog=catalog,
        )
        return cls(plan, {})

    @classmethod
    def from_sql(
        cls,
        query: str,
        **tables: CompatibleFrameType,
    ) -> DataFrame:
        """Create a ``DataFrame`` from the result of executing a SQL query (DuckDB dialect).

        Parameters
        ----------
        query
            SQL query string (DuckDB dialect).
        **tables
            Named tables to use in the query. Can be Arrow Table, RecordBatch, or DataFrame.

        Returns
        -------
        DataFrame containing the query results.
        """
        from .sql import SQLContext

        if tables:
            # Create a SQL context with the provided tables
            with SQLContext(frames=tables) as ctx:
                return ctx.execute(query)
        else:
            # Use execute_global to auto-register frames from the calling scope
            return SQLContext.execute_global(query)

    @classmethod
    def from_datasource(cls, source: BaseSQLSource, query: str, expected_output_schema: pyarrow.Schema):
        """Create a DataFrame from the result of querying a SQL data source.

        Parameters
        ----------
        source
            SQL source to query (e.g., PostgreSQL, Snowflake, BigQuery).
        query
            SQL query to execute against the data source.
        expected_output_schema
            Output schema of the query result. The datasource's driver converts
            the native query result to this schema.

        Returns
        -------
        DataFrame containing the query results from the data source.

        Examples
        --------
        >>> import pyarrow as pa
        >>> from chalkdf import DataFrame
        >>> from chalk.sql import PostgreSQLSource
        >>> source = PostgreSQLSource(...)
        >>> schema = pa.schema([("user_id", pa.int64()), ("name", pa.string())])
        >>> df = DataFrame.from_datasource(source, "SELECT * FROM users", schema)
        """
        BaseSQLSource = _get_base_sql_source_cls()

        if not isinstance(source, BaseSQLSource):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise ValueError(f"source must be a BaseSQLSource, got {source}")
        if not isinstance(expected_output_schema, pyarrow.Schema):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise ValueError("expected_output_schema must be a pyarrow.Schema")
        plan = ChalkTable.from_datasource(source, query, expected_output_schema)
        return cls(plan)

    def _apply_function(
        self, new_plan: ChalkTable, additional_tables: typing.Mapping[str, MaterializedTable] = _empty_table_dict
    ) -> DataFrame:
        """Return a new ``DataFrame`` with ``new_plan`` and merged tables."""

        combined_tables = normalize_materialized_tables({**self._tables, **additional_tables})
        return DataFrame(new_plan, combined_tables)

    def _compile(
        self,
        *,
        config: CompilationConfig | None = None,
        recompile: bool = False,
    ) -> CompiledPlan:
        """Compile the current plan if necessary.

        Configuration is resolved from multiple sources in priority order:
        1. Explicit ``config`` parameter (highest priority)
        2. Active `compilation_config` context manager
        3. Global defaults from `set_compilation_defaults`
        4. Environment variables (e.g., ``CHALK_USE_VELOX_PARQUET_READER``)
        5. Built-in fallback defaults

        Parameters
        ----------
        config
            Explicit compilation configuration (highest priority).
        recompile
            Force recompilation even if a plan exists.

        Returns
        -------
        CompiledPlan ready for execution.
        """

        if self._compiled_plan is None or recompile:
            # Resolve final configuration from all sources
            resolved_config = resolve_config(config)

            # Convert to CompilationOptions kwargs
            options_kwargs = resolved_config.to_dict()
            options = CompilationOptions(**options_kwargs)

            self._compiled_plan = CompiledPlan("velox", options, [self._plan])
        return self._compiled_plan

    def explain_logical(self) -> str:
        """Return a string representation of the logical query plan.

        Returns
        -------
        String representation of the logical plan showing the high-level
        operations that will be performed.

        Examples
        --------
        >>> from chalkdf import DataFrame
        >>> from chalk.features import _
        >>> df = DataFrame.from_dict({"x": [1, 2, 3], "y": [4, 5, 6]})
        >>> filtered = df.filter(_.x > 1)
        >>> print(filtered.explain_logical())
        """

        return self._compile().explain_logical()

    def explain_physical(self) -> str:
        """Return a string representation of the physical execution plan.

        Returns
        -------
        String representation of the physical plan showing the low-level
        execution details and optimizations.

        Examples
        --------
        >>> from chalkdf import DataFrame
        >>> from chalk.features import _
        >>> df = DataFrame.from_dict({"x": [1, 2, 3], "y": [4, 5, 6]})
        >>> filtered = df.filter(_.x > 1)
        >>> print(filtered.explain_physical())
        """

        return self._compile().explain_physical()

    def explain_as_json(self) -> object:
        """
        Computes plan JSON for debugging the structure of the computation.
        """
        return self._compile().as_plan_json()

    def _run_context(self) -> PlanRunContext:
        """Construct a default :class:`PlanRunContext` for execution."""

        return PlanRunContext(
            correlation_id=None,
            environment_id="test",
            deployment_id="test_deployment",
            requester_id="requester_id",
            operation_id="dummy_op",
            execution_timestamp=pyarrow.scalar(datetime.now(timezone.utc), pyarrow.timestamp("us", "UTC")),
            is_online=True,
            max_samples=None,
            observed_at_lower_bound=None,
            observed_at_upper_bound=None,
            customer_metadata={},
            shard_id=0,
            extra_attributes={},
            query_context={},
            error_collector=InMemoryErrorCollector(1000),
            metrics_event_collector=InMemoryMetricsEventCollector(1000),
            chalk_metrics=None,
            batch_reporter=None,
            timeline_trace_writer=None,
            plan_metrics_storage_service=None,
            python_context=None,
        )

    def _execute_to_arrow(self, tables: typing.Mapping[str, MaterializedTable]) -> pyarrow.Table:
        """Execute the plan and collect the result into a single Arrow table."""
        debug_context = chalk_dataframe_debug_context_ob.get()
        if debug_context is not None and debug_context.on_run is not None:
            debug_context.on_run(self)

        result = (
            self._compile()
            .run(
                self._run_context(),
                {**self._tables, **tables},
                {"__execution_ts__": pyarrow.scalar(datetime.now(timezone.utc), pyarrow.timestamp("us", "UTC"))},
            )
            .result()
        )
        return pyarrow.Table.from_batches(result.batches)

    def _as_agg_expr(self, underscore_or_agg_expression: AggExpr | Underscore) -> AggExpr:
        Underscore = _get_underscore_cls()

        if isinstance(underscore_or_agg_expression, AggExpr):
            return underscore_or_agg_expression
        elif isinstance(underscore_or_agg_expression, Underscore):
            from .underscore_conversion.convert_underscore_to_expr import convert_underscore_to_agg_expr

            return convert_underscore_to_agg_expr(underscore_or_agg_expression, self.get_plan().schema_dict)
        else:
            raise ValueError(f"Expected to receive an AggExpr or Underscore, got {type(underscore_or_agg_expression)}")

    def _as_expr_with_alias(self, underscore_or_expression: Expr | Underscore) -> tuple[Expr, str | None]:
        Underscore = _get_underscore_cls()

        if isinstance(underscore_or_expression, Expr):
            return underscore_or_expression, None
        elif isinstance(underscore_or_expression, Underscore):
            from .underscore_conversion.convert_underscore_to_expr import convert_underscore_to_expr_with_alias

            return convert_underscore_to_expr_with_alias(underscore_or_expression, self.get_plan().schema_dict)
        else:
            raise ValueError(f"Expected to receive an Expr or Underscore, got {type(underscore_or_expression)}")

    def _as_expr(self, underscore_or_expression: Expr | Underscore) -> Expr:
        Underscore = _get_underscore_cls()

        if isinstance(underscore_or_expression, Expr):
            return underscore_or_expression
        elif isinstance(underscore_or_expression, Underscore):
            from .underscore_conversion.convert_underscore_to_expr import convert_underscore_to_expr

            return convert_underscore_to_expr(underscore_or_expression, self.get_plan().schema_dict)
        else:
            raise ValueError(f"Expected to receive an Expr or Underscore, got {type(underscore_or_expression)}")

    @property
    def column_names(self) -> list[str]:
        """Return a list of the column names on this dataframe"""

        return self.schema.names()

    @property
    def column_dtypes(self) -> list[pyarrow.DataType]:
        """Return a list of column data types on this dataframe"""

        return self.schema.dtypes()

    @property
    def schema(self) -> Schema:
        """Return schema of this dataframe"""

        return Schema(self.get_plan().schema_dict)

    @property
    def num_columns(self) -> int:
        """Return the number of columns on this dataframe"""

        return self.schema.len()

    def get_plan(self) -> ChalkTable:
        """Expose the underlying :class:`ChalkTable` plan."""

        return self._plan

    def get_tables(self) -> dict[str, MaterializedTable]:
        """Return the mapping of materialized tables for this DataFrame."""

        return self._tables

    def with_columns(
        self, *columns: typing.Mapping[str, Expr | Underscore] | Expr | Underscore | tuple[str, Expr | Underscore]
    ) -> DataFrame:
        """Add or replace columns.

        Accepts multiple forms:
        - A mapping of column names to expressions
        - Positional tuples of (name, expression)
        - Bare positional expressions that must include ``.alias(<name>)``

        Parameters
        ----------
        *columns
            Column definitions as mappings, tuples, or aliased expressions.

        Returns
        -------
        DataFrame with the specified columns added or replaced.

        Examples
        --------
        >>> from chalkdf import DataFrame
        >>> from chalk.features import _
        >>> df = DataFrame.from_dict({"x": [1, 2, 3], "y": [4, 5, 6]})
        >>> # Add a new column using a dict with _ syntax
        >>> df2 = df.with_columns({"z": _.x + _.y})
        >>> # Add a new column using alias
        >>> df3 = df.with_columns((_.x + _.y).alias("z"))
        """

        existing = self._plan.schema_dict
        stuff = {k: Expr.column(k, existing[k]) for k in existing}

        entries: list[tuple[str | None, Expr | Underscore]] = []
        if len(columns) == 0:
            raise ValueError("with_columns requires at least one column expression")

        for col in columns:
            if isinstance(col, dict):
                entries.extend((k, v) for k, v in col.items())
            else:
                entries.append((None, col))

        for maybe_name, value in entries:
            if isinstance(value, tuple) and len(value) == 2 and isinstance(value[0], str):
                name_hint, expr_val = value
            else:
                name_hint, expr_val = maybe_name, value

            expr, alias = self._as_expr_with_alias(expr_val)
            name = alias or name_hint
            if name is None:
                raise ValueError("Positional with_columns expressions must use alias() to set the column name")
            stuff[name] = expr

        new_plan = self._plan.project(stuff)

        return self._apply_function(new_plan)

    def with_unique_id(self, name: str) -> DataFrame:
        """Add a monotonically increasing unique identifier column.

        Parameters
        ----------
        name
            Name of the new ID column.

        Returns
        -------
        DataFrame with a new column containing unique, incrementing IDs.

        Examples
        --------
        >>> from chalkdf import DataFrame
        >>> df = DataFrame.from_dict({"x": [10, 20, 30]})
        >>> df_with_id = df.with_unique_id("row_id")
        """

        new_plan = self._plan.with_unique_id(name)
        return self._apply_function(new_plan)

    def filter(self, expr: Expr | Underscore) -> DataFrame:
        """Filter rows based on a boolean expression.

        Parameters
        ----------
        expr
            Boolean expression to filter rows. Only rows where the expression
            evaluates to True are kept.

        Returns
        -------
        DataFrame containing only the rows that match the filter condition.

        Examples
        --------
        >>> from chalkdf import DataFrame
        >>> from chalk.features import _
        >>> df = DataFrame.from_dict({"x": [1, 2, 3, 4], "y": [10, 20, 30, 40]})
        >>> filtered = df.filter(_.x > 2)
        """

        new_plan = self._plan.filter(self._as_expr(expr))
        return self._apply_function(new_plan)

    def slice(self, start: int, length: int | None = None) -> DataFrame:
        """Return a subset of rows starting at a specific position.

        Parameters
        ----------
        start
            Zero-based index where the slice begins.
        length
            Number of rows to include. If None, includes all remaining rows.

        Returns
        -------
        DataFrame containing the sliced rows.

        Examples
        --------
        >>> from chalkdf import DataFrame
        >>> df = DataFrame.from_dict({"x": [1, 2, 3, 4, 5]})
        >>> # Get rows 1-3 (indices 1, 2, 3)
        >>> sliced = df.slice(1, 3)
        """

        # Can't actually express "no limit" with velox limit/offset, but this'll do.
        if length is None:
            length = (2**63) - 1
        elif length <= 0:
            raise ValueError(
                f"'length' parameter in function 'slice' must be a positive integer if specified, received {length}"
            )
        new_plan = self._plan.limit(length, start)
        return self._apply_function(new_plan)

    def col(self, column: str) -> Underscore:
        """Get a column expression from the DataFrame.

        Parameters
        ----------
        column
            Name of the column to retrieve.

        Returns
        -------
        Column expression (as Underscore) that can be used in operations.

        Examples
        --------
        >>> from chalkdf import DataFrame
        >>> from chalk.features import _
        >>> df = DataFrame.from_dict({"x": [1, 2, 3], "y": [4, 5, 6]})
        >>> # Use col to reference columns in expressions
        >>> df_filtered = df.filter(_.x > 1)
        """
        return self.column(column)

    def column(self, column: str) -> Underscore:
        """Get a column expression from the DataFrame.

        Alias for col() method.

        Parameters
        ----------
        column
            Name of the column to retrieve.

        Returns
        -------
        Column expression (as Underscore) that can be used in operations.

        Examples
        --------
        >>> from chalkdf import DataFrame
        >>> from chalk.features import _
        >>> df = DataFrame.from_dict({"x": [1, 2, 3], "y": [4, 5, 6]})
        >>> df_sum = df.with_columns({"sum": _.x + _.y})
        """
        if column not in self.column_names:
            raise ValueError(f"Column '{column}' not found in DataFrame")
        UnderscoreAttr, UnderscoreRoot = _get_underscore_attr_and_root()
        return UnderscoreAttr(UnderscoreRoot(), column)

    def project(self, columns: typing.Mapping[str, Expr | Underscore]) -> DataFrame:
        """Project to a new set of columns using expressions.

        Parameters
        ----------
        columns
            Mapping of output column names to expressions that define them.

        Returns
        -------
        DataFrame with only the specified columns.

        Examples
        --------
        >>> from chalkdf import DataFrame
        >>> from chalk.features import _
        >>> df = DataFrame.from_dict({"x": [1, 2, 3], "y": [4, 5, 6]})
        >>> projected = df.project({"sum": _.x + _.y, "x": _.x})
        """

        projections: dict[str, Expr] = {}
        for k, v in columns.items():
            expr, alias = self._as_expr_with_alias(v)
            name = alias or k
            projections[name] = expr
        new_plan = self._plan.project(projections)
        return self._apply_function(new_plan)

    def select(self, *columns: str, strict: bool = True) -> DataFrame:
        """Select existing columns by name.

        Parameters
        ----------
        *columns
            Names of columns to select.
        strict
            If True, raise an error if any column doesn't exist. If False,
            silently ignore missing columns.

        Returns
        -------
        DataFrame with only the selected columns.

        Examples
        --------
        >>> from chalkdf import DataFrame
        >>> df = DataFrame.from_dict({"x": [1, 2, 3], "y": [4, 5, 6], "z": [7, 8, 9]})
        >>> selected = df.select("x", "y")
        """

        try:
            projections = {
                col: Expr.column(col, self._plan.schema_dict[col])
                for col in columns
                if (col in self.column_names or strict)
            }
        except KeyError as ke:
            raise ValueError(f"Column '{ke.args[0]}' not found in DataFrame")

        new_plan = self._plan.project(projections)
        return self._apply_function(new_plan)

    def drop(self, *columns: str, strict: bool = True) -> DataFrame:
        """Drop specified columns from the DataFrame.

        Parameters
        ----------
        *columns
            Names of columns to drop.
        strict
            If True, raise an error if any column doesn't exist. If False,
            silently ignore missing columns.

        Returns
        -------
        DataFrame without the dropped columns.

        Examples
        --------
        >>> from chalkdf import DataFrame
        >>> df = DataFrame.from_dict({"x": [1, 2, 3], "y": [4, 5, 6], "z": [7, 8, 9]})
        >>> df_dropped = df.drop("z")
        """
        if strict:
            bad_cols = tuple(col for col in columns if col not in self.column_names)
            if len(bad_cols) > 0:
                raise ValueError(f"Column(s) '{', '.join(bad_cols)}' not found in DataFrame")
        return self.select(*(col for col in self.column_names if col not in columns))

    def explode(self, column: str) -> DataFrame:
        """Explode a list or array column into multiple rows.

        Each element in the list becomes a separate row, with other column
        values duplicated.

        Parameters
        ----------
        column
            Name of the list/array column to explode.

        Returns
        -------
        DataFrame with the list column expanded into multiple rows.

        Examples
        --------
        >>> from chalkdf import DataFrame
        >>> df = DataFrame.from_dict({"id": [1, 2], "items": [[10, 20], [30]]})
        >>> exploded = df.explode("items")
        """
        new_plan = self._plan.explode([column])
        return self._apply_function(new_plan)

    def join(
        self,
        other: DataFrame,
        on: dict[str, str] | typing.Sequence[str],
        how: str = "inner",
        right_suffix: str | None = None,
    ) -> DataFrame:
        """Join this ``DataFrame`` with another.

        Parameters
        ----------
        other
            Right-hand ``DataFrame``.
        on
            Column names or mapping of left->right join keys.
        how
            Join type (e.g. ``"inner"`` or ``"left"``).
        right_suffix
            Optional suffix applied to right-hand columns when names collide.

        Returns
        -------
        Resulting ``DataFrame`` after the join.
        """

        if isinstance(on, dict):
            on_left = list(on.keys())
            on_right = [on[r] for r in on_left]
        else:
            on_right = on_left = list(on)
        join_pairs = list(zip(on_left, on_right))
        join_kind = string_to_join_kind(how)

        right_df = other
        helper_mapping: dict[str, str] = {}
        if join_kind == JoinKind.FULL_OUTER:
            # Duplicate right join keys into helper columns so we can coalesce them into the left keys after the join.
            helper_suffix = "__chalkdf_right_key__"
            used_names = set(self.column_names) | set(other.column_names)
            helper_exprs: dict[str, Expr | Underscore] = {}
            for left_key, right_key in join_pairs:
                helper_name = f"{left_key}{helper_suffix}"
                counter = 0
                while helper_name in used_names:
                    counter += 1
                    helper_name = f"{left_key}{helper_suffix}_{counter}"
                helper_mapping[left_key] = helper_name
                used_names.add(helper_name)
                helper_exprs[helper_name] = other.column(right_key)

            if helper_exprs:
                right_df = other.with_columns(helper_exprs)

        new_plan = self._plan.join(right_df._plan, on_left, join_kind, right_keys=on_right, right_suffix=right_suffix)

        # Full outer joins need the right-side join key values on right-only rows.
        # Coalesce the left join keys with the duplicated right key helpers, then drop the helpers.
        if join_kind == JoinKind.FULL_OUTER:
            schema = new_plan.schema_dict
            helper_names = set(helper_mapping.values())
            projections: dict[str, Expr] = {}
            for name, dtype in schema.items():
                if name in helper_names:
                    continue

                helper_col = helper_mapping.get(name)
                if helper_col is not None and helper_col in schema:
                    projections[name] = Expr.coalesce(
                        [Expr.column(name, dtype), Expr.column(helper_col, schema[helper_col])]
                    )
                else:
                    projections[name] = Expr.column(name, dtype)

            new_plan = new_plan.project(projections)

        return self._apply_function(new_plan, additional_tables=right_df._tables)

    def join_asof(
        self,
        other: DataFrame,
        on: str,
        *,
        right_on: str | None = None,
        by: list[str] | None = None,
        right_by: list[str] | None = None,
        strategy: AsOfJoinStrategy | typing.Literal["forward", "backward"] = "backward",
        right_suffix: str | None = None,
        coalesce: bool = True,
    ) -> DataFrame:
        """Perform an as-of join with another DataFrame.

        An as-of join is similar to a left join, but instead of matching on equality,
        it matches on the nearest key from the right DataFrame. This is commonly used
        for time-series data where you want to join with the most recent observation.

        **Important**: Both DataFrames must be sorted by the ``on`` column before calling
        this method. Use ``.order_by(on)`` to sort if needed.

        Parameters
        ----------
        other
            Right-hand DataFrame to join with.
        on
            Column name in the left DataFrame to join on (must be sorted).
        right_on
            Column name in the right DataFrame to join on. If None, uses ``on``.
        by
            Additional exact-match columns for left DataFrame (optional).
        right_by
            Additional exact-match columns for right DataFrame. If None, uses ``by``.
        strategy
            Join strategy - "backward" (default) matches with the most recent past value,
            "forward" matches with the nearest future value. Can also pass AsOfJoinStrategy enum.
        right_suffix
            Suffix to add to overlapping column names from the right DataFrame.
        coalesce
            Whether to coalesce the join keys (default True).

        Returns
        -------
        Resulting DataFrame after the as-of join.
        """
        # Convert string strategy to enum if needed
        if isinstance(strategy, str):
            if strategy == "backward":
                strategy_enum = AsOfJoinStrategy.BACKWARD
            elif strategy == "forward":
                strategy_enum = AsOfJoinStrategy.FORWARD
            else:
                raise ValueError(f"Invalid strategy '{strategy}'. Must be 'forward' or 'backward'")
        else:
            strategy_enum = strategy

        new_plan = self._plan.join_asof(
            other._plan,
            on=on,
            right_on=right_on,
            by=by,
            right_by=right_by,
            strategy=strategy_enum,
            right_suffix=right_suffix,
            coalesce=coalesce,
        )
        return self._apply_function(new_plan, additional_tables=other._tables)

    def window(
        self,
        by: typing.Sequence[str],
        order_by: typing.Sequence[str | tuple[str, str]],
        *expressions: WindowExpr,
    ) -> DataFrame:
        """Compute windowed expressions 'expressions' over 'by' columns ordered by 'order_by' columns. Overlap in `by` and `order_by` is not allowed"""

        sort_cols = _process_sort_cols([*by, *order_by])
        new_plan = (
            self._plan.partition_by(list(by))
            .sort_by(sort_cols)
            .window(list(expressions), [*by], _process_sort_cols([*order_by]))
        )
        return self._apply_function(new_plan)

    def agg(self, by: typing.Sequence[str], *aggregations: AggExpr | Underscore) -> DataFrame:
        """Group by columns and apply aggregation expressions.

        Parameters
        ----------
        by
            Column names to group by.
        *aggregations
            Aggregation expressions to apply to each group (e.g., sum, count, mean).

        Returns
        -------
        DataFrame with one row per group containing the aggregated values.

        Examples
        --------
        >>> from chalkdf import DataFrame
        >>> from chalk.features import _
        >>> df = DataFrame.from_dict({"group": ["A", "A", "B"], "value": [1, 2, 3]})
        >>> agg_df = df.agg(["group"], _.value.sum().alias("total"))
        """

        new_plan = self._plan.aggregate_exprs([*by], [self._as_agg_expr(agg) for agg in aggregations])
        return self._apply_function(new_plan)

    def distinct_on(self, *columns: str) -> DataFrame:
        """Remove duplicate rows based on specified columns.

        For rows with identical values in the specified columns, only one
        row is kept (chosen arbitrarily).

        Parameters
        ----------
        *columns
            Column names to check for duplicates.

        Returns
        -------
        DataFrame with duplicate rows removed.

        Examples
        --------
        >>> from chalkdf import DataFrame
        >>> df = DataFrame.from_dict({"x": [1, 1, 2], "y": [10, 20, 30]})
        >>> unique = df.distinct_on("x")
        """

        if len(columns) == 0:
            raise ValueError("Must specify column(s) to distinct on.")

        return self.agg(
            columns, *[self.column(col).one().alias(col) for col in self.column_names if col not in columns]
        ).project({x: self.col(x) for x in self.column_names})

    def order_by(self, *columns: str | tuple[str, str]) -> DataFrame:
        """Sort the DataFrame by one or more columns.

        Parameters
        ----------
        *columns
            Column names to sort by. Can be strings (for ascending order) or
            tuples of (column_name, direction) where direction is "asc" or "desc".

        Returns
        -------
        DataFrame sorted by the specified columns.

        Examples
        --------
        >>> from chalkdf import DataFrame
        >>> df = DataFrame.from_dict({"x": [3, 1, 2], "y": [30, 10, 20]})
        >>> # Sort by x ascending
        >>> sorted_df = df.order_by("x")
        >>> # Sort by x descending, then y ascending
        >>> sorted_df = df.order_by(("x", "desc"), "y")
        """

        sort_cols = _process_sort_cols(columns)
        new_plan = self._plan.sort_by(sort_cols)
        return self._apply_function(new_plan)

    def write(
        self,
        target_path: str,
        target_file_name: str | None = None,
        *,
        file_format: str = "parquet",
        serde_parameters: typing.Mapping[str, str] | None = None,
        compression: str | None = None,
        ensure_files: bool = False,
        connector_id: str | None = None,
    ) -> DataFrame:
        """Persist the DataFrame plan using Velox's Hive connector.

        Parameters
        ----------
        target_path
            Directory to write output files.
        target_file_name
            Optional explicit file name.
        file_format
            Output format (default ``parquet``).
        serde_parameters
            Optional SerDe options for text formats.
        compression
            Optional compression codec.
        ensure_files
            Ensure writers emit files even if no rows were produced.
        connector_id
            Optional connector id override.

        Returns
        -------
        DataFrame representing the TableWrite operator.
        """

        plan = self._plan.write(
            target_path=target_path,
            target_file_name=target_file_name,
            file_format=file_format,
            serde_parameters=dict(serde_parameters) if serde_parameters is not None else {},
            compression=compression,
            ensure_files=ensure_files,
            connector_id=connector_id,
        )
        return self._apply_function(plan)

    def rename(self, new_names: dict[str, str]) -> DataFrame:
        """Rename columns in the DataFrame.

        Parameters
        ----------
        new_names
            Dictionary mapping old column names to new column names.

        Returns
        -------
        DataFrame with renamed columns.

        Examples
        --------
        >>> from chalkdf import DataFrame
        >>> df = DataFrame.from_dict({"x": [1, 2, 3], "y": [4, 5, 6]})
        >>> renamed = df.rename({"x": "id", "y": "value"})
        """

        for nn in new_names:
            if nn not in self.column_names:
                raise ValueError(f"Column '{nn}' not found in DataFrame")

        return self.project({new_names.get(k, k): self.col(k) for k in self.column_names})

    def to_arrow(self, tables: typing.Mapping[str, MaterializedTable] = _empty_table_dict) -> pyarrow.Table:
        """Execute the query plan and return the result as a PyArrow Table.

        Parameters
        ----------
        tables
            Optional mapping of table names to materialized Arrow data for execution.

        Returns
        -------
        PyArrow Table containing the query results.

        Examples
        --------
        >>> from chalkdf import DataFrame
        >>> from chalk.features import _
        >>> df = DataFrame.from_dict({"x": [1, 2, 3], "y": [4, 5, 6]})
        >>> filtered = df.filter(_.x > 1)
        >>> arrow_table = filtered.to_arrow()
        """

        if not tables:
            existing = self._maybe_materialized()
            if existing is not None:
                return existing
        return self._execute_to_arrow(tables)

    def as_plan_json(self) -> object:
        compiled_plan = self._compile()
        return compiled_plan.as_plan_json()

    def run(self, tables: typing.Mapping[str, MaterializedTable] = _empty_table_dict) -> DataFrame:
        """Execute the query plan and return a materialized DataFrame.

        Parameters
        ----------
        tables
            Optional mapping of table names to materialized Arrow data for execution.

        Returns
        -------
        DataFrame backed by an in-memory Arrow table with the query results.

        Examples
        --------
        >>> from chalkdf import DataFrame
        >>> from chalk.features import _
        >>> df = DataFrame.from_dict({"x": [1, 2, 3], "y": [4, 5, 6]})
        >>> filtered = df.filter(_.x > 1)
        >>> materialized = filtered.run()
        """

        return DataFrame.from_arrow(self.to_arrow(tables))
