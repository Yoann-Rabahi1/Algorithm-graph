import streamlit as st
import time
import math
import pandas as pd

from graphs.download_graph import *
from algorithms.bellman_ford_functions import *
from vizualisation.plotly_graph import *

st.set_page_config(page_title="Bellman-Ford", layout="wide")

# -----------------------------------------------------------
# TITRE + INTRO
# -----------------------------------------------------------
st.title("🧭 Algorithme de Bellman-Ford — Plus courts chemins")

st.markdown("""
Cette page implémente l'algorithme de Bellman-Ford pour calculer les plus courts chemins :

- **Matrice complète** des distances (itération 0 à |V|-1)
- **Exactement |V|-1 itérations** de relaxation
- **Détection de cycle négatif**
- **Affichage du graphe final** avec le chemin optimal et les distances
""")

# -----------------------------------------------------------
# SESSION STATE
# -----------------------------------------------------------
for key, default in {
    "graph": None,
    "node_list": [],
    "dist": None,
    "parent": None,
    "neg_cycle": False,
    "iterations": [],
    "source": None,
    "target": None,
    "computed": False,
    "start_time": None,
    "elapsed": None
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# -----------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")

    if st.button("🔥 Charger le graphe Bellman-Ford", type="primary"):
        st.session_state.graph = create_bellman_ford_graph()
        st.session_state.node_list = list(st.session_state.graph.nodes())
        st.session_state.computed = False
        st.success("Graphe chargé !")
        st.rerun()

    if st.session_state.graph is not None:
        st.subheader("🎯 Source et cible")

        nodes = st.session_state.node_list

        start_idx = st.selectbox(
            "Source",
            range(len(nodes)),
            format_func=lambda i: str(nodes[i]),
            index=0
        )

        possible_targets = [i for i in range(len(nodes)) if i != start_idx]

        end_idx = st.selectbox(
            "Cible (ne peut pas être la source)",
            possible_targets,
            format_func=lambda i: str(nodes[i]),
            index=0
        )

        st.session_state.source = nodes[start_idx]
        st.session_state.target = nodes[end_idx]

# -----------------------------------------------------------
# CONTROLS
# -----------------------------------------------------------
st.header("🎮 Contrôles")

col1, col2 = st.columns(2)

with col1:
    if st.button("▶️ Calculer Bellman-Ford", disabled=st.session_state.graph is None):
        st.session_state.start_time = time.time()

        dist, parent, neg_cycle, iterations = bellman_ford_run(
            st.session_state.graph,
            st.session_state.source,
            weight="length"
        )

        st.session_state.dist = dist
        st.session_state.parent = parent
        st.session_state.neg_cycle = neg_cycle
        st.session_state.iterations = iterations
        st.session_state.computed = True
        st.session_state.elapsed = time.time() - st.session_state.start_time
        st.rerun()

with col2:
    if st.button("🧹 Reset"):
        for key in ["dist", "parent", "neg_cycle", "iterations", "computed", "elapsed"]:
            st.session_state[key] = None if key != "neg_cycle" else False
        st.rerun()

# -----------------------------------------------------------
# STATUS
# -----------------------------------------------------------
if st.session_state.computed:
    colA, colB, colC = st.columns(3)

    with colA:
        if st.session_state.neg_cycle:
            st.error("⚠️ Cycle négatif détecté")
        else:
            st.success("✅ Calcul terminé")

    with colB:
        num_nodes = len(st.session_state.node_list)
        expected_iterations = num_nodes  # n iterations (0 à n-1)
        actual_iterations = len(st.session_state.iterations)
        st.metric("Itérations", f"{actual_iterations} (0 à {num_nodes-1})")

    with colC:
        st.metric("Temps écoulé", f"{st.session_state.elapsed:.4f} sec")

# -----------------------------------------------------------
# TABLEAU DES DISTANCES
# -----------------------------------------------------------
if st.session_state.computed:

    st.header("📊 Évolution des distances")
    
    st.markdown("""
    **Légende :** 
    - **Itération 0** : État initial (source = 0, autres = ∞)
    - **Itérations 1 à |V|-1** : Relaxations successives de toutes les arêtes
    """)

    nodes = st.session_state.node_list
    table = []

    # Construire la table avec toutes les itérations
    for iteration_idx, snapshot in enumerate(st.session_state.iterations):
        row = []
        for n in nodes:
            d = snapshot.get(n, math.inf)
            if d == math.inf:
                row.append("∞")
            elif d == 0.0:
                row.append("0")
            else:
                row.append(f"{d:.1f}")
        table.append(row)

    # Créer le DataFrame avec les bons index
    df = pd.DataFrame(table, columns=nodes)
    df.index = [f"Itération {i}" for i in range(len(table))]

    # Afficher avec styling
    st.dataframe(df, use_container_width=True)
    
    # Informations supplémentaires
    st.info(f"""
    📌 **Nombre total d'itérations** : {len(st.session_state.iterations)}  
    📌 **Nombre de nœuds** : {len(nodes)}  
    📌 **Formule** : {len(nodes)-1} itérations de relaxation + 1 état initial = {len(nodes)} lignes
    """)

# -----------------------------------------------------------
# VISUALISATION FINALE
# -----------------------------------------------------------
if st.session_state.computed:

    st.header("🗺️ Visualisation finale")

    final_step = {
        "dist": st.session_state.dist,
        "parent": st.session_state.parent
    }

    fig = plot_bellman_ford_final_path(
        st.session_state.graph,
        final_step,
        st.session_state.source,
        st.session_state.target
    )

    st.plotly_chart(fig, use_container_width=True)

    # Résultat numérique détaillé
    st.subheader("📋 Résultat")
    
    tgt = st.session_state.target
    src = st.session_state.source
    dist = st.session_state.dist

    if st.session_state.neg_cycle:
        st.error("⚠️ **Cycle négatif détecté** : les distances ne sont pas fiables.")
    elif dist[tgt] == math.inf:
        st.warning(f"❌ **Aucun chemin** de {src} vers {tgt}.")
    else:
        # Reconstruction du chemin
        path = reconstruct_path(st.session_state.parent, src, tgt)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.success(f"✅ **Distance minimale** de {src} à {tgt} : **{dist[tgt]:.2f}**")
        
        with col2:
            if path:
                path_str = " → ".join(path)
                st.info(f"🛤️ **Chemin optimal** : {path_str}")
                
        # Détails du chemin
        if path and len(path) > 1:
            st.markdown("### Détails du chemin")
            path_details = []
            cumulative_dist = 0
            
            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]
                edge_weight = st.session_state.graph[u][v].get('length', 0)
                cumulative_dist += edge_weight
                path_details.append({
                    "Étape": i + 1,
                    "De": u,
                    "Vers": v,
                    "Poids": f"{edge_weight:+.1f}",
                    "Distance cumulée": f"{cumulative_dist:.1f}"
                })
            
            df_path = pd.DataFrame(path_details)
            st.dataframe(df_path, use_container_width=True, hide_index=True)

# -----------------------------------------------------------
# TOUTES LES DISTANCES
# -----------------------------------------------------------
if st.session_state.computed and not st.session_state.neg_cycle:
    st.header("📏 Distances finales depuis la source")
    
    dist_data = []
    for node in st.session_state.node_list:
        d = st.session_state.dist[node]
        if d == math.inf:
            dist_str = "∞ (non atteignable)"
        elif d == 0:
            dist_str = "0 (source)"
        else:
            dist_str = f"{d:.2f}"
        
        dist_data.append({
            "Nœud": node,
            "Distance depuis " + st.session_state.source: dist_str
        })
    
    df_distances = pd.DataFrame(dist_data)
    st.dataframe(df_distances, use_container_width=True, hide_index=True)

# -----------------------------------------------------------
# FOOTER
# -----------------------------------------------------------
st.divider()
st.markdown("""
### ℹ️ À propos de Bellman-Ford

L'algorithme de Bellman-Ford calcule les plus courts chemins même en présence de **poids négatifs** :

1. **Initialisation** : distance(source) = 0, toutes les autres = ∞
2. **Relaxation** : répéter |V|-1 fois la relaxation de toutes les arêtes
3. **Détection de cycle négatif** : vérifier si une relaxation supplémentaire améliore encore les distances
4. **Reconstruction** : suivre les parents pour obtenir le chemin optimal

**Complexité** : O(|V| × |E|)  
**Avantage** : gère les poids négatifs et détecte les cycles négatifs  
**Inconvénient** : plus lent que Dijkstra pour les graphes sans poids négatifs
""")