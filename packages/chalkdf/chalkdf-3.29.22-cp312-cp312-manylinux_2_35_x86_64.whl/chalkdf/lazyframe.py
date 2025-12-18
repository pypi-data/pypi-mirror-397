from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable, Mapping, Type, cast

import pyarrow as _pa

from chalkdf._chalk_import import _get_expr_pb, _get_primitive_feature_converter, _get_underscore_cls
from chalkdf.dataframe import DataFrame
from libchalk.chalksql import ChalkSqlCatalog
from libchalk.chalktable import ChalkTable, Expr

_ARG_WRAPPER_FUNC = "chalk_lazy_arg_v1"
_USE_ARG_WRAPPER = False

_SCHEMA_LITERAL_TYPE_KEY = "__lazyframe_literal_type__"
_SCHEMA_LITERAL_SCHEMA_VALUE = "pyarrow_schema"
_SCHEMA_LITERAL_BYTES_KEY = "serialized_schema"


def _schema_to_literal_payload(schema: _pa.Schema) -> dict[str, Any]:
    return {
        _SCHEMA_LITERAL_TYPE_KEY: _SCHEMA_LITERAL_SCHEMA_VALUE,
        _SCHEMA_LITERAL_BYTES_KEY: schema.serialize().to_pybytes(),
    }


def _maybe_schema_from_literal_payload(obj: Mapping[str, Any]) -> _pa.Schema | None:
    if obj.get(_SCHEMA_LITERAL_TYPE_KEY) != _SCHEMA_LITERAL_SCHEMA_VALUE:
        return None

    serialized = obj.get(_SCHEMA_LITERAL_BYTES_KEY)
    if isinstance(serialized, _pa.Buffer):
        buffer = serialized
    elif isinstance(serialized, (bytes, bytearray, memoryview)):
        buffer = _pa.py_buffer(serialized)
    else:
        raise ValueError("Serialized schema payload must be bytes-like.")

    return _pa.ipc.read_schema(_pa.BufferReader(buffer))


if TYPE_CHECKING:
    from chalk._gen.chalk.expression.v1 import expression_pb2 as expr_pb
    from chalk.client.client_grpc import ChalkGRPCClient


# Custom stack container with Expr-aware equality for proper stack comparisons
class _LazyFrameStack(list):
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, _LazyFrameStack):
            return NotImplemented
        if len(self) != len(other):
            return False

        def _compare_element(a1: Any, a2: Any):
            if isinstance(a1, list):
                if isinstance(a2, list):
                    for a1_element, a2_element in zip(a1, a2):
                        if not _compare_element(a1_element, a2_element):
                            return False
                    return True
                else:
                    return False

            if isinstance(a1, dict):
                if isinstance(a2, dict):
                    if a1.keys() != a2.keys():
                        return False
                    for key in a1:
                        if not _compare_element(a1[key], a2[key]):
                            return False
                    return True
                else:
                    return False

            if isinstance(a1, Expr) and isinstance(a2, Expr):
                if not a1._structure_equals(a2):
                    return False
                return True
            elif isinstance(a1, Expr) or isinstance(a2, Expr):
                # types mismatch, but we cant coerce to bool so we need to
                # explicitly handle it
                return False
            else:
                return a1 == a2

        # compare each function call
        for (args1, kwargs1), (args2, kwargs2) in zip(self, other):
            if len(args1) != len(args2):
                return False

            # compare args to ensure they match
            for a1, a2 in zip(args1, args2):
                if not _compare_element(a1, a2):
                    return False

            # compare kwargs with short circuiting
            if kwargs1.keys() != kwargs2.keys():
                return False
            for key in kwargs1:
                if not _compare_element(kwargs1[key], kwargs2[key]):
                    return False
        return True


class LazyFrameM(type):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """
        Initialize the LazyFrameM instance.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.
        """
        super().__init__(*args, **kwargs)
        # print("LazyFrameM initialized with args:", args, "and kwargs:", kwargs)

    def __getattr__(self, item: str) -> Any:
        df = LazyFrame()
        return getattr(df, item)


class LazyFrame(metaclass=LazyFrameM):
    """Lazy DataFrame that builds query plans without immediate execution.

    LazyFrame records operations as a call stack and only executes them when
    explicitly requested. This allows for query optimization and deferred
    execution patterns.

    Examples
    --------
    >>> from chalkdf import LazyFrame
    >>> lf = LazyFrame()
    >>> result = lf.from_dict({"x": [1, 2, 3]}).filter(x=2).to_proto()
    """

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        """Initialize a new LazyFrame instance.

        Parameters
        ----------
        *args
            Positional arguments (reserved for future use).
        **kwargs
            Keyword arguments (reserved for future use).
        """
        super().__init__()

        self.stack: _LazyFrameStack = _LazyFrameStack()

    def __getattr__(self, item: str) -> Callable[..., LazyFrame]:
        def proxy(
            *args: Any,
            **kwargs: Any,
        ) -> LazyFrame:
            """
            Proxy method to handle attribute access.

            Args:
                *args: Positional arguments.
                **kwargs: Keyword arguments.
            """
            kwargs["_function_name"] = item
            self._push_call(*args, **kwargs)
            return self

        return proxy

    def _push_call(self, *args: Any, **kwargs: Any) -> None:
        """
        Push a call onto the stack.

        Args:
            *args: Positional arguments.
            **kwargs: Keyword arguments.
        """

        if "_function_name" not in kwargs:
            raise ValueError("_function_name is required in kwargs")

        self.stack.append((args, kwargs))

    def run(self, client: ChalkGRPCClient) -> _pa.RecordBatch:
        """Execute the lazy query plan via a gRPC client.

        Parameters
        ----------
        client
            ChalkGRPCClient instance to execute the plan.

        Returns
        -------
        PyArrow RecordBatch containing the query results.

        Examples
        --------
        >>> from chalkdf import LazyFrame
        >>> from chalk.client import ChalkGRPCClient
        >>> lf = LazyFrame().from_dict({"x": [1, 2, 3]})
        >>> client = ChalkGRPCClient()
        >>> result = lf.run(client)
        """
        res = client.execute_plan(lazy_frame_calls=self.to_proto())
        if res.errors:
            raise ValueError(res.errors)
        buffer = _pa.py_buffer(res.feather)
        reader = _pa.ipc.open_stream(buffer)
        return reader.read_next_batch()

    def _convert_to_df(self, *, base_df: DataFrame | None = None, catalog: ChalkSqlCatalog | None = None) -> DataFrame:
        el = DataFrame if base_df is None else base_df

        def _materialize(value: Any) -> Any:
            if isinstance(value, LazyFrame):
                return value._convert_to_df(catalog=catalog)
            if isinstance(value, tuple):
                return tuple(_materialize(item) for item in value)
            if isinstance(value, list):
                return [_materialize(item) for item in value]
            if isinstance(value, dict):
                return {k: _materialize(v) for k, v in value.items()}
            return value

        for head in self.stack:
            pos_args = head[0]
            kwargs = dict(head[1])
            if (fn := kwargs.get("_function_name", None)) is None:
                raise ValueError("_function_name is required in kwargs")

            if fn == "scan" and isinstance(kwargs.get("schema"), dict):
                maybe_schema = _maybe_schema_from_literal_payload(kwargs["schema"])
                if maybe_schema is not None:
                    kwargs["schema"] = maybe_schema

            del kwargs["_function_name"]
            pos_args = tuple(_materialize(arg) for arg in pos_args)
            kwargs = {k: _materialize(v) for k, v in kwargs.items()}
            if not hasattr(el, fn):
                raise ValueError(f"{fn} is not a valid function in {el.__name__}")
            if fn == "from_catalog_table":
                if catalog is None:
                    raise ValueError("catalog is required to use `from_catalog_table`, none was provided")
                kwargs["catalog"] = catalog
            el = getattr(el, fn)(
                *pos_args,
                **kwargs,
            )
        return cast(DataFrame, el)

    def _prepare_calls_for_proto(
        self, *, catalog: ChalkSqlCatalog | None
    ) -> list[tuple[tuple[Any, ...], dict[str, Any]]]:
        current_df: DataFrame | None = None
        prepared: list[tuple[tuple[Any, ...], dict[str, Any]]] = []

        for args, kwargs in self.stack:
            fn = kwargs.get("_function_name")
            if fn is None:
                raise ValueError("_function_name missing for LazyFrame stack entry")

            raw_kwargs = {k: v for k, v in kwargs.items() if k != "_function_name"}
            raw_args = tuple(args)

            if current_df is not None:
                schema: Mapping[str, _pa.DataType] = current_df.get_plan().schema_dict
                args_prepared = self._maybe_convert_call_args(fn, raw_args, schema)
                kwargs_prepared = self._maybe_convert_call_kwargs(fn, raw_kwargs, schema)
            else:
                args_prepared = raw_args
                kwargs_prepared = raw_kwargs

            prepared.append((args_prepared, {**kwargs_prepared, "_function_name": fn}))

            eval_args = args_prepared if current_df is not None else raw_args
            eval_kwargs = dict(kwargs_prepared if current_df is not None else raw_kwargs)

            if current_df is None:
                eval_target: Callable[..., Any] | None = getattr(DataFrame, fn, None)
            else:
                eval_target = getattr(current_df, fn, None)

            if eval_target is None:
                continue

            if fn == "from_catalog_table" and "catalog" not in eval_kwargs:
                if catalog is None:
                    # Cannot evaluate without catalog; skip schema propagation.
                    continue
                eval_kwargs["catalog"] = catalog

            eval_args = tuple(self._replace_lazyframes(arg, catalog) for arg in eval_args)
            eval_kwargs = {k: self._replace_lazyframes(v, catalog) for k, v in eval_kwargs.items()}

            try:
                result = eval_target(*eval_args, **eval_kwargs)
            except Exception:
                continue
            else:
                if isinstance(result, DataFrame):
                    current_df = result

        return prepared

    def _maybe_convert_call_args(
        self, fn: str, args: tuple[Any, ...], schema: Mapping[str, _pa.DataType]
    ) -> tuple[Any, ...]:
        if not args:
            return tuple()
        if fn in {"with_columns", "project"}:
            converted_args = []
            for arg in args:
                if isinstance(arg, Mapping):
                    converted_args.append(
                        {
                            self._get_alias_or_default(k, v, schema): self._convert_expr_tree_with_alias(v, schema)
                            for k, v in arg.items()
                        }
                    )
                    continue
                if isinstance(arg, tuple) and len(arg) == 2 and isinstance(arg[0], str):
                    converted_args.append({arg[0]: self._convert_expr_tree_with_alias(arg[1], schema)})
                    continue

                Underscore = _get_underscore_cls()
                if Underscore is not None and isinstance(arg, Underscore):
                    from .underscore_conversion.convert_underscore_to_expr import convert_underscore_to_expr_with_alias

                    expr, alias = convert_underscore_to_expr_with_alias(arg, schema)
                    if alias is None:
                        raise ValueError("Positional underscore expressions for with_columns/project must call alias()")
                    converted_args.append({alias: expr})
                    continue

                expr = self._convert_expr_tree_with_alias(arg, schema)
                if isinstance(expr, Expr):
                    raise ValueError(
                        "Positional with_columns/project expressions must include an alias for the column name"
                    )
                converted_args.append(expr)
            return tuple(converted_args)
        if fn == "filter":
            converted = [self._convert_expr_tree(args[0], schema)]
            converted.extend(args[1:])
            return tuple(converted)
        return args

    def _maybe_convert_call_kwargs(
        self, fn: str, kwargs: dict[str, Any], schema: Mapping[str, _pa.DataType]
    ) -> dict[str, Any]:
        if not kwargs:
            return {}
        if fn in {"with_columns", "project"}:
            return {
                self._get_alias_or_default(k, v, schema): self._convert_expr_tree_with_alias(v, schema)
                for k, v in kwargs.items()
            }
        if fn == "filter":
            return {k: self._convert_expr_tree(v, schema) if k == "expr" else v for k, v in kwargs.items()}
        return dict(kwargs)

    def _convert_expr_tree_with_alias(self, value: Any, schema: Mapping[str, _pa.DataType]) -> Any:
        Underscore = _get_underscore_cls()
        if Underscore is not None and isinstance(value, Underscore):
            from .underscore_conversion.convert_underscore_to_expr import convert_underscore_to_expr_with_alias

            expr, _ = convert_underscore_to_expr_with_alias(value, schema)
            return expr
        return self._convert_expr_tree(value, schema)

    def _get_alias_or_default(self, key: str, value: Any, schema: Mapping[str, _pa.DataType]) -> str:
        Underscore = _get_underscore_cls()
        if Underscore is not None and isinstance(value, Underscore):
            from .underscore_conversion.convert_underscore_to_expr import convert_underscore_to_expr_with_alias

            _, alias = convert_underscore_to_expr_with_alias(value, schema)
            if alias is not None:
                return alias
        return key

    def _convert_expr_tree(self, value: Any, schema: Mapping[str, _pa.DataType]) -> Any:
        Underscore = _get_underscore_cls()

        if isinstance(value, Expr):
            return value
        if isinstance(value, LazyFrame):
            return value
        if Underscore is not None and isinstance(value, Underscore):
            from .underscore_conversion.convert_underscore_to_expr import convert_underscore_to_expr

            return convert_underscore_to_expr(value, schema)
        if isinstance(value, list):
            return [self._convert_expr_tree(v, schema) for v in value]
        if isinstance(value, tuple):
            return tuple(self._convert_expr_tree(v, schema) for v in value)
        if isinstance(value, dict):
            return {k: self._convert_expr_tree(v, schema) for k, v in value.items()}
        return value

    def _replace_lazyframes(self, value: Any, catalog: ChalkSqlCatalog | None) -> Any:
        if isinstance(value, LazyFrame):
            return value._convert_to_df(catalog=catalog)
        if isinstance(value, list):
            return [self._replace_lazyframes(v, catalog) for v in value]
        if isinstance(value, tuple):
            return tuple(self._replace_lazyframes(v, catalog) for v in value)
        if isinstance(value, dict):
            return {k: self._replace_lazyframes(v, catalog) for k, v in value.items()}
        return value

    def to_proto(self, *, catalog: ChalkSqlCatalog | None = None) -> expr_pb.LogicalExprNode:
        """
        Convert this LazyFrame's call stack into a nested LogicalExprNode proto.

        Each entry in the stack becomes an ExprCall, chained via get_attribute on the previous node.
        Provide `catalog` when using `from_catalog_table` and underscore expressions so we can resolve schema.
        """
        expr_pb = _get_expr_pb()
        PrimitiveFeatureConverter = _get_primitive_feature_converter()
        prepared_calls = self._prepare_calls_for_proto(catalog=catalog)

        def _wrap_arg(kind: str, payload: expr_pb.LogicalExprNode) -> expr_pb.LogicalExprNode:
            if not _USE_ARG_WRAPPER:
                return payload
            kind_scalar = _pa.scalar(kind)
            kind_pb = PrimitiveFeatureConverter.from_pyarrow_to_protobuf(kind_scalar)
            kind_lit = expr_pb.LogicalExprNode(
                literal_value=expr_pb.ExprLiteral(value=kind_pb, is_arrow_scalar_object=False)
            )
            return expr_pb.LogicalExprNode(
                call=expr_pb.ExprCall(
                    func=expr_pb.LogicalExprNode(identifier=expr_pb.Identifier(name=_ARG_WRAPPER_FUNC)),
                    kwargs={"kind": kind_lit, "value": payload},
                )
            )

        # Helper to wrap a Python/pyarrow value into a literal LogicalExprNode
        def _val_to_node(val: Any) -> expr_pb.LogicalExprNode:
            # LazyFrame nested as argument: embed its full proto
            if isinstance(val, LazyFrame):
                return _wrap_arg("lazyframe", val.to_proto(catalog=catalog))

            # pyarrow.RecordBatch or Table -> list of struct arrow ScalarValue literal
            if isinstance(val, (_pa.RecordBatch, _pa.Table)):
                rows = val.to_pylist()
                pa_scalar = _pa.scalar(rows)
                pb_scalar = PrimitiveFeatureConverter.from_pyarrow_to_protobuf(pa_scalar)
                lit = expr_pb.ExprLiteral(value=pb_scalar, is_arrow_scalar_object=True)
                return _wrap_arg("literal", expr_pb.LogicalExprNode(literal_value=lit))

            if isinstance(val, _pa.Schema):
                schema_payload = _schema_to_literal_payload(val)
                payload = _val_to_node(schema_payload)
                # schema_payload returns a dict wrapper, so unwrap one level
                if (
                    payload.HasField("call")
                    and payload.call.func.HasField("identifier")
                    and payload.call.func.identifier.name == "chalk_lazy_arg"
                ):
                    payload = payload.call.kwargs["value"]
                return _wrap_arg("schema", payload)

            # assume the keys are strings and the values need to be converted
            if isinstance(val, dict):
                converted_values = {k: _val_to_node(v) for k, v in val.items()}
                return _wrap_arg(
                    "literal",
                    expr_pb.LogicalExprNode(
                        call=expr_pb.ExprCall(
                            func=expr_pb.LogicalExprNode(identifier=expr_pb.Identifier(name="dict")),
                            kwargs=converted_values,
                        )
                    ),
                )

            if isinstance(val, Expr):
                return _wrap_arg("expr", expr_pb.LogicalExprNode.FromString(val.to_proto_bytes()))

            # Primitive or pyarrow.Scalar -> arrow ScalarValue literal
            try:
                is_arrow = isinstance(val, _pa.Scalar)
                pa_scalar = val if is_arrow else _pa.scalar(val)
                pb_scalar = PrimitiveFeatureConverter.from_pyarrow_to_protobuf(pa_scalar)
                lit = expr_pb.ExprLiteral(value=pb_scalar, is_arrow_scalar_object=is_arrow)
                return _wrap_arg("literal", expr_pb.LogicalExprNode(literal_value=lit))
            except Exception:
                raise ValueError(f"Cannot convert argument to proto literal: {val!r}")

        node: expr_pb.LogicalExprNode | None = None
        # iterate through recorded calls in order
        for args, kwargs in prepared_calls:
            fn = kwargs.get("_function_name")
            # copy kwargs except internal marker
            kw = {k: v for k, v in kwargs.items() if k != "_function_name"}
            # build argument protos
            args_nodes = [_val_to_node(a) for a in args]
            kwargs_nodes = {k: _val_to_node(v) for k, v in kw.items()}

            # prepare the function expression: method call on previous node or base frame
            parent = node or expr_pb.LogicalExprNode(identifier=expr_pb.Identifier(name="chalk_data_frame"))
            get_attr = expr_pb.ExprGetAttribute(parent=parent, attribute=expr_pb.Identifier(name=fn))
            func_node = expr_pb.LogicalExprNode(get_attribute=get_attr)

            # build this call node
            call_node = expr_pb.ExprCall(func=func_node, args=args_nodes, kwargs=kwargs_nodes)
            node = expr_pb.LogicalExprNode(call=call_node)

        # if no calls, return bare frame identifier
        return node or expr_pb.LogicalExprNode(identifier=expr_pb.Identifier(name="chalk_data_frame"))

    def _to_proto(self):
        return self.to_proto()

    @classmethod
    def from_proto_str(cls: Type[LazyFrame], node_bytes: bytes) -> LazyFrame:
        """Reconstruct a LazyFrame from serialized protobuf bytes.

        Parameters
        ----------
        node_bytes
            Serialized LogicalExprNode protobuf bytes.

        Returns
        -------
        LazyFrame reconstructed from the protobuf representation.

        Examples
        --------
        >>> from chalkdf import LazyFrame
        >>> lf = LazyFrame().from_dict({"x": [1, 2, 3]})
        >>> proto_bytes = lf.to_proto().SerializeToString()
        >>> restored_lf = LazyFrame.from_proto_str(proto_bytes)
        """
        expr_pb = _get_expr_pb()

        return cls.from_proto(expr_pb.LogicalExprNode.FromString(node_bytes))

    @classmethod
    def from_proto(cls: Type[LazyFrame], node: expr_pb.LogicalExprNode) -> LazyFrame:
        """Reconstruct a LazyFrame from its LogicalExprNode proto.

        Traverses nested ExprCall/get_attribute to repopulate the call stack.

        Parameters
        ----------
        node
            LogicalExprNode protobuf message created by to_proto().

        Returns
        -------
        LazyFrame with the call stack restored from the proto representation.

        Examples
        --------
        >>> from chalkdf import LazyFrame
        >>> lf = LazyFrame().from_dict({"x": [1, 2, 3]})
        >>> proto = lf.to_proto()
        >>> restored_lf = LazyFrame.from_proto(proto)
        """
        PrimitiveFeatureConverter = _get_primitive_feature_converter()

        def _proto_type_to_pa(dtype_node: Any) -> _pa.DataType | None:
            if hasattr(dtype_node, "int64") and dtype_node.HasField("int64"):
                return _pa.int64()
            if hasattr(dtype_node, "int32") and dtype_node.HasField("int32"):
                return _pa.int32()
            if hasattr(dtype_node, "float64") and dtype_node.HasField("float64"):
                return _pa.float64()
            if hasattr(dtype_node, "float32") and dtype_node.HasField("float32"):
                return _pa.float32()
            if hasattr(dtype_node, "utf8") and dtype_node.HasField("utf8"):
                return _pa.string()
            if hasattr(dtype_node, "large_utf8") and dtype_node.HasField("large_utf8"):
                return _pa.large_string()
            if hasattr(dtype_node, "bool") and dtype_node.HasField("bool"):
                return _pa.bool_()
            return None

        def _decode_literal_node(n: expr_pb.LogicalExprNode) -> Any:
            if n.HasField("literal_value"):
                lit = n.literal_value
                pa_scalar = PrimitiveFeatureConverter.from_protobuf_to_pyarrow(lit.value)
                if lit.is_arrow_scalar_object:
                    try:
                        if (
                            _pa.types.is_list(pa_scalar.type)
                            and _pa.types.is_struct(pa_scalar.type.value_type)
                            and isinstance(pa_scalar.as_py(), list)
                        ):
                            return _pa.Table.from_pylist(pa_scalar.as_py())
                    except Exception:
                        pass
                    return pa_scalar
                return pa_scalar.as_py()
            if n.HasField("call") and n.call.func.HasField("identifier") and n.call.func.identifier.name == "dict":
                dict_value = {k: _node_to_val(v) for k, v in n.call.kwargs.items()}
                schema_value = _maybe_schema_from_literal_payload(dict_value)
                if schema_value is not None:
                    return schema_value
                return dict_value
            raise ValueError("not a literal")

        def _decode_legacy_cast(node: expr_pb.LogicalExprNode) -> Expr | None:
            if not (node.HasField("call") and node.call.func.HasField("identifier")):
                return None
            if node.call.func.identifier.name != "cast":
                return None
            if len(node.call.args) < 2:
                return None
            first_arg = node.call.args[0]
            target_type = (
                _proto_type_to_pa(first_arg.typed_identifier.type) if first_arg.HasField("typed_identifier") else None
            )
            expr_arg = _node_to_expr(node.call.args[-1])
            if target_type is None or expr_arg is None:
                return None
            return Expr.cast(expr_arg, target_type)

        def _node_to_expr(node: expr_pb.LogicalExprNode) -> Expr | None:
            if node.HasField("typed_identifier"):
                dtype = _proto_type_to_pa(node.typed_identifier.type) or _pa.string()
                return Expr.column(node.typed_identifier.name, dtype)
            if node.HasField("literal_value"):
                lit_val = PrimitiveFeatureConverter.from_protobuf_to_pyarrow(node.literal_value.value)
                if node.literal_value.is_arrow_scalar_object:
                    if isinstance(lit_val, _pa.Scalar):
                        return Expr.lit(lit_val)
                return Expr.lit(_pa.scalar(lit_val))
            try:
                return Expr.from_proto(node)
            except Exception:
                legacy = _decode_legacy_cast(node)
                if legacy is not None:
                    return legacy

            if node.HasField("call") and node.call.func.HasField("identifier"):
                fn_name = node.call.func.identifier.name
                expr_args: list[Expr] = []
                for arg in node.call.args:
                    expr_arg = _node_to_expr(arg)
                    if expr_arg is None:
                        return None
                    expr_args.append(expr_arg)

                expr_fn = getattr(Expr, fn_name, None)
                if callable(expr_fn):
                    try:
                        return expr_fn(*expr_args)
                    except Exception:
                        pass

                if expr_args and hasattr(expr_args[0], fn_name):
                    method = getattr(expr_args[0], fn_name)
                    if callable(method):
                        try:
                            return method(*expr_args[1:])
                        except Exception:
                            return None

            return None

        def _node_to_val(n: expr_pb.LogicalExprNode) -> Any:
            if (
                n.HasField("call")
                and n.call.func.HasField("identifier")
                and n.call.func.identifier.name == _ARG_WRAPPER_FUNC
            ):
                kind_node = n.call.kwargs.get("kind")
                value_node = n.call.kwargs.get("value")
                kind = None
                if kind_node and kind_node.HasField("literal_value"):
                    kind_pa = PrimitiveFeatureConverter.from_protobuf_to_pyarrow(kind_node.literal_value.value)
                    kind = kind_pa.as_py()
                if kind == "expr":
                    return _node_to_expr(value_node)
                if kind == "lazyframe":
                    return cls.from_proto(value_node)
                if kind == "schema":
                    schema_value = _maybe_schema_from_literal_payload(_node_to_val(value_node))
                    if schema_value is not None:
                        return schema_value
                if kind == "literal":
                    return _node_to_val(value_node)
                # Fallback to legacy handling if kind missing

            try:
                return _decode_literal_node(n)
            except Exception:
                pass

            expr_val = _node_to_expr(n)
            if expr_val is not None:
                return expr_val

            if n.HasField("call"):
                func = n.call.func
                if (
                    func.HasField("get_attribute")
                    and func.get_attribute.parent.HasField("identifier")
                    and func.get_attribute.parent.identifier.name == "chalk_data_frame"
                ):
                    return cls.from_proto(n)
            if n.HasField("get_attribute"):
                parent = n.get_attribute.parent
                if parent.HasField("identifier") and parent.identifier.name == "chalk_data_frame":
                    return cls.from_proto(n)

            raise ValueError(f"Unsupported literal node for LazyFrame.from_proto: {n}")

        lf = cls()
        # collect (args, kwargs, fn) entries in reverse order
        calls: list[tuple[tuple[Any, ...], dict[str, Any], str]] = []
        cur = node
        # unwind nested calls
        while True:
            if cur.HasField("call"):
                call = cur.call
                fn = None
                func = call.func
                if func.HasField("get_attribute"):
                    fn = func.get_attribute.attribute.name
                    parent = func.get_attribute.parent
                elif func.HasField("identifier"):
                    name = func.identifier.name
                    if name == "chalk_data_frame":
                        # reached base, stop unwinding
                        break
                    fn = name
                    parent = None
                else:
                    break

                # decode args/kwargs
                args = tuple(_node_to_val(a) for a in call.args)
                kwargs = {k: _node_to_val(v) for k, v in call.kwargs.items()}
                calls.append((args, kwargs, fn))
                # move up to parent for next iteration
                if func.HasField("get_attribute") and parent is not None:
                    cur = parent
                    continue
            break

        # rebuild stack in original order
        for args, kwargs, fn in reversed(calls):
            kwargs = {**kwargs, "_function_name": fn}
            lf.stack.append((args, kwargs))
        return lf

    @classmethod
    def plan_from_proto_str(cls: Type[LazyFrame], node_bytes: bytes, catalog: ChalkSqlCatalog | None) -> ChalkTable:
        """Convert serialized protobuf bytes directly to a ChalkTable plan.

        Parameters
        ----------
        node_bytes
            Serialized LogicalExprNode protobuf bytes.
        catalog
            Optional ChalkSqlCatalog for resolving table references.

        Returns
        -------
        ChalkTable query plan ready for execution.

        Examples
        --------
        >>> from chalkdf import LazyFrame
        >>> lf = LazyFrame().from_dict({"x": [1, 2, 3]})
        >>> proto_bytes = lf.to_proto().SerializeToString()
        >>> plan = LazyFrame.plan_from_proto_str(proto_bytes, catalog=None)
        """
        expr_pb = _get_expr_pb()

        return cls.plan_from_proto(expr_pb.LogicalExprNode.FromString(node_bytes), catalog=catalog)

    @classmethod
    def plan_from_proto(
        cls: Type[LazyFrame], node: expr_pb.LogicalExprNode, catalog: ChalkSqlCatalog | None = None
    ) -> ChalkTable:
        """Convert a LogicalExprNode proto to a ChalkTable plan.

        Parameters
        ----------
        node
            LogicalExprNode protobuf message.
        catalog
            Optional ChalkSqlCatalog for resolving table references.

        Returns
        -------
        ChalkTable query plan ready for execution.

        Examples
        --------
        >>> from chalkdf import LazyFrame
        >>> lf = LazyFrame().from_dict({"x": [1, 2, 3]})
        >>> proto = lf.to_proto()
        >>> plan = LazyFrame.plan_from_proto(proto)
        """
        expr_pb = _get_expr_pb()

        if not isinstance(node, expr_pb.LogicalExprNode):
            raise TypeError(
                "LazyFrame.from_proto expects an instance of "
                "`chalk._gen.chalk.expression.v1.expression_pb2.LogicalExprNode`."
            )
        lazy_frame = LazyFrame.from_proto(node)
        df = lazy_frame._convert_to_df(catalog=catalog)
        res = df.get_plan()
        return res

    def __repr__(self) -> str:
        if not self.stack:
            return "LazyFrame()"
        lines: list[str] = ["LazyFrame(", "    chalk_data_frame"]
        for args, kwargs in self.stack:
            fn = kwargs.get("_function_name")
            kw = {k: v for k, v in kwargs.items() if k != "_function_name"}
            args_repr = ", ".join(repr(a) for a in args)
            kwargs_repr = ", ".join(f"{k}={v!r}" for k, v in kw.items())
            all_args = ", ".join(x for x in (args_repr, kwargs_repr) if x)
            lines.append(f"    .{fn}({all_args})")
        lines.append(")")
        return "\n".join(lines)

    __str__ = __repr__

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, LazyFrame):
            return NotImplemented

        if self.stack == other.stack:
            return True

        try:
            # Fallback to proto-level comparison so underscore-based plans and
            # deserialized plans (which may contain Expr objects) are treated
            # as equivalent when they serialize to the same logical plan.
            return self.to_proto() == other.to_proto()
        except Exception:
            return False
