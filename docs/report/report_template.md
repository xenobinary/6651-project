# COMP 6651 Project Report

Team: <Team Members and Student IDs>
Date: <Submission Date>

## 1. Problem Description

Graph coloring is a central topic within graph theory that finds its origin in the notorious Four Color Problem, dating
back to 1852 [1]. An online coloring is a coloring algorithm that immediately colors the vertices of a graph G taken from a list without looking ahead or changing colors already assigned [2]. Any online algorithm may require at least (2n/(log n)2 )χ (G) colors in the worst case [3].

Probably the conceptually simplest online algorithm for graph coloring is the greedy algorithm, which is known as FirstFit [2]. Suppose we have a total order over the set of available colors. Then upon arrival of each vertex, FirstFit assigns to it the smallest color according to that order, among the ones that maintain a proper coloring. This algorithm has been extensively analyzed in the literature, also for particular graph classes [2,4]. Another famous algorithm due to [6] for online coloring of bipartite graphs is called CBIP (Coloring Based on Interval Partitioning): when a vertex v = σ (i) arrives, CBIP computes an entire connected component CC to which v belongs in the partial graph known so far.

In this project, we need to implement these two greedy online graph coloring algorithm using Python 3.13.7. For learning purpose, we strictly use limited Python libraries except for base ones, such as `collections` and `typings` for basic data structures. We perform two empirical studies of the FirstFit on k-colorable online graph for k $\in$ {2, 3, 4} and CBIP on 2-colorable online graph. First, we consider four parameters: number of nodes in G (n), the value used to generate the online k-colorable graph (k), number of generated graphs created for computing average competitive ratio (N), and the probability that and undirecte edge is added (p) which is used to generat an random online graph. We use three metrics for performance comparision: competitive ratio ($\rho(Alg,G)$), Average Competitive ratio, and Standard Deviation of Competitive ratio.
Second, we try to use a heuristic method to improve the performance of FirstFit. The vertices are sorted by degree in a non-increasing order. We also perform an empirical study with the same parameters and metrics on FirstFit on k-colorable online graph.

Based on the results of studies, we should draw some conclusions about the performance of these two greedy algorithms and how we can increase the performance of FirstFit algorithm.

## 2. Implementation Details
### 2.1 Data Structures
Our implementation uses a lightweight, mutable, undirected graph class `Graph` optimized for online coloring experiments:

Data Representation:
- Vertex Set: Implicit in the keys of a dictionary `_adj: Dict[int, Set[int]]`. Vertices are 1-indexed positive integers.
- Adjacency: Each key maps to a Python `set` of neighbor vertex IDs.
- Dynamism: The graph can grow as new edges introduce higher‑indexed vertices (`ensure_vertex`). 
- No Parallel / Self Loops: `add_edge(u,v)` ignores self loops (`u==v`) and relies on set insertion to avoid parallel edges.

Key Operations:
1. `ensure_vertex(v)`: Adds a new empty adjacency set for v if absent; updates nodes count `_n`.
2. `add_edge(u,v)`: Validates / creates endpoints, inserts into both adjacency sets (for undirected graphs).
3. `neighbors(v)`: Returns the neighbor set (empty set if v absent).
4. `degree(v)`: Size of adjacency set — used by heuristic ordering (degree sort) prior to FirstFit.
5. `connected_component(start, allowed)`: BFS restricted to a subset `allowed` representing the currently revealed vertices in online coloring; core for CBIP to isolate the component containing the arriving vertex.
6. `bipartition_component(component)`: Level‑based BFS 2‑color attempt producing (A,B) sets; even if the component is not bipartite, it still returns a parity partition used by CBIP’s strategy of assigning a fresh color to one side.
7. `induced_subgraph_vertices(allowed)`: Produces an adjacency projection limited to `allowed` — helpful for analysis without mutating the original.
8. `read_edges_file` / `write_edges_file`: Deterministic plain text edge list I/O (each undirected edge written once with u < v) supporting reproducible experiment datasets.

Pseudocode (core routines):

Initialization:
```
INIT_GRAPH(n):
	adj := dictionary mapping i in [1..n] -> empty set
	max_id := n
	return (adj, max_id)
```

Ensure Vertex:
```
ENSURE_VERTEX(adj, max_id, v):
	if v not in adj:
		adj[v] := empty set
		if v > max_id: max_id := v
	return max_id
```

Add Edge (undirected, no self loop, no parallel edge):
```
ADD_EDGE(adj, max_id, u, v):
	if u == v: return max_id
	max_id := ENSURE_VERTEX(adj, max_id, u)
	max_id := ENSURE_VERTEX(adj, max_id, v)
	adj[u].add(v)
	adj[v].add(u)
	return max_id
```

Connected Component (restricted):
```
CONNECTED_COMPONENT(adj, start, allowed):
	if start not in allowed: return empty set
	comp := {start}
	queue := [start]
	while queue not empty:
		v := pop_front(queue)
		for u in adj.get(v, empty set):
			if u in allowed and u not in comp:
				comp.add(u)
				push_back(queue, u)
	return comp
```

Bipartition via BFS parity:
```
BIPARTITION_COMPONENT(adj, component):
	color := empty map
	A := empty set; B := empty set
	for v in component:
		if v in color: continue
		queue := [v]
		color[v] := 0; A.add(v)
		while queue not empty:
			x := pop_front(queue)
			for y in adj.get(x, empty set):
				if y not in component: continue
				if y not in color:
					color[y] := 1 - color[x]
					if color[y] == 0: A.add(y) else: B.add(y)
					push_back(queue, y)
				else:
					// Edge within same level indicates non-bipartite; ignore
	return (A, B)
```

These structures and routines provide all primitives required by FirstFit (neighbor color inspection) and CBIP (component extraction + bipartition) while remaining simple enough for transparent performance measurement.

### 2.2 Algorithms
This section summarizes the online coloring algorithms implemented in `first_fit.py` and `cbip.py`.

FirstFit (greedy online):
- Idea: On vertex arrival `v`, pick the smallest positive color not used by already colored neighbors of `v`.
- State: `color: v -> c`, `revealed` set for vertices seen so far.
- Complexity: For each `v`, checking neighbor colors is O(deg(v)); overall ~ O(∑v deg(v)) = O(m).

```
FIRST_FIT(G, order):
	color := empty map; revealed := empty set
	for v in order:
		used := { color[u] for u in N_G(v) if u in revealed }
		c := 1
		while c in used: c := c + 1
		color[v] := c
		revealed.add(v)
	return color
```

Heuristic FirstFit (degree order):
- Idea: Sort `order` by non‑increasing static degree, then apply FirstFit.
- Note: Not strictly online; used to assess heuristic impact.
- Cost: Sorting O(n log n) + FirstFit O(m).

```
FIRST_FIT_DEGREE_HEUR(G, order):
	order' := order sorted by degree(v) descending
	return FIRST_FIT(G, order')
```

CBIP (for k = 2 colorable graphs):
- Idea per arrival `v`: Consider component induced by `revealed ∪ {v}` containing `v`, bipartition it into (A,B) by BFS levels, ensure `v ∈ A`, then assign to `v` the smallest color unused on side `B` among revealed vertices.
- State: `color`, `revealed`; uses `connected_component` and `bipartition_component` from `Graph`.
- Complexity: Per step, O(|V_c|+|E_c|) to BFS the current component `c`; color selection O(deg_B(v)).

```
CBIP(G, order):
	color := empty map; revealed := empty set
	for v in order:
		allowed := revealed ∪ {v}
		comp := CONNECTED_COMPONENT(G, v, allowed)
		(A, B) := BIPARTITION_COMPONENT(G, comp)
		if v ∉ A and v ∈ B: swap(A, B)
		usedB := { color[u] | u ∈ B ∩ revealed }
		c := 1
		while c in usedB: c := c + 1
		color[v] := c
		revealed.add(v)
	return color
```

Both algorithms maintain proper colorings online; CBIP leverages component parity to limit conflicts on bipartite inputs, while FirstFit is general and fast but may use more colors depending on the arrival order.

### 2.3 Generator
We generate k-colorable graphs by construction and store them in a simple EDGES format.

Inputs and Constraints:
- `n`: number of vertices (1..n), `k`: target colorability with `n ≥ k ≥ 1`, `p ∈ [0,1]`: extra cross-edge probability.
- Randomness via Python `random`; use `--seed` in `main.py` for reproducibility.

Method (k-colorable by construction):
- Partition 1..n into `k` non-empty independent sets `S1..Sk` (first k vertices one per set; remaining assigned uniformly at random).
- For every vertex `v ∈ Si` and every other set `Sj (j ≠ i)`:
  - Add one mandatory cross edge `(v,u)` with `u` chosen uniformly from `Sj`.
  - For each other `u2 ∈ Sj \ {u}`, add `(v,u2)` independently with probability `p`.
- No intra-set edges are created, so the graph remains k-colorable by assigning color i to all vertices in `Si`.

Presentation Order:
- `random_order(n)` returns a random permutation of `[1..n]` used as the online arrival order in experiments.

Storage (EDGES format):
- One undirected edge per line: `u v` (space-separated integers) with `u < v`.
- Writer: `Graph.write_edges_file` ensures each undirected edge is written exactly once, sorted.
- Reader: `Graph.read_edges_file` accepts blank lines and lines starting with `#` as comments.
- Files named `graph_n{n}_k{k}_idx{i}.edges` under `data/generated/` by default.

Pseudocode:
```
GENERATE(n, k, p):
	create k empty sets S[1..k]
	assign vertices: first k one per set; rest uniformly at random
	for i in 1..k:
		for v in S[i]:
			for j in 1..k, j ≠ i:
				u := uniform choice from S[j]
				add_edge(v, u)
				for each u2 in S[j] \ {u}:
					if rand() < p: add_edge(v, u2)
	return G, {S[1],..,S[k]}
```

Cost: Partitioning O(n); edge addition O(∑i |Si|·(k−1)) for mandatory cross edges plus expected `p·`(all other cross pairs). The writer runs in O(m).

## 3. Implementation Correctness
We validated correctness at two levels: software invariants and algorithmic properties on small, verifiable graphs.

Software correctness:
- Edge handling: Unit tests confirm self-loops are ignored and parallel edges are not duplicated (set-based adjacency).
- Symmetry: Adding `(u,v)` results in `u ∈ N(v)` and `v ∈ N(u)`.
- I/O: EDGES writer outputs each undirected edge once (`u < v`); reader tolerates comments and blanks.

Algorithm correctness (examples):
- FirstFit proper coloring: On random k‑colorable graphs (e.g., `n=10,k=3,p=0.2` with fixed seed), every edge `(u,v)` satisfies `color[u] ≠ color[v]`.
- FirstFit on 3‑cycle: Triangle graph `(1-2-3-1)` with order `[1,2,3]` uses 3 colors, matching the chromatic number and verifying greedy behavior.
- CBIP on bipartite inputs: On random bipartite graphs (`k=2`), CBIP yields proper colorings; on a 4‑cycle `(1-2-3-4-1)`, CBIP uses ≤2 colors.

Tests added in `project/tests/test_sanity.py`:
- `test_graph_ignores_self_loops_and_parallel`: boundary behavior of `Graph.add_edge`.
- `test_first_fit_valid_coloring`: randomized k‑colorable instance correctness.
- `test_first_fit_small_known_graph`: triangle example expecting 3 colors.
- `test_cbip_on_bipartite`: randomized bipartite instance correctness.
- `test_cbip_small_known_bipartite`: square example expecting ≤2 colors.

Reproducibility and run:
- Set a seed to reproduce: `random.seed(<int>)` via `--seed` in `main.py` or within tests.
- Run tests:
```
python -m unittest project/tests/test_sanity.py -v
```

Independent verification (small graphs):
- We manually checked small graphs where chromatic numbers are known (triangle = 3, square = 2). The outputs match expectations for the given arrival orders, supporting correctness of the implementations.

## 4. Results
We report average competitive ratio and standard deviation across multiple graph sizes and densities. Data is written to `project/outputs/summary.csv` by `run_all`.

Parameter grid actually used for reported results:
- `n`: 50, 100, 150, 200, 300, 400, 500, 600, 700, 800, 900, 1000.
- `k`: {2, 3, 4} (CBIP only for k=2).
- `N`: 100 repetitions per (n,k,p) to reduce statistical noise.
- `p`: {0.05, 0.1, 0.2, 0.3}.

Algorithms:
- `FirstFit[p=...]` for k ∈ {2,3,4}
- `CBIP[p=...]` for k=2
- `FirstFit(HeuristicDegree)[p=...]` for k ∈ {2,3,4}

How to run:
```
cd project
./scripts/run.sh
```
This executes `comp6651.simulations.run_all` and writes `outputs/summary.csv`.

Summary of empirical findings (selected highlights):
- Density effect (p) for k=2: FirstFit ratio grows sharply with n when p=0.05 (≈2.04→5.10) but is almost flat for p=0.3 (≈1.48→1.54).
- CBIP stability: Near‑optimal and improves with higher p (≈2.055→1.34 at n=1000).
- Heuristic improvement: Largest relative gain at k=2, p=0.05 (−39.8%); diminishing returns as p rises or k increases.
- Scaling with k: Higher k increases FirstFit ratio; high p dampens this growth.
- Variability: Sparse graphs show higher std dev; heuristic and CBIP reduce or stabilize variance.

Sample comparison (n=1000 endpoints):
- k=2: FirstFit 5.10 / 3.97 / 1.98 / 1.54 vs CBIP 2.055 / 1.86 / 1.55 / 1.34 vs Heuristic 3.07 / 1.92 / 1.215 / 1.075 (p=0.05/0.1/0.2/0.3)
- k=3: FirstFit 6.97 / 7.36 / 3.93 / 2.38 vs Heuristic 5.53 / 5.32 / 1.88 / 1.29
- k=4: FirstFit 6.33 / 8.36 / 5.75 / 2.85 vs Heuristic 5.73 / 6.93 / 3.15 / 1.62

Interpretation: Higher density accelerates constraint propagation so greedy coloring approaches chromatic efficiency; ordering high‑degree vertices early curbs late color proliferation in sparse graphs; CBIP’s component bipartition naturally restrains color growth on bipartite inputs.

## 5. Analysis and Conclusions
Key Trends:
- Sparsity drives color proliferation for plain FirstFit; competitive ratio grows with n at low p.
- Density suppresses proliferation, bringing greedy results close to optimal even for higher k.
- CBIP leverages bipartite structure to stay near theoretical bounds across n.
- Degree heuristic yields largest relative gains when baseline ratio is high (low p, small k).

Comparative Performance:
- For k=2, p=0.05, CBIP (~2.06) less than half of FirstFit (5.10); heuristic narrows gap (3.07).
- Heuristic does not surpass CBIP on bipartite graphs but is valuable when k>2.

Effect of k:
- Increasing k raises baseline color demand; density mitigates impact as early constraints align colors.

Variance and Robustness:
- Higher std dev for sparse graphs indicates order sensitivity; heuristic imposes deterministic ordering reducing variability.
- CBIP maintains moderate variance due to structural exploration (component BFS).

Limitations:
- Heuristic breaks strict online model (needs degrees beforehand).
- Graph generator enforces k-colorability; does not test adversarial or skewed degree distributions.
- Only one heuristic studied; richer strategies (degeneracy ordering, predictive models) remain unexplored.

Conclusions:
- Structure-aware (CBIP) and ordering heuristics substantially reduce competitive ratio where naive greedy falters.
- Density alone can bring greedy coloring near optimal; when sparse, degree ordering offers practical improvement.
- For bipartite inputs, CBIP is preferred; for general k-colorable graphs, FirstFit with ordering heuristics balances simplicity and performance.

## 6. Heuristic Design Rationale
Design Choice:
- Non‑increasing degree ordering colors high‑constraint vertices first.

Expected Effect:
- Early constraint propagation reduces need for introducing new colors on low‑degree tails.

Observed Effect:
- Up to ~40% ratio reduction (k=2, p=0.05, n=1000); diminishing absolute gains with higher p.
- Lower or stabilized variance compared to plain FirstFit.

Trade-offs:
- Not strictly online; assumes global degree knowledge.
- Minimal overhead (one sort) relative to simulation workload.

Potential Extensions:
- Degeneracy (k‑core) ordering; hybrid CBIP/greedy for mixed components; adaptive reordering via saturation metrics.

Justification:
- Simple, effective in sparse regimes, and illustrative of impact of vertex ordering on online coloring performance.

## 7. Team Work Distribution
List tasks per member (generator, algorithms, experiments, analysis, writing, QA).

## 8. References
List academic references and any resources used (proper citation). No copied code.

[1] A. Antoniadis, H. Broersma, and Y. Meng, “Incorporating predictions in online graph coloring algorithms,” Discrete Applied Mathematics, vol. 379, pp. 434–445, 2026, doi: https://doi.org/10.1016/j.dam.2025.08.063.

[2] Gyárfás, A. and Lehel, J. (1988), On-line and first fit colorings of graphs. J. Graph Theory, 12: 217-227. https://doi.org/10.1002/jgt.3190120212

[3] Magnús M. Halldórsson, Mario Szegedy, Lower bounds for on-line graph coloring, Theoret. Comput. Sci. 130 (1) (1994) 163–174.

[4] Sandy Irani, Coloring inductive graphs on-line, Algorithmica 11 (1) (1994) 53–72.

[5] Y. Li, V. V. Narayan, and D. Pankratov, “Online Coloring and a New Type of Adversary for Online Graph Problems,” Algorithmica, vol. 84, no. 5, pp. 1232–1251, 2022, doi: 10.1007/s00453-021-00920-w.

[6] Lovász, L., Saks, M., Trotter, W.T.: An on-line graph coloring algorithm with sublinear performance
ratio. Discret. Math. 75(1–3), 319–325 (1989)
