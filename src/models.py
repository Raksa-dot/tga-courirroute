"""
Modul `models.py`
Mendefinisikan struktur data berorientasi objek untuk Graf Berbobot Tak Berarah G = (V, E, w).
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple
import math


@dataclass(frozen=True)
class LocationNode:
    """Merepresentasikan satu simpul lokasi (Vertex) pada jaringan pengiriman."""
    id: str
    name: str
    x: float = 0.0
    y: float = 0.0


@dataclass(frozen=True)
class RoadEdge:
    """Merepresentasikan satu ruas jalan berbobot (Weighted Edge) antar dua lokasi."""
    source: str
    target: str
    weight: float

    def __post_init__(self) -> None:
        if self.source == self.target:
            raise ValueError(f"Self-loop tidak diizinkan: ({self.source}, {self.target}).")
        if not math.isfinite(self.weight) or self.weight < 0:
            raise ValueError(
                f"Bobot jalan harus bernilai non-negatif (w >= 0), ditemukan: {self.weight} "
                f"pada ruas ({self.source}, {self.target})."
            )


@dataclass
class RouteResult:
    """Menyimpan hasil pencarian jalur teroptimal beserta metrik evaluasi algoritma."""
    start: str
    end: str
    distance: Optional[float]
    path: List[str]
    visited_order: List[str] = field(default_factory=list)
    iterations: int = 0
    relaxations: int = 0
    dist_table: Dict[str, float] = field(default_factory=dict)
    prev_table: Dict[str, Optional[str]] = field(default_factory=dict)
    trace_logs: List[str] = field(default_factory=list)

    @property
    def is_reachable(self) -> bool:
        """Mengembalikan True jika tujuan dapat dijangkau dari titik awal."""
        return self.distance is not None and len(self.path) > 0

    def format_route(self, separator: str = " -> ") -> str:
        """Memformat urutan simpul jalur menjadi string yang mudah dibaca."""
        if not self.is_reachable:
            return "Tidak ada jalur (Graf Terputus)"
        return separator.join(self.path)


class WeightedGraph:
    """
    Representasi Graf Berbobot Tak Berarah G = (V, E, w).
    Mendukung konversi ke Adjacency List O(V + E) maupun Adjacency Matrix O(V^2).
    """

    def __init__(self) -> None:
        self._nodes: Dict[str, LocationNode] = {}
        self._edges: List[RoadEdge] = []
        self._adj_list: Dict[str, List[Tuple[str, float]]] = {}

    @property
    def nodes(self) -> Dict[str, LocationNode]:
        return self._nodes

    @property
    def edges(self) -> List[RoadEdge]:
        return list(self._edges)

    @property
    def node_ids(self) -> List[str]:
        return list(self._nodes.keys())

    @property
    def adjacency_list(self) -> Dict[str, List[Tuple[str, float]]]:
        return self._adj_list

    def add_node(self, node: LocationNode) -> None:
        """Menambahkan simpul lokasi baru ke dalam graf."""
        self._nodes[node.id] = node
        if node.id not in self._adj_list:
            self._adj_list[node.id] = []

    def add_edge(self, source: str, target: str, weight: float) -> None:
        """Menambahkan atau memperbarui ruas jalan dua arah (undirected) dengan validasi bobot."""
        if source not in self._nodes:
            raise ValueError(f"Simpul asal '{source}' belum terdaftar di dalam graf.")
        if target not in self._nodes:
            raise ValueError(f"Simpul tujuan '{target}' belum terdaftar di dalam graf.")

        edge = RoadEdge(source=source, target=target, weight=float(weight))

        # Perbarui jika sisi sudah ada, atau tambahkan sisi baru
        for idx, existing in enumerate(self._edges):
            if {existing.source, existing.target} == {source, target}:
                self._edges[idx] = edge
                self._rebuild_adjacency_list()
                return

        self._edges.append(edge)
        self._adj_list[source].append((target, edge.weight))
        self._adj_list[target].append((source, edge.weight))

    def _rebuild_adjacency_list(self) -> None:
        self._adj_list = {node_id: [] for node_id in self._nodes}
        for edge in self._edges:
            self._adj_list[edge.source].append((edge.target, edge.weight))
            self._adj_list[edge.target].append((edge.source, edge.weight))

    def degree(self, node_id: str) -> int:
        """Mengembalikan derajat simpul deg(v)."""
        if node_id not in self._adj_list:
            raise ValueError(f"Simpul '{node_id}' tidak ditemukan.")
        return len(self._adj_list[node_id])

    def to_adjacency_matrix(self) -> Tuple[List[str], List[List[float]]]:
        """Membangun Adjacency Matrix berukuran |V| x |V|."""
        ids = self.node_ids
        idx_map = {node_id: i for i, node_id in enumerate(ids)}
        n = len(ids)
        matrix = [[0.0 if i == j else math.inf for j in range(n)] for i in range(n)]

        for edge in self._edges:
            i, j = idx_map[edge.source], idx_map[edge.target]
            matrix[i][j] = edge.weight
            matrix[j][i] = edge.weight

        return ids, matrix
