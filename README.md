# COMP 6651 Project: Online Graph Coloring

This repository contains a reference scaffold for the COMP 6651 Fall 2025 project on greedy algorithms for online graph coloring.

Highlights
- No external graph libraries; pure Python standard library only.
- Implements: random k-colorable graph generator, FirstFit, CBIP (k=2), and a pluggable heuristic variant for FirstFit.
- Reproducible simulations via pre-generated immutable dataset of graphs + vertex arrival orders.
- CSV outputs suitable for inclusion in the report.

## Repo layout
- `src/comp6651/` — source code package
  - `graph.py` — Graph data structure and utilities (connected component, bipartition)
  - `algorithms/first_fit.py` — FirstFit algorithm
  - `algorithms/cbip.py` — CBIP algorithm (for bipartite graphs)
  - `generator/generate.py` — Random online k-colorable graph generator and EDGES I/O
  - `simulations.py` — Batch runners to reproduce tables
  - `metrics.py` — Competitive ratio and statistics helpers
  - `main.py` — CLI entry point (quick demo)
- `tests/` — unit tests using Python's built-in `unittest`
- `docs/report/` — report template (Markdown) and figures folder
- `docs/design/` — design document
- `scripts/run.sh` — convenience runner (sets PYTHONPATH and runs a small demo)

## Quickstart
Prerequisites: Python 3.10+.

Run a tiny demo simulation and see CSV output under `outputs/`:

```bash
bash scripts/run.sh
```

Run unit tests:

```bash
PYTHONPATH=src python -m unittest -v
```

Generate EDGES files only (legacy single-parameter mode):

```bash
PYTHONPATH=src python -m comp6651.main --generate --n 50 --k 3 --p 0.1 --N 5 --out data/generated
```

## EDGES format
Each undirected edge is stored once per line as two vertex IDs separated by whitespace, e.g.

```
1 2
3 7
```

Vertices are 1-indexed. Files include no header; blank lines and lines starting with `#` are ignored.

## Notes
- CBIP is evaluated for k=2 as per the project spec.
- Chromatic number used for competitive ratio is set to the generator parameter `k` for k-colorable graphs; for bipartite graphs, χ(G)=2.
- Heuristic example provided: Highest-Degree-First ordering (documented in the report as modifying "online").

## Reproducible Simulation Workflow
To ensure identical results across runs, first create a fixed dataset of graphs and vertex arrival orders covering all `(n, k, p)` combinations used in the study. Subsequent simulation runs will only read these stored artifacts.

### 1. Prepare Dataset
This pre-generates `.edges` (graph) and `.order` (vertex arrival order) files plus a simple `manifest.txt`.

```bash
PYTHONPATH=src python -m comp6651.main \
  --prepare-dataset \
  --seed 123 \
  --out data \
  --dataset-dir data/dataset \
  --N_dataset 100
```

Generated file naming convention:
```
n{n}/k{k}/p{p}/graph_idx{rep}.edges
n{n}/k{k}/p{p}/graph_idx{rep}.order
```
The order file contains a single line of space-separated vertex IDs representing the online arrival order.

### 2. Run Simulations Using Dataset
```bash
PYTHONPATH=src python -m comp6651.main \
  --run-sims \
  --dataset-dir data/dataset \
  --out outputs
```

This produces `outputs/summary.csv` using only the pre-generated graphs & orders. If a required file is missing, the run aborts to prevent accidental on-the-fly generation.

### 3. Manifest File
`manifest.txt` records: seed, `N`, lists of `n_values`, `k_values`, `p_values`, and total instance count. This helps confirm identical experimental conditions between collaborators or report reproduction attempts.

### Why Store Orders?
Online coloring performance depends on vertex arrival order. Storing both graph structure and the specific order guarantees full reproducibility (same competitive ratios) instead of relying solely on seeding.

### Legacy Mode
The older `--generate` and ad hoc `--run-sims` without a dataset remain available for quick experimentation, but formal results should use the dataset workflow above.

