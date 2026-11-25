"""
Unit Test Suite (`tests/test_courier_route.py`)
Menguji kebenaran struktur data Graf Berbobot, Algoritma Dijkstra (Min-Heap & Array),
Kasus Batas (Edge Cases), serta Finite State Machine (FSM) Pengiriman Paket.
"""

import unittest

from src.models import LocationNode, WeightedGraph
from src.dataset import create_default_courier_graph, create_disconnected_courier_graph
from src.algorithms import (
    dijkstra_min_heap,
    dijkstra_linear_array,
    find_all_simple_paths,
)
from src.automata import DeliveryStatusFSM


class TestCourierRouteGraphAndDijkstra(unittest.TestCase):
    """Pengujian terstruktur untuk pemodelan graf dan algoritma pencarian rute."""

    def setUp(self) -> None:
        self.graph = create_default_courier_graph()

    def test_graph_properties_and_handshaking_lemma(self) -> None:
        """Memastikan jumlah simpul |V|=7, sisi |E|=9, dan jumlah derajat = 2|E| = 18."""
        self.assertEqual(len(self.graph.nodes), 7)
        self.assertEqual(len(self.graph.edges), 9)
        total_degree = sum(self.graph.degree(n) for n in self.graph.node_ids)
        self.assertEqual(total_degree, 2 * len(self.graph.edges))

    def test_adjacency_matrix_symmetry(self) -> None:
        """Memastikan matriks ketetanggaan graf tak berarah bersifat simetris (A[i][j] == A[j][i])."""
        ids, matrix = self.graph.to_adjacency_matrix()
        self.assertEqual(len(ids), 7)
        for i in range(len(ids)):
            self.assertEqual(matrix[i][i], 0.0)
            for j in range(len(ids)):
                self.assertEqual(matrix[i][j], matrix[j][i])

    def test_normal_case_warehouse_to_f(self) -> None:
        """Kasus Normal Utama: Rute G -> F harus menghasilkan G -> B -> E -> F dengan jarak 12.0 km."""
        res_heap = dijkstra_min_heap(self.graph, "G", "F", record_trace=True)
        res_array = dijkstra_linear_array(self.graph, "G", "F")

        self.assertTrue(res_heap.is_reachable)
        self.assertAlmostEqual(res_heap.distance, 12.0)
        self.assertEqual(res_heap.path, ["G", "B", "E", "F"])
        self.assertGreater(len(res_heap.trace_logs), 0)

        # Pastikan versi Min-Heap O((V+E) log V) dan Array O(V^2) memberikan hasil identik
        self.assertAlmostEqual(res_heap.distance, res_array.distance)
        self.assertEqual(res_heap.path, res_array.path)

    def test_optimality_against_all_simple_paths(self) -> None:
        """Verifikasi bahwa jarak Dijkstra G -> F lebih kecil atau sama dengan seluruh jalur DFS."""
        res = dijkstra_min_heap(self.graph, "G", "F")
        all_paths = find_all_simple_paths(self.graph, "G", "F")

        self.assertGreaterEqual(len(all_paths), 4)
        best_dfs_dist, best_dfs_path = all_paths[0]
        self.assertAlmostEqual(res.distance, best_dfs_dist)
        self.assertEqual(res.path, best_dfs_path)

    def test_edge_case_disconnected_graph(self) -> None:
        """Kasus Batas 1: Graf terputus harus mengembalikan distance=None dan path=[]."""
        disconnected = create_disconnected_courier_graph()

        res_f = dijkstra_min_heap(disconnected, "G", "F")
        self.assertFalse(res_f.is_reachable)
        self.assertIsNone(res_f.distance)
        self.assertEqual(res_f.path, [])

        res_z = dijkstra_min_heap(disconnected, "G", "Z")
        self.assertFalse(res_z.is_reachable)
        self.assertIsNone(res_z.distance)
        self.assertEqual(res_z.path, [])

    def test_edge_case_same_start_and_end(self) -> None:
        """Kasus Batas 2: Titik awal sama dengan tujuan (G -> G) menghasilkan jarak 0.0 km."""
        res = dijkstra_min_heap(self.graph, "G", "G")
        self.assertTrue(res.is_reachable)
        self.assertAlmostEqual(res.distance, 0.0)
        self.assertEqual(res.path, ["G"])
        self.assertEqual(res.iterations, 1)

    def test_edge_case_equal_weight_paths_tie_breaking(self) -> None:
        """Kasus Batas 3: Dua jalur berbobot sama (G -> D: 11.0 km via A atau B)."""
        res = dijkstra_min_heap(self.graph, "G", "D")
        self.assertTrue(res.is_reachable)
        self.assertAlmostEqual(res.distance, 11.0)
        self.assertIn(res.path, [["G", "A", "D"], ["G", "B", "D"]])

    def test_edge_case_invalid_inputs(self) -> None:
        """Kasus Batas 4: Penolakan simpul tidak terdaftar, bobot negatif, dan self-loop."""
        with self.assertRaises(ValueError):
            dijkstra_min_heap(self.graph, "G", "SIMPUL_ASING")

        g_temp = WeightedGraph()
        g_temp.add_node(LocationNode("A", "Lokasi A"))
        g_temp.add_node(LocationNode("B", "Lokasi B"))

        with self.assertRaises(ValueError):
            g_temp.add_edge("A", "B", -5.0)

        with self.assertRaises(ValueError):
            g_temp.add_edge("A", "A", 2.0)

    def test_delivery_status_fsm(self) -> None:
        """Menguji validasi transisi Finite State Automaton (FSM) pengiriman paket."""
        fsm = DeliveryStatusFSM()
        self.assertEqual(fsm.current_state, "IDLE")

        # Transisi valid: IDLE -> ASSIGNED
        log1 = fsm.trigger("terima_pesanan")
        self.assertTrue(log1.is_valid)
        self.assertEqual(fsm.current_state, "ASSIGNED")

        # Transisi tidak valid: ASSIGNED langsung paket_diterima (harus ditolak)
        log_invalid = fsm.trigger("paket_diterima")
        self.assertFalse(log_invalid.is_valid)
        self.assertEqual(fsm.current_state, "ASSIGNED")

        # Transisi valid hingga state akhir DELIVERED
        fsm.trigger("mulai_jalan")
        log_final = fsm.trigger("paket_diterima")
        self.assertTrue(log_final.is_valid)
        self.assertTrue(log_final.is_accepting)
        self.assertEqual(fsm.current_state, "DELIVERED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
