import os
import numpy as np
import streamlit as st
import time
import math
import pandas as pd

from vizualisation.plotly_graph import *
from graphs.download_graph import *  
from algorithms.dijkstra_functions import *

st.set_page_config(page_title="Parcours de Graphes - Dijkstra", layout="wide")
st.title("🗺️ Visualisation de l'algorithme de Dijkstra")

st.markdown("""
Bienvenue dans cet espace dédié à l'exploration interactive de **l'algorithme de Dijkstra**.

Cette page te permet de :

- **Charger un graphe** (réel via OpenStreetMap ou un graphe de test)
- **Choisir un point de départ et d'arrivée**
- **Observer pas à pas** comment Dijkstra explore le réseau
- **Visualiser les distances, les nœuds visités et le chemin final**
- **Voir la matrice des distances** à chaque itération
- Comprendre intuitivement **comment l'algorithme trouve le plus court chemin**

L'objectif est de rendre l'algorithme **visuel, pédagogique et manipulable**.
""")


# Initialisation des variables de session
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
                st.session_state.computed = False
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
col_btn1, col_btn2, col_btn3, col_btn4, col_btn5, col_btn6 = st.columns(6)

with col_btn1:
    if st.button("▶️ Animation", disabled=st.session_state.running):
        if st.session_state.graph is not None:
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
                        st.session_state.start_node,
                        st.session_state.end_node
                    )

                )
            st.rerun()
        else:
            st.error("⚠️ Veuillez d'abord charger un graphe!")

with col_btn2:
    if st.button("⚡ Calcul Direct", disabled=st.session_state.graph is None):
        st.session_state.start_time = time.time()
        st.session_state.start_node = start_node_id
        st.session_state.end_node = end_node_id
        
        dist, parent, visited, iterations = dijkstra_complete(
            st.session_state.graph,
            st.session_state.start_node,
            st.session_state.end_node
        )
        
        st.session_state.dist_final = dist
        st.session_state.parent_final = parent
        st.session_state.visited_final = visited
        st.session_state.iterations = iterations
        st.session_state.computed = True
        st.session_state.elapsed = time.time() - st.session_state.start_time
        st.rerun()

with col_btn3:
    if st.button("⏸️ Pause", disabled=not st.session_state.running or st.session_state.paused):
        st.session_state.paused = True
        st.rerun()

with col_btn4:
    if st.button("▶️ Reprendre", disabled=not st.session_state.paused):
        st.session_state.paused = False
        st.rerun()

with col_btn5:
    if st.button("⏩ Étape", disabled=not st.session_state.paused or st.session_state.step_index >= len(st.session_state.steps)):
        st.session_state.step_index += 1
        st.rerun()

with col_btn6:
    if st.button("⏹️ Reset"):
        st.session_state.running = False
        st.session_state.paused = False
        st.session_state.finished = False
        st.session_state.computed = False
        st.session_state.step_index = 0
        st.session_state.steps = []
        st.session_state.dist_final = None
        st.session_state.parent_final = None
        st.session_state.visited_final = None
        st.session_state.iterations = None
        st.rerun()

st.divider()

# ============================================================
# Informations sur l'état (Animation)
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
                dist_str = f"{dist:.0f}" if dist != float('inf') else "∞"
                st.metric("Distance → arrivée", dist_str)

# ============================================================
# Status (Calcul direct)
# ============================================================
if st.session_state.computed:
    colA, colB, colC = st.columns(3)

    with colA:
        st.success("✅ Calcul terminé")

    with colB:
        num_iterations = len(st.session_state.iterations) if st.session_state.iterations else 0
        st.metric("Itérations", f"{num_iterations}")

    with colC:
        st.metric("Temps écoulé", f"{st.session_state.elapsed:.4f} sec")

# ============================================================
# MATRICE DES DISTANCES
# ============================================================
if st.session_state.computed and st.session_state.iterations and st.session_state.is_test_graph:
    
    st.header("📊 Évolution des distances")
    
    st.markdown("""
    **Légende :** 
    - **Itération 0** : État initial (source = 0, autres = ∞)
    - **Itérations suivantes** : Après traitement de chaque nœud
    """)
    
    # Obtenir tous les nœuds visités
    visited_nodes = sorted(list(st.session_state.visited_final))
    
    # Construire le tableau
    table = []
    for iteration_idx, snapshot in enumerate(st.session_state.iterations):
        row = []
        for n in visited_nodes:
            d = snapshot.get(n, math.inf)
            if d == math.inf:
                row.append("∞")
            elif d == 0.0:
                row.append("0")
            else:
                row.append(f"{d:.1f}")
        table.append(row)
    
    # Créer le DataFrame
    df = pd.DataFrame(table, columns=visited_nodes)
    df.index = [f"Itération {i}" for i in range(len(table))]
    
    st.dataframe(df, use_container_width=True)
    
    st.info(f"""
    📌 **Nombre total d'itérations** : {len(st.session_state.iterations)}  
    📌 **Nœuds visités** : {len(visited_nodes)}
    """)

# ============================================================
# VISUALISATION FINALE (Calcul direct)
# ============================================================
if st.session_state.computed:
    
    st.header("🗺️ Visualisation finale")
    
    # Créer un step factice pour la visualisation
    final_step = {
        "dist": st.session_state.dist_final,
        "parent": st.session_state.parent_final,
        "visited": st.session_state.visited_final,
        "current": None
    }
    
    fig = plot_final_path_dijkstra(
        st.session_state.graph,
        final_step,
        st.session_state.start_node,
        st.session_state.end_node,
        is_test_graph=st.session_state.is_test_graph
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Résultat numérique
    st.subheader("📋 Résultat")
    
    distance = st.session_state.dist_final.get(st.session_state.end_node, math.inf)
    
    if distance == math.inf:
        st.warning(f"❌ **Aucun chemin** de {st.session_state.start_node} vers {st.session_state.end_node}.")
    else:
        # Reconstruction du chemin
        path = reconstruct_path(
            st.session_state.parent_final,
            st.session_state.start_node,
            st.session_state.end_node
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success(f"✅ **Distance minimale** : **{distance:.2f}**")
        
        with col2:
            if path:
                path_str = " → ".join([str(p) for p in path])
                st.info(f"🛤️ **Chemin optimal** ({len(path)} nœuds)")
                if st.session_state.is_test_graph:
                    st.write(path_str)
        
        # Détails du chemin (pour graphe de test)
        if path and len(path) > 1 and st.session_state.is_test_graph:
            st.markdown("### Détails du chemin")
            path_details = []
            cumulative_dist = 0
            
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                edge_data = st.session_state.graph.get_edge_data(u, v)
                if isinstance(edge_data, dict):
                    edge_weight = min(d.get('length', 1) for d in edge_data.values())
                else:
                    edge_weight = edge_data.get('length', 1)
                
                cumulative_dist += edge_weight
                path_details.append({
                    "Étape": i + 1,
                    "De": u,
                    "Vers": v,
                    "Distance": f"{edge_weight:.1f}",
                    "Distance cumulée": f"{cumulative_dist:.1f}"
                })
            
            df_path = pd.DataFrame(path_details)
            st.dataframe(df_path, use_container_width=True, hide_index=True)

# ============================================================
# DISTANCES FINALES (Calcul direct)
# ============================================================
if st.session_state.computed and st.session_state.is_test_graph:
    st.header("📏 Distances finales depuis la source")
    
    dist_data = []
    visited_nodes = sorted(list(st.session_state.visited_final))
    
    for node in visited_nodes:
        d = st.session_state.dist_final.get(node, math.inf)
        if d == math.inf:
            dist_str = "∞ (non atteignable)"
        elif d == 0:
            dist_str = "0 (source)"
        else:
            dist_str = f"{d:.2f}"
        
        dist_data.append({
            "Nœud": node,
            f"Distance depuis {st.session_state.start_node}": dist_str
        })
    
    df_distances = pd.DataFrame(dist_data)
    st.dataframe(df_distances, use_container_width=True, hide_index=True)

# ============================================================
# Visualisation du graphe (Animation)
# ============================================================
if not st.session_state.computed:
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
                    st.success(f"🎉 **Chemin trouvé !** Distance totale : **{dist:.2f}**")

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
    
    L'algorithme de Dijkstra trouve le plus court chemin entre deux nœuds dans un graphe pondéré avec des poids **positifs**.
    
    **Principe :**
    1. **Initialisation** : distance(source) = 0, toutes les autres = ∞
    2. **Exploration** : sélectionner le nœud non visité avec la plus petite distance
    3. **Relaxation** : mettre à jour les distances des voisins
    4. **Répéter** jusqu'à atteindre la cible ou explorer tous les nœuds
    
    **Complexité** : O((|V| + |E|) log |V|) avec file de priorité
    
    **Graphe de test :**
    - 10 villes françaises
    - Distances en km
    - Nœuds agrandis + poids visibles
    
    **Graphe OSM :**
    - Réseau routier réel
    - Affichage simplifié pour la lisibilité
    
    **Avantage** : Optimal pour graphes avec poids positifs
    **Limitation** : Ne fonctionne pas avec des poids négatifs (utiliser Bellman-Ford)
    """)