from collections import deque, defaultdict
from typing import Dict, List, Set, Tuple, Iterable


class Graph:
    """Simple undirected graph using 1-indexed integer vertex IDs.

    - No parallel edges are stored.
    - Adjacency list representation.
    """

    def __init__(self, n: int = 0):
        if n < 0:
            raise ValueError("n must be non-negative")
        self._n = n
        self._adj: Dict[int, Set[int]] = {i: set() for i in range(1, n + 1)}

    @property
    def n(self) -> int:
        return self._n

    def ensure_vertex(self, v: int) -> None:
        if v not in self._adj:
            self._adj[v] = set()
            self._n = max(self._n, v)

    def add_edge(self, u: int, v: int) -> None:
        if u == v: # No self-loops
            return
        self.ensure_vertex(u)
        self.ensure_vertex(v)
        self._adj[u].add(v)
        self._adj[v].add(u)

    def add_edges(self, edges: Iterable[Tuple[int, int]]) -> None:
        for u, v in edges:
            self.add_edge(u, v)

    def neighbors(self, v: int) -> Set[int]:
        return self._adj.get(v, set())

    def vertices(self) -> List[int]:
        return list(self._adj.keys())

    def degree(self, v: int) -> int:
        return len(self._adj.get(v, ()))

    def induced_subgraph_vertices(self, allowed: Set[int]) -> Dict[int, Set[int]]:
        return {v: {u for u in self._adj.get(v, ()) if u in allowed} for v in allowed}

    def connected_component(self, start: int, allowed: Set[int]) -> Set[int]:
        """Return the connected component containing start, restricted to allowed vertices."""
        if start not in allowed:
            return set()
        comp: Set[int] = set()
        dq: deque[int] = deque([start])
        comp.add(start)
        while dq:
            v = dq.popleft()
            for u in self._adj.get(v, ()): 
                if u in allowed and u not in comp:
                    comp.add(u)
                    dq.append(u)
        return comp

    def bipartition_component(self, component: Set[int]) -> Tuple[Set[int], Set[int]]:
        """Attempt to 2-color the given component; returns (A,B) sets.

        If the component is not bipartite, this still returns a partition obtained via BFS levels.
        """
        color: Dict[int, int] = {}
        A: Set[int] = set()
        B: Set[int] = set()
        for v in component:
            if v in color:
                continue
            # BFS from v
            dq: deque[int] = deque([v])
            color[v] = 0
            A.add(v)
            while dq:
                x = dq.popleft()
                for y in self._adj.get(x, ()): 
                    if y not in component:
                        continue
                    if y not in color:
                        color[y] = 1 - color[x]
                        (A if color[y] == 0 else B).add(y)
                        dq.append(y)
                    else:
                        # Non-bipartite edge detected, still maintain partition by level parity
                        pass
        return A, B

    @staticmethod
    def read_edges_file(path: str) -> "Graph":
        g = Graph(0)
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                if len(parts) != 2:
                    continue
                u, v = int(parts[0]), int(parts[1])
                g.add_edge(u, v)
        return g

    def write_edges_file(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            for u in sorted(self._adj.keys()):
                for v in sorted(self._adj[u]):
                    if u < v:  # Write each undirected edge once
                        f.write(f"{u} {v}\n")
