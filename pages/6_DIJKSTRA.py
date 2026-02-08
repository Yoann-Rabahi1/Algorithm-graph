import os
import numpy as np
import streamlit as st
import time
import math
import pandas as pd

from vizualisation.plotly_graph import *
from graphs.download_graph import *  
from algorithms.dijkstra_functions import *
from error_handlings import (
    validate_graph,
    validate_dijkstra,
    validate_start_node,
    validate_final_distance,
    validate_coordinates,
    validate_mst_graph
)

PAGE_ID = "DIJKSTRA"

if "current_page" not in st.session_state:
    st.session_state.current_page = PAGE_ID

# 🔁 Si on change de page → reset complet
if st.session_state.current_page != PAGE_ID:
    st.session_state.clear()
    st.session_state.current_page = PAGE_ID
    st.rerun()

st.set_page_config(page_title="Parcours de Graphes - Dijkstra", layout="wide")
st.title("🗺️ Visualisation de l'algorithme de Dijkstra")

st.markdown("""
Bienvenue dans cet espace dédié à l'exploration interactive de **l'algorithme de Dijkstra**.

Cette page te permet de :

- **Charger un graphe** (réel via OpenStreetMap ou un graphe de test)
- **Choisir un point de départ (A) et d'arrivée (B)**
- **Observer pas à pas** comment Dijkstra explore le réseau
- **Visualiser les distances, les nœuds visités et le chemin final**
- **Voir la matrice des distances** à chaque itération
- Comprendre intuitivement **comment l'algorithme trouve le plus court chemin**

L'objectif est de rendre l'algorithme **visuel, pédagogique et manipulable**.
""")

# ============================================================
# SESSION STATE
# ============================================================
for key, default in {
    'paused': False,
    'running': False,
    'step_index': 0,
    'steps': [],
    'start_node': None,
    'end_node': None,
    'graph': None,
    'finished': False,
    'graph_loaded': False,
    'node_list': [],
    'is_test_graph': False,
    'computed': False,
    'dist_final': None,
    'parent_final': None,
    'visited_final': None,
    'iterations': None,
    'elapsed': None,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ============================================================
# SIDEBAR
# ============================================================
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # -----------------------------
    # Chargement du graphe
    # -----------------------------
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
                st.session_state.step_index = 0
                st.session_state.running = False
                st.session_state.paused = False
                st.session_state.finished = False
                st.session_state.computed = False

                st.session_state.node_list = list(G.nodes())

                st.rerun()
            
            except Exception as e:
                st.error(f"❌ Erreur lors du chargement : {str(e)}")

    # -----------------------------
    # Sélection des nœuds A et B
    # -----------------------------
    if st.session_state.graph_loaded:
        st.divider()
        st.subheader("🎯 Points de départ et d'arrivée")

        nodes = st.session_state.node_list

        if len(nodes) > 0:
            start_idx = st.selectbox(
                "Nœud de départ (A)",
                range(len(nodes)),
                index=0,
                format_func=lambda i: str(nodes[i])
            )

            end_idx = st.selectbox(
                "Nœud d'arrivée (B)",
                range(len(nodes)),
                index=min(5, len(nodes)-1),
                format_func=lambda i: str(nodes[i])
            )

            start_node_id = nodes[start_idx]
            end_node_id = nodes[end_idx]

            st.session_state.start_node = start_node_id
            st.session_state.end_node = end_node_id

            if start_node_id == end_node_id:
                st.error("⚠️ Le nœud de départ et d'arrivée doivent être différents.")
                st.stop()

        else:
            st.warning("⚠️ Aucun nœud disponible dans le graphe.")
            start_node_id = None
            end_node_id = None

        # -----------------------------
        # Vitesse
        # -----------------------------
        st.divider()
        st.subheader("⚡ Vitesse de l'animation")
        speed = st.slider("Délai entre étapes (sec)", 0.01, 1.0, 0.2, 0.01)

        # -----------------------------
        # Options d'affichage
        # -----------------------------
        st.divider()
        st.subheader("👁️ Options d'affichage")
        show_all_nodes = st.checkbox("Afficher tous les nœuds en couleur", value=False)
        show_distances = st.checkbox("Afficher les distances", value=True)

    else:
        st.warning("⚠️ Chargez d'abord un graphe")
        start_node_id = None
        end_node_id = None
        speed = 0.2
        show_all_nodes = False
        show_distances = True

# ============================================================
# ZONE PRINCIPALE — CONTRÔLES
# ============================================================
st.header("🎮 Contrôles")

col1, col2, col3, col4, col5, col6 = st.columns(6)

# ▶️ Animation
with col1:
    if st.button("▶️ Animation", disabled=st.session_state.running):
        if st.session_state.graph is None:
            st.error("⚠️ Charge d'abord un graphe.")
        else:
            validate_graph(st.session_state.graph, start_node_id, end_node_id)
            validate_dijkstra(st.session_state.graph)
            validate_start_node(st.session_state.graph, start_node_id)
            validate_coordinates(st.session_state.graph)

            st.session_state.running = True
            st.session_state.paused = False
            st.session_state.finished = False
            st.session_state.computed = False
            st.session_state.step_index = 0

            st.session_state.start_node = start_node_id
            st.session_state.end_node = end_node_id
            
            with st.spinner("Génération des étapes..."):
                st.session_state.steps = list(
                    dijkstra_steps(
                        st.session_state.graph,
                        start_node_id,
                        end_node_id
                    )
                )
            st.rerun()

# ⚡ Calcul direct
with col2:
    if st.button("⚡ Calcul Direct", disabled=st.session_state.graph is None):

        validate_graph(st.session_state.graph, start_node_id, end_node_id)
        validate_dijkstra(st.session_state.graph)
        validate_start_node(st.session_state.graph, start_node_id)
        validate_coordinates(st.session_state.graph)

        st.session_state.start_time = time.time()

        dist, parent, visited, iterations = dijkstra_complete(
            st.session_state.graph,
            start_node_id,
            end_node_id
        )
        
        st.session_state.dist_final = dist
        st.session_state.parent_final = parent
        st.session_state.visited_final = visited
        st.session_state.iterations = iterations
        st.session_state.computed = True
        st.session_state.elapsed = time.time() - st.session_state.start_time

        validate_final_distance(dist, end_node_id)

        st.rerun()

# ⏸️ Pause
with col3:
    if st.button("⏸️ Pause", disabled=not st.session_state.running or st.session_state.paused):
        st.session_state.paused = True
        st.rerun()

# ▶️ Reprendre
with col4:
    if st.button("▶️ Reprendre", disabled=not st.session_state.paused):
        st.session_state.paused = False
        st.rerun()

# ⏩ Étape
with col5:
    if st.button("⏩ Étape", disabled=not st.session_state.paused):
        st.session_state.step_index += 1
        st.rerun()

# ⏹️ Reset
with col6:
    if st.button("⏹️ Reset"):
        for key in ['running','paused','finished','computed','steps','step_index',
                    'dist_final','parent_final','visited_final','iterations']:
            st.session_state[key] = False if isinstance(st.session_state[key], bool) else None
        st.rerun()

# ============================================================
# VISUALISATION — VERSION FINALE
# ============================================================
st.divider()
st.header("📊 Visualisation")

graph_placeholder = st.empty()
G = st.session_state.graph

if G is None:
    st.warning("⚠️ Aucun graphe chargé.")
    st.stop()

validate_coordinates(G)

# ------------------------------------------------------------
# 1) MODE : CALCUL DIRECT → AFFICHAGE FINAL UNIQUEMENT
# ------------------------------------------------------------
if st.session_state.computed:

    final_step = {
        "dist": st.session_state.dist_final,
        "parent": st.session_state.parent_final,
        "visited": st.session_state.visited_final,
        "current": None
    }

    fig = plot_final_path_dijkstra(
        G,
        final_step,
        st.session_state.start_node,
        st.session_state.end_node,
        is_test_graph=st.session_state.is_test_graph
    )

    graph_placeholder.plotly_chart(fig, use_container_width=True)

    st.subheader("📋 Résultat")

    distance = st.session_state.dist_final.get(st.session_state.end_node, math.inf)
    validate_final_distance(st.session_state.dist_final, st.session_state.end_node)

    if distance == math.inf:
        st.warning(f"❌ Aucun chemin de {st.session_state.start_node} vers {st.session_state.end_node}.")
    else:
        path = reconstruct_path(
            st.session_state.parent_final,
            st.session_state.start_node,
            st.session_state.end_node
        )

        st.success(f"Distance minimale : **{distance:.2f}**")

        if path:
            st.info(f"🛤️ Chemin optimal ({len(path)} nœuds)")
            if st.session_state.is_test_graph:
                st.write(" → ".join([str(p) for p in path]))

    st.stop()   # ⛔ STOP : rien d’autre ne doit s’afficher


# ------------------------------------------------------------
# 2) MODE : ANIMATION EN COURS
# ------------------------------------------------------------
if st.session_state.running and not st.session_state.paused:

    if not st.session_state.steps:
        st.warning("⚠️ Aucune étape générée.")
        st.stop()

    if st.session_state.step_index >= len(st.session_state.steps):
        st.session_state.running = False
        st.session_state.finished = True
        st.rerun()

    step = st.session_state.steps[st.session_state.step_index]

    fig = (
        plot_dijkstra_step(G, step, st.session_state.start_node, st.session_state.end_node, is_test_graph=st.session_state.is_test_graph)
        if show_all_nodes else
        plot_dijkstra_step_dynamic(G, step, st.session_state.start_node, st.session_state.end_node, is_test_graph=st.session_state.is_test_graph)
    )

    graph_placeholder.plotly_chart(fig, use_container_width=True)

    time.sleep(speed)
    st.session_state.step_index += 1
    st.rerun()


# ------------------------------------------------------------
# 3) MODE : PAUSE OU FIN D’ANIMATION
# ------------------------------------------------------------
elif st.session_state.paused or st.session_state.finished:

    idx = min(st.session_state.step_index, len(st.session_state.steps) - 1)
    step = st.session_state.steps[idx]

    if st.session_state.finished:
        fig = plot_final_path_dijkstra(
            G, step, st.session_state.start_node, st.session_state.end_node,
            is_test_graph=st.session_state.is_test_graph
        )
    else:
        fig = (
            plot_dijkstra_step(G, step, st.session_state.start_node, st.session_state.end_node, is_test_graph=st.session_state.is_test_graph)
            if show_all_nodes else
            plot_dijkstra_step_dynamic(G, step, st.session_state.start_node, st.session_state.end_node, is_test_graph=st.session_state.is_test_graph)
        )

    graph_placeholder.plotly_chart(fig, use_container_width=True)


# ------------------------------------------------------------
# 4) MODE : GRAPHE INITIAL (A et B affichés)
# ------------------------------------------------------------
elif st.session_state.start_node is not None and st.session_state.end_node is not None:

    fig = plot_graph_with_points(
        G,
        st.session_state.start_node,
        st.session_state.end_node,
        is_test_graph=st.session_state.is_test_graph
    )
    graph_placeholder.plotly_chart(fig, use_container_width=True)


# ------------------------------------------------------------
# 5) MODE : GRAPHE BRUT
# ------------------------------------------------------------
else:
    fig = plot_graph_plotly(G, is_test_graph=st.session_state.is_test_graph)
    graph_placeholder.plotly_chart(fig, use_container_width=True)

# ============================================================
# MATRICE DES DISTANCES (calcul direct)
# ============================================================
if st.session_state.computed and st.session_state.iterations and st.session_state.is_test_graph:

    st.header("📊 Évolution des distances")

    visited_nodes = sorted(list(st.session_state.visited_final))

    table = []
    for snapshot in st.session_state.iterations:
        row = []
        for n in visited_nodes:
            d = snapshot.get(n, math.inf)
            row.append("∞" if d == math.inf else f"{d:.1f}")
        table.append(row)

    df = pd.DataFrame(table, columns=visited_nodes)
    df.index = [f"Itération {i}" for i in range(len(table))]

    st.dataframe(df, use_container_width=True)

# ============================================================
# FOOTER
# ============================================================
st.divider()
with st.expander("ℹ️ À propos de Dijkstra"):
    st.markdown("""
    L'algorithme de Dijkstra trouve le plus court chemin dans un graphe pondéré **à poids positifs**.
    Il utilise une **file de priorité** et met à jour les distances par relaxation.
    """)
