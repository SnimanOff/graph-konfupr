import unittest

from src.apkgraph.graph import build_graph, load_order, to_mermaid

A, B, C, D = ((name, "1") for name in "ABCD")
DIAMOND = {A: [B, C], B: [D], C: [D], D: []}


class GraphTests(unittest.TestCase):
    def test_diamond_visits_d_once(self):
        self.assertEqual(build_graph(A, DIAMOND.get, 5), DIAMOND)

    def test_depth_and_filter(self):
        self.assertEqual(build_graph(A, DIAMOND.get, 1, "C"), {A: [B], B: []})

    def test_cycle_terminates(self):
        data = {A: [B], B: [A]}
        self.assertEqual(build_graph(A, data.get, 9), data)

    def test_load_order(self):
        self.assertEqual(load_order(DIAMOND), [D, B, C, A])

    def test_cycle_has_no_order(self):
        with self.assertRaisesRegex(ValueError, "цикл"):
            load_order({A: [B], B: [A]})

    def test_mermaid(self):
        expected = ('flowchart LR\n    n0["A@1"]\n    n1["B@1"]\n'
                    '    n0 --> n1\n')
        self.assertEqual(to_mermaid({A: [B], B: []}), expected)
