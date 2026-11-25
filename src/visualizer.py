"""
Modul `visualizer.py`
Menghasilkan visualisasi graf berbobot dan jalur teroptimal dalam format gambar vektor SVG.
"""

from typing import List, Optional
import os

from .models import WeightedGraph


def render_graph_svg(
    graph: WeightedGraph,
    highlight_path: List[str],
    start_node: str,
    end_node: str,
    title: str = "Visualisasi Graf Jaringan Pengiriman Paket (CourierRoute)",
    subtitle: str = "Garis hijau tebal menunjukkan jalur teroptimal hasil Algoritma Dijkstra",
    save_path: Optional[str] = None,
) -> str:
    """Merender topologi WeightedGraph beserta highlight jalur optimal ke dalam string SVG."""
    active_edges = set()
    for i in range(len(highlight_path) - 1):
        u, v = sorted([highlight_path[i], highlight_path[i + 1]])
        active_edges.add(f"{u}-{v}")

    svg_lines = [
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 780 520" width="100%" '
        'style="max-width:780px;background:#fbfdff;border:1px solid #dfe7f1;'
        'border-radius:16px;font-family:Segoe UI,Inter,Arial,sans-serif">',
        "  <defs>",
        '    <filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">',
        '      <feDropShadow dx="0" dy="2" stdDeviation="2.5" flood-color="#172338" flood-opacity="0.12"/>',
        "    </filter>",
        "  </defs>",
        '  <rect x="0" y="0" width="780" height="64" fill="#14213d" rx="16"/>',
        '  <rect x="0" y="48" width="780" height="16" fill="#14213d"/>',
        f'  <text x="24" y="30" fill="#ffffff" font-size="16" font-weight="700">{title}</text>',
        f'  <text x="24" y="50" fill="#aab9d4" font-size="12">{subtitle}</text>',
        '  <g transform="translate(10, 35)">',
    ]

    # 1. Gambar ruas jalan (Edges) beserta kotak label bobotnya
    for edge in graph.edges:
        p = graph.nodes[edge.source]
        q = graph.nodes[edge.target]
        key = "-".join(sorted([edge.source, edge.target]))
        is_active = key in active_edges

        stroke_color = "#14a673" if is_active else "#c5d0df"
        stroke_width = "5.5" if is_active else "3"
        label_color = "#0b7a53" if is_active else "#52637b"
        label_bg = "#e5f8f0" if is_active else "#ffffff"
        label_border = "#14a673" if is_active else "#d0dae8"

        mx = (p.x + q.x) / 2.0
        my = (p.y + q.y) / 2.0

        svg_lines.append(
            f'    <line x1="{p.x}" y1="{p.y}" x2="{q.x}" y2="{q.y}" '
            f'stroke="{stroke_color}" stroke-width="{stroke_width}" stroke-linecap="round"/>'
        )
        svg_lines.append(
            f'    <rect x="{mx - 24:.1f}" y="{my - 21:.1f}" width="48" height="20" rx="6" '
            f'fill="{label_bg}" stroke="{label_border}" stroke-width="1.2"/>'
        )
        svg_lines.append(
            f'    <text x="{mx:.1f}" y="{my - 7:.1f}" text-anchor="middle" '
            f'fill="{label_color}" font-size="11.5" font-weight="700">{edge.weight:g} km</text>'
        )

    # 2. Gambar simpul lokasi (Vertices)
    for node_id, node in graph.nodes.items():
        in_path = node_id in highlight_path
        if node_id == start_node:
            fill, stroke, text_col = "#fff3df", "#e6a33d", "#8e5a12"
        elif in_path:
            fill, stroke, text_col = "#e5f8f0", "#14a673", "#0b7a53"
        else:
            fill, stroke, text_col = "#ffffff", "#94a7c2", "#263852"

        stroke_w = "4" if (in_path or node_id == start_node) else "3"
        svg_lines.extend([
            f'    <g transform="translate({node.x},{node.y})">',
            f'      <circle r="24" fill="{fill}" stroke="{stroke}" stroke-width="{stroke_w}" filter="url(#shadow)"/>',
            f'      <text y="5" text-anchor="middle" fill="{text_col}" font-size="15" font-weight="800">{node.id}</text>',
            f'      <text y="41" text-anchor="middle" fill="#42526a" font-size="11.5" font-weight="600">{node.name}</text>',
            "    </g>",
        ])

    svg_lines.append("  </g>")

    # 3. Footer informasi rute & legenda
    route_str = " → ".join(highlight_path) if highlight_path else "Tidak ada jalur (Graf Terputus)"
    svg_lines.extend([
        '  <rect x="16" y="472" width="748" height="34" rx="8" fill="#f1f5fb" stroke="#dfe7f1"/>',
        f'  <text x="28" y="493" fill="#172338" font-size="12.5" font-weight="700">'
        f"Hasil Rute ({start_node} → {end_node}): {route_str}</text>",
        '  <circle cx="555" cy="489" r="6" fill="#fff3df" stroke="#e6a33d" stroke-width="2.5"/>',
        '  <text x="567" y="493" fill="#506078" font-size="11.5">Titik Awal</text>',
        '  <circle cx="645" cy="489" r="6" fill="#e5f8f0" stroke="#14a673" stroke-width="2.5"/>',
        '  <text x="657" y="493" fill="#506078" font-size="11.5">Jalur Optimal</text>',
        "</svg>",
    ])

    svg_content = "\n".join(svg_lines)
    if save_path:
        os.makedirs(os.path.dirname(os.path.abspath(save_path)), exist_ok=True)
        with open(save_path, "w", encoding="utf-8") as file_obj:
            file_obj.write(svg_content)

    return svg_content
