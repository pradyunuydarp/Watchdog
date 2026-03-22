# Watchdog Docs (LaTeX + PlantUML)

This folder contains the architecture and design documents in LaTeX, with diagrams authored in PlantUML.

## Files

- `watchdog-architecture.tex`: system overview + feature list + architecture prototypes
- `watchdog-design.tex`: deeper service-level design for the chosen target (kept prototype-friendly for now)
- `common/preamble.tex`: shared LaTeX preamble
- `sections/`: shared sections included by the docs

## Diagrams

PlantUML sources live in `docs/diagrams/puml/` and rendered images in `docs/diagrams/images/`.

To (re)render images locally:

```bash
./docs/diagrams/render.sh
```

If a LaTeX toolchain is installed, the same script also builds PDFs into `docs/latex/out/` (prefers `tectonic`, falls back to `pdflatex`).
To force offline builds with `tectonic` (no downloads), run `WATCHDOG_TECTONIC_OFFLINE=1 ./docs/diagrams/render.sh`.

## Building PDFs

This repo does not currently include a LaTeX toolchain. Install one of the following:

- `tectonic` (recommended: single binary; downloads a TeX bundle on first run)
- macOS: MacTeX (`pdflatex`) or TeX Live
- Linux: texlive-latex-base + texlive-latex-extra

Then build:

```bash
cd docs/latex
mkdir -p out
tectonic -o out watchdog-architecture.tex
tectonic -o out watchdog-design.tex
```

Or using `pdflatex`:

```bash
cd docs/latex
pdflatex -interaction=nonstopmode watchdog-architecture.tex
pdflatex -interaction=nonstopmode watchdog-design.tex
```
