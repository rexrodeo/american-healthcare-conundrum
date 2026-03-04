#!/bin/bash
# ============================================================
# Medicare OTC Drug Analysis — Environment Setup
# Mac Mini M4 (Apple Silicon), macOS
# ============================================================
# Run this once to bootstrap your Python + DuckDB environment.
# Assumes you have Homebrew installed. If not: https://brew.sh

set -e

echo "==> Installing Python 3.12 via Homebrew (if needed)..."
brew install python@3.12 || true

echo "==> Creating virtual environment..."
python3.12 -m venv .venv
source .venv/bin/activate

echo "==> Installing dependencies..."
pip install --upgrade pip
pip install \
    duckdb \
    pandas \
    requests \
    tqdm \
    rich \
    pyarrow \
    matplotlib \
    seaborn \
    jupyterlab

echo "==> Verifying DuckDB..."
python -c "import duckdb; print(f'DuckDB version: {duckdb.__version__}')"

echo ""
echo "✅  Setup complete!"
echo "    Activate your environment any time with: source .venv/bin/activate"
echo "    Then run: python 02_download_data.py"
