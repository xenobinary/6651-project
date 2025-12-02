import argparse
import os
import random
from .generator.generate import generate_online_k_colorable_graph, write_edges, random_order
from .algorithms.first_fit import first_fit, first_fit_heuristic_degree_order
from .algorithms.cbip import cbip
from .metrics import compute_competitive_ratio
from .simulations import run_all, prepare_dataset


def main():
    parser = argparse.ArgumentParser(description="COMP 6651 Online Graph Coloring Project")
    parser.add_argument("--generate", action="store_true", help="Only generate EDGES files and exit")
    # parser.add_argument("--n", type=int, default=50)
    # parser.add_argument("--k", type=int, default=2)
    # parser.add_argument("--p", type=float, default=0.1)
    # parser.add_argument("--N", type=int, default=5, help="Number of graphs for generation")
    # parser.add_argument("--out", type=str, default="data/generated", help="Output directory for EDGES files or summaries")
    parser.add_argument("--run-sims", action="store_true", help="Run simulations (requires dataset for reproducibility)")
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--prepare-dataset", action="store_true", help="Pre-generate full dataset for simulations")
    parser.add_argument("--dataset-dir", type=str, default=None, help="Directory containing pre-generated graphs/orders for simulations")
    parser.add_argument("--N_dataset", type=int, default=100, help="Number of instances per (n,k,p) when preparing dataset")
    parser.add_argument("--workers", type=int, default=os.cpu_count() or 1, help="Parallel workers for simulations (use ~16 on your machine)")
    parser.add_argument("--no-progress", action="store_true", help="Disable progress printing during simulations")
    parser.add_argument("--include-batch", action="store_true", help="Include batch semi-online variants (degree only)")
    parser.add_argument("--batch-sizes", type=str, default="10,50", help="Comma-separated batch sizes for batch variants (e.g. 5,10,25,50)")

    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    if args.generate:  # Legacy single parameter generation
        os.makedirs(args.out, exist_ok=True)
        for i in range(args.N):
            g, parts = generate_online_k_colorable_graph(args.n, args.k, args.p)
            path = os.path.join(args.out, f"graph_n{args.n}_k{args.k}_idx{i+1}.edges")
            write_edges(g, path)
        print(f"Generated {args.N} graphs at {args.out}")
        return

    if args.prepare_dataset:
        # Fixed parameter sets (could expose later via CLI if needed)
        n_values = [50, 100, 150, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
        p_values = [0.05, 0.1, 0.2, 0.3]
        k_values = [2, 3, 4]
        target_dir = args.dataset_dir or os.path.join(args.out, "dataset")
        prepare_dataset(
            dataset_dir=target_dir,
            n_values=n_values,
            p_values=p_values,
            k_values=k_values,
            N=args.N_dataset,
            seed=args.seed,
        )
        return

    if args.run_sims:
        if not args.dataset_dir:
            raise SystemExit("--run-sims now requires --dataset-dir (prepare it first with --prepare-dataset)")
        os.makedirs(args.out, exist_ok=True)
        batch_sizes = [int(x) for x in args.batch_sizes.split(',') if x.strip().isdigit()]
        run_all(
            args.out,
            dataset_dir=args.dataset_dir,
            workers=args.workers,
            show_progress=not args.no_progress,
            include_batch=args.include_batch,
            batch_sizes=batch_sizes,
        )
        return

    # Quick demo: generate one graph, run algorithms, print ratios
    # g, _ = generate_online_k_colorable_graph(args.n, args.k, args.p)
    # order = random_order(args.n)
    # ff = first_fit(g, order)
    # ratio_ff = compute_competitive_ratio(ff, args.k)
    # print(f"FirstFit: used {max(ff.values()) if ff else 0} colors, ratio={ratio_ff:.3f}")

    # if args.k == 2:
    #     c = cbip(g, order)
    #     ratio_c = compute_competitive_ratio(c, 2)
    #     print(f"CBIP: used {max(c.values()) if c else 0} colors, ratio={ratio_c:.3f}")

    # ffh = first_fit_heuristic_degree_order(g, order)
    # ratio_ffh = compute_competitive_ratio(ffh, args.k)
    # print(f"FirstFit(HeuristicDegree): used {max(ffh.values()) if ffh else 0} colors, ratio={ratio_ffh:.3f}")


if __name__ == "__main__":
    main()
