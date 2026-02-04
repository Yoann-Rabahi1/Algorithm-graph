import os
import numpy as np
import streamlit as st
import time
from plotly_graph import *
from download_graph import *

st.set_page_config(page_title="Parcours de Graphes - Dijkstra", layout="wide")

st.title("🗺️ Visualisation de l'algorithme de Dijkstra")

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

# ============================================================
# SIDEBAR - Paramètres
# ============================================================
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # Section 1: Chargement du graphe
    st.subheader("📍 Chargement du graphe")
    
    load_method = st.radio(
        "Source du graphe",
        ["Graphes sauvegardés", "Télécharger depuis OSM", "Graphe de test"],
        index=0
    )
    
    if load_method == "Graphes sauvegardés":
        # Lister les graphes disponibles dans le dossier data
        saved_graphs = list_saved_graphs()
        
        if len(saved_graphs) > 0:
            selected_graph = st.selectbox(
                "Sélectionner un graphe",
                saved_graphs,
                help="Graphes disponibles dans le dossier data/"
            )
            
            # Afficher les infos du graphe sélectionné
            if st.button("📊 Voir les infos", key="info_btn"):
                with st.spinner("Chargement des informations..."):
                    info = get_graph_info(selected_graph)
                    if "error" in info:
                        st.error(f"Erreur: {info['error']}")
                    else:
                        st.info(f"📊 Nœuds: {info['nodes']}")
                        st.info(f"🔗 Arêtes: {info['edges']}")
            
            # Option pour supprimer un graphe
            if st.checkbox("🗑️ Mode suppression"):
                if st.button("Supprimer ce graphe", type="secondary"):
                    if delete_graph(selected_graph):
                        st.success(f"Graphe {selected_graph} supprimé!")
                        st.rerun()
                    else:
                        st.error("Erreur lors de la suppression")
        else:
            st.warning("📂 Aucun graphe sauvegardé trouvé")
            st.info("Téléchargez un graphe depuis OSM ou créez un graphe de test")
            selected_graph = None
    
    elif load_method == "Télécharger depuis OSM":
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
        
        # Nom du fichier pour la sauvegarde
        default_filename = place_name.replace(", ", "_").replace(" ", "_").lower()
        save_filename = st.text_input(
            "Nom du fichier à sauvegarder",
            value=default_filename,
            help="Le graphe sera sauvegardé dans data/ avec ce nom"
        )
    
    if st.button("🔄 Charger le graphe", type="primary"):
        with st.spinner("Chargement du graphe..."):
            try:
                if load_method == "Graphes sauvegardés":
                    if selected_graph:
                        st.session_state.graph = load_graph(selected_graph)
                        st.success(f"✅ Graphe {selected_graph} chargé!")
                    else:
                        st.error("❌ Aucun graphe sélectionné")
                        st.stop()
                    
                elif load_method == "Télécharger depuis OSM":
                    # Télécharger depuis OSM
                    st.session_state.graph = download_and_save(
                        place_name, 
                        filename=save_filename,
                        network_type=network_type
                    )
                    st.success(f"✅ Graphe téléchargé et sauvegardé dans data/{save_filename}!")
                    
                else:  # Graphe de test
                    import networkx as nx
                    G = nx.MultiDiGraph()
                    # Créer un petit graphe de test avec des coordonnées
                    np.random.seed(42)
                    for i in range(30):
                        G.add_node(i, x=np.random.rand()*100, y=np.random.rand()*100)
                    
                    # Créer un réseau connecté
                    for i in range(29):
                        G.add_edge(i, i+1, 0, length=np.random.rand()*10)
                    
                    # Ajouter des connexions aléatoires
                    for _ in range(20):
                        u, v = np.random.randint(0, 30, 2)
                        if u != v:
                            G.add_edge(u, v, 0, length=np.random.rand()*10)
                    
                    st.session_state.graph = G
                    st.success("✅ Graphe de test créé!")
                
                st.session_state.graph_loaded = True
                st.session_state.node_list = list(st.session_state.graph.nodes())
                st.rerun()
                
            except FileNotFoundError:
                st.error("❌ Fichier introuvable.")
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
    
    if st.session_state.graph_loaded and len(st.session_state.node_list) > 0:
        # Sélection par index dans la liste
        max_display = min(100, len(st.session_state.node_list))
        
        start_idx = st.selectbox(
            "Nœud de départ",
            range(max_display),
            index=0,
            format_func=lambda x: f"Nœud {x}: {str(st.session_state.node_list[x])[:30]}"
        )
        
        end_idx = st.selectbox(
            "Nœud d'arrivée",
            range(max_display),
            index=min(10, max_display-1),
            format_func=lambda x: f"Nœud {x}: {str(st.session_state.node_list[x])[:30]}"
        )
        
        start_node_id = st.session_state.node_list[start_idx]
        end_node_id = st.session_state.node_list[end_idx]
        
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
        value=False,
        help="Si désactivé, seuls les nœuds visités sont en couleur (le graphe complet reste visible en arrière-plan)"
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
            
            # Générer toutes les étapes de l'algorithme
            with st.spinner("Génération des étapes..."):
                st.session_state.steps = list(
                    dijkstra_steps(
                        st.session_state.graph, 
                        st.session_state.start_node
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
                node_str = str(current_step["current"])
                st.metric("Nœud actuel", node_str[:20] + "..." if len(node_str) > 20 else node_str)
                if show_distances and st.session_state.end_node in current_step["dist"]:
                    dist = current_step["dist"][st.session_state.end_node]
                    if dist != float('inf'):
                        st.metric("Distance → arrivée", f"{dist:.2f} m")
                    else:
                        st.metric("Distance → arrivée", "∞")

# ============================================================
# Visualisation du graphe
# ============================================================
st.divider()
st.header("📊 Visualisation")

graph_placeholder = st.empty()

# Logique d'affichage
if st.session_state.graph is not None:
    
    # MODE 1: Animation en cours (running et non pausé)
    if st.session_state.running and not st.session_state.paused:
        if st.session_state.step_index < len(st.session_state.steps):
            current_step = st.session_state.steps[st.session_state.step_index]
            
            # Choisir le type d'affichage
            if show_all_nodes:
                fig = plot_dijkstra_step(
                    st.session_state.graph, 
                    current_step, 
                    st.session_state.start_node, 
                    st.session_state.end_node
                )
            else:
                fig = plot_dijkstra_step_dynamic(
                    st.session_state.graph, 
                    current_step, 
                    st.session_state.start_node, 
                    st.session_state.end_node
                )
            
            graph_placeholder.plotly_chart(fig, width='stretch')
            
            # Attendre et passer à l'étape suivante
            time.sleep(speed)
            st.session_state.step_index += 1
            st.rerun()
        else:
            # Algorithme terminé
            st.session_state.running = False
            st.session_state.finished = True
            st.rerun()
    
    # MODE 2: En pause ou terminé (affichage statique)
    elif st.session_state.paused or st.session_state.finished:
        if st.session_state.step_index > 0 and st.session_state.step_index <= len(st.session_state.steps):
            current_step = st.session_state.steps[min(st.session_state.step_index, len(st.session_state.steps)-1)]
            
            if st.session_state.finished:
                # Afficher le chemin final
                fig = plot_final_path(
                    st.session_state.graph, 
                    current_step, 
                    st.session_state.start_node, 
                    st.session_state.end_node
                )
                
                # Afficher les résultats
                if st.session_state.end_node in current_step["dist"]:
                    dist = current_step["dist"][st.session_state.end_node]
                    if dist != float('inf'):
                        st.success(f"🎉 **Chemin trouvé!** Distance totale: **{dist:.2f} mètres**")
                        
                        # Reconstruire et afficher le chemin
                        path = []
                        node = st.session_state.end_node
                        while node is not None:
                            path.append(node)
                            node = current_step["parent"].get(node)
                        path.reverse()
                        
                        if len(path) > 1:
                            st.info(f"📍 Nombre de nœuds dans le chemin: {len(path)}")
                    else:
                        st.error("❌ Aucun chemin trouvé entre les deux points")
            
            elif show_all_nodes:
                fig = plot_dijkstra_step(
                    st.session_state.graph, 
                    current_step, 
                    st.session_state.start_node, 
                    st.session_state.end_node
                )
            else:
                fig = plot_dijkstra_step_dynamic(
                    st.session_state.graph, 
                    current_step, 
                    st.session_state.start_node, 
                    st.session_state.end_node
                )
            
            graph_placeholder.plotly_chart(fig, width='stretch')
    
    # MODE 3: État initial (avant de démarrer)
    elif st.session_state.start_node is not None and st.session_state.end_node is not None:
        fig = plot_graph_with_points(
            st.session_state.graph, 
            start_node_id, 
            end_node_id
        )
        graph_placeholder.plotly_chart(fig, width='stretch')
    
    # MODE 4: Graphe sans sélection
    else:
        fig = plot_graph_plotly(st.session_state.graph)
        graph_placeholder.plotly_chart(fig, width='stretch')

else:
    # Aucun graphe chargé
    st.warning("⚠️ **Aucun graphe chargé**")
    st.info("""
    👈 Utilisez la barre latérale pour charger un graphe:
    - **Graphes sauvegardés**: Sélectionnez parmi les graphes dans `data/`
    - **Télécharger depuis OSM**: Pour télécharger un nouveau graphe
    - **Graphe de test**: Pour tester rapidement l'interface
    """)

# ============================================================
# Footer avec informations
# ============================================================
st.divider()
with st.expander("ℹ️ À propos de l'algorithme de Dijkstra"):
    st.markdown("""
    ### Algorithme de Dijkstra
    
    L'algorithme de Dijkstra trouve le plus court chemin entre deux nœuds dans un graphe pondéré.
    
    **Affichage:**
    - Le graphe complet est **toujours visible** en arrière-plan (gris très clair)
    - Les nœuds et arêtes explorés apparaissent en surbrillance au fur et à mesure
    
    **Code couleur:**
    - 🟢 **Vert**: Nœud de départ
    - 🔴 **Rouge**: Nœud d'arrivée
    - 🟡 **Jaune**: Nœud en cours d'exploration
    - 🔵 **Bleu**: Nœuds déjà visités
    - ⚪ **Gris clair**: Graphe complet en arrière-plan
    - 🟩 **Ligne verte épaisse**: Chemin final trouvé
    
    **Fonctionnalités:**
    - ▶️ Démarrer l'animation
    - ⏸️ Mettre en pause
    - ⏩ Avancer étape par étape en mode pause
    - ⏹️ Réinitialiser
    """)

with st.expander("📂 Gestion des graphes sauvegardés"):
    st.markdown("""
    ### Dossier data/
    
    Tous les graphes téléchargés sont automatiquement sauvegardés dans le dossier `data/`.
    
    **Pour ajouter vos propres graphes:**
    1. Placez vos fichiers de graphe (format pickle) dans le dossier `data/`
    2. Ils apparaîtront automatiquement dans la liste "Graphes sauvegardés"
    
    **Suppression:**
    - Activez le "Mode suppression" dans la sidebar
    - Sélectionnez le graphe à supprimer
    - Cliquez sur "Supprimer ce graphe"
    """)