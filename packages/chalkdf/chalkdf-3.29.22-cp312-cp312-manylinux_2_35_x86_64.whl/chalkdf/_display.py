from __future__ import annotations

import html
import math
import shutil
import typing
from dataclasses import dataclass

import pyarrow

MaterializedLike = pyarrow.RecordBatch | pyarrow.Table


DEFAULT_MAX_WIDTH = 32


def normalize_materialized_tables(tables: typing.Mapping[str, MaterializedLike]) -> dict[str, pyarrow.Table]:
    """Convert any RecordBatches into Tables for consistent handling."""

    normalized: dict[str, pyarrow.Table] = {}
    for name, table in tables.items():
        if isinstance(table, pyarrow.RecordBatch):
            normalized[name] = pyarrow.Table.from_batches([table])
        else:
            normalized[name] = table
    return normalized


def calc_table_width(col_widths: dict[str, int], n_cols: int | None = None) -> int:
    """Calculate total table width with current column widths
    Table structure: "│ " + col1 + " ┆ " + col2 + " ┆ " + ... + colN + " │"
    For n columns (Start: "│ " = 2 chars, Each column: width chars, Between columns: " ┆ " = 3 chars each, (n-1) times, End: " │" = 2 chars)
    Width = 2 + sum(widths) + 3*(n-1) + 2 = 4 + sum(widths) + 3*n - 3 = 1 + sum(widths) + 3*n"""
    if n_cols is None:
        n_cols = len(col_widths)
    return 1 + sum(col_widths.values()) + 3 * n_cols


@dataclass
class Column:
    type: str
    header_width: int
    content_width: int
    content: list[str]

    def width(self) -> int:
        return max(self.header_width, self.content_width)


def format_materialized_table(table: pyarrow.Table, head: int = 3, tail: int = 3) -> str:
    """Return a multiline preview string for a materialized Arrow table."""

    total_rows = table.num_rows
    total_cols = len(table.column_names)
    row_label = "row" if total_rows == 1 else "rows"
    col_label = "column" if total_cols == 1 else "columns"
    lines: list[str] = [f"DataFrame(materialized {total_rows} {row_label} x {total_cols} {col_label})"]

    if total_rows == 0:
        lines.append("No rows to display.")
        return "\n".join(lines)

    columns = [name for name in table.column_names]
    if not columns:
        lines.append("Showing all rows:")
        lines.append("(no columns)")
        return "\n".join(lines)

    column_dict = {
        name: Column(
            type=str(table.schema.field(i).type),
            header_width=max(len(str(table.schema.field(i).type)), len(name)),
            content_width=DEFAULT_MAX_WIDTH,
            content=[],
        )
        for i, name in enumerate(columns)
    }

    # Get terminal width
    terminal_width = shutil.get_terminal_size(fallback=(120, 24)).columns
    num_cols = len(columns)

    if total_rows <= head + tail:
        row_indices = list(range(total_rows))
        include_gap = False
    else:
        row_indices = list(range(head))
        row_indices.extend(range(total_rows - tail, total_rows))
        preview_prefix = (
            f"Showing first {head} row{'s' if head > 1 else ''} and last {tail} row{'s' if tail > 1 else ''}:"
        )
        include_gap = True
        lines.append(preview_prefix)

    preview_table = table.take(pyarrow.array(row_indices)) if row_indices else table.slice(0, 0)
    preview_data = preview_table.to_pydict()

    for name in columns:
        # Format values without truncation first
        max_width = 0

        for v in preview_data.get(name, []):
            formatted_value = _format_preview_value(v, max_width=None)
            column_dict[name].content.append(formatted_value)
            max_width = max(max_width, len(formatted_value))

        column_dict[name].content_width = max_width

    # Calculate initial column widths
    col_widths = {name: column_dict[name].width() for name in columns}
    current_width = calc_table_width(col_widths)

    # If table is too wide, remove central columns until it fits
    if current_width > terminal_width and num_cols > 1:
        # Keep removing central columns one at a time until we fit
        # Strategy: alternate removing from center-left and center-right
        display_columns = list(columns)

        while len(display_columns) > 1:
            # Calculate width if we had a "..." marker (3 chars)
            # We need to account for the marker column in our width calculation
            test_widths = {name: col_widths[name] for name in display_columns}
            test_widths["..."] = 3  # The marker column
            test_width = calc_table_width(test_widths, len(display_columns) + 1)

            if test_width <= terminal_width:
                break

            # Remove the middle column
            # If even number of columns, remove from center-right
            mid = len(display_columns) // 2
            display_columns.pop(mid)

        # Now add the "..." marker between the left and right columns
        if len(display_columns) < num_cols:
            # Split into left and right portions
            keep_start = (len(display_columns) + 1) // 2
            keep_end = len(display_columns) - keep_start

            # Reconstruct the column list with marker
            left_cols = display_columns[:keep_start]
            right_cols = display_columns[-keep_end:] if keep_end > 0 else []

            # Add marker column to column_dict
            column_dict["..."] = Column(
                type="...",
                header_width=3,
                content_width=3,
                content=["..."] * len(row_indices),
            )

            # Update columns and widths
            columns = left_cols + ["..."] + right_cols
            column_dict = {name: column_dict[name] for name in columns}
        else:
            # All columns fit
            columns = display_columns
            column_dict = {name: column_dict[name] for name in columns}

    # Build table with unicode box-drawing characters (polars style)
    # Top border: ┌─────┬─────┐
    top_border = "┌─" + "─┬─".join("─" * c.width() for c in column_dict.values()) + "─┐"
    lines.append(top_border)

    # Header row with column names
    header = "│ " + " ┆ ".join(name.ljust(c.width()) for name, c in column_dict.items()) + " │"
    lines.append(header)

    # Type row with separator (like polars --- separator)
    type_separator = "│ " + " ┆ ".join("─" * c.width() for c in column_dict.values()) + " │"
    lines.append(type_separator)

    # Type row with actual types
    lines.append("│ " + " ┆ ".join(c.type.ljust(c.width()) for c in column_dict.values()) + " │")

    # Header separator: ╞═════╪═════╡
    header_separator = "╞═" + "═╪═".join("═" * c.width() for c in column_dict.values()) + "═╡"
    lines.append(header_separator)

    split_index = min(head, len(row_indices))
    ellipsis_row = "│ " + " ┆ ".join("...".ljust(c.width()) for c in column_dict.values()) + " │"

    for idx in range(len(row_indices)):
        if include_gap and idx == split_index:
            lines.append(ellipsis_row)
        row_parts = [c.content[idx].ljust(c.width()) for c in column_dict.values()]
        lines.append("│ " + " ┆ ".join(row_parts) + " │")

    # Bottom border: └─────┴─────┘
    bottom_border = "└─" + "─┴─".join("─" * c.width() for c in column_dict.values()) + "─┘"
    lines.append(bottom_border)

    if include_gap:
        omitted = total_rows - head - tail
        if omitted > 0:
            lines.append(f"({omitted} more rows)")

    return "\n".join(lines)


def format_materialized_table_html(table: pyarrow.Table, head: int = 5, tail: int = 5) -> str:
    """Return an HTML table string for a materialized Arrow table."""
    total_rows = table.num_rows
    columns = table.column_names

    if total_rows == 0:
        return "<div><p>Empty DataFrame</p></div>"

    if total_rows <= head + tail:
        row_indices = list(range(total_rows))
        include_gap = False
    else:
        row_indices = list(range(head))
        row_indices.extend(range(total_rows - tail, total_rows))
        include_gap = True

    preview_table = table.take(pyarrow.array(row_indices)) if row_indices else table.slice(0, 0)
    preview_data = preview_table.to_pydict()

    html_parts = []
    html_parts.append('<div style="overflow-x: auto;">')
    html_parts.append('<table border="1" class="dataframe">')

    # Header
    html_parts.append("<thead>")
    html_parts.append('<tr style="text-align: right;">')
    for name in columns:
        html_parts.append(f"<th>{html.escape(name)}</th>")
    html_parts.append("</tr>")

    # Types
    html_parts.append("<tr>")
    for i in range(len(columns)):
        dtype = str(table.schema.field(i).type)
        html_parts.append(f"<th><small>{html.escape(dtype)}</small></th>")
    html_parts.append("</tr>")
    html_parts.append("</thead>")

    # Body
    html_parts.append("<tbody>")

    split_index = min(head, len(row_indices))

    for idx in range(len(row_indices)):
        if include_gap and idx == split_index:
            html_parts.append("<tr>")
            for _ in columns:
                html_parts.append("<td>...</td>")
            html_parts.append("</tr>")

        html_parts.append("<tr>")
        for name in columns:
            val = preview_data[name][idx]
            formatted = _format_preview_value(val, max_width=None)
            html_parts.append(f"<td>{html.escape(formatted)}</td>")
        html_parts.append("</tr>")

    html_parts.append("</tbody>")
    html_parts.append("</table>")

    # Footer info
    row_label = "row" if total_rows == 1 else "rows"
    total_cols = len(columns)
    col_label = "column" if total_cols == 1 else "columns"
    html_parts.append(f"<p>{total_rows} {row_label} x {total_cols} {col_label}</p>")
    html_parts.append("</div>")

    return "".join(html_parts)


def format_plan_summary(
    schema_dict: typing.Mapping[str, typing.Any],
    materialized_table_count: int,
) -> str:
    """Return a one-line summary for a logical plan."""

    column_names = list(schema_dict.keys())
    total_cols = len(column_names)
    col_label = "column" if total_cols == 1 else "columns"
    lines = [
        f"DataFrame(plan; {total_cols} {col_label}, {materialized_table_count} materialized table(s))",
    ]
    if column_names:
        preview_fields: list[str] = []
        for name in column_names[:5]:
            field = schema_dict[name]
            dtype = getattr(field, "type", field)
            preview_fields.append(f"{name} ({str(dtype)})")
        preview = ", ".join(preview_fields)
        if total_cols > 5:
            preview += ", ..."
        lines.append(f"Columns: {preview}")
    else:
        lines.append("Columns: (none)")
    return "\n".join(lines)


def _format_preview_value(value: typing.Any, max_width: int | None = DEFAULT_MAX_WIDTH) -> str:
    if value is None:
        return "null"
    if isinstance(value, float):
        if math.isnan(value):
            return "nan"
        if math.isinf(value):
            return "inf" if value > 0 else "-inf"
        return f"{value:.6g}"
    text = str(value)
    if max_width is not None and len(text) > max_width:
        return text[: max_width - 3] + "..."
    return text
