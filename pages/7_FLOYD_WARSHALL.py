import streamlit as st
import time
import math
import pandas as pd

from graphs.download_graph import create_french_cities_graph
from vizualisation.plotly_graph import plot_fw_pair, plot_fw_path
from algorithms.floyd_warshall_functions import (
    floyd_warshall_steps, 
    floyd_warshall_complete,
    reconstruct_path_from_step,
    reconstruct_path_from_nxt,
    plot_floyd_warshall_final
)

st.set_page_config(page_title="Floyd Warshall", layout="wide")
st.title("🔍 Floyd-Warshall — Plus courts chemins entre tous les couples")

st.markdown("""
Floyd-Warshall calcule les distances minimales entre **tous** les couples (i, j).

- **Matrice complète** des distances (itération initiale + k=0 à k=|V|-1)
- **Animation étape par étape** (k, i, j)
- **Visualisation finale** avec chemin optimal et distances
""")

# ---------------------------
# Session state
# ---------------------------
for key, default in {
    "graph": None,
    "node_list": [],
    "steps": [],
    "step_index": 0,
    "running": False,
    "paused": False,
    "finished": False,
    "start_time": None,
    "src": None,
    "dst": None,
    "dist_final": None,
    "nxt_final": None,
    "all_matrices": None,
    "computed": False,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ---------------------------
# Sidebar
# ---------------------------
with st.sidebar:
    st.header("⚙️ Configuration")

    if st.button("🔥 Charger le graphe des métropoles", type="primary"):
        st.session_state.graph = create_french_cities_graph()
        st.session_state.node_list = list(st.session_state.graph.nodes())
        st.session_state.steps = []
        st.session_state.step_index = 0
        st.session_state.running = False
        st.session_state.paused = False
        st.session_state.finished = False
        st.session_state.computed = False
        st.success("Graphe chargé")
        st.rerun()

    st.subheader("⚡ Vitesse")
    speed = st.slider("Délai entre étapes (sec)", 0.01, 1.0, 0.15, 0.01)

    if st.session_state.graph is not None and st.session_state.node_list:
        st.subheader("🎯 Couple (source, destination)")
        src_idx = st.selectbox(
            "Source",
            range(len(st.session_state.node_list)),
            index=0,
            format_func=lambda i: str(st.session_state.node_list[i])
        )
        dst_idx = st.selectbox(
            "Destination",
            range(len(st.session_state.node_list)),
            index=min(1, len(st.session_state.node_list) - 1),
            format_func=lambda i: str(st.session_state.node_list[i])
        )
        st.session_state.src = st.session_state.node_list[src_idx]
        st.session_state.dst = st.session_state.node_list[dst_idx]

# ---------------------------
# Controls
# ---------------------------
st.header("🎮 Contrôles")
c1, c2, c3, c4, c5, c6 = st.columns(6)

with c1:
    if st.button("▶️ Démarrer Animation", disabled=st.session_state.running):
        if st.session_state.graph is None:
            st.error("Charge d'abord le graphe")
        else:
            st.session_state.running = True
            st.session_state.paused = False
            st.session_state.finished = False
            st.session_state.step_index = 0
            st.session_state.start_time = time.time()
            st.session_state.steps = list(floyd_warshall_steps(st.session_state.graph, weight="length"))
            st.rerun()

with c2:
    if st.button("⚡ Calculer Direct", disabled=st.session_state.graph is None):
        st.session_state.start_time = time.time()
        
        dist, nxt, all_matrices = floyd_warshall_complete(
            st.session_state.graph,
            weight="length"
        )
        
        st.session_state.dist_final = dist
        st.session_state.nxt_final = nxt
        st.session_state.all_matrices = all_matrices
        st.session_state.computed = True
        st.session_state.elapsed = time.time() - st.session_state.start_time
        st.rerun()

with c3:
    if st.button("⏸️ Pause", disabled=not st.session_state.running or st.session_state.paused):
        st.session_state.paused = True
        st.rerun()

with c4:
    if st.button("▶️ Reprendre", disabled=not st.session_state.paused):
        st.session_state.paused = False
        st.rerun()

with c5:
    if st.button("⏩ Étape", disabled=not st.session_state.paused):
        st.session_state.step_index += 1
        st.rerun()

with c6:
    if st.button("⏹️ Reset"):
        st.session_state.running = False
        st.session_state.paused = False
        st.session_state.finished = False
        st.session_state.step_index = 0
        st.session_state.steps = []
        st.session_state.computed = False
        st.session_state.dist_final = None
        st.session_state.nxt_final = None
        st.session_state.all_matrices = None
        st.rerun()

# ---------------------------
# Status (Animation)
# ---------------------------
if st.session_state.steps:
    colA, colB, colC = st.columns(3)

    with colA:
        if st.session_state.finished:
            st.success("✅ Animation terminée")
        elif st.session_state.paused:
            st.warning("⏸️ En pause")
        elif st.session_state.running:
            st.info("▶️ En cours")

    with colB:
        progress = min(1.0, st.session_state.step_index / max(1, len(st.session_state.steps)))
        st.metric("Progression", f"{st.session_state.step_index}/{len(st.session_state.steps)}")
        st.progress(progress)

    with colC:
        if st.session_state.start_time:
            st.metric("Temps écoulé", f"{(time.time()-st.session_state.start_time):.2f} sec")

# ---------------------------
# Status (Calcul direct)
# ---------------------------
if st.session_state.computed:
    colA, colB, colC = st.columns(3)

    with colA:
        st.success("✅ Calcul terminé")

    with colB:
        num_nodes = len(st.session_state.node_list)
        num_iterations = len(st.session_state.all_matrices)
        st.metric("Itérations", f"{num_iterations} (init + k=0 à {num_nodes-1})")

    with colC:
        st.metric("Temps écoulé", f"{st.session_state.elapsed:.4f} sec")

# ---------------------------
# MATRICE DES DISTANCES
# ---------------------------
if st.session_state.computed and st.session_state.all_matrices:
    
    st.header("📊 Matrice des distances")
    
    st.markdown("""
    **Légende :** 
    - **Matrice 0** : État initial (diagonale = 0, arêtes directes, reste = ∞)
    - **Matrices 1 à |V|** : Après relaxation par nœud intermédiaire k
    """)
    
    nodes = st.session_state.node_list
    
    # Sélecteur de matrice
    matrix_idx = st.selectbox(
        "Choisir une matrice à afficher",
        range(len(st.session_state.all_matrices)),
        format_func=lambda i: f"Matrice {i}" + (" (initiale)" if i == 0 else f" (après k={nodes[i-1]})")
    )
    
    # Afficher la matrice sélectionnée
    matrix = st.session_state.all_matrices[matrix_idx]
    
    # Créer le DataFrame
    table = []
    for i, row in enumerate(matrix):
        formatted_row = []
        for val in row:
            if val == math.inf:
                formatted_row.append("∞")
            elif val == 0.0:
                formatted_row.append("0")
            else:
                formatted_row.append(f"{val:.1f}")
        table.append(formatted_row)
    
    df = pd.DataFrame(table, columns=nodes, index=nodes)
    
    st.dataframe(df, use_container_width=True)
    
    # Afficher toutes les matrices en accordéon
    with st.expander("📋 Voir toutes les matrices"):
        for idx, matrix in enumerate(st.session_state.all_matrices):
            if idx == 0:
                st.subheader("Matrice 0 (initiale)")
            else:
                st.subheader(f"Matrice {idx} (après k={nodes[idx-1]})")
            
            table = []
            for i, row in enumerate(matrix):
                formatted_row = []
                for val in row:
                    if val == math.inf:
                        formatted_row.append("∞")
                    elif val == 0.0:
                        formatted_row.append("0")
                    else:
                        formatted_row.append(f"{val:.1f}")
                table.append(formatted_row)
            
            df = pd.DataFrame(table, columns=nodes, index=nodes)
            st.dataframe(df, use_container_width=True)

# ---------------------------
# VISUALISATION FINALE
# ---------------------------
if st.session_state.computed:
    
    st.header("🗺️ Visualisation finale")
    
    src = st.session_state.src
    dst = st.session_state.dst
    
    if src and dst:
        fig = plot_floyd_warshall_final(
            st.session_state.graph,
            st.session_state.dist_final,
            st.session_state.nxt_final,
            st.session_state.node_list,
            src,
            dst
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Résultat numérique
        st.subheader("📋 Résultat")
        
        idx_map = {st.session_state.node_list[i]: i for i in range(len(st.session_state.node_list))}
        i_src = idx_map[src]
        i_dst = idx_map[dst]
        distance = st.session_state.dist_final[i_src][i_dst]
        
        if distance == math.inf:
            st.warning(f"❌ **Aucun chemin** de {src} vers {dst}.")
        else:
            # Reconstruction du chemin
            path = reconstruct_path_from_nxt(
                st.session_state.nxt_final,
                st.session_state.node_list,
                src,
                dst
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.success(f"✅ **Distance minimale** de {src} à {dst} : **{distance:.2f}**")
            
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
                        "Poids": f"{edge_weight:.1f}",
                        "Distance cumulée": f"{cumulative_dist:.1f}"
                    })
                
                df_path = pd.DataFrame(path_details)
                st.dataframe(df_path, use_container_width=True, hide_index=True)

# ---------------------------
# MATRICE FINALE DE TOUTES LES DISTANCES
# ---------------------------
if st.session_state.computed:
    st.header("📏 Matrice finale de toutes les distances")
    
    st.markdown("""
    Cette matrice montre la distance minimale entre **chaque paire** de nœuds.
    """)
    
    nodes = st.session_state.node_list
    final_matrix = st.session_state.dist_final
    
    table = []
    for i, row in enumerate(final_matrix):
        formatted_row = []
        for val in row:
            if val == math.inf:
                formatted_row.append("∞")
            elif val == 0.0:
                formatted_row.append("0")
            else:
                formatted_row.append(f"{val:.1f}")
        table.append(formatted_row)
    
    df_final = pd.DataFrame(table, columns=nodes, index=nodes)
    st.dataframe(df_final, use_container_width=True)
    
    # Statistiques
    st.subheader("📊 Statistiques")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Distance maximale (hors infini)
        max_dist = 0
        for row in final_matrix:
            for val in row:
                if val != math.inf and val != 0:
                    max_dist = max(max_dist, val)
        st.metric("Distance max", f"{max_dist:.1f}")
    
    with col2:
        # Paires connectées
        connected_pairs = 0
        total_pairs = 0
        for i in range(len(nodes)):
            for j in range(len(nodes)):
                if i != j:
                    total_pairs += 1
                    if final_matrix[i][j] != math.inf:
                        connected_pairs += 1
        st.metric("Paires connectées", f"{connected_pairs}/{total_pairs}")
    
    with col3:
        # Distance moyenne (hors infini et diagonale)
        sum_dist = 0
        count = 0
        for i in range(len(nodes)):
            for j in range(len(nodes)):
                if i != j and final_matrix[i][j] != math.inf:
                    sum_dist += final_matrix[i][j]
                    count += 1
        avg_dist = sum_dist / count if count > 0 else 0
        st.metric("Distance moyenne", f"{avg_dist:.1f}")

# ---------------------------
# Visualisation (Animation)
# ---------------------------
if not st.session_state.computed:
    st.header("🔄 Animation")
    graph_placeholder = st.empty()

    if st.session_state.graph is None:
        st.warning("Aucun graphe chargé")
        st.stop()

    G = st.session_state.graph
    nodes = list(G.nodes())

    def show_step(step):
        src = st.session_state.src
        dst = st.session_state.dst

        # Affichage chemin si possible
        path = []
        if src is not None and dst is not None:
            path = reconstruct_path_from_step(step, nodes, src, dst)

        if path:
            fig = plot_fw_path(G, path)
        else:
            fig = plot_fw_pair(G, src, dst)

        graph_placeholder.plotly_chart(fig, use_container_width=True)

        # Infos texte
        if step.get("phase") == "relax":
            k = step["k"]
            i = step["i"]
            j = step["j"]
            updated = step["updated"]
            k_name = nodes[k] if k is not None else "?"
            i_name = nodes[i] if i is not None else "?"
            j_name = nodes[j] if j is not None else "?"
            
            st.write(
                f"**k={k_name}**, i={i_name}, j={j_name}, "
                f"updated={updated}, dist(i,j)={step['dist_ij_new']:.1f}"
            )

    # Animation
    if st.session_state.running and not st.session_state.paused:
        if st.session_state.step_index < len(st.session_state.steps):
            step = st.session_state.steps[st.session_state.step_index]
            show_step(step)
            time.sleep(speed)
            st.session_state.step_index += 1
            st.rerun()
        else:
            st.session_state.running = False
            st.session_state.finished = True
            st.rerun()
    else:
        if st.session_state.steps:
            step = st.session_state.steps[min(st.session_state.step_index, len(st.session_state.steps) - 1)]
            show_step(step)
        else:
            st.info("Clique sur ▶️ Démarrer Animation ou ⚡ Calculer Direct")

# ---------------------------
# FOOTER
# ---------------------------
st.divider()
st.markdown("""
### ℹ️ À propos de Floyd-Warshall

L'algorithme de Floyd-Warshall calcule les plus courts chemins entre **toutes les paires** de nœuds :

1. **Initialisation** : dist[i][i] = 0, dist[i][j] = poids(i,j) si arête existe, sinon ∞
2. **Relaxation** : pour chaque nœud intermédiaire k, pour chaque paire (i,j), 
   si dist[i][k] + dist[k][j] < dist[i][j], alors on met à jour dist[i][j]
3. **Résultat** : matrice finale des distances minimales entre toutes les paires

**Complexité** : O(|V|³)  
**Avantage** : calcule tous les chemins en une seule exécution, gère les poids négatifs  
**Inconvénient** : plus lent pour un seul chemin (préférer Dijkstra ou Bellman-Ford)
""")