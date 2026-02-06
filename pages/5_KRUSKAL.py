import streamlit as st
import time
import numpy as np

from download_graph import *
from kruskal_functions import kruskal_steps_osmnx
from plotly_graph import plot_graph_plotly, plot_kruskal_step, plot_kruskal_mst

st.title("🌳 Visualisation de l'algorithme de Kruskal (MST)")

st.markdown("""
Kruskal construit un **arbre couvrant minimal**:
- il trie les arêtes par poids croissant,
- il ajoute une arête si elle ne crée pas de cycle,
- sinon il la refuse.

Cette page te permet de :
- charger un graphe,
- lancer Kruskal étape par étape,
- pause, reprise, mode étape,
- visualiser le MST en construction.
""")

# -----------------------------------------------------------
# SESSION STATE
# -----------------------------------------------------------
if "graph" not in st.session_state:
    st.session_state.graph = None
if "steps" not in st.session_state:
    st.session_state.steps = []
if "step_index" not in st.session_state:
    st.session_state.step_index = 0
if "running" not in st.session_state:
    st.session_state.running = False
if "paused" not in st.session_state:
    st.session_state.paused = False
if "finished" not in st.session_state:
    st.session_state.finished = False
if "start_time" not in st.session_state:
    st.session_state.start_time = None

# speed default
if "speed" not in st.session_state:
    st.session_state.speed = 0.2

# -----------------------------------------------------------
# SIDEBAR - chargement graphe + vitesse
# -----------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")

    st.subheader("📍 Chargement du graphe")
    load_method = st.radio(
        "Source du graphe",
        ["Graphes sauvegardés", "Télécharger depuis OSM", "Graphe de test"],
        index=0
    )

    selected_graph = None

    if load_method == "Graphes sauvegardés":
        saved_graphs = list_saved_graphs()
        if saved_graphs:
            selected_graph = st.selectbox("Sélectionner un graphe", saved_graphs)
        else:
            st.warning("📂 Aucun graphe sauvegardé trouvé")

    elif load_method == "Télécharger depuis OSM":
        place_name = st.text_input("Nom du lieu", value="Osny, France")
        network_type = st.selectbox("Type de réseau", ["drive", "walk", "bike", "all"])
        default_filename = place_name.replace(", ", "_").replace(" ", "_").lower()
        save_filename = st.text_input("Nom du fichier à sauvegarder", value=default_filename)

    if st.button("🔄 Charger le graphe", type="primary"):
        try:
            if load_method == "Graphes sauvegardés":
                st.session_state.graph = load_graph(selected_graph)

            elif load_method == "Télécharger depuis OSM":
                st.session_state.graph = download_and_save(
                    place_name, filename=save_filename, network_type=network_type
                )

            else:
                # si tu veux le graphe métropoles, remplace par create_french_cities_graph()
                import networkx as nx
                G = nx.MultiDiGraph()
                np.random.seed(42)
                for i in range(30):
                    G.add_node(i, x=float(np.random.rand()*100), y=float(np.random.rand()*100))
                for i in range(29):
                    G.add_edge(i, i+1, 0, length=float(np.random.rand()*10))
                for _ in range(20):
                    u, v = np.random.randint(0, 30, 2)
                    if u != v:
                        G.add_edge(int(u), int(v), 0, length=float(np.random.rand()*10))
                st.session_state.graph = G

            # reset animation
            st.session_state.steps = []
            st.session_state.step_index = 0
            st.session_state.running = False
            st.session_state.paused = False
            st.session_state.finished = False
            st.session_state.start_time = None

            st.success("✅ Graphe chargé")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Erreur: {e}")

    st.subheader("⚡ Vitesse")
    st.session_state.speed = st.slider("Délai entre étapes (sec)", 0.01, 1.0, float(st.session_state.speed), 0.01)

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
                kruskal_steps_osmnx(st.session_state.graph, weight="length")
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
            st.success("MST terminé")
        elif st.session_state.paused:
            st.warning("En pause")
        elif st.session_state.running:
            st.info("En cours")

    with colB:
        progress = min(1.0, st.session_state.step_index / len(st.session_state.steps))
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

if st.session_state.graph is None:
    st.warning("⚠️ Aucun graphe chargé.")
else:
    # MODE ANIMATION
    if st.session_state.running and not st.session_state.paused:
        if st.session_state.step_index < len(st.session_state.steps):
            step = st.session_state.steps[st.session_state.step_index]
            fig = plot_kruskal_step(st.session_state.graph, step)
            graph_placeholder.plotly_chart(fig, use_container_width=True)

            time.sleep(st.session_state.speed)
            st.session_state.step_index += 1
            st.rerun()
        else:
            st.session_state.running = False
            st.session_state.finished = True
            st.rerun()

    # MODE PAUSE / FIN
    elif st.session_state.paused or st.session_state.finished:
        step = st.session_state.steps[min(st.session_state.step_index, len(st.session_state.steps) - 1)]
        fig = plot_kruskal_step(st.session_state.graph, step)
        graph_placeholder.plotly_chart(fig, use_container_width=True)

        # infos MST courant
        st.info(f"Arêtes MST: {len(step['mst_edges'])}, coût: {step['total_cost']:.2f}")

        # si fini, affiche MST final propre
        if st.session_state.finished:
            st.subheader("✅ MST final")
            fig2 = plot_kruskal_mst(st.session_state.graph, step["mst_edges"])
            st.plotly_chart(fig2, use_container_width=True)

    # MODE INITIAL
    else:
        st.info("Charge un graphe puis clique sur ▶️ Démarrer.")
        fig = plot_graph_plotly(st.session_state.graph)
        graph_placeholder.plotly_chart(fig, use_container_width=True)
