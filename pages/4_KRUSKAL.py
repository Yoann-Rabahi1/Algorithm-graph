import streamlit as st
import time
import networkx as nx

from graphs.download_graph import *
from algorithms.kruskal_functions import *
from error_handlings import (
    validate_graph,
    validate_mst_graph,
    validate_coordinates
)
from vizualisation.plotly_graph import *

# ============================================================
# RESET AUTOMATIQUE DE PAGE
# ============================================================
PAGE_ID = "KRUSKAL"

if "current_page" not in st.session_state:
    st.session_state.current_page = PAGE_ID

if st.session_state.current_page != PAGE_ID:
    st.session_state.clear()
    st.session_state.current_page = PAGE_ID
    st.rerun()

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(page_title="Kruskal - MST", layout="wide")
st.title("🔗 Algorithme de Kruskal")

st.markdown("""
Cette page permet de visualiser l’algorithme de **Kruskal**.

- **Graphe de test** → animation complète  
- **Graphe OSMnx** → ACPM Direct uniquement  
""")

# ============================================================
# SESSION STATE
# ============================================================
DEFAULTS = {
    "graph": None,
    "steps": [],
    "step_index": 0,
    "running": False,
    "paused": False,
    "finished": False,
    "graph_loaded": False,
    "is_test_graph": False,
    "mst_computed": False,
    "mst_graph": None,
    "start_time": None
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.header("⚙️ Configuration")

    st.subheader("📍 Chargement du graphe")

    load_method = st.radio(
        "Source du graphe",
        ["Graphe de test (Villes françaises)", "Télécharger depuis OSM"],
        index=0
    )

    if load_method == "Télécharger depuis OSM":
        place_name = st.text_input("Nom du lieu", "Osny, France")
        network_type = st.selectbox("Type de réseau", ["drive", "walk", "bike", "all"])

    if st.button("🔄 Charger le graphe", type="primary"):
        with st.spinner("Chargement du graphe..."):
            try:
                if load_method == "Télécharger depuis OSM":
                    G = get_graph(place_name, network_type=network_type)
                    st.session_state.is_test_graph = False
                else:
                    G = create_french_cities_graph()
                    st.session_state.is_test_graph = True

                validate_graph(G)
                validate_mst_graph(G)
                validate_coordinates(G)

                st.session_state.graph = G
                st.session_state.graph_loaded = True
                st.session_state.steps = []
                st.session_state.step_index = 0
                st.session_state.running = False
                st.session_state.paused = False
                st.session_state.finished = False
                st.session_state.mst_computed = False

                st.success("Graphe chargé !")
                st.rerun()

            except Exception as e:
                st.error(f"❌ Erreur : {str(e)}")

    if st.session_state.graph_loaded:
        st.divider()
        st.success("Graphe chargé")
        st.info(f"📊 Nœuds : {len(st.session_state.graph.nodes())}")
        st.info(f"🔗 Arêtes : {len(st.session_state.graph.edges())}")

        if st.session_state.is_test_graph:
            st.divider()
            st.subheader("⚡ Vitesse de l'animation")
            speed = st.slider("Délai entre étapes (sec)", 0.01, 1.0, 0.2, 0.01)
        else:
            speed = 0.2

# ============================================================
# CONTROLES
# ============================================================
st.header("🎮 Contrôles")

col1, col2, col3, col4, col5, col6 = st.columns(6)

# ============================================================
# MODE GRAPHE DE TEST → ANIMATION COMPLÈTE
# ============================================================
if st.session_state.is_test_graph:

    # ▶️ Démarrer
    with col1:
        if st.button("▶️ Démarrer", disabled=st.session_state.running):
            G = st.session_state.graph

            st.session_state.running = True
            st.session_state.paused = False
            st.session_state.finished = False
            st.session_state.step_index = 0
            st.session_state.mst_computed = False
            st.session_state.start_time = time.time()

            st.session_state.steps = list(kruskal_steps(G, weight="length"))
            st.rerun()

    # ⏸️ Pause
    with col2:
        if st.button("⏸️ Pause", disabled=not st.session_state.running or st.session_state.paused):
            st.session_state.paused = True
            st.rerun()

    # ▶️ Reprendre
    with col3:
        if st.button("▶️ Reprendre", disabled=not st.session_state.paused):
            st.session_state.paused = False
            st.rerun()

    # ⏩ Étape
    with col4:
        if st.button("⏩ Étape", disabled=not st.session_state.paused):
            st.session_state.step_index += 1
            st.rerun()

    # ⏹️ Reset
    with col5:
        if st.button("⏹️ Reset"):
            for key in DEFAULTS:
                st.session_state[key] = DEFAULTS[key]
            st.rerun()

    # ❌ ACPM Direct masqué
    with col6:
        st.info("ACPM Direct indisponible pour le graphe de test.")

# ============================================================
# MODE OSMNX → ACPM DIRECT UNIQUEMENT
# ============================================================
else:

    # ACPM Direct
    with col1:
        if st.button("⚡ ACPM Direct"):
            G = st.session_state.graph

            st.session_state.start_time = time.time()

            G2 = nx.to_undirected(G)
            T = nx.minimum_spanning_tree(G2, weight="length")

            st.session_state.mst_graph = T
            st.session_state.mst_computed = True

            st.success("🌳 ACPM calculé !")
            st.rerun()

    # Reset
    with col2:
        if st.button("⏹️ Reset"):
            for key in DEFAULTS:
                st.session_state[key] = DEFAULTS[key]
            st.rerun()

# ============================================================
# BARRE D'ÉTAT / PROGRESSION / TEMPS (TEST UNIQUEMENT)
# ============================================================
if st.session_state.is_test_graph and (
    st.session_state.running or st.session_state.paused or st.session_state.finished
):

    colA, colB, colC = st.columns(3)

    with colA:
        if st.session_state.finished:
            st.success("✔️ Terminé")
        elif st.session_state.paused:
            st.warning("⏸️ En pause")
        else:
            st.info("▶️ En cours")

    with colB:
        total_steps = len(st.session_state.steps)
        current_step = min(st.session_state.step_index, total_steps)
        st.metric("Progression", f"{current_step}/{total_steps}")
        if total_steps > 0:
            st.progress(current_step / total_steps)

    with colC:
        if st.session_state.start_time:
            elapsed = time.time() - st.session_state.start_time
            st.metric("Temps écoulé", f"{elapsed:.2f} sec")

# ============================================================
# VISUALISATION
# ============================================================
st.header("📊 Visualisation")
graph_placeholder = st.empty()

G = st.session_state.graph

if G is None:
    st.warning("⚠️ Aucun graphe chargé.")
    st.stop()

# ============================================================
# MODE OSMNX → ACPM DIRECT UNIQUEMENT
# ============================================================
if not st.session_state.is_test_graph:

    if st.session_state.mst_graph is not None:

        T = st.session_state.mst_graph

        fig = plot_kruskal_mst(G, T.edges(data="length"), False)
        graph_placeholder.plotly_chart(fig, use_container_width=True)

        st.subheader("📋 Résultats de l’ACPM")

        total_cost = sum(data.get("length", 1) for (_, _, data) in T.edges(data=True))
        st.success(f"🌳 Coût total : {total_cost:.2f}")

        st.info(f"🔗 Arêtes : {len(T.edges())}")
        st.info(f"📊 Nœuds : {len(T.nodes())}")

        elapsed = time.time() - st.session_state.start_time
        st.info(f"⏱️ Temps d'exécution : {elapsed:.2f} sec")

        st.stop()

    else:
        fig = plot_graph_plotly(G, is_test_graph=False)
        graph_placeholder.plotly_chart(fig, use_container_width=True)
        st.info("Clique sur ⚡ ACPM Direct pour calculer l'arbre couvrant minimal.")
        st.stop()

# ============================================================
# MODE TEST → ANIMATION COMPLÈTE
# ============================================================
# --- ANIMATION ---
if st.session_state.running and not st.session_state.paused:

    if st.session_state.step_index < len(st.session_state.steps):
        step = st.session_state.steps[st.session_state.step_index]

        fig = plot_kruskal_step(G, step, True)
        graph_placeholder.plotly_chart(fig, use_container_width=True)

        time.sleep(speed)
        st.session_state.step_index += 1
        st.rerun()

    else:
        st.session_state.running = False
        st.session_state.finished = True
        st.rerun()

# --- PAUSE / FIN ---
elif st.session_state.steps:

    step = st.session_state.steps[min(st.session_state.step_index, len(st.session_state.steps) - 1)]

    if st.session_state.finished:
        fig = plot_kruskal_mst(G, step["mst_edges"], True)
    else:
        fig = plot_kruskal_step(G, step, True)

    graph_placeholder.plotly_chart(fig, use_container_width=True)

# --- MODE INITIAL ---
else:
    fig = plot_graph_plotly(G, is_test_graph=True)
    graph_placeholder.plotly_chart(fig, use_container_width=True)
    st.info("Clique sur ▶️ Démarrer pour lancer Kruskal.")

# ============================================================
# FOOTER
# ============================================================
st.divider()
st.markdown("""
### ℹ️ À propos de Kruskal

L’algorithme de Kruskal trie les arêtes par poids et les ajoute
si elles ne créent pas de cycle, jusqu’à obtenir un MST.
""")
