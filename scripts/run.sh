#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
export PYTHONPATH=src

python -m comp6651.main --run-sims --dataset-dir data/dataset/ --out outputs/
