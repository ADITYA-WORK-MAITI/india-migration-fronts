#!/usr/bin/env bash
# Install packages and pull the counts from the GBIF API (about 5 minutes, 3 x 504 small requests).
# The counts used for the saved results are already in data/; delete them to force a fresh pull.
# GBIF's eBird dataset grows daily, so a fresh pull gives slightly different counts from the ones
# used in results/ (pulled 2026-11-21). The conclusions should not change.
set -euo pipefail
cd "$(dirname "$0")"
pip install -r requirements.txt
mkdir -p data
[ -f data/counts_2015_2025.json ] || python3 src/pull_counts.py 2015,2025 data/counts_2015_2025.json
[ -f data/counts_2015_2020.json ] || python3 src/pull_counts.py 2015,2020 data/counts_2015_2020.json
[ -f data/counts_2021_2025.json ] || python3 src/pull_counts.py 2021,2025 data/counts_2021_2025.json
echo "setup done"
