import streamlit as st
import time

from graphs.download_graph import create_french_cities_graph
from vizualisation.plotly_graph import plot_fw_pair, plot_fw_path
from algorithms.floyd_warshall_functions import floyd_warshall_steps, reconstruct_path_from_step

st.set_page_config(page_title="Floyd Warshall", layout="wide")
st.title("🔁 Floyd-Warshall, plus courts chemins entre tous les couples")

st.markdown("""
Floyd-Warshall calcule les distances minimales entre **tous** les couples (i, j).
On anime les étapes (k, i, j), et tu peux choisir un couple source/destination pour visualiser le chemin.
""")

# ---------------------------
# Session state
# ---------------------------
for key, default in {
    "graph": None,
    "node_list": [],
    "steps": [],
    "step_index": 0,
    "running": False,
    "paused": False,
    "finished": False,
    "start_time": None,
    "src": None,
    "dst": None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ---------------------------
# Sidebar
# ---------------------------
with st.sidebar:
    st.header("⚙️ Configuration")

    if st.button("📥 Charger le graphe des métropoles", type="primary"):
        st.session_state.graph = create_french_cities_graph()
        st.session_state.node_list = list(st.session_state.graph.nodes())
        st.session_state.steps = []
        st.session_state.step_index = 0
        st.session_state.running = False
        st.session_state.paused = False
        st.session_state.finished = False
        st.success("Graphe chargé")
        st.rerun()

    st.subheader("⚡ Vitesse")
    speed = st.slider("Délai entre étapes (sec)", 0.01, 1.0, 0.15, 0.01)

    if st.session_state.graph is not None and st.session_state.node_list:
        st.subheader("🎯 Couple (source, destination)")
        src_idx = st.selectbox(
            "Source",
            range(len(st.session_state.node_list)),
            index=0,
            format_func=lambda i: str(st.session_state.node_list[i])
        )
        dst_idx = st.selectbox(
            "Destination",
            range(len(st.session_state.node_list)),
            index=min(1, len(st.session_state.node_list) - 1),
            format_func=lambda i: str(st.session_state.node_list[i])
        )
        st.session_state.src = st.session_state.node_list[src_idx]
        st.session_state.dst = st.session_state.node_list[dst_idx]

# ---------------------------
# Controls
# ---------------------------
st.header("🎮 Contrôles")
c1, c2, c3, c4, c5 = st.columns(5)

with c1:
    if st.button("▶️ Démarrer", disabled=st.session_state.running):
        if st.session_state.graph is None:
            st.error("Charge d'abord le graphe")
        else:
            st.session_state.running = True
            st.session_state.paused = False
            st.session_state.finished = False
            st.session_state.step_index = 0
            st.session_state.start_time = time.time()
            st.session_state.steps = list(floyd_warshall_steps(st.session_state.graph, weight="length"))
            st.rerun()

with c2:
    if st.button("⏸️ Pause", disabled=not st.session_state.running or st.session_state.paused):
        st.session_state.paused = True
        st.rerun()

with c3:
    if st.button("▶️ Reprendre", disabled=not st.session_state.paused):
        st.session_state.paused = False
        st.rerun()

with c4:
    if st.button("⏩ Étape", disabled=not st.session_state.paused):
        st.session_state.step_index += 1
        st.rerun()

with c5:
    if st.button("⏹️ Stop"):
        st.session_state.running = False
        st.session_state.paused = False
        st.session_state.finished = False
        st.session_state.step_index = 0
        st.session_state.steps = []
        st.rerun()

# ---------------------------
# Status
# ---------------------------
if st.session_state.steps:
    colA, colB, colC = st.columns(3)

    with colA:
        if st.session_state.finished:
            st.success("Terminé")
        elif st.session_state.paused:
            st.warning("En pause")
        elif st.session_state.running:
            st.info("En cours")

    with colB:
        progress = min(1.0, st.session_state.step_index / max(1, len(st.session_state.steps)))
        st.metric("Progression", f"{st.session_state.step_index}/{len(st.session_state.steps)}")
        st.progress(progress)

    with colC:
        if st.session_state.start_time:
            st.metric("Temps écoulé", f"{(time.time()-st.session_state.start_time):.2f} sec")

# ---------------------------
# Visualisation
# ---------------------------
st.header("📊 Visualisation")
graph_placeholder = st.empty()

if st.session_state.graph is None:
    st.warning("Aucun graphe chargé")
    st.stop()

G = st.session_state.graph
nodes = list(G.nodes())

def show_step(step):
    src = st.session_state.src
    dst = st.session_state.dst

    # Affichage chemin si possible
    path = []
    if src is not None and dst is not None:
        path = reconstruct_path_from_step(step, nodes, src, dst)

    if path:
        fig = plot_fw_path(G, path)
    else:
        fig = plot_fw_pair(G, src, dst)

    graph_placeholder.plotly_chart(fig, use_container_width=True)

    # Infos texte
    if step.get("phase") == "relax":
        k = step["k"]
        i = step["i"]
        j = step["j"]
        updated = step["updated"]
        st.write(
            "k=", k, ", i=", i, ", j=", j,
            ", updated=", updated,
            ", dist(i,j)=", step["dist_ij_new"]
        )

# Animation
if st.session_state.running and not st.session_state.paused:
    if st.session_state.step_index < len(st.session_state.steps):
        step = st.session_state.steps[st.session_state.step_index]
        show_step(step)
        time.sleep(speed)
        st.session_state.step_index += 1
        st.rerun()
    else:
        st.session_state.running = False
        st.session_state.finished = True
        st.rerun()
else:
    if st.session_state.steps:
        step = st.session_state.steps[min(st.session_state.step_index, len(st.session_state.steps) - 1)]
        show_step(step)
    else:
        st.info("Clique sur ▶️ Démarrer")
