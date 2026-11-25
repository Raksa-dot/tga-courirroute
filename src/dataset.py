"""
Modul `dataset.py`
Menyediakan data topologi standar jaringan pengiriman paket `CourierRoute` (7 lokasi, 9 jalan)
serta generator graf jalan raya acak untuk pengujian skalabilitas kompleksitas algoritma.
"""

from typing import List, Tuple
import random

from .models import LocationNode, WeightedGraph


DEFAULT_LOCATIONS: List[Tuple[str, str, float, float]] = [
    ("G", "Gudang Pusat", 100.0, 235.0),
    ("A", "Lokasi A",     280.0, 105.0),
    ("B", "Lokasi B",     280.0, 350.0),
    ("C", "Lokasi C",     480.0,  65.0),
    ("D", "Lokasi D",     480.0, 235.0),
    ("E", "Lokasi E",     480.0, 390.0),
    ("F", "Lokasi F",     670.0, 235.0),
]

DEFAULT_ROADS: List[Tuple[str, str, float]] = [
    ("G", "A", 5.0),
    ("G", "B", 4.0),
    ("A", "C", 3.0),
    ("A", "D", 6.0),
    ("B", "D", 7.0),
    ("B", "E", 2.0),
    ("C", "F", 5.0),
    ("D", "F", 2.0),
    ("E", "F", 6.0),
]


def create_default_courier_graph() -> WeightedGraph:
    """Membangun objek WeightedGraph standar studi kasus CourierRoute (7 simpul, 9 sisi)."""
    graph = WeightedGraph()
    for node_id, name, x, y in DEFAULT_LOCATIONS:
        graph.add_node(LocationNode(id=node_id, name=name, x=x, y=y))
    for u, v, w in DEFAULT_ROADS:
        graph.add_edge(u, v, w)
    return graph


def create_disconnected_courier_graph() -> WeightedGraph:
    """
    Membangun skenario kasus batas (Edge Case) Graf Terputus:
    - Seluruh akses jalan menuju Lokasi F ditutup (C-F, D-F, E-F dihapus).
    - Ditambahkan Lokasi Z (Pulau Terisolasi) tanpa ruas jalan penghubung.
    """
    graph = WeightedGraph()
    for node_id, name, x, y in DEFAULT_LOCATIONS:
        graph.add_node(LocationNode(id=node_id, name=name, x=x, y=y))
    graph.add_node(LocationNode(id="Z", name="Lokasi Z (Terisolasi)", x=670.0, y=395.0))

    for u, v, w in DEFAULT_ROADS:
        if "F" not in (u, v):
            graph.add_edge(u, v, w)
    return graph


def generate_sparse_road_graph(
    num_nodes: int, avg_degree: int = 3, seed: int = 42
) -> Tuple[WeightedGraph, str, str]:
    """
    Membangun graf jaringan jalan jarang (sparse graph) terhubung dengan `num_nodes` simpul
    untuk kebutuhan benchmark empiris Min-Heap O((V+E) log V) vs Array Linear Scan O(V^2).
    """
    rng = random.Random(seed + num_nodes)
    graph = WeightedGraph()
    node_ids = [f"N{i}" for i in range(num_nodes)]

    for node_id in node_ids:
        graph.add_node(LocationNode(id=node_id, name=f"Titik {node_id}"))

    seen_pairs = set()
    # Buat tulang punggung rantai terhubung
    for i in range(num_nodes - 1):
        weight = round(rng.uniform(1.0, 10.0), 1)
        graph.add_edge(node_ids[i], node_ids[i + 1], weight)
        seen_pairs.add((i, i + 1))

    target_edges = min((num_nodes * avg_degree) // 2, (num_nodes * (num_nodes - 1)) // 2)
    while len(graph.edges) < target_edges:
        a, b = sorted(rng.sample(range(num_nodes), 2))
        if (a, b) not in seen_pairs:
            seen_pairs.add((a, b))
            graph.add_edge(node_ids[a], node_ids[b], round(rng.uniform(1.0, 15.0), 1))

    return graph, node_ids[0], node_ids[-1]
