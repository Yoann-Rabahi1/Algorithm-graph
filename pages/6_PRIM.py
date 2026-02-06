import streamlit as st
import time

from download_graph import create_french_cities_graph
from prim_functions import prim_steps, plot_prim_step, plot_prim_mst

st.set_page_config(page_title="Prim - MST", layout="wide")

st.title("🌲 Algorithme de Prim — Arbre couvrant minimal (MST)")

st.markdown("""
Cette page te permet de visualiser **Prim étape par étape**:

- on part d’un nœud
- on ajoute toujours l’arête la moins coûteuse qui relie l’arbre à un nouveau nœud
- on construit le MST progressivement
""")

# -----------------------------------------------------------
# SESSION STATE
# -----------------------------------------------------------
for key, default in {
    "graph": None,
    "steps": [],
    "step_index": 0,
    "running": False,
    "paused": False,
    "finished": False,
    "start_time": None,
    "start_node": None
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# -----------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")

    if st.button("📥 Charger le graphe des métropoles", type="primary"):
        st.session_state.graph = create_french_cities_graph()
        st.success("Graphe chargé !")
        st.rerun()

    if st.session_state.graph is not None:
        st.subheader("🎯 Nœud de départ")
        nodes = list(st.session_state.graph.nodes())
        st.session_state.start_node = st.selectbox("Choisis un nœud", nodes)

    st.subheader("⚡ Vitesse")
    speed = st.slider("Délai entre étapes (sec)", 0.01, 1.0, 0.2, 0.01)

# -----------------------------------------------------------
# CONTROLS
# -----------------------------------------------------------
st.header("🎮 Contrôles")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("▶️ Démarrer", disabled=st.session_state.running):
        if st.session_state.graph is None:
            st.error("Charge d'abord le graphe des métropoles.")
        else:
            st.session_state.running = True
            st.session_state.paused = False
            st.session_state.finished = False
            st.session_state.step_index = 0
            st.session_state.start_time = time.time()

            st.session_state.steps = list(
                prim_steps(
                    st.session_state.graph,
                    start_node=st.session_state.start_node,
                    weight="length"
                )
            )
            st.rerun()

with col2:
    if st.button("⏸️ Pause", disabled=not st.session_state.running or st.session_state.paused):
        st.session_state.paused = True
        st.rerun()

with col3:
    if st.button("▶️ Reprendre", disabled=not st.session_state.paused):
        st.session_state.paused = False
        st.rerun()

with col4:
    if st.button("⏩ Étape", disabled=not st.session_state.paused):
        st.session_state.step_index += 1
        st.rerun()

with col5:
    if st.button("⏹️ Stop"):
        st.session_state.running = False
        st.session_state.paused = False
        st.session_state.finished = False
        st.session_state.step_index = 0
        st.session_state.steps = []
        st.rerun()

# -----------------------------------------------------------
# STATUS
# -----------------------------------------------------------
if st.session_state.steps:
    colA, colB, colC = st.columns(3)

    with colA:
        if st.session_state.finished:
            st.success("MST terminé")
        elif st.session_state.paused:
            st.warning("En pause")
        elif st.session_state.running:
            st.info("En cours...")

    with colB:
        progress = st.session_state.step_index / len(st.session_state.steps)
        st.metric("Progression", f"{st.session_state.step_index}/{len(st.session_state.steps)}")
        st.progress(progress)

    with colC:
        if st.session_state.start_time:
            elapsed = time.time() - st.session_state.start_time
            st.metric("Temps écoulé", f"{elapsed:.2f} sec")

# -----------------------------------------------------------
# VISUALISATION
# -----------------------------------------------------------
st.header("📊 Visualisation")
graph_placeholder = st.empty()

if st.session_state.graph is not None:

    if st.session_state.running and not st.session_state.paused:

        if st.session_state.step_index < len(st.session_state.steps):
            step = st.session_state.steps[st.session_state.step_index]

            fig = plot_prim_step(st.session_state.graph, step)
            graph_placeholder.plotly_chart(fig, use_container_width=True)

            time.sleep(speed)
            st.session_state.step_index += 1
            st.rerun()

        else:
            st.session_state.running = False
            st.session_state.finished = True
            st.rerun()

    else:
        if st.session_state.steps:
            step = st.session_state.steps[min(
                st.session_state.step_index,
                len(st.session_state.steps) - 1
            )]

            if st.session_state.finished:
                fig = plot_prim_mst(st.session_state.graph, step["mst_edges"])
            else:
                fig = plot_prim_step(st.session_state.graph, step)

            graph_placeholder.plotly_chart(fig, use_container_width=True)

            st.info(f"Arêtes MST: {len(step['mst_edges'])}, coût: {step['total_cost']:.2f}")

            if st.session_state.finished and st.session_state.start_time:
                elapsed = time.time() - st.session_state.start_time
                st.info(f"⏱️ Temps total d'exécution : {elapsed:.2f} sec")

        else:
            st.info("Clique sur ▶️ Démarrer pour lancer Prim.")
else:
    st.warning("Aucun graphe chargé.")

st.divider()
st.markdown("""
### ℹ️ À propos de Prim

Prim construit un MST en partant d’un nœud, puis en ajoutant à chaque étape
l’arête la plus légère qui connecte un nouveau nœud à l’arbre déjà construit.
""")
