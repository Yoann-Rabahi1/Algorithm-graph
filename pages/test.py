import streamlit as st

from kruskal_functions import kruskal_osmnx
from plotly_graph import plot_graph_plotly, plot_kruskal_mst

st.title("🌳 Kruskal MST")

st.header("📊 Visualisation")

# 1) Pas de graphe en mémoire
if "graph" not in st.session_state or st.session_state.graph is None:
    st.warning("⚠️ Aucun graphe chargé dans st.session_state.graph")

# 2) Graphe présent
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
            st.success(f"Coût total = {total_cost:.2f}")
            st.write(f"Arêtes MST = {len(mst_edges)}")

            fig = plot_kruskal_mst(G, mst_edges)
            st.plotly_chart(fig, use_container_width=True)
