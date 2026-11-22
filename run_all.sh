#!/usr/bin/env bash
# Rerun every analysis on the pulled counts. About 3 minutes.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p results figures
python3 src/fronts.py data/counts_2015_2025.json 0.5 0.5 main
python3 src/robustness.py
python3 src/name_species.py
python3 src/figure.py
echo "all done"
