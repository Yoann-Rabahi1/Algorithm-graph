import json
import streamlit as st
import streamlit.components.v1 as components

from download_graph import create_french_cities_graph
from kruskal_functions import kruskal_steps

st.set_page_config(page_title="Kruskal Cytoscape", layout="wide")
st.title("🌳 Kruskal (MST) avec Cytoscape.js, animation côté navigateur")

st.markdown("""
Ici, le graphe est affiché et animé en **JavaScript (Cytoscape.js)**.
Python calcule les étapes une seule fois, puis le navigateur joue l’animation sans rerun Streamlit.
""")

# ---------------------------
# Session state
# ---------------------------
if "graph" not in st.session_state:
    st.session_state.graph = None
if "steps" not in st.session_state:
    st.session_state.steps = []

colA, colB, colC = st.columns(3)

with colA:
    if st.button("📥 Charger le graphe des métropoles", type="primary"):
        st.session_state.graph = create_french_cities_graph()
        st.session_state.steps = []
        st.success("Graphe chargé")

with colB:
    if st.button("⚙️ Calculer steps Kruskal", disabled=st.session_state.graph is None):
        st.session_state.steps = list(kruskal_steps(st.session_state.graph, weight="length"))
        st.success("Steps générés: " + str(len(st.session_state.steps)))

with colC:
    st.write("")
    st.write("Graphe:", "OK" if st.session_state.graph is not None else "Non chargé")
    st.write("Steps:", len(st.session_state.steps))

if st.session_state.graph is None:
    st.warning("Charge d'abord le graphe")
    st.stop()

if not st.session_state.steps:
    st.info("Clique sur 'Calculer steps Kruskal'")
    st.stop()

G = st.session_state.graph
steps = st.session_state.steps

# ---------------------------
# Préparer nodes/edges
# ---------------------------
nodes = []
for n, data in G.nodes(data=True):
    if "x" not in data or "y" not in data:
        st.error("Ton graphe n'a pas les attributs x/y sur les noeuds.")
        st.stop()

    nodes.append({
        "data": {"id": str(n), "label": str(n)},
        "position": {"x": float(data["x"]) * 10.0, "y": float(-data["y"]) * 10.0}
    })

edges = []
seen = set()
i = 0
for u, v, data in G.edges(data=True):
    su, sv = str(u), str(v)
    key = (su, sv)
    if key in seen:
        continue
    seen.add(key)

    w = float(data.get("length", 1.0))
    edges.append({
        "data": {
            "id": "e" + str(i),
            "source": su,
            "target": sv,
            "weight": w,
            "key": su + "|" + sv
        }
    })
    i += 1

def norm_edge(u, v):
    return str(u) + "|" + str(v)

# ---------------------------
# Transformer steps -> format JS
# ---------------------------
js_steps = []
for s in steps:
    cur = s.get("current_edge")
    mst = s.get("mst_edges", [])
    visited = s.get("visited_edges", [])

    cur_id = None
    if cur is not None:
        u, v, w = cur
        cur_id = norm_edge(u, v)

    mst_ids = [norm_edge(u, v) for (u, v, w) in mst]
    vis_ids = [norm_edge(u, v) for (u, v, w) in visited]

    js_steps.append({
        "current": cur_id,
        "mst": mst_ids,
        "visited": vis_ids
    })

payload = {"nodes": nodes, "edges": edges, "steps": js_steps}

# ---------------------------
# HTML + JS (sans ${} du tout)
# ---------------------------
html = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <script src="https://unpkg.com/cytoscape@3.27.0/dist/cytoscape.min.js"></script>
  <style>
    body { margin:0; font-family: sans-serif; }
    #toolbar { display:flex; gap:8px; padding:8px; align-items:center; }
    #cy { width: 100%; height: 650px; border-radius: 10px; background: #d9eef7; }
    button { padding:6px 10px; cursor:pointer; }
    input[type="range"] { width: 200px; }
    .info { margin-left:auto; }
  </style>
</head>
<body>
  <div id="toolbar">
    <button id="play">Play</button>
    <button id="pause">Pause</button>
    <button id="step">Step</button>
    <button id="reset">Reset</button>
    <label>Speed <input id="speed" type="range" min="10" max="1000" value="200"></label>
    <div class="info" id="info">step 0</div>
  </div>
  <div id="cy"></div>

  <script>
    const data = __PAYLOAD__;
    let idx = 0;
    let timer = null;

    // map edge "u|v" -> cytoscape edge id
    const edgeMap = new Map();
    data.edges.forEach(function(e) {
      edgeMap.set(e.data.key, e.data.id);
    });

    const cy = cytoscape({
      container: document.getElementById('cy'),
      elements: {
        nodes: data.nodes,
        edges: data.edges
      },
      layout: { name: 'preset' },
      style: [
        {
          selector: 'node',
          style: {
            'label': 'data(label)',
            'font-size': 10,
            'text-valign': 'center',
            'text-halign': 'center',
            'background-color': '#111',
            'color': '#fff',
            'width': 18,
            'height': 18
          }
        },
        {
          selector: 'edge',
          style: {
            'width': 2,
            'line-color': '#999',
            'curve-style': 'bezier'
          }
        },
        {
          selector: '.visited',
          style: { 'line-color': 'orange', 'width': 4 }
        },
        {
          selector: '.mst',
          style: { 'line-color': 'green', 'width': 6 }
        },
        {
          selector: '.current',
          style: { 'line-color': 'yellow', 'width': 7 }
        }
      ]
    });

    function clearClasses() {
      cy.edges().removeClass('visited mst current');
    }

    function applyStep(i) {
      if (i < 0) i = 0;
      if (i >= data.steps.length) i = data.steps.length - 1;
      idx = i;

      clearClasses();
      const s = data.steps[idx];

      // visited
      s.visited.forEach(function(k) {
        const eid = edgeMap.get(k);
        if (eid) cy.getElementById(eid).addClass('visited');
      });

      // mst
      s.mst.forEach(function(k) {
        const eid = edgeMap.get(k);
        if (eid) cy.getElementById(eid).addClass('mst');
      });

      // current
      if (s.current) {
        const eid = edgeMap.get(s.current);
        if (eid) cy.getElementById(eid).addClass('current');
      }

      document.getElementById('info').textContent =
        "step " + (idx + 1) + "/" + data.steps.length;
    }

    function play() {
      if (timer) return;
      const speed = Number(document.getElementById('speed').value);
      timer = setInterval(function() {
        if (idx >= data.steps.length - 1) {
          pause();
          return;
        }
        applyStep(idx + 1);
      }, speed);
    }

    function pause() {
      if (timer) {
        clearInterval(timer);
        timer = null;
      }
    }

    document.getElementById('play').onclick = play;
    document.getElementById('pause').onclick = pause;
    document.getElementById('step').onclick = function() {
      pause();
      applyStep(idx + 1);
    };
    document.getElementById('reset').onclick = function() {
      pause();
      applyStep(0);
    };

    applyStep(0);
  </script>
</body>
</html>
"""

html = html.replace("__PAYLOAD__", json.dumps(payload))
components.html(html, height=740, scrolling=False)
