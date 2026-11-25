# 📦 CourierRoute — Sistem Pencarian Jalur Teroptimal dalam Jaringan Pengiriman Paket Menggunakan Graf Berbobot

**Anggota Kelompok:**
1. **Rangga Akhdan A.S.P** — `2411102441111`
2. **M. Nabil Syafiq** — `2411102441110`
3. **Fatwa Ikhwan Maulaya** — `2411102441063`

Proyek Mata Kuliah **Teori Graph dan Automata** yang mengimplementasikan pemodelan **Graf Berbobot Tak Berarah $G = (V, E, w)$**, pencarian jalur terpendek menggunakan **Algoritma Dijkstra** (*Min-Heap Priority Queue* $O((V + E) \log V)$ dan *Array Linear Scan* $O(V^2)$), serta **Deterministic Finite Automaton (FSM)** 5-tupel $M = (Q, \Sigma, \delta, q_0, F)$ untuk validasi alur status pengiriman paket.

---

## 📁 Struktur Direktori Proyek (Hasil Refactoring)

```text
Teori Graf/
├── PROJECT TEORI GRAPH DAN AUTOMATA.pdf       # Dokumen panduan & rubrik penilaian proyek
├── README.md                                  # Dokumentasi utama & panduan struktur direktori
├── main.py                                    # Entry-point CLI untuk menjalankan demo, trace, SVG, & benchmark
│
├── src/                                       # Paket Python Modular (Clean Code & Type-Annotated)
│   ├── __init__.py                            # Ekspor antarmuka paket publik
│   ├── models.py                              # Dataclass LocationNode, RoadEdge, RouteResult, & WeightedGraph
│   ├── algorithms.py                          # Dijkstra Min-Heap O((V+E)log V), Array O(V²), & DFS All Paths
│   ├── automata.py                            # Finite State Automaton (DeliveryStatusFSM)
│   ├── visualizer.py                          # Generator visualisasi graf SVG
│   └── dataset.py                             # Dataset CourierRoute (7 lokasi, 9 jalan) & generator graf uji
│
├── tests/                                     # Unit Testing Otomatis (Python unittest)
│   └── test_courier_route.py                  # Pengujian kasus normal, edge cases, matriks, & FSM
│
├── notebooks/                                 # Buku Kerja Interaktif Jupyter Notebook (.ipynb)
│   └── Sistem_Pencarian_Jalur_Teroptimal_Graf_Berbobot.ipynb
│
├── docs/                                      # Laporan Proyek Lengkap & Catatan Dokumentasi
│   ├── Laporan_Project_Teori_Graf.md          # Laporan utama sesuai 5 bab rubrik PDF & panduan presentasi
│   └── README_CourierRoute.md                 # Dokumentasi ringkas prototipe CourierRoute
│
├── assets/                                    # Hasil Visualisasi Graf Berformat Vektor (.svg)
│   ├── visualisasi_jalur_optimal.svg          # Visualisasi rute optimal G -> B -> E -> F (12.0 km)
│   └── visualisasi_graf_terputus.svg          # Visualisasi kasus batas saat akses jalan ke F terputus
│
└── web/                                       # Aplikasi Web Interaktif (HTML5, CSS3, dan JS Terpisah)
    ├── CourierRoute.html                      # Halaman utama aplikasi simulasi web
    ├── css/
    │   └── style.css                          # Styling antarmuka modern & responsif
    └── js/
        └── app.js                             # Logika graf, Dijkstra, render SVG, & simulator FSM di browser
```

---

## 🚀 Cara Menjalankan Proyek

### 1. Menjalankan Simulasi CLI & Generator Visualisasi (`main.py`)
```powershell
python main.py
```
Perintah ini akan menampilkan tabel *Adjacency List*, *Adjacency Matrix* $7 \times 7$, *trace* langkah-demi-langkah Dijkstra (`G -> F`), pengujian seluruh lokasi & *edge cases*, memperbarui gambar visualisasi di `assets/`, serta menjalankan benchmark kompleksitas.

### 2. Menjalankan Unit Testing Otomatis (`tests/`)
```powershell
python -m unittest discover -s tests -v
```

### 3. Membuka Jupyter Notebook (`notebooks/`)
Buka file [notebooks/Sistem_Pencarian_Jalur_Teroptimal_Graf_Berbobot.ipynb](notebooks/Sistem_Pencarian_Jalur_Teroptimal_Graf_Berbobot.ipynb) di VS Code, JupyterLab, atau Google Colab. Seluruh *cell* sudah dieksekusi dan mengintegrasikan modul hasil *refactoring* dari paket `src/`.

### 4. Membuka Laporan Proyek (`docs/`) & Aplikasi Web (`web/`)
- **Laporan Lengkap (`.md`):** [docs/Laporan_Project_Teori_Graf.md](docs/Laporan_Project_Teori_Graf.md)
- **Demo Web Interaktif (`.html`):** Buka [web/CourierRoute.html](web/CourierRoute.html) langsung di browser.
