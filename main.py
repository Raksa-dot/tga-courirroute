"""
Entry-Point Utama (`main.py`)
Menjalankan keseluruhan alur Sistem Pencarian Jalur Teroptimal Pengiriman Paket (CourierRoute):
1. Menampilkan representasi Adjacency List dan Adjacency Matrix.
2. Menjalankan Algoritma Dijkstra (G -> F) lengkap dengan trace langkah demi langkah.
3. Menguji skenario normal dan skenario kasus batas (Edge Cases).
4. Menghasilkan file visualisasi SVG ke dalam folder `assets/`.
5. Menjalankan benchmark kompleksitas waktu Min-Heap O((V+E) log V) vs Array O(V^2).
"""

import math
import os
import time

from src.dataset import (
    create_default_courier_graph,
    create_disconnected_courier_graph,
    generate_sparse_road_graph,
)
from src.algorithms import (
    dijkstra_min_heap,
    dijkstra_linear_array,
    find_all_simple_paths,
)
from src.automata import DeliveryStatusFSM
from src.visualizer import render_graph_svg


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ASSETS_DIR = os.path.join(BASE_DIR, "assets")


def print_section(title: str) -> None:
    print("\n" + "=" * 84)
    print(title)
    print("=" * 84)


def run_cli_demo() -> None:
    graph = create_default_courier_graph()

    # 1. Representasi Graf
    print_section("1. REPRESENTASI ADJACENCY LIST & DERAJAT SIMPUL G = (V, E, w)")
    print(f"{'Simpul':<8} | {'Nama Lokasi':<15} | {'Derajat deg(v)':<14} | {'Daftar Tetangga (Jarak)'}")
    print("-" * 84)
    for node_id in graph.node_ids:
        node = graph.nodes[node_id]
        neighbors = ", ".join(f"{v} ({w:g} km)" for v, w in graph.adjacency_list[node_id])
        print(f"  {node_id:<6} | {node.name:<15} | {graph.degree(node_id):^14} | {neighbors}")

    print_section("2. REPRESENTASI ADJACENCY MATRIX (7x7 dalam satuan km)")
    ids, matrix = graph.to_adjacency_matrix()
    header = "Dari / Ke | " + " | ".join(f"{n:^5}" for n in ids)
    print(header)
    print("-" * len(header))
    for i, u in enumerate(ids):
        row = " | ".join("  ∞  " if math.isinf(val) else f"{val:^5.0f}" for val in matrix[i])
        print(f"   {u:<6} | {row}")

    # 2. Pencarian Jalur Utama (G -> F) dengan Trace
    print_section("3. TRACE LANGKAH-DEMI-LANGKAH ALGORITMA DIJKSTRA (G -> F)")
    main_result = dijkstra_min_heap(graph, start="G", end="F", record_trace=True)
    for line in main_result.trace_logs:
        print(line)

    print("-" * 84)
    print(f"• Rute Teroptimal : {main_result.format_route(' -> ')}")
    print(f"• Total Jarak     : {main_result.distance:.1f} km")
    print(f"• Statistik       : {main_result.iterations} simpul dikunci, {main_result.relaxations} uji relaksasi")

    # 3. Pengujian Seluruh Tujuan & Verifikasi DFS
    print_section("4. PENGUJIAN SKENARIO NORMAL (RUTE DARI GUDANG 'G' KE SELURUH LOKASI)")
    print(f"{'Tujuan':<20} | {'Jarak Minimum':<15} | {'Urutan Jalur Teroptimal'}")
    print("-" * 84)
    for target in graph.node_ids:
        res = dijkstra_min_heap(graph, "G", target)
        print(
            f"{target} ({graph.nodes[target].name:<14}) | "
            f"{res.distance:>10.1f} km  | {res.format_route(' -> ')}"
        )

    print_section("5. VERIFIKASI MATEMATIS: PERBANDINGAN SELURUH JALUR G -> F (DFS)")
    for rank, (dist_val, path_list) in enumerate(find_all_simple_paths(graph, "G", "F"), start=1):
        badge = "★ TEROPTIMAL (DIJKSTRA)" if rank == 1 else f"Selisih +{dist_val - main_result.distance:.1f} km"
        print(f"  #{rank:<2} | {dist_val:>6.1f} km | {' -> '.join(path_list):<28} | {badge}")

    # 4. Pengujian Kasus Batas (Edge Cases) & Pembuatan Visualisasi SVG
    print_section("6. PENGUJIAN KASUS BATAS (EDGE CASES) & GENERASI VISUALISASI SVG")
    disconnected_graph = create_disconnected_courier_graph()
    res_disc = dijkstra_min_heap(disconnected_graph, "G", "F")
    res_same = dijkstra_min_heap(graph, "G", "G")
    res_tie = dijkstra_min_heap(graph, "G", "D")

    print(f"• [EC-01] Graf Terputus (G -> F ditutup) : Jarak = {res_disc.distance}, Jalur = {res_disc.path}")
    print(f"• [EC-02] Titik Awal = Tujuan (G -> G)   : Jarak = {res_same.distance:.1f} km, Jalur = {res_same.path}")
    print(f"• [EC-03] Jalur Ganda Setara (G -> D)    : Jarak = {res_tie.distance:.1f} km, Jalur = {res_tie.format_route()}")

    optimal_svg_path = os.path.join(ASSETS_DIR, "visualisasi_jalur_optimal.svg")
    disconnected_svg_path = os.path.join(ASSETS_DIR, "visualisasi_graf_terputus.svg")

    render_graph_svg(
        graph=graph,
        highlight_path=main_result.path,
        start_node="G",
        end_node="F",
        title="Visualisasi Jalur Teroptimal CourierRoute: Gudang (G) → Lokasi F (12.0 km)",
        subtitle="Jalur Terpilih: G → B (4 km) → E (2 km) → F (6 km) | Total Jarak Minimum = 12.0 km",
        save_path=optimal_svg_path,
    )

    # Untuk visualisasi graf terputus, tampilkan 7 simpul utama tanpa sisi ke F
    disc_vis_graph = create_default_courier_graph()
    disc_vis_graph._edges = [e for e in disc_vis_graph.edges if "F" not in (e.source, e.target)]
    disc_vis_graph._rebuild_adjacency_list()
    render_graph_svg(
        graph=disc_vis_graph,
        highlight_path=[],
        start_node="G",
        end_node="F",
        title="Visualisasi Edge Case: Graf Terputus (Akses Jalan Menuju Lokasi F Ditutup)",
        subtitle="Sistem mendeteksi dist[F] = ∞ dan mengembalikan status: Tidak ada jalur dari G ke F",
        save_path=disconnected_svg_path,
    )
    print(f"• File SVG tersimpan di: {optimal_svg_path}")
    print(f"• File SVG tersimpan di: {disconnected_svg_path}")

    # 5. Benchmark Kompleksitas
    print_section("7. BENCHMARK KOMPLEKSITAS: MIN-HEAP O((V+E) log V) vs ARRAY O(V^2)")
    print(f"{'Jumlah Lokasi (V)':<18} | {'Jalan (E)':<10} | {'Min-Heap (ms)':<15} | {'Array O(V²) (ms)':<17} | {'Speedup'}")
    print("-" * 84)
    for v_size in [7, 50, 200, 500, 1000]:
        if v_size == 7:
            g_bench, s_node, e_node = graph, "G", "F"
        else:
            g_bench, s_node, e_node = generate_sparse_road_graph(v_size)

        t0 = time.perf_counter()
        r_heap = dijkstra_min_heap(g_bench, s_node, e_node)
        t_heap = (time.perf_counter() - t0) * 1000.0

        t1 = time.perf_counter()
        r_arr = dijkstra_linear_array(g_bench, s_node, e_node)
        t_arr = (time.perf_counter() - t1) * 1000.0

        assert math.isclose(r_heap.distance, r_arr.distance)
        speedup = t_arr / max(t_heap, 1e-6)
        print(f"{v_size:>17} | {len(g_bench.edges):>10} | {t_heap:>12.3f} ms | {t_arr:>14.3f} ms | {speedup:>6.1f}x")

    # 6. Simulasi FSM Pengiriman
    print_section("8. SIMULASI FINITE STATE AUTOMATON (FSM) STATUS PENGIRIMAN PAKET")
    fsm = DeliveryStatusFSM()
    for event in ["terima_pesanan", "paket_diterima", "mulai_jalan", "paket_diterima"]:
        log = fsm.trigger(event)
        print(f"  Aksi '{event:<15}' -> {log.message}")


if __name__ == "__main__":
    run_cli_demo()
