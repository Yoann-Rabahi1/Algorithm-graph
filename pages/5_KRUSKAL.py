import streamlit as st
import numpy as np


from download_graph import *
from kruskal_functions import * 
from plotly_graph import *




if "graph" not in st.session_state:
    st.session_state.graph = None
if "node_list" not in st.session_state:
    st.session_state.node_list = []
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
if "start_node" not in st.session_state:
    st.session_state.start_node = None
if "start_time" not in st.session_state:
    st.session_state.start_time = None


st.title("🌳 KRUSKAL (MST)")

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

            st.success("✅ Graphe chargé")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Erreur: {e}")

st.divider()
st.header("📊 Visualisation")

if "graph" not in st.session_state or st.session_state.graph is None:
    st.warning("⚠️ Aucun graphe chargé")
else:
    G = st.session_state.graph

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Graphe")
        st.plotly_chart(plot_graph_plotly(G), use_container_width=True)

    with col2:
        st.subheader("MST Kruskal")
        if st.button("🌳 Calculer MST"):
            mst_edges, total_cost = kruskal_osmnx(G, weight="length")
            st.success(f"Coût total = {total_cost:.2f}, arêtes MST = {len(mst_edges)}")
            st.plotly_chart(plot_kruskal_mst(G, mst_edges), use_container_width=True)
