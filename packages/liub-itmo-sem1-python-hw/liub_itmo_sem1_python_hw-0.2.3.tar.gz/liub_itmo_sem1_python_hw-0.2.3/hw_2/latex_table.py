from __future__ import annotations


def render_table_document(
    rows: list[list[object]],
    *,
    caption: str | None = "Caption",
    label: str | None = "tab:mytab",
    extra_blocks: list[str] | None = None,
) -> str:
    if not rows or not rows[0]:
        raise ValueError("Table can't be empty")

    cols_len = len(rows[0])
    align = " ".join("c" for _ in range(cols_len))

    def row_format(row: list[object]) -> str:
        cells = [str(cell) for cell in row[:cols_len]]
        if len(cells) < cols_len:
            cells.extend("" for _ in range(cols_len - len(cells)))

        return " & ".join(cells) + r" \\"

    table = [
        rf"\begin{{tabular}}{{{align}}}",
        r"\toprule",
        row_format(rows[0]),
        r"\midrule",
        *[row_format(row) for row in rows[1:]],
        r"\bottomrule",
        r"\end{tabular}",
    ]

    doc = [
        r"\documentclass{article}",
        r"\usepackage{booktabs}",
        r"\usepackage{graphicx}",
        r"\begin{document}",
        r"\begin{table}[ht]",
        r"\centering",
        *table,
    ]
    if caption:
        doc.append(rf"\caption{{{caption}}}")
    if label:
        doc.append(rf"\label{{{label}}}")
    doc.append(r"\end{table}")

    if extra_blocks:
        doc.extend(extra_blocks)
    doc.extend([r"\end{document}", ""])

    return "\n".join(doc)


def render_image_block(
    image_path: str,
    *,
    caption: str | None = None,
    label: str | None = None,
    width: str = r"0.6\textwidth",
) -> list[str]:
    block = [
        r"\begin{figure}[ht]",
        r"\centering",
        rf"\includegraphics[width={width}]{{{image_path}}}",
    ]

    if caption:
        block.append(rf"\caption{{{caption}}}")
    if label:
        block.append(rf"\label{{{label}}}")

    block.append(r"\end{figure}")
    return block
