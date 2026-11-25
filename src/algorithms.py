"""
Modul `algorithms.py`
Berisi implementasi Algoritma Pencarian Jalur Terpendek:
1. `dijkstra_min_heap`     : Algoritma Dijkstra berbasis Min-Heap Priority Queue O((V + E) log V).
2. `dijkstra_linear_array` : Algoritma Dijkstra berbasis Array Linear Scan O(V^2).
3. `find_all_simple_paths` : Eksplorasi DFS untuk menemukan seluruh jalur sederhana sebagai pembanding.
"""

from typing import Dict, List, Optional, Set, Tuple
import heapq
import math

from .models import RouteResult, WeightedGraph


def _validate_endpoints(graph: WeightedGraph, start: str, end: str) -> None:
    """Memastikan simpul awal dan simpul tujuan terdaftar di dalam graf."""
    if start not in graph.nodes:
        raise ValueError(f"Simpul awal '{start}' tidak ditemukan di dalam graf.")
    if end not in graph.nodes:
        raise ValueError(f"Simpul tujuan '{end}' tidak ditemukan di dalam graf.")


def _reconstruct_path(
    prev: Dict[str, Optional[str]], start: str, end: str, final_dist: float
) -> List[str]:
    """TAHAP 4: Merunut balik (backtracking) jalur optimal dari tujuan ke titik awal."""
    if math.isinf(final_dist):
        return []

    path: List[str] = []
    curr: Optional[str] = end
    while curr is not None:
        path.append(curr)
        curr = prev[curr]
    path.reverse()

    return path if (path and path[0] == start) else []


def dijkstra_min_heap(
    graph: WeightedGraph,
    start: str,
    end: str,
    record_trace: bool = False,
) -> RouteResult:
    """
    Mencari jalur teroptimal dari `start` ke `end` menggunakan Algoritma Dijkstra
    dengan struktur data Binary Min-Heap Priority Queue.

    Kompleksitas Waktu : O((V + E) log V)
    Kompleksitas Ruang : O(V + E)
    """
    _validate_endpoints(graph, start, end)
    adj = graph.adjacency_list

    # TAHAP 1: Inisialisasi tabel jarak dan tabel pendahulu (prev)
    dist: Dict[str, float] = {node_id: math.inf for node_id in graph.node_ids}
    prev: Dict[str, Optional[str]] = {node_id: None for node_id in graph.node_ids}
    dist[start] = 0.0

    priority_queue: List[Tuple[float, str]] = [(0.0, start)]
    visited: Set[str] = set()
    visited_order: List[str] = []
    trace_logs: List[str] = []
    iterations = 0
    relaxations = 0

    # TAHAP 2: Pemilihan simpul terdekat (Greedy Selection)
    while priority_queue:
        current_dist, u = heapq.heappop(priority_queue)

        if u in visited:
            continue
        visited.add(u)
        visited_order.append(u)
        iterations += 1

        if record_trace:
            snapshot = " | ".join(
                f"{k}:{'∞' if math.isinf(v) else f'{v:g}'}" for k, v in dist.items()
            )
            trace_logs.append(
                f"[Iterasi {iterations}] Kunci Simpul '{u}' (Jarak = {current_dist:.1f} km) "
                f"| Tabel dist: [{snapshot}]"
            )

        # Optimasi Early-Exit: berhenti segera saat simpul tujuan telah dikunci
        if u == end:
            if record_trace:
                trace_logs.append(
                    f"   ✓ Tujuan '{end}' telah dikunci dengan jarak minimum {current_dist:.1f} km."
                )
            break

        # TAHAP 3: Relaksasi tetangga (Edge Relaxation)
        for v, weight in adj[u]:
            if v in visited:
                continue

            relaxations += 1
            candidate_dist = current_dist + weight
            old_dist = dist[v]

            if candidate_dist < old_dist:
                dist[v] = candidate_dist
                prev[v] = u
                heapq.heappush(priority_queue, (candidate_dist, v))
                if record_trace:
                    old_str = "∞" if math.isinf(old_dist) else f"{old_dist:.1f}"
                    trace_logs.append(
                        f"   -> Relaksasi ({u} -> {v}, +{weight:g} km): "
                        f"{old_str} > {candidate_dist:.1f} km [UPDATE dist[{v}]={candidate_dist:.1f}, prev[{v}]={u}]"
                    )
            elif record_trace:
                trace_logs.append(
                    f"   -> Cek jalan ({u} -> {v}, +{weight:g} km): "
                    f"{old_dist:.1f} <= {candidate_dist:.1f} km [TETAP]"
                )

    # TAHAP 4: Rekonstruksi Jalur
    final_distance = None if math.isinf(dist[end]) else dist[end]
    path = _reconstruct_path(prev, start, end, dist[end])

    return RouteResult(
        start=start,
        end=end,
        distance=final_distance,
        path=path,
        visited_order=visited_order,
        iterations=iterations,
        relaxations=relaxations,
        dist_table=dist,
        prev_table=prev,
        trace_logs=trace_logs,
    )


def dijkstra_linear_array(
    graph: WeightedGraph,
    start: str,
    end: str,
) -> RouteResult:
    """
    Implementasi Algoritma Dijkstra tanpa Priority Queue (menggunakan pencarian linear O(V)
    di setiap iterasi, sebagaimana pada prototipe web CourierRoute.html).

    Kompleksitas Waktu : O(V^2)
    Kompleksitas Ruang : O(V + E)
    """
    _validate_endpoints(graph, start, end)
    node_ids = graph.node_ids
    adj = graph.adjacency_list

    dist: Dict[str, float] = {n: math.inf for n in node_ids}
    prev: Dict[str, Optional[str]] = {n: None for n in node_ids}
    visited: Set[str] = set()
    visited_order: List[str] = []
    dist[start] = 0.0

    iterations = 0
    relaxations = 0

    while True:
        # Linear scan O(V) untuk mencari simpul belum dikunjungi dengan dist terkecil
        u: Optional[str] = None
        for candidate in node_ids:
            if candidate not in visited and (u is None or dist[candidate] < dist[u]):
                u = candidate

        if u is None or math.isinf(dist[u]):
            break

        visited.add(u)
        visited_order.append(u)
        iterations += 1

        if u == end:
            break

        for v, weight in adj[u]:
            if v not in visited:
                relaxations += 1
                if dist[u] + weight < dist[v]:
                    dist[v] = dist[u] + weight
                    prev[v] = u

    final_distance = None if math.isinf(dist[end]) else dist[end]
    path = _reconstruct_path(prev, start, end, dist[end])

    return RouteResult(
        start=start,
        end=end,
        distance=final_distance,
        path=path,
        visited_order=visited_order,
        iterations=iterations,
        relaxations=relaxations,
        dist_table=dist,
        prev_table=prev,
    )


def find_all_simple_paths(
    graph: WeightedGraph,
    start: str,
    end: str,
) -> List[Tuple[float, List[str]]]:
    """
    Mencari seluruh lintasan sederhana (tanpa siklus) dari `start` ke `end` menggunakan
    Depth-First Search (DFS), diurutkan dari total jarak terpendek ke terjauh.
    """
    _validate_endpoints(graph, start, end)
    adj = graph.adjacency_list
    results: List[Tuple[float, List[str]]] = []

    def _dfs(current: str, current_path: List[str], current_dist: float) -> None:
        if current == end:
            results.append((current_dist, list(current_path)))
            return
        for neighbor, weight in adj[current]:
            if neighbor not in current_path:
                current_path.append(neighbor)
                _dfs(neighbor, current_path, current_dist + weight)
                current_path.pop()

    _dfs(start, [start], 0.0)
    return sorted(results, key=lambda item: item[0])
