import csv
import os
import random
from typing import Callable, Dict, List, Tuple, Optional
from concurrent.futures import ProcessPoolExecutor, as_completed
from .generator.generate import (
    generate_online_k_colorable_graph,
    random_order,
    read_edges,
    read_order,
    write_edges,
    write_order,
)
from .algorithms.first_fit import (
    first_fit,
    first_fit_heuristic_degree_order,
)
from .algorithms.cbip import cbip
from .algorithms.batched import make_batch_first_fit
from .metrics import compute_competitive_ratio, aggregate

AlgorithmFn = Callable[["Graph", List[int]], Dict[int, int]]  # type: ignore


def _combo_dir(n: int, k: int, p: float) -> str:
    return f"n{n}/k{k}/p{p}"


def _graph_filename(n: int, k: int, p: float, idx: int) -> str:
    return f"{_combo_dir(n,k,p)}/graph_idx{idx}.edges"


def _order_filename(n: int, k: int, p: float, idx: int) -> str:
    return f"{_combo_dir(n,k,p)}/graph_idx{idx}.order"


def _run_single(alg_fn: AlgorithmFn, k: int, n: int, p: float, rep: int, dataset_dir: Optional[str]) -> float:
    if dataset_dir:
        g_path = os.path.join(dataset_dir, _graph_filename(n, k, p, rep))
        o_path = os.path.join(dataset_dir, _order_filename(n, k, p, rep))
        g = read_edges(g_path)
        order = read_order(o_path)
    else:
        g, _ = generate_online_k_colorable_graph(n=n, k=k, p=p)
        order = random_order(n)
    coloring = alg_fn(g, order)
    chromatic_number = k
    return compute_competitive_ratio(coloring, chromatic_number)


def run_simulation(
    algorithm_name: str,
    alg_fn: AlgorithmFn,
    n_values: List[int],
    k: int,
    N: int,
    p: float,
    dataset_dir: Optional[str] = None,
    workers: int = 1,
    show_progress: bool = False,
) -> List[Tuple[str, int, int, int, float, float]]:
    """Run simulations returning rows for CSV: (algorithm,k,n,N,avg_ratio,sd_ratio).

    If dataset_dir is provided, graphs and orders are loaded from pre-generated files.
    Otherwise, they are generated on the fly.
    """
    rows: List[Tuple[str, int, int, int, float, float]] = []
    for n in n_values:
        ratios: List[float] = []
        if dataset_dir:
            for rep in range(1, N + 1):
                g_path = os.path.join(dataset_dir, _graph_filename(n, k, p, rep))
                o_path = os.path.join(dataset_dir, _order_filename(n, k, p, rep))
                if not os.path.exists(g_path) or not os.path.exists(o_path):
                    raise FileNotFoundError(f"Missing files for n={n}, k={k}, p={p}, rep={rep}")

        if workers and workers > 1:
            with ProcessPoolExecutor(max_workers=workers) as ex:
                futures = []
                for rep in range(1, N + 1):
                    futures.append(ex.submit(_run_single, alg_fn, k, n, p, rep, dataset_dir))
                done = 0
                for fut in as_completed(futures):
                    ratios.append(fut.result())
                    done += 1
                    if show_progress and done % max(1, N // 10) == 0:
                        print(f"[{algorithm_name}] n={n}, k={k}, p={p}: {done}/{N} completed")
        else:
            for rep in range(1, N + 1):
                ratios.append(_run_single(alg_fn, k, n, p, rep, dataset_dir))
                if show_progress and rep % max(1, N // 10) == 0:
                    print(f"[{algorithm_name}] n={n}, k={k}, p={p}: {rep}/{N} completed")
        avg, sd = aggregate(ratios)
        rows.append((algorithm_name, k, n, N, avg, sd))
    return rows


def run_all(
    output_dir: str,
    dataset_dir: Optional[str] = None,
    workers: int = 1,
    show_progress: bool = True,
    include_batch: bool = False,
    batch_sizes: Optional[List[int]] = None,
) -> None:
    os.makedirs(output_dir, exist_ok=True)
    # Parameter sets (could expose later via CLI if needed)
    n_values = [50, 100, 150, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
    N = 100
    p_values = [0.05, 0.1, 0.2, 0.3]

    all_rows: List[Tuple[str, int, int, int, float, float]] = []

    from .graph import Graph  # local import to avoid circular ref in type hint

    for p in p_values:
        for k in (2, 3, 4):
            all_rows.extend(run_simulation(f"FirstFit[p={p}]", first_fit, n_values, k, N, p, dataset_dir, workers, show_progress))
        all_rows.extend(run_simulation(f"CBIP[p={p}]", cbip, n_values, 2, N, p, dataset_dir, workers, show_progress))
        for k in (2, 3, 4):
            all_rows.extend(run_simulation(
                f"FirstFit(HeuristicDegree)[p={p}]", first_fit_heuristic_degree_order, n_values, k, N, p, dataset_dir, workers, show_progress
            ))
        if include_batch:
            sizes = batch_sizes or [10, 50]
            for size in sizes:
                for k in (2, 3, 4):
                    deg_algo = make_batch_first_fit(size, "degree")
                    all_rows.extend(run_simulation(
                        f"FirstFitBatchDegree(size={size})[p={p}]", deg_algo, n_values, k, N, p, dataset_dir, workers, show_progress
                    ))

    out_path = os.path.join(output_dir, "summary.csv")
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["Algorithm", "k", "n", "N", "AvgCompetitiveRatio", "StdDev"])
        for r in all_rows:
            w.writerow(r)

    print(f"Wrote {len(all_rows)} rows to {out_path}")


def prepare_dataset(
    dataset_dir: str,
    n_values: List[int],
    p_values: List[float],
    k_values: List[int],
    N: int,
    seed: int | None = None,
) -> None:
    """Pre-generate graphs and orders for all parameter combinations for reproducibility."""
    if seed is not None:
        random.seed(seed)
    os.makedirs(dataset_dir, exist_ok=True)
    total = 0
    for p in p_values:
        for k in k_values:
            for n in n_values:
                for rep in range(1, N + 1):
                    g, _ = generate_online_k_colorable_graph(n=n, k=k, p=p)
                    order = random_order(n)
                    g_path = os.path.join(dataset_dir, _graph_filename(n, k, p, rep))
                    o_path = os.path.join(dataset_dir, _order_filename(n, k, p, rep))
                    write_edges(g, g_path)
                    write_order(order, o_path)
                    total += 1
    manifest_path = os.path.join(dataset_dir, "manifest.txt")
    with open(manifest_path, "w", encoding="utf-8") as f:
        f.write(f"seed={seed}\n")
        f.write(f"N={N}\n")
        f.write("n_values=" + ",".join(str(x) for x in n_values) + "\n")
        f.write("k_values=" + ",".join(str(x) for x in k_values) + "\n")
        f.write("p_values=" + ",".join(str(x) for x in p_values) + "\n")
        f.write(f"total_instances={total}\n")
    print(f"Prepared dataset with {total} graph/order pairs at {dataset_dir}")
