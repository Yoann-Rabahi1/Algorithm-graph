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
Cette page reprend la même mise en page que Kruskal, mais adaptée à Bellman-Ford :

- tableau unique des distances (colonnes = nœuds, lignes = itérations)  
- EXACTEMENT |V|-1 itérations  
- détection de cycle négatif  
- affichage final du graphe et du chemin optimal  
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

    if st.button("📥 Charger le graphe Bellman-Ford", type="primary"):
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
            st.session_state[key] = None
        st.rerun()

# -----------------------------------------------------------
# STATUS
# -----------------------------------------------------------
if st.session_state.computed:
    colA, colB, colC = st.columns(3)

    with colA:
        if st.session_state.neg_cycle:
            st.error("Cycle négatif détecté")
        else:
            st.success("Calcul terminé")

    with colB:
        st.metric("Itérations", f"{len(st.session_state.iterations)} / {len(st.session_state.node_list)-1}")

    with colC:
        st.metric("Temps écoulé", f"{st.session_state.elapsed:.2f} sec")

# -----------------------------------------------------------
# TABLEAU DES DISTANCES
# -----------------------------------------------------------
if st.session_state.computed:

    st.header("📘 Évolution des distances")

    nodes = st.session_state.node_list
    table = []

    for snapshot in st.session_state.iterations:
        row = []
        for n in nodes:
            d = snapshot.get(n, math.inf)
            row.append(d if d != math.inf else None)
        table.append(row)

    df = pd.DataFrame(table, columns=nodes)
    df.index = [f"it {i+1}" for i in range(len(table))]

    st.dataframe(df, use_container_width=True)

# -----------------------------------------------------------
# VISUALISATION FINALE
# -----------------------------------------------------------
if st.session_state.computed:

    st.header("📊 Visualisation finale")

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

    # Résultat numérique
    tgt = st.session_state.target
    dist = st.session_state.dist

    if st.session_state.neg_cycle:
        st.error("Cycle négatif détecté : distances non fiables.")
    elif dist[tgt] == math.inf:
        st.warning("Aucun chemin vers la cible.")
    else:
        st.success(f"Distance minimale : **{dist[tgt]:.2f}**")

# -----------------------------------------------------------
# FOOTER
# -----------------------------------------------------------
st.divider()
st.markdown("""
### ℹ️ À propos de Bellman-Ford

Bellman-Ford calcule les plus courts chemins même en présence de **poids négatifs** :

1. relaxation de toutes les arêtes |V|-1 fois  
2. détection d’un cycle négatif  
3. reconstruction du chemin final  

Cette page affiche **toutes les distances** puis le **graphe final**.
""")
