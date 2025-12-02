import os
import random
from typing import List, Set, Tuple
from ..graph import Graph


def generate_online_k_colorable_graph(n: int, k: int, p: float) -> Tuple[Graph, List[Set[int]]]:
    """Generate an undirected k-colorable graph following the project spec idea.

    - Partition vertices into k non-empty independent sets S1..Sk.
    - For each pair of sets (Si,Sj), ensure at least one cross edge from each v in Si to some u in Sj.
    - Add additional cross edges with independent probability p.

    Returns (Graph, partitions) where partitions is a list of sets of vertex ids.
    """
    if n < k or k < 1:
        raise ValueError("Require n >= k >= 1")
    if not (0.0 <= p <= 1.0):
        raise ValueError("p must be in [0,1]")

    g = Graph(n)
    # Initialize a list of k empty sets (containing integer values) for the partitions
    partitions: List[Set[int]] = [set() for _ in range(k)]

    # Assign first k vertices one per partition, then distribute the rest randomly
    v_id = 1
    for i in range(k):
        partitions[i].add(v_id)
        v_id += 1
    while v_id <= n:
        idx = random.randint(0, k - 1)
        partitions[idx].add(v_id)
        v_id += 1

    # Add cross edges to guarantee inter-set connectivity and additional with prob p
    for i in range(k):
        Si = partitions[i]
        for v in Si:
            for j in range(k):
                if i == j:
                    continue
                Sj = partitions[j]
                if not Sj:
                    continue
                # ensure at least one edge to Sj
                u = random.choice(tuple(Sj))
                g.add_edge(v, u) # graph is undirected, so this suffices
                # add additional edges with prob p
                for u2 in Sj:
                    if u2 == u:
                        continue
                    if random.random() < p: # random.random() returns [0.0, 1.0)
                        g.add_edge(v, u2)
    return g, partitions


def random_order(n: int) -> List[int]:
    order = list(range(1, n + 1))
    random.shuffle(order)
    return order


def write_edges(g: Graph, path: str) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    g.write_edges_file(path)


def read_edges(path: str) -> Graph:
    return Graph.read_edges_file(path)


def write_order(order: List[int], path: str) -> None:
    """Persist a vertex arrival order to disk (space separated)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(" ".join(str(x) for x in order))


def read_order(path: str) -> List[int]:
    with open(path, "r", encoding="utf-8") as f:
        content = f.read().strip()
        if not content:
            return []
        return [int(x) for x in content.split()]
