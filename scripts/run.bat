@echo off
cd /d "%~dp0\.."
set PYTHONPATH=src

python -m comp6651.main --run-sims --dataset-dir data/dataset/ --out outputs/
