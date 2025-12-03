#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=src
# Run with true randomness by default (no fixed seed). To reproduce results, add: --seed <int>
python -m comp6651.main --run-sims --dataset-dir data/dataset/ --out outputs/
