import streamlit as st
import time
import networkx as nx
import osmnx as ox

from graphs.download_graph import *
from algorithms.kruskal_functions import *
from error_handlings import (
    validate_graph,
    validate_mst_graph,
    validate_coordinates
)
from vizualisation.plotly_graph import *

PAGE_ID = "KRUSKAL"

if "current_page" not in st.session_state:
    st.session_state.current_page = PAGE_ID

# 🔁 Si on change de page → reset complet
if st.session_state.current_page != PAGE_ID:
    st.session_state.clear()
    st.session_state.current_page = PAGE_ID
    st.rerun()

st.set_page_config(page_title="Kruskal - MST", layout="wide")
st.title("🌳 Visualisation de l'algorithme de Kruskal")

st.markdown("""
Bienvenue dans l’espace dédié à **l’algorithme de Kruskal**.

Cette page te permet de :

- **Charger un graphe** (test ou OSM)
- **Observer pas à pas** la construction du MST
- **Visualiser les arêtes triées, visitées et sélectionnées**
- **Voir l’ACPM final**
- **Calculer directement l’ACPM** via NetworkX
""")

# ============================================================
# SESSION STATE
# ============================================================
for key, default in {
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
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ============================================================
# SIDEBAR — Chargement du graphe
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
                    st.success("🌍 Graphe OSM chargé !")
                else:
                    G = create_french_cities_graph()
                    st.session_state.is_test_graph = True
                    st.success("🧪 Graphe de test chargé !")

                validate_graph(G)
                validate_mst_graph(G)
                validate_coordinates(G)

                st.session_state.graph = G
                st.session_state.graph_loaded = True
                st.session_state.steps = []
                st.session_state.mst_computed = False
                st.session_state.step_index = 0
                st.session_state.running = False
                st.session_state.paused = False
                st.session_state.finished = False

                st.rerun()

            except Exception as e:
                st.error(f"❌ Erreur : {str(e)}")

    if st.session_state.graph_loaded:
        st.divider()
        st.success("✅ Graphe chargé")
        st.info(f"📊 Nœuds : {len(st.session_state.graph.nodes())}")
        st.info(f"🔗 Arêtes : {len(st.session_state.graph.edges())}")

        st.divider()
        st.subheader("⚡ Vitesse de l'animation")
        speed = st.slider("Délai entre étapes (sec)", 0.01, 1.0, 0.2, 0.01)

    else:
        st.warning("⚠️ Chargez d'abord un graphe")
        speed = 0.2

# ============================================================
# ZONE PRINCIPALE — Contrôles
# ============================================================
st.header("🎮 Contrôles")

col1, col2, col3, col4, col5, col6 = st.columns(6)

# ▶️ Démarrer
with col1:
    if st.button("▶️ Démarrer", disabled=st.session_state.running):
        if st.session_state.graph is None:
            st.error("Charge d'abord un graphe.")
        else:
            st.session_state.running = True
            st.session_state.paused = False
            st.session_state.finished = False
            st.session_state.step_index = 0
            st.session_state.mst_computed = False
            st.session_state.start_time = time.time()

            st.session_state.steps = list(
                kruskal_steps(st.session_state.graph, weight="length")
            )
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
        st.session_state.running = False
        st.session_state.paused = False
        st.session_state.finished = False
        st.session_state.steps = []
        st.session_state.step_index = 0
        st.session_state.mst_computed = False
        st.session_state.mst_graph = None
        st.rerun()

# ⚡ ACPM Direct
with col6:
    if not st.session_state.is_test_graph:
        if st.button("⚡ ACPM Direct"):
            G = st.session_state.graph
            if G is None:
                st.error("Charge d'abord un graphe.")
            else:
                st.session_state.start_time = time.time()

                # Conversion en graphe non orienté si nécessaire
                G2 = nx.to_undirected(G)

                T = nx.minimum_spanning_tree(G2, weight="length")

                st.session_state.mst_graph = T
                st.session_state.mst_computed = True
                st.session_state.running = False
                st.session_state.paused = False
                st.session_state.finished = False
                st.session_state.steps = []

                st.success("🌳 ACPM calculé !")
                st.rerun()
    else:
        st.info("⚡ Le calcul direct est désactivé pour le graphe de test.")

# ============================================================
# VISUALISATION
# ============================================================
st.header("📊 Visualisation")
graph_placeholder = st.empty()

G = st.session_state.graph

if G is not None:

    # ========================================================
    # ACPM DIRECT — AFFICHAGE + INFORMATIONS
    # ========================================================
    if st.session_state.mst_computed and st.session_state.mst_graph is not None:

        T = st.session_state.mst_graph

        fig = plot_kruskal_mst(
            G,
            T.edges(data="length"),
            st.session_state.is_test_graph
        )
        graph_placeholder.plotly_chart(fig, use_container_width=True)

        st.subheader("📋 Résultats de l’ACPM (Calcul Direct)")

        # Coût total
        total_cost = sum(
            data.get("length", 1)
            for (_, _, data) in T.edges(data=True)
        )
        st.success(f"🌳 **Coût total de l’ACPM : {total_cost:.2f}**")

        # Nombre d'arêtes
        st.info(f"🔗 **Arêtes sélectionnées : {len(T.edges())}**")

        # Nombre de nœuds
        st.info(f"📊 **Nœuds couverts : {len(T.nodes())}**")

        # Liste des arêtes (graphe de test uniquement)
        if st.session_state.is_test_graph:
            st.markdown("### 📄 Détails des arêtes du MST")
            mst_list = []
            for u, v, data in T.edges(data=True):
                w = data.get("length", 1)
                mst_list.append({
                    "De": u,
                    "Vers": v,
                    "Poids": f"{w:.2f}"
                })
            st.dataframe(mst_list, use_container_width=True)

        # Temps d'exécution
        if st.session_state.start_time:
            elapsed = time.time() - st.session_state.start_time
            st.info(f"⏱️ **Temps total d'exécution : {elapsed:.2f} sec**")

        st.stop()

    # ========================================================
    # ANIMATION KRUSKAL
    # ========================================================
    if st.session_state.running and not st.session_state.paused:

        if st.session_state.step_index < len(st.session_state.steps):
            step = st.session_state.steps[st.session_state.step_index]

            fig = plot_kruskal_step(G, step, st.session_state.is_test_graph)
            graph_placeholder.plotly_chart(fig, use_container_width=True)

            time.sleep(speed)
            st.session_state.step_index += 1
            st.rerun()

        else:
            st.session_state.running = False
            st.session_state.finished = True
            st.rerun()

    # ========================================================
    # PAUSE / FIN
    # ========================================================
    elif st.session_state.steps:

        step = st.session_state.steps[min(
            st.session_state.step_index,
            len(st.session_state.steps) - 1
        )]

        if st.session_state.finished:
            fig = plot_kruskal_mst(G, step["mst_edges"], st.session_state.is_test_graph)
        else:
            fig = plot_kruskal_step(G, step, st.session_state.is_test_graph)

        graph_placeholder.plotly_chart(fig, use_container_width=True)

        if st.session_state.finished:
            total_cost = sum(w for (_, _, w) in step["mst_edges"])
            st.success(f"🌳 Coût total de l’ACPM : **{total_cost:.2f}**")

    # ========================================================
    # MODE INITIAL
    # ========================================================
    else:
        fig = plot_graph_plotly(G, is_test_graph=st.session_state.is_test_graph)
        graph_placeholder.plotly_chart(fig, use_container_width=True)
        st.info("Clique sur ▶️ Démarrer pour lancer Kruskal.")

else:
    st.warning("⚠️ Aucun graphe chargé.")

# -----------------------------------------------------------
# FOOTER
# -----------------------------------------------------------
st.divider()
st.markdown("""
### ℹ️ À propos de Kruskal

L’algorithme de Kruskal construit un **arbre couvrant minimal (MST)** en :

1. triant les arêtes par poids,  
2. ajoutant les arêtes les plus légères,  
3. évitant les cycles grâce à **union-find**,  
4. jusqu’à connecter tout le graphe.
""")
