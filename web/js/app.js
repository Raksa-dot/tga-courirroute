/**
 * CourierRoute — Modul Aplikasi Interaktif (`web/js/app.js`)
 * Mengimplementasikan:
 * 1. Pemodelan Graf Berbobot Tak Berarah G = (V, E, w)
 * 2. Algoritma Pencarian Jalur Terpendek Dijkstra
 * 3. Deterministic Finite Automaton (FSM) Status Pengiriman Paket
 */

const INITIAL_NODES = {
  G: { name: "Gudang",   x: 100, y: 235 },
  A: { name: "Lokasi A", x: 280, y: 105 },
  B: { name: "Lokasi B", x: 280, y: 350 },
  C: { name: "Lokasi C", x: 480, y: 65  },
  D: { name: "Lokasi D", x: 480, y: 235 },
  E: { name: "Lokasi E", x: 480, y: 390 },
  F: { name: "Lokasi F", x: 670, y: 235 }
};

const INITIAL_EDGES = [
  ["G", "A", 5],
  ["G", "B", 4],
  ["A", "C", 3],
  ["A", "D", 6],
  ["B", "D", 7],
  ["B", "E", 2],
  ["C", "F", 5],
  ["D", "F", 2],
  ["E", "F", 6]
];

// Tabel transisi Deterministic Finite Automaton (DFA / FSM)
const FSM_TRANSITIONS = {
  IDLE:      { terima_pesanan: "ASSIGNED" },
  ASSIGNED:  { mulai_jalan: "EN_ROUTE" },
  EN_ROUTE:  { paket_diterima: "DELIVERED", gagal_kirim: "FAILED" },
  FAILED:    { jadwalkan_ulang: "ASSIGNED" },
  DELIVERED: {}
};

let nodes = JSON.parse(JSON.stringify(INITIAL_NODES));
let edges = INITIAL_EDGES.map((edge) => [...edge]);
let bestPath = [];
let bestDistance = null;
let currentFsmState = "IDLE";

const $ = (id) => document.getElementById(id);

/**
 * Mengisi opsi dropdown lokasi awal, tujuan, dan form tambah jalan.
 */
function populateSelectOptions() {
  const ids = Object.keys(nodes);
  ["start", "end", "from", "to"].forEach((selectId) => {
    const selectEl = $(selectId);
    const previousValue = selectEl.value;
    selectEl.innerHTML = ids
      .map((id) => `<option value="${id}">${id} — ${nodes[id].name}</option>`)
      .join("");
    if (ids.includes(previousValue)) {
      selectEl.value = previousValue;
    }
  });
  if (!$("end").value || $("end").value === $("start").value) {
    $("end").value = "F";
  }
}

/**
 * Menjalankan Algoritma Dijkstra untuk mencari rute terpendek dari `src` ke `dst`.
 * @param {string} src - ID simpul asal
 * @param {string} dst - ID simpul tujuan
 * @returns {{distance: number|null, path: string[]}}
 */
function runDijkstra(src, dst) {
  const dist = {};
  const prev = {};
  const visited = {};

  // Tahap 1: Inisialisasi
  Object.keys(nodes).forEach((nodeId) => {
    dist[nodeId] = Infinity;
  });
  dist[src] = 0;

  // Tahap 2: Pemilihan simpul terdekat (Greedy Selection)
  while (true) {
    let u = null;
    for (const n of Object.keys(nodes)) {
      if (!visited[n] && (u === null || dist[n] < dist[u])) {
        u = n;
      }
    }

    if (u === null || dist[u] === Infinity) {
      break;
    }

    visited[u] = true;
    if (u === dst) {
      break;
    }

    // Tahap 3: Relaksasi Tetangga (Edge Relaxation)
    for (const [a, b, weight] of edges) {
      const neighbor = a === u ? b : b === u ? a : null;
      if (neighbor !== null && !visited[neighbor] && dist[u] + weight < dist[neighbor]) {
        dist[neighbor] = dist[u] + weight;
        prev[neighbor] = u;
      }
    }
  }

  // Tahap 4: Rekonstruksi Jalur (Backtracking)
  if (dist[dst] === Infinity) {
    return { distance: null, path: [] };
  }

  const path = [dst];
  let current = dst;
  while (current !== src) {
    current = prev[current];
    if (!current) {
      return { distance: null, path: [] };
    }
    path.unshift(current);
  }

  return { distance: dist[dst], path };
}

/**
 * Merender visualisasi SVG graf jaringan dan memperbarui tabel daftar jalan.
 */
function renderGraph() {
  const svg = $("graph");
  const activeEdgeSet = new Set();

  for (let i = 0; i < bestPath.length - 1; i++) {
    const edgeKey = [bestPath[i], bestPath[i + 1]].sort().join("-");
    activeEdgeSet.add(edgeKey);
  }

  let svgMarkup = "";

  // 1. Gambar seluruh sisi (Edges)
  edges.forEach(([a, b, w]) => {
    const p = nodes[a];
    const q = nodes[b];
    const key = [a, b].sort().join("-");
    const isActive = activeEdgeSet.has(key);
    const mx = (p.x + q.x) / 2;
    const my = (p.y + q.y) / 2;

    svgMarkup += `
      <line class="edge ${isActive ? "path" : ""}" x1="${p.x}" y1="${p.y}" x2="${q.x}" y2="${q.y}"/>
      <text class="edge-label ${isActive ? "path" : ""}" x="${mx}" y="${my - 9}" text-anchor="middle">${w} km</text>
    `;
  });

  // 2. Gambar seluruh simpul (Vertices)
  Object.keys(nodes).forEach((nodeId) => {
    const p = nodes[nodeId];
    const classes = [
      "node",
      bestPath.includes(nodeId) ? "onpath" : "",
      nodeId === $("start").value ? "start" : "",
      nodeId === $("end").value ? "end" : "",
      nodeId === "G" ? "warehouse" : ""
    ].filter(Boolean).join(" ");

    svgMarkup += `
      <g class="${classes}" transform="translate(${p.x},${p.y})">
        <circle r="23"/>
        <text y="0">${nodeId}</text>
        <text y="39" style="font-size:11px;font-weight:600;fill:#66758d">${p.name}</text>
      </g>
    `;
  });

  svg.innerHTML = svgMarkup;
  $("nodeCount").textContent = Object.keys(nodes).length;
  $("edgeCount").textContent = edges.length;

  // 3. Perbarui tabel jalan
  $("edgeTable").innerHTML = edges
    .map(([a, b, w]) => {
      const isOptimal = activeEdgeSet.has([a, b].sort().join("-"));
      const badge = isOptimal
        ? '<span class="pill" style="color:#0b8d61;background:#e6f7ef">Rute Optimal</span>'
        : '<span class="pill">Tersedia</span>';
      return `<tr><td><b>${a} — ${b}</b></td><td>${w} km</td><td>${badge}</td></tr>`;
    })
    .join("");
}

/**
 * Menangani aksi pencarian rute terpendek saat tombol diklik.
 */
function handleFindShortestPath() {
  const startNode = $("start").value;
  const endNode = $("end").value;
  const result = runDijkstra(startNode, endNode);

  bestPath = result.path;
  bestDistance = result.distance;
  renderGraph();

  if (result.distance === null) {
    $("result").innerHTML = `
      <div class="result-label">Rute Tidak Ditemukan</div>
      <div class="distance">—</div>
      <div class="route">Tidak ada jalur dari ${startNode} ke ${endNode}. Graf mungkin terputus.</div>
    `;
  } else {
    const routeHtml = result.path
      .map((n) => `<span>${n}</span>`)
      .join('<span class="arrow"> → </span>');

    $("result").innerHTML = `
      <div class="result-top">
        <span class="result-label">Jarak Minimum</span>
        <span class="pill">Dijkstra</span>
      </div>
      <div class="distance">${result.distance.toFixed(1)} km</div>
      <div class="route">${routeHtml}</div>
      <div class="note">Rute optimal ditemukan dari ${startNode} ke ${endNode}.</div>
    `;
  }
}

/**
 * Menangani transisi state pada Finite State Machine (FSM) pengiriman paket.
 */
function triggerFsmTransition(event) {
  const allowedNext = FSM_TRANSITIONS[currentFsmState] || {};
  const nextState = allowedNext[event];
  const logEl = $("fsmLog");
  const badgeEl = $("fsmStateBadge");

  if (!nextState) {
    logEl.style.color = "#c53030";
    logEl.textContent = `[DITOLAK] Transisi δ(${currentFsmState}, ${event}) tidak valid!`;
    return;
  }

  const prevState = currentFsmState;
  currentFsmState = nextState;
  badgeEl.textContent = currentFsmState;
  logEl.style.color = "#0b7a53";
  logEl.textContent = `[VALID] δ(${prevState}, ${event}) → ${currentFsmState}${
    currentFsmState === "DELIVERED" ? " (FINAL STATE)" : ""
  }`;
}

// Event Listeners
$("find").onclick = handleFindShortestPath;
$("start").onchange = () => { bestPath = []; renderGraph(); };
$("end").onchange = () => { bestPath = []; renderGraph(); };

$("add").onclick = () => {
  const fromNode = $("from").value;
  const toNode = $("to").value;
  const weightVal = parseFloat($("weight").value);

  if (fromNode === toNode) {
    alert("Pilih dua lokasi yang berbeda.");
    return;
  }
  if (!Number.isFinite(weightVal) || weightVal < 0) {
    alert("Jarak harus berupa angka non-negatif (w >= 0).");
    return;
  }

  const existingIdx = edges.findIndex(
    (e) => (e[0] === fromNode && e[1] === toNode) || (e[0] === toNode && e[1] === fromNode)
  );
  if (existingIdx >= 0) {
    edges[existingIdx][2] = weightVal;
  } else {
    edges.push([fromNode, toNode, weightVal]);
  }

  $("weight").value = "";
  bestPath = [];
  renderGraph();
  handleFindShortestPath();
};

$("reset").onclick = () => {
  nodes = JSON.parse(JSON.stringify(INITIAL_NODES));
  edges = INITIAL_EDGES.map((e) => [...e]);
  bestPath = [];
  populateSelectOptions();
  renderGraph();
  handleFindShortestPath();
};

$("random").onclick = () => {
  edges = INITIAL_EDGES.map((e) => [
    e[0],
    e[1],
    Math.round((1 + Math.random() * 8) * 10) / 10
  ]);
  bestPath = [];
  renderGraph();
  handleFindShortestPath();
};

document.querySelectorAll(".fsm-btn[data-event]").forEach((btn) => {
  btn.addEventListener("click", () => {
    triggerFsmTransition(btn.getAttribute("data-event"));
  });
});

$("fsmResetBtn").onclick = () => {
  currentFsmState = "IDLE";
  $("fsmStateBadge").textContent = "IDLE";
  $("fsmLog").style.color = "#42526a";
  $("fsmLog").textContent = "FSM di-reset kembali ke state awal q₀ = IDLE.";
};

// Inisialisasi aplikasi
populateSelectOptions();
renderGraph();
handleFindShortestPath();
