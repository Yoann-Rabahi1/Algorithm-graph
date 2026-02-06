import streamlit as st
import time
from dfs_functions import plot_dfs_step, dfs_steps
from download_graph import create_french_cities_graph

from plotly_graph import *

st.set_page_config(page_title="DFS - Parcours en Profondeur", layout="wide")

st.title("🌲 Visualisation de l'algorithme DFS (Depth-First Search)")

st.markdown("""
DFS explore un graphe **en profondeur**, en suivant un chemin jusqu’au bout avant de revenir en arrière.

Cette page te permet de :
- charger le graphe des métropoles,
- choisir un nœud de départ,
- observer l’exploration étape par étape,
- suivre la progression et le temps d’exécution.
""")

# -----------------------------------------------------------
# SESSION STATE
# -----------------------------------------------------------
defaults = {
    "graph": None,
    "node_list": [],
    "steps": [],
    "step_index": 0,
    "running": False,
    "paused": False,
    "finished": False,
    "start_node": None,
    "start_time": None
}

for key, val in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = val

# -----------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")

    if st.button("📥 Charger le graphe des métropoles", type="primary"):
        st.session_state.graph = create_french_cities_graph()
        st.session_state.node_list = list(st.session_state.graph.nodes())
        st.success("Graphe chargé !")
        st.rerun()

    if st.session_state.graph is not None:
        st.subheader("🎯 Nœud de départ")

        start_idx = st.selectbox(
            "Choisis un nœud",
            range(len(st.session_state.node_list)),
            format_func=lambda i: str(st.session_state.node_list[i])
        )

        st.session_state.start_node = st.session_state.node_list[start_idx]

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
            st.error("Charge d'abord un graphe.")
        else:
            st.session_state.running = True
            st.session_state.paused = False
            st.session_state.finished = False
            st.session_state.step_index = 0
            st.session_state.start_time = time.time()

            st.session_state.steps = list(
                dfs_steps(
                    st.session_state.graph,
                    st.session_state.start_node
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
# STATUS + PROGRESSION + TEMPS
# -----------------------------------------------------------
if st.session_state.steps:
    colA, colB, colC = st.columns(3)

    with colA:
        if st.session_state.finished:
            st.success("Exploration terminée")
        elif st.session_state.paused:
            st.warning("En pause")
        elif st.session_state.running:
            st.info("Exploration en cours")

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

    # --- MODE ANIMATION ---
    if st.session_state.running and not st.session_state.paused:

        if st.session_state.step_index < len(st.session_state.steps):
            step = st.session_state.steps[st.session_state.step_index]

            fig = plot_dfs_step(
                st.session_state.graph,
                step,
                st.session_state.start_node,
                is_test_graph=True
            )

            graph_placeholder.plotly_chart(fig, use_container_width=True)

            time.sleep(speed)
            st.session_state.step_index += 1
            st.rerun()

        else:
            st.session_state.running = False
            st.session_state.finished = True
            st.rerun()

    # --- MODE PAUSE ---
    elif st.session_state.paused and not st.session_state.finished:

        step = st.session_state.steps[st.session_state.step_index]

        fig = plot_dfs_step(
            st.session_state.graph,
            step,
            st.session_state.start_node,
            is_test_graph=True
        )

        graph_placeholder.plotly_chart(fig, use_container_width=True)

    # --- MODE FIN ---
    elif st.session_state.finished:

        final_step = st.session_state.steps[-1]

        fig = plot_dfs_step(
            st.session_state.graph,
            final_step,
            st.session_state.start_node,
            is_test_graph=True
        )

        graph_placeholder.plotly_chart(fig, use_container_width=True)

        # Liste complète des visités dans l'ordre
        st.success(f"📌 Ordre de visite ({len(final_step['visit_order'])}) : {final_step['visit_order']}")

        # Temps total
        if st.session_state.start_time:
            elapsed = time.time() - st.session_state.start_time
            st.info(f"⏱️ Temps total d'exécution : {elapsed:.2f} sec")

    # --- MODE INITIAL : afficher le graphe statique ---
    else:
        fig = plot_graph_plotly(st.session_state.graph, is_test_graph=True)
        graph_placeholder.plotly_chart(fig, use_container_width=True)
        st.info("Sélectionne un nœud puis clique sur ▶️ Démarrer.")

else:
    st.warning("Aucun graphe chargé.")

# -----------------------------------------------------------
# FOOTER
# -----------------------------------------------------------
st.divider()
st.markdown("""
### ℹ️ À propos du DFS

DFS explore un graphe en profondeur :
- il suit un chemin jusqu’au bout,
- puis revient en arrière,
- puis explore un autre chemin.

Il est utile pour :
- explorer la structure d’un graphe,
- détecter des cycles,
- générer un arbre DFS,
- analyser la connectivité.

Cette page te permet de visualiser son fonctionnement étape par étape.
""")
