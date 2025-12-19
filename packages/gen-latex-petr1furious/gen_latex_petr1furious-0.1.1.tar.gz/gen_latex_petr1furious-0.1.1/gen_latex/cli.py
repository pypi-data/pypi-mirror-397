from __future__ import annotations

import csv
import subprocess
from pathlib import Path

import typer
from typing_extensions import Annotated

from .latex import generate_image, generate_table


app = typer.Typer(add_completion=False)


def _build_document(table_tex: str, image_tex: str) -> str:
    return (
        "\\documentclass{article}\n"
        "\\usepackage{graphicx}\n"
        "\\usepackage[margin=1in]{geometry}\n"
        "\\begin{document}\n"
        "\\begin{center}\n"
        f"{table_tex}\n"
        "\\end{center}\n"
        "\\bigskip\n"
        f"{image_tex}\n"
        "\\end{document}\n"
    )


def _run_pdflatex(tex_file: Path) -> None:
    subprocess.run(
        [
            "pdflatex",
            "-interaction=nonstopmode",
            "-halt-on-error",
            "-output-directory",
            str(tex_file.parent),
            str(tex_file),
        ],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.STDOUT,
    )


@app.command()
def main(
    table: Annotated[
        Path,
        typer.Option(
            "--table",
            "-t",
            help="CSV path",
        ),
    ],
    outfile: Annotated[
        Path, typer.Argument(metavar="output.tex",
                             help="Where to save the LaTeX file")
    ] = Path("artifacts/output.tex"),
    image: Annotated[
        Path, typer.Option(
            "--image", "-i", help="PNG path")
    ] = Path("artifacts/image.png"),
    pdf: Annotated[
        bool, typer.Option(
            "--pdf/--no-pdf", help="Run pdflatex to produce PDF")
    ] = False,
) -> None:
    with table.open("r", encoding="utf-8", newline="") as f:
        table_data = list(csv.reader(f))

    table_tex = generate_table(table_data)
    image_tex = generate_image(image)
    doc = _build_document(table_tex, image_tex)

    outfile.parent.mkdir(parents=True, exist_ok=True)
    outfile.write_text(doc)
    typer.echo(f"Saved LaTeX to {outfile}")

    if pdf:
        try:
            _run_pdflatex(outfile)
        except FileNotFoundError:
            raise typer.Exit(
                "pdflatex not found") from None
        except subprocess.CalledProcessError:
            raise typer.Exit(
                "pdflatex failed") from None
        typer.echo(f"Saved PDF to {outfile.with_suffix('.pdf')}")


if __name__ == "__main__":
    app()
