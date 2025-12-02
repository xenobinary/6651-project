from typing import Dict, List, Callable
from ..graph import Graph


def make_batch_first_fit(batch_size: int, strategy: str = "degree") -> Callable[[Graph, List[int]], Dict[int, int]]:
    """Factory producing a degree-ordered batch FirstFit (semi-online).

    Collects `batch_size` vertices from the arrival order, then colors them with
    a non-increasing static degree order within the batch while only using
    information revealed so far. Setting `batch_size=1` reproduces vanilla FirstFit.
    """

    assert batch_size >= 1, "batch_size must be >= 1"
    strategy = strategy.lower()
    if strategy not in {"degree"}:
        raise ValueError("strategy must be: degree")

    def algo(graph: Graph, order: List[int]) -> Dict[int, int]:
        color: Dict[int, int] = {}
        revealed_set = set()  # vertices colored so far (previous batches + current batch partial)
        n = len(order)
        # Precompute degrees once for degree ordering
        degrees = {v: graph.degree(v) for v in order}
        for start in range(0, n, batch_size):
            batch = order[start : start + batch_size]
            batch = sorted(batch, key=lambda v: degrees[v], reverse=True)
            for v in batch:
                # Neighbor colors restricted to already revealed vertices only
                neighbor_colors = {color[u] for u in graph.neighbors(v) if u in revealed_set}
                c = 1
                while c in neighbor_colors:
                    c += 1
                color[v] = c
                revealed_set.add(v)
        return color

    return algo


def batch_first_fit_degree_10(graph: Graph, order: List[int]) -> Dict[int, int]:
    return make_batch_first_fit(10, "degree")(graph, order)

def batch_first_fit_degree_50(graph: Graph, order: List[int]) -> Dict[int, int]:
    return make_batch_first_fit(50, "degree")(graph, order)
