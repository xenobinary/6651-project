import os
import unittest
import random

import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from comp6651.graph import Graph
from comp6651.algorithms.first_fit import first_fit
from comp6651.algorithms.cbip import cbip
from comp6651.generator.generate import generate_online_k_colorable_graph, random_order


class TestAlgorithms(unittest.TestCase):
    def test_graph_add_edge(self):
        g = Graph()
        g.add_edge(1, 2)
        self.assertIn(2, g.neighbors(1))
        self.assertIn(1, g.neighbors(2))

    def test_graph_ignores_self_loops_and_parallel(self):
        g = Graph()
        g.add_edge(1, 1)  # ignored
        g.add_edge(1, 2)
        g.add_edge(1, 2)  # parallel ignored by set semantics
        self.assertEqual(g.degree(1), 1)
        self.assertEqual(g.degree(2), 1)

    def test_first_fit_valid_coloring(self):
        random.seed(42)
        g, _ = generate_online_k_colorable_graph(n=10, k=3, p=0.2)
        order = random_order(10)
        coloring = first_fit(g, order)
        # Check proper coloring
        for v in range(1, 11):
            for u in g.neighbors(v):
                if u > v:  # check each edge once
                    self.assertNotEqual(coloring[v], coloring[u])

    def test_first_fit_small_known_graph(self):
        # Triangle (3-cycle) requires 3 colors with FirstFit depending on order
        g = Graph()
        g.add_edge(1, 2)
        g.add_edge(2, 3)
        g.add_edge(3, 1)
        order = [1, 2, 3]
        coloring = first_fit(g, order)
        self.assertEqual(len({coloring[1], coloring[2], coloring[3]}), 3)

    def test_cbip_on_bipartite(self):
        random.seed(1)
        g, _ = generate_online_k_colorable_graph(n=12, k=2, p=0.3)
        order = random_order(12)
        coloring = cbip(g, order)
        # Proper coloring check
        for v in range(1, 13):
            for u in g.neighbors(v):
                if u > v:
                    self.assertNotEqual(coloring[v], coloring[u])

    def test_cbip_small_known_bipartite(self):
        # Square (4-cycle) is bipartite; CBIP should use at most 2 colors
        g = Graph()
        edges = [(1,2), (2,3), (3,4), (4,1)]
        for u,v in edges:
            g.add_edge(u,v)
        order = [1, 2, 3, 4]
        coloring = cbip(g, order)
        self.assertLessEqual(max(coloring.values()), 2)


if __name__ == "__main__":
    unittest.main()
