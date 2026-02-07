import streamlit as st
import time
import math
import pandas as pd

from download_graph import create_french_cities_graph
from bellman_ford_functions import bellman_ford_run, reconstruct_path, plot_bellman_result

st.set_page_config(page_title="Bellman Ford", layout="wide")

st.title("🧭 Bellman Ford, plus courts chemins")
st.markdown("""
Ici on ne spam pas le graphe à chaque relaxation.
On calcule Bellman Ford, on affiche la table de distances, puis on affiche le chemin final.
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

    if st.button("📥 Charger le graphe des métropoles", type="primary"):
        st.session_state.graph = create_french_cities_graph()
        st.session_state.node_list = list(st.session_state.graph.nodes())
        st.session_state.computed = False
        st.success("Graphe chargé !")
        st.rerun()

    if st.session_state.graph is not None:
        st.subheader("🎯 Source et cible")

        s_idx = st.selectbox(
            "Source",
            range(len(st.session_state.node_list)),
            format_func=lambda i: str(st.session_state.node_list[i]),
            index=0
        )
        t_idx = st.selectbox(
            "Cible",
            range(len(st.session_state.node_list)),
            format_func=lambda i: str(st.session_state.node_list[i]),
            index=min(1, len(st.session_state.node_list) - 1)
        )

        st.session_state.source = st.session_state.node_list[s_idx]
        st.session_state.target = st.session_state.node_list[t_idx]

        st.divider()
        show_iterations = st.checkbox("Afficher dist à chaque itération", value=False)
        show_unreached = st.checkbox("Afficher aussi les noeuds inaccessibles", value=False)

# -----------------------------------------------------------
# ACTION
# -----------------------------------------------------------
st.header("🎮 Contrôles")

col1, col2 = st.columns(2)

with col1:
    if st.button("▶️ Calculer Bellman Ford", disabled=st.session_state.graph is None):
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
    if st.button("🧹 Reset résultats"):
        st.session_state.dist = None
        st.session_state.parent = None
        st.session_state.neg_cycle = False
        st.session_state.iterations = []
        st.session_state.computed = False
        st.session_state.elapsed = None
        st.rerun()

# -----------------------------------------------------------
# RESULTATS
# -----------------------------------------------------------
if st.session_state.computed:

    if st.session_state.elapsed is not None:
        st.info(f"⏱️ Temps de calcul: {st.session_state.elapsed:.4f} sec")

    if st.session_state.neg_cycle:
        st.error("Cycle négatif détecté, les distances ne sont pas fiables.")
    else:
        st.success("Calcul terminé, pas de cycle négatif détecté.")

    dist = st.session_state.dist
    source = st.session_state.source
    target = st.session_state.target

    # Tableau dist finale
    st.subheader("📋 Distances finales")
    rows = []
    for n, d in dist.items():
        if not show_unreached and d == math.inf:
            continue
        rows.append({"node": str(n), "dist": (None if d == math.inf else float(d))})

    df = pd.DataFrame(rows).sort_values(by=["dist"], na_position="last")
    st.dataframe(df, use_container_width=True)

    # Optionnel, dist par itération
    if "show_iterations" in locals() and show_iterations:
        st.subheader("🔁 Distances par itération")
        it_rows = []
        for it, snap in enumerate(st.session_state.iterations, start=1):
            for n, d in snap.items():
                if not show_unreached and d == math.inf:
                    continue
                it_rows.append({
                    "iter": it,
                    "node": str(n),
                    "dist": (None if d == math.inf else float(d))
                })
        df_it = pd.DataFrame(it_rows)
        st.dataframe(df_it, use_container_width=True)

    # Chemin final
    st.subheader("🧭 Chemin source -> cible")
    path = reconstruct_path(st.session_state.parent, source, target)
    if not path:
        st.warning("Pas de chemin trouvé vers la cible.")
    else:
        d = dist.get(target, math.inf)
        st.success(f"Distance source -> cible: {d:.2f}")
        st.write(path)

    # Graphe final
    st.subheader("📊 Visualisation finale")
    fig = plot_bellman_result(
        st.session_state.graph,
        source=source,
        target=target,
        path=path,
        dist=dist
    )
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("Charge le graphe, choisis source et cible, puis clique sur ▶️ Calculer.")
