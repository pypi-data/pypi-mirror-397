#!/usr/bin/env python3

from typing import Sequence, List


def generate_table_latex(data: Sequence[Sequence[str]]) -> str:
    if not data:
        raise ValueError("data must contain at least one row")

    max_cols = max(len(row) for row in data)
    if max_cols == 0:
        raise ValueError("each row must contain at least one cell")

    col_widths: List[int] = [0] * max_cols
    for row in data:
        for i in range(max_cols):
            cell = str(row[i]) if i < len(row) else ""
            col_widths[i] = max(col_widths[i], len(cell))

    col_spec = "l" * max_cols

    lines: List[str] = []
    lines.append(r"\begin{tabular}{" + col_spec + "}")
    lines.append(r"\hline")

    for row in data:
        padded_cells: List[str] = []
        for i in range(max_cols):
            cell = str(row[i]) if i < len(row) else ""
            padded_cells.append(cell.ljust(col_widths[i]))
        lines.append(" & ".join(padded_cells) + r" \\")
        lines.append(r"\hline")

    lines.append(r"\end{tabular}")

    return "\n".join(lines)

def generate_image_latex(image_path: str) -> str:
    lines: list[str] = []
    lines.append(r"\begin{figure}[h!]")
    lines.append(r"  \centering")
    lines.append(rf"  \includegraphics[width=0.8\textwidth]{{{image_path}}}")
    lines.append(r"\end{figure}")

    return "\n".join(lines)