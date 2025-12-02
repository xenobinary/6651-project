from typing import Dict, List, Set
from ..graph import Graph


def first_fit(graph: Graph, order: List[int]) -> Dict[int, int]:
    """Greedy FirstFit online coloring.

    For each vertex v in presentation order, assign the smallest positive integer color
    not used by its already-revealed neighbors.
    Returns: mapping vertex -> color (positive ints)
    """
    color: Dict[int, int] = {}
    revealed: Set[int] = set()

    for v in order:
        neighbor_colors = {color[u] for u in graph.neighbors(v) if u in revealed}
        c = 1
        while c in neighbor_colors:
            c += 1
        color[v] = c
        revealed.add(v)
    return color


def first_fit_heuristic_degree_order(graph: Graph, order: List[int]) -> Dict[int, int]:
    """Variant: reorder by non-increasing current degree among not-yet-revealed vertices.

    Note: This modifies the notion of strict online processing; provided as a heuristic variant.
    """
    # Build a degree-based order (highest first) using the static graph degrees
    degree_sorted = sorted(order, key=lambda v: graph.degree(v), reverse=True)
    return first_fit(graph, degree_sorted)

