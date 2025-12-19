FROM python:3.14-slim

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    texlive-latex-base \
    texlive-latex-recommended \
    texlive-pictures \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app/hw_2

RUN python -m pip install --no-cache-dir typer

ENV PYTHONPATH=/app/hw_2

# Expected runtime mounts:
# - /input/table.csv
# - /input/image.png
# - /output/ (directory)
RUN mkdir -p /input /output

CMD ["python", "-m", "gen_latex.cli", "/output/output.tex", "--table", "/input/table.csv", "--image", "/input/image.png", "--pdf"]
