# COMP 6651 Project: Online Graph Coloring

This repository contains our COMP 6651 Fall 2025 project on greedy algorithms for online graph coloring.

Highlights
- No external graph libraries; pure Python standard library only.
- Implements: random k-colorable graph generator, FirstFit, CBIP (k=2), a full-ordered heuristic variant for FirstFit, and a batch-ordered variant for FirstFit.
- Reproducible simulations via pre-generated immutable dataset of graphs + vertex arrival orders.
- CSV outputs suitable for inclusion in the report.

## Repo layout
- `src/comp6651/`: source code package
  - `graph.py`: Graph data structure and utilities (connected component, bipartition)
  - `algorithms/first_fit.py`: FirstFit algorithm, Full-ordered heuristic variant
  - `algorithms/cbip.py`: CBIP algorithm (for bipartite graphs)
  - `algorithms/batched.py` Batch-ordered variant for FirstFit.
  - `generator/generate.py`: Random online k-colorable graph generator and EDGES I/O
  - `simulations.py`: Batch runners to reproduce tables
  - `metrics.py`: Competitive ratio and statistics helpers
  - `main.py`: CLI entry point
- `tests/`: unit tests using Python's built-in `unittest`
- `notebooks/plot_results.ipynb`: Notebook for producing figures from the results
- `scripts/run.sh`: convenience runner
- `data/datset`: All generated EDGES and ORDER files

## Reproduce
Prerequisites: Python 3.13+.

Run all the algorithms.
[Linux]
```bash
bash scripts/run.sh
```

[Windows]
```
scripts/run.bat
```

This produces `outputs/summary.csv` using only the pre-generated graphs & orders. If a required file is missing, the run aborts to prevent accidental on-the-fly generation.

## EDGES format
Each undirected edge is stored once per line as two vertex IDs separated by whitespace, e.g.

```
1 2
3 7
```

Vertices are 1-indexed. Files include no header; blank lines and lines starting with `#` are ignored.
