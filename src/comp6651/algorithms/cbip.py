from typing import Dict, List, Set
from ..graph import Graph


def cbip(graph: Graph, order: List[int]) -> Dict[int, int]:
    """CBIP algorithm specialized to bipartite (k=2-colorable) graphs.

    For each vertex v, we consider the connected component of seen vertices plus v,
    compute a bipartition (A,B) with v in A, then assign the smallest color not
    used by vertices in B.
    """
    color: Dict[int, int] = {}
    revealed: Set[int] = set()

    for v in order:
        # Component among revealed plus v
        allowed = set(revealed)
        allowed.add(v)
        comp = graph.connected_component(v, allowed)
        A, B = graph.bipartition_component(comp)
        # Ensure v is in A; if not, swap
        if v not in A and v in B:
            A, B = B, A
        used_in_B = {color[u] for u in B if u in revealed and u in color}
        c = 1
        while c in used_in_B:
            c += 1
        color[v] = c
        revealed.add(v)
    return color
