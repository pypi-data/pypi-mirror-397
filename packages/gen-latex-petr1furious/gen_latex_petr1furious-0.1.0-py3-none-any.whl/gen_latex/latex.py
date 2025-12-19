from __future__ import annotations

from pathlib import Path


def _escape_latex(s: str) -> str:
    return (
        s.replace("\\", r"\textbackslash{}")
        .replace("&", r"\&")
        .replace("%", r"\%")
        .replace("$", r"\$")
        .replace("#", r"\#")
        .replace("_", r"\_")
        .replace("{", r"\{")
        .replace("}", r"\}")
        .replace("~", r"\textasciitilde{}")
        .replace("^", r"\textasciicircum{}")
    )


def generate_table(data: list[list[str]]) -> str:
    if not data:
        return ""

    cols = len(data[0])
    if cols == 0:
        return ""

    for row in data:
        if len(row) != cols:
            raise ValueError("All rows must have the same number of columns")

    col_spec = "|" + ("c|" * cols)
    rows = [
        " & ".join(_escape_latex(str(cell)) for cell in row) + r" \\"
        for row in data
    ]
    body = "\n\\hline\n".join(rows)
    return (
        f"\\begin{{tabular}}{{{col_spec}}}\n"
        f"\\hline\n"
        f"{body}\n"
        f"\\hline\n"
        f"\\end{{tabular}}"
    )


def generate_image(path: str | Path, *, width: str = r"0.8\textwidth") -> str:
    p = Path(path).as_posix()
    return (
        "\\begin{figure}[h]\n"
        "\\centering\n"
        f"\\includegraphics[width={width}]{{{p}}}\n"
        "\\end{figure}"
    )
