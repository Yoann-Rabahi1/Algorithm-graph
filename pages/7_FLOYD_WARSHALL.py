import streamlit as st
import time
import math
import pandas as pd

from graphs.download_graph import create_french_cities_graph
from vizualisation.plotly_graph import plot_fw_pair, plot_fw_path
from algorithms.floyd_warshall_functions import (
    floyd_warshall_complete,
    reconstruct_path_from_nxt,
    plot_floyd_warshall_final
)

PAGE_ID = "FLOYD_WARSHALL"

if "current_page" not in st.session_state:
    st.session_state.current_page = PAGE_ID

# 🔁 Si on change de page → reset complet
if st.session_state.current_page != PAGE_ID:
    st.session_state.clear()
    st.session_state.current_page = PAGE_ID
    st.rerun()

st.set_page_config(page_title="Floyd Warshall", layout="wide")
st.title("🔍 Floyd-Warshall — Plus courts chemins entre tous les couples")

st.markdown("""
Floyd-Warshall calcule les distances minimales entre **tous** les couples (i, j).

- calcul complet des matrices (init + k)
- affichage matrice choisie
- affichage final du chemin optimal (source → destination)
""")

# ---------------------------
# Session state
# ---------------------------
for key, default in {
    "graph": None,
    "node_list": [],
    "src": None,
    "dst": None,
    "dist_final": None,
    "nxt_final": None,
    "all_matrices": None,
    "computed": False,
    "elapsed": None
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
        st.session_state.computed = False
        st.session_state.dist_final = None
        st.session_state.nxt_final = None
        st.session_state.all_matrices = None
        st.session_state.elapsed = None
        st.success("Graphe chargé")
        st.rerun()

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
# Controls (ONLY 2 BUTTONS)
# ---------------------------
st.header("🎮 Contrôles")
c1, c2 = st.columns(2)

with c1:
    if st.button("⚡ Calculer", disabled=st.session_state.graph is None):
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

with c2:
    if st.button("⏹️ Reset"):
        st.session_state.computed = False
        st.session_state.dist_final = None
        st.session_state.nxt_final = None
        st.session_state.all_matrices = None
        st.session_state.elapsed = None
        st.rerun()

# ---------------------------
# Status
# ---------------------------
if st.session_state.computed:
    colA, colB, colC = st.columns(3)

    with colA:
        st.success("✅ Calcul terminé")

    with colB:
        num_nodes = len(st.session_state.node_list)
        num_iterations = len(st.session_state.all_matrices) if st.session_state.all_matrices else 0
        st.metric("Itérations", f"{num_iterations} (init + k=0 à {num_nodes-1})")

    with colC:
        if st.session_state.elapsed is not None:
            st.metric("Temps", f"{st.session_state.elapsed:.4f} sec")

# ---------------------------
# If not computed yet
# ---------------------------
if st.session_state.graph is None:
    st.warning("Aucun graphe chargé")
    st.stop()

if not st.session_state.computed:
    st.info("Charge le graphe, choisis source/destination, puis clique sur ⚡ Calculer.")
    st.stop()

# ---------------------------
# MATRICE DES DISTANCES
# ---------------------------
if st.session_state.all_matrices:
    st.header("📊 Matrice des distances")

    nodes = st.session_state.node_list

    matrix_idx = st.selectbox(
        "Choisir une matrice à afficher",
        range(len(st.session_state.all_matrices)),
        format_func=lambda i: f"Matrice {i}" + (" (initiale)" if i == 0 else f" (après k={nodes[i-1]})")
    )

    matrix = st.session_state.all_matrices[matrix_idx]

    table = []
    for row in matrix:
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

    st.subheader("📋 Résultat")

    idx_map = {st.session_state.node_list[i]: i for i in range(len(st.session_state.node_list))}
    i_src = idx_map[src]
    i_dst = idx_map[dst]
    distance = st.session_state.dist_final[i_src][i_dst]

    if distance == math.inf:
        st.warning(f"❌ Aucun chemin de {src} vers {dst}.")
    else:
        path = reconstruct_path_from_nxt(
            st.session_state.nxt_final,
            st.session_state.node_list,
            src,
            dst
        )

        col1, col2 = st.columns(2)
        with col1:
            st.success(f"✅ Distance minimale de {src} à {dst} : {distance:.2f}")
        with col2:
            if path:
                st.info("🛤️ Chemin optimal : " + " → ".join(path))

        if path and len(path) > 1:
            st.markdown("### Détails du chemin")
            path_details = []
            cumulative_dist = 0.0

            for i in range(len(path) - 1):
                u, v = path[i], path[i + 1]

                # NetworkX MultiGraph safety
                edge_weight = None
                data_uv = st.session_state.graph.get_edge_data(u, v)
                if isinstance(data_uv, dict):
                    # MultiGraph: choose min length
                    lens = []
                    for k, data in data_uv.items():
                        if isinstance(data, dict) and "length" in data:
                            lens.append(float(data["length"]))
                    if lens:
                        edge_weight = min(lens)
                if edge_weight is None:
                    edge_weight = 0.0

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
# MATRICE FINALE
# ---------------------------
st.header("📏 Matrice finale de toutes les distances")

nodes = st.session_state.node_list
final_matrix = st.session_state.dist_final

table = []
for row in final_matrix:
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

st.divider()
st.markdown("""
### ℹ️ Floyd-Warshall
Complexité O(|V|³), utile pour obtenir tous les plus courts chemins en une exécution.
""")
