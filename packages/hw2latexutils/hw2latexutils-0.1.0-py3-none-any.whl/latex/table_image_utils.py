from pathlib import Path
from typing import Iterable


def array2latex(
    data: list[list[str]],
    align: str = "l",
    hline: bool = True,
    caption: str | None = None,
) -> str:
    table = []
    rows = []

    if caption:
        table.append(r"\begin{table}[H]")
        table.append(rf"\caption{{{caption}}}")
        table.append(r"\begin{center}")

    for i, row in enumerate(data):
        rows.append(" & ".join(map(str, row)) + r" \\")
        if hline and i == 0:
            rows.append(r"\hline")

    ncols = max(len(row) for row in data)
    colspec = align * ncols if len(align) == 1 else align

    table.extend([rf"\begin{{tabular}}{{{colspec}}}", *rows, r"\end{tabular}"])

    if caption:
        table.append(r"\end{center}")
        table.append(r"\end{table}")

    return "\n".join(table)


def figure_latex(
    image_path: str | Path,
    caption: str | None = None,
    width: str = r"\textwidth",
) -> str:
    image_str = str(image_path)

    figure_lines: list[str] = [
        r"\begin{figure}[H]",
        r"\centering",
        rf"\includegraphics[width={width}]{{{image_str}}}",
    ]

    if caption:
        figure_lines.append(rf"\caption{{{caption}}}")

    figure_lines.append(r"\end{figure}")

    return "\n".join(figure_lines)


def document_with_table_and_image(
    table_data: list[list[str]],
    table_align: str = "l",
    table_hline: bool = True,
    table_caption: str | None = None,
    image_path: str | Path = "image.png",
    image_caption: str | None = None,
    document_title: str = "Задание 2",
    extra_preamble: Iterable[str] | None = None,
) -> str:
    preamble: list[str] = [
        r"\documentclass{article}",
        r"\usepackage[russian]{babel}",
        r"\usepackage[utf8]{inputenc}",
        r"\usepackage{graphicx}",
        r"\usepackage{float}",
    ]

    if extra_preamble:
        preamble.extend(extra_preamble)

    body: list[str] = [
        r"\begin{document}",
        "",
        document_title,
        "",
        array2latex(
            data=table_data,
            align=table_align,
            hline=table_hline,
            caption=table_caption,
        ),
        "",
        figure_latex(
            image_path=image_path,
            caption=image_caption,
            width=r"0.6\textwidth",
        ),
        "",
        r"\end{document}",
    ]

    return "\n".join([*preamble, "", *body])


__all__ = [
    "array2latex",
    "figure_latex",
    "document_with_table_and_image",
]
