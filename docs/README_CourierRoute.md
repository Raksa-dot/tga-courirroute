# CourierRoute — Optimasi Rute Kurir

Prototipe web untuk tugas mata kuliah Teori Graf dan Automata.

## Materi yang diterapkan
- **Teori Graf:** vertex, edge, weighted graph, adjacency list, shortest path.
- **Algoritma:** Dijkstra untuk menemukan rute dengan total jarak minimum.
- **Automata:** Finite State Machine (FSM) untuk status pengiriman (Idle, Assigned, En Route, Delivered, Failed).

## Fitur demo
- Visualisasi graf 7 lokasi (G, A–F) dan 9 jalan berbobot.
- Pilih lokasi asal dan tujuan.
- Jalankan Dijkstra, tampilkan jalur dan total jarak.
- Highlight jalan dan simpul pada jalur yang ditemukan.
- Simulasi status pengiriman dengan FSM dan validasi transisi.
- Tabel daftar jalan.

## Cara menjalankan
1. Ekstrak ZIP (jika menggunakan paket ZIP).
2. Buka `courierroute_demo.html` di Chrome, Edge, atau Firefox.
3. Pilih lokasi asal dan tujuan, kemudian klik **Cari rute Dijkstra**.
4. Uji tombol FSM sesuai urutan: Pesanan diterima → Mulai perjalanan → Paket diterima / Pengiriman gagal.

Tidak perlu instalasi, server, atau koneksi internet.

## Data contoh
G-A 5 km; G-B 4 km; A-C 3 km; A-D 6 km; B-D 7 km; B-E 2 km; C-F 5 km; D-F 2 km; E-F 6 km.

Untuk rute G ke F, salah satu rute minimum adalah G → B → E → F dengan jarak 12 km.

## Batasan demo
- Bobot jalan adalah data contoh, bukan jarak peta aktual.
- Jalan dianggap dua arah.
- Dijkstra mengoptimalkan satu pasangan asal–tujuan; optimasi urutan kunjungan banyak pelanggan (TSP/VRP) belum diimplementasikan.
- FSM merupakan simulasi alur status, bukan integrasi perangkat kurir.

## Pengembangan berikutnya
- Tambah/edit/hapus lokasi dan jalan.
- Jalan satu arah dan kondisi jalan ditutup.
- Peta geografis menggunakan Leaflet + OpenStreetMap.
- Multi-pelanggan dengan heuristik VRP/TSP.
- Ekspor hasil dan laporan pengujian algoritma.
