#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${ROOT_DIR}/../.." && pwd)"
PUML_DIR="${ROOT_DIR}/puml"
IMG_DIR="${ROOT_DIR}/images"
LATEX_DIR="$(cd "${ROOT_DIR}/../latex" && pwd)"
PDF_OUT_DIR="${LATEX_DIR}/out"

mkdir -p "${IMG_DIR}"

plantuml -tpng -o "${IMG_DIR}" "${PUML_DIR}"/*.puml

echo "Rendered diagrams to ${IMG_DIR}"

if command -v tectonic >/dev/null 2>&1; then
  mkdir -p "${PDF_OUT_DIR}"
  echo "Building PDFs with tectonic to ${PDF_OUT_DIR}"

  build_with_tectonic() {
    local tex="$1"
    # Ensure caches live inside the repo (useful for sandboxed environments).
    export XDG_CACHE_HOME="${REPO_ROOT}/.cache"
    export TECTONIC_CACHE_DIR="${REPO_ROOT}/.cache/tectonic"
    mkdir -p "${TECTONIC_CACHE_DIR}"

    local log="${PDF_OUT_DIR}/tectonic-$(basename "${tex}" .tex).log"
    local offline="${WATCHDOG_TECTONIC_OFFLINE:-0}"

    run_tectonic() {
      # Prefer the modern CLI if available; fall back to older flags.
      local extra=()
      if [[ "${offline}" == "1" ]]; then
        extra+=(--only-cached)
      fi
      tectonic "${extra[@]}" "$@" -X compile --outdir "${PDF_OUT_DIR}" "${tex}" >"${log}" 2>&1 || \
        tectonic "${extra[@]}" "$@" -o "${PDF_OUT_DIR}" "${tex}" >"${log}" 2>&1
    }

    # First try the normal path (may download bundles on first run).
    if run_tectonic; then
      return 0
    fi

    # If the normal path fails (common in sandboxed environments), retry offline unless already offline.
    if [[ "${offline}" != "1" ]]; then
      if WATCHDOG_TECTONIC_OFFLINE=1 run_tectonic; then
        echo "tectonic succeeded in offline mode (--only-cached) for ${tex}"
        return 0
      fi
    fi

    echo "tectonic failed for ${tex}; see ${log}"
    tail -n 30 "${log}" || true
    return 1
  }

  if (
    cd "${LATEX_DIR}"
    build_with_tectonic watchdog-architecture.tex
    build_with_tectonic watchdog-architecture.tex
    build_with_tectonic watchdog-design.tex
    build_with_tectonic watchdog-design.tex
  ); then
    echo "Built PDFs in ${PDF_OUT_DIR}"
  else
    echo "tectonic failed; skipping PDF build (diagrams are still rendered)."
  fi
elif command -v pdflatex >/dev/null 2>&1; then
  mkdir -p "${PDF_OUT_DIR}"
  echo "Building PDFs with pdflatex to ${PDF_OUT_DIR}"

  (
    cd "${LATEX_DIR}"
    pdflatex -interaction=nonstopmode -halt-on-error -output-directory "${PDF_OUT_DIR}" watchdog-architecture.tex
    pdflatex -interaction=nonstopmode -halt-on-error -output-directory "${PDF_OUT_DIR}" watchdog-architecture.tex
    pdflatex -interaction=nonstopmode -halt-on-error -output-directory "${PDF_OUT_DIR}" watchdog-design.tex
    pdflatex -interaction=nonstopmode -halt-on-error -output-directory "${PDF_OUT_DIR}" watchdog-design.tex
  )

  echo "Built PDFs in ${PDF_OUT_DIR}"
else
  echo "No LaTeX engine found (tectonic/pdflatex); skipping PDF build."
fi
