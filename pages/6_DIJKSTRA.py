import os
import numpy as np
import streamlit as st
import time
from plotly_graph import *
from graphs.download_graph import *  
from dijkstra_functions import *

st.set_page_config(page_title="Parcours de Graphes - Dijkstra", layout="wide")
st.title("🗺️ Visualisation de l'algorithme de Dijkstra")

st.markdown("""
Bienvenue dans cet espace dédié à l'exploration interactive de **l'algorithme de Dijkstra**.

Cette page te permet de :

- **Charger un graphe** (réel via OpenStreetMap ou un graphe de test)
- **Choisir un point de départ et d'arrivée**
- **Observer pas à pas** comment Dijkstra explore le réseau
- **Visualiser les distances, les nœuds visités et le chemin final**
- Comprendre intuitivement **comment l’algorithme trouve le plus court chemin**

L’objectif est de rendre l’algorithme **visuel, pédagogique et manipulable**, afin que tu puisses analyser son comportement sur des graphes simples comme sur des réseaux routiers réels.
""")


# Initialisation des variables de session
if 'paused' not in st.session_state:
    st.session_state.paused = False
if 'running' not in st.session_state:
    st.session_state.running = False
if 'step_index' not in st.session_state:
    st.session_state.step_index = 0
if 'steps' not in st.session_state:
    st.session_state.steps = []
if 'start_node' not in st.session_state:
    st.session_state.start_node = None
if 'end_node' not in st.session_state:
    st.session_state.end_node = None
if 'graph' not in st.session_state:
    st.session_state.graph = None
if 'finished' not in st.session_state:
    st.session_state.finished = False
if 'graph_loaded' not in st.session_state:
    st.session_state.graph_loaded = False
if 'node_list' not in st.session_state:
    st.session_state.node_list = []
if 'is_test_graph' not in st.session_state:
    st.session_state.is_test_graph = False

# ============================================================
# SIDEBAR - Paramètres
# ============================================================
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Section 1: Chargement du graphe
    st.subheader("📍 Chargement du graphe")
    
    load_method = st.radio(
        "Source du graphe",
        ["Graphe de test (Villes françaises)", "Télécharger depuis OSM"],
        index=0
    )
    
    if load_method == "Télécharger depuis OSM":
        place_name = st.text_input(
            "Nom du lieu",
            value="Osny, France",
            help="Nom du lieu (ville, quartier, etc.)"
        )
        
        network_type = st.selectbox(
            "Type de réseau",
            ["drive", "walk", "bike", "all"],
            help="Type de réseau routier"
        )
    
    if st.button("🔄 Charger le graphe", type="primary"):
        with st.spinner("Chargement du graphe..."):
            try:
                if load_method == "Télécharger depuis OSM":
                    st.session_state.graph = get_graph(
                        place_name,
                        network_type=network_type
                    )
                    st.session_state.is_test_graph = False
                    st.success("✅ Graphe téléchargé depuis OSM !")
                else:
                    st.session_state.graph = create_french_cities_graph()
                    st.session_state.is_test_graph = True
                    st.success("✅ Graphe de test (Villes françaises) créé !")
                
                st.session_state.graph_loaded = True
                st.session_state.node_list = list(st.session_state.graph.nodes())
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Erreur lors du chargement : {str(e)}")
    
    if st.session_state.graph_loaded:
        st.divider()
        st.success("✅ Graphe chargé")
        st.info(f"📊 **Nœuds**: {len(st.session_state.graph.nodes())}")
        st.info(f"🔗 **Arêtes**: {len(st.session_state.graph.edges())}")
        
        st.divider()
        
        # Section 2: Sélection des nœuds
        st.subheader("🎯 Points de départ et d'arrivée")
        
        if len(st.session_state.node_list) > 0:

            # Tous les nœuds disponibles
            max_display = len(st.session_state.node_list)

            start_idx = st.selectbox(
                "Nœud de départ",
                range(max_display),
                index=0,
                format_func=lambda x: f"{str(st.session_state.node_list[x])}"
            )

            end_idx = st.selectbox(
                "Nœud d'arrivée",
                range(max_display),
                index=min(5, max_display-1),
                format_func=lambda x: f"{str(st.session_state.node_list[x])}"
            )

            start_node_id = st.session_state.node_list[start_idx]
            end_node_id = st.session_state.node_list[end_idx]

            # Empêcher start == end
            if start_node_id == end_node_id:
                st.error("⚠️ Le nœud de départ et d'arrivée doivent être différents.")
                st.stop()

        else:
            start_node_id = None
            end_node_id = None

    else:
        st.warning("⚠️ Chargez d'abord un graphe")
        start_node_id = None
        end_node_id = None
    
    st.divider()
    
    # Section 3: Paramètres de visualisation
    st.subheader("⚡ Vitesse de l'animation")
    
    speed = st.slider(
        "Délai entre chaque étape (secondes)",
        min_value=0.01,
        max_value=2.0,
        value=0.2,
        step=0.01
    )
    
    st.divider()
    
    st.subheader("👁️ Options d'affichage")
    
    show_all_nodes = st.checkbox(
        "Afficher tous les nœuds en couleur",
        value=False
    )
    
    show_distances = st.checkbox("Afficher les distances", value=True)

# ============================================================
# ZONE PRINCIPALE
# ============================================================
st.header("🎮 Contrôles")

# Boutons de contrôle
col_btn1, col_btn2, col_btn3, col_btn4, col_btn5 = st.columns(5)

with col_btn1:
    if st.button("▶️ Démarrer", disabled=st.session_state.running):
        if st.session_state.graph is not None:
            st.session_state.running = True
            st.session_state.paused = False
            st.session_state.finished = False
            st.session_state.step_index = 0
            st.session_state.start_node = start_node_id
            st.session_state.end_node = end_node_id
            
            with st.spinner("Génération des étapes..."):
                st.session_state.steps = list(
                    dijkstra_steps(
                        st.session_state.graph,
                        st.session_state.start_node,
                        st.session_state.end_node
                    )

                )
            st.rerun()
        else:
            st.error("⚠️ Veuillez d'abord charger un graphe!")

with col_btn2:
    if st.button("⏸️ Pause", disabled=not st.session_state.running or st.session_state.paused):
        st.session_state.paused = True
        st.rerun()

with col_btn3:
    if st.button("▶️ Reprendre", disabled=not st.session_state.paused):
        st.session_state.paused = False
        st.rerun()

with col_btn4:
    if st.button("⏩ Étape", disabled=not st.session_state.paused or st.session_state.step_index >= len(st.session_state.steps)):
        st.session_state.step_index += 1
        st.rerun()

with col_btn5:
    if st.button("⏹️ Stop"):
        st.session_state.running = False
        st.session_state.paused = False
        st.session_state.finished = False
        st.session_state.step_index = 0
        st.session_state.steps = []
        st.rerun()

st.divider()

# ============================================================
# Informations sur l'état
# ============================================================
if st.session_state.running or st.session_state.finished:
    col_info1, col_info2, col_info3 = st.columns(3)
    
    with col_info1:
        if st.session_state.finished:
            st.success("✅ Algorithme terminé!")
        elif st.session_state.paused:
            st.warning("⏸️ En pause")
        else:
            st.info("▶️ En cours d'exécution...")
    
    with col_info2:
        if len(st.session_state.steps) > 0:
            progress = st.session_state.step_index / len(st.session_state.steps)
            st.metric("Progression", f"{st.session_state.step_index}/{len(st.session_state.steps)}")
            st.progress(progress)
    
    with col_info3:
        if len(st.session_state.steps) > 0 and st.session_state.step_index < len(st.session_state.steps):
            current_step = st.session_state.steps[st.session_state.step_index]
            if current_step["current"] is not None:
                st.metric("Nœud actuel", str(current_step["current"]))
            
            if show_distances and st.session_state.end_node in current_step["dist"]:
                dist = current_step["dist"][st.session_state.end_node]
                st.metric("Distance → arrivée", f"{dist:.0f} km" if dist != float('inf') else "∞")

# ============================================================
# Visualisation du graphe
# ============================================================
st.divider()
st.header("📊 Visualisation")

graph_placeholder = st.empty()

if st.session_state.graph is not None:
    
    # MODE 1 : Animation
    if st.session_state.running and not st.session_state.paused:
        if st.session_state.step_index < len(st.session_state.steps):
            current_step = st.session_state.steps[st.session_state.step_index]
            
            if show_all_nodes:
                fig = plot_dijkstra_step(
                    st.session_state.graph,
                    current_step,
                    st.session_state.start_node,
                    st.session_state.end_node,
                    is_test_graph=st.session_state.is_test_graph
                )
            else:
                fig = plot_dijkstra_step_dynamic(
                    st.session_state.graph,
                    current_step,
                    st.session_state.start_node,
                    st.session_state.end_node,
                    is_test_graph=st.session_state.is_test_graph
                )
            
            graph_placeholder.plotly_chart(fig, use_container_width=True)
            
            time.sleep(speed)
            st.session_state.step_index += 1
            st.rerun()
        else:
            st.session_state.running = False
            st.session_state.finished = True
            st.rerun()
    
    # MODE 2 : Pause ou terminé
    elif st.session_state.paused or st.session_state.finished:
        if st.session_state.step_index > 0:
            current_step = st.session_state.steps[min(st.session_state.step_index, len(st.session_state.steps)-1)]
            
            if st.session_state.finished:
                fig = plot_final_path_dijkstra(
                    st.session_state.graph,
                    current_step,
                    st.session_state.start_node,
                    st.session_state.end_node,
                    is_test_graph=st.session_state.is_test_graph
                )
            else:
                if show_all_nodes:
                    fig = plot_dijkstra_step(
                        st.session_state.graph,
                        current_step,
                        st.session_state.start_node,
                        st.session_state.end_node,
                        is_test_graph=st.session_state.is_test_graph
                    )
                else:
                    fig = plot_dijkstra_step_dynamic(
                        st.session_state.graph,
                        current_step,
                        st.session_state.start_node,
                        st.session_state.end_node,
                        is_test_graph=st.session_state.is_test_graph
                    )
            
            graph_placeholder.plotly_chart(fig, use_container_width=True)
    
    # MODE 3 : Graphe initial
    elif st.session_state.start_node is not None and st.session_state.end_node is not None:
        fig = plot_graph_with_points(
            st.session_state.graph,
            start_node_id,
            end_node_id,
            is_test_graph=st.session_state.is_test_graph
        )
        graph_placeholder.plotly_chart(fig, use_container_width=True)

        # -----------------------------------------------------------
    # Affichage des résultats quand l'algorithme est terminé
    # -----------------------------------------------------------
    if st.session_state.finished:

        current_step = st.session_state.steps[-1]

        # Vérifier si la distance vers la cible existe
        if st.session_state.end_node in current_step["dist"]:
            dist = current_step["dist"][st.session_state.end_node]

            if dist != float('inf'):
                st.success(f"🎉 **Chemin trouvé !** Distance totale : **{dist:.2f} mètres**")

                # Reconstruction du chemin
                path = []
                node = st.session_state.end_node
                while node is not None:
                    path.append(node)
                    node = current_step["parent"].get(node)
                path.reverse()

                if len(path) > 1:
                    st.info(f"📍 Nombre de nœuds dans le chemin : {len(path)}")

            else:
                st.error("❌ Aucun chemin trouvé entre les deux points")

    
    # MODE 4 : Graphe brut
    else:
        fig = plot_graph_plotly(
            st.session_state.graph,
            is_test_graph=st.session_state.is_test_graph
        )
        graph_placeholder.plotly_chart(fig, use_container_width=True)

else:
    st.warning("⚠️ **Aucun graphe chargé**")
    st.info("""
    👈 Utilisez la barre latérale pour charger un graphe :
    - **Graphe de test** : Réseau de villes françaises
    - **Télécharger depuis OSM** : Graphe réel
    """)

# ============================================================
# Footer
# ============================================================
st.divider()

with st.expander("ℹ️ À propos de l'algorithme de Dijkstra"):
    st.markdown("""
    ### Algorithme de Dijkstra
    
    L'algorithme de Dijkstra trouve le plus court chemin entre deux nœuds dans un graphe pondéré.
    
    **Graphe de test :**
    - 10 villes françaises
    - Distances en km
    - Nœuds agrandis + poids visibles
    
    **Graphe OSM :**
    - Réseau routier réel
    - Affichage simplifié pour la lisibilité
    """)

