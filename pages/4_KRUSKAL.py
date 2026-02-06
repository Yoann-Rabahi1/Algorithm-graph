import streamlit as st
import time

from download_graph import *
from kruskal_functions import *
from plotly_graph import *

st.set_page_config(page_title="Kruskal - MST", layout="wide")

# -----------------------------------------------------------
# TITRE + INTRO
# -----------------------------------------------------------
st.title("🌳 Algorithme de Kruskal — Arbre couvrant minimal (MST)")

st.markdown("""
Cette page te permet de visualiser **Kruskal étape par étape**, exactement comme DFS :

- tri des arêtes par poids  
- union-find  
- construction progressive du MST  
- visualisation dynamique  
- coût total final  

Le graphe utilisé est **uniquement celui des métropoles françaises**.
""")

# -----------------------------------------------------------
# SESSION STATE
# -----------------------------------------------------------
for key, default in {
    "graph": None,
    "steps": [],
    "step_index": 0,
    "running": False,
    "paused": False,
    "finished": False,
    "start_time": None
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
        st.success("Graphe chargé !")
        st.rerun()

    st.subheader("⚡ Vitesse")
    speed = st.slider("Délai entre étapes (sec)", 0.01, 1.0, 0.2, 0.01)

# -----------------------------------------------------------
# CONTROLS
# -----------------------------------------------------------
st.header("🎮 Contrôles")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("▶️ Démarrer", disabled=st.session_state.running):
        if st.session_state.graph is None:
            st.error("Charge d'abord le graphe des métropoles.")
        else:
            st.session_state.running = True
            st.session_state.paused = False
            st.session_state.finished = False
            st.session_state.step_index = 0
            st.session_state.start_time = time.time()

            st.session_state.steps = list(
                kruskal_steps(st.session_state.graph, weight="length")
            )
            st.rerun()

with col2:
    if st.button("⏸️ Pause", disabled=not st.session_state.running or st.session_state.paused):
        st.session_state.paused = True
        st.rerun()

with col3:
    if st.button("▶️ Reprendre", disabled=not st.session_state.paused):
        st.session_state.paused = False
        st.rerun()

with col4:
    if st.button("⏩ Étape", disabled=not st.session_state.paused):
        st.session_state.step_index += 1
        st.rerun()

with col5:
    if st.button("⏹️ Stop"):
        st.session_state.running = False
        st.session_state.paused = False
        st.session_state.finished = False
        st.session_state.step_index = 0
        st.session_state.steps = []
        st.rerun()

# -----------------------------------------------------------
# STATUS (progression + temps)
# -----------------------------------------------------------
if st.session_state.steps:
    colA, colB, colC = st.columns(3)

    with colA:
        if st.session_state.finished:
            st.success("MST terminé")
        elif st.session_state.paused:
            st.warning("En pause")
        elif st.session_state.running:
            st.info("En cours...")

    with colB:
        progress = st.session_state.step_index / len(st.session_state.steps)
        st.metric("Progression", f"{st.session_state.step_index}/{len(st.session_state.steps)}")
        st.progress(progress)

    with colC:
        if st.session_state.start_time:
            elapsed = time.time() - st.session_state.start_time
            st.metric("Temps écoulé", f"{elapsed:.2f} sec")


# -----------------------------------------------------------
# VISUALISATION
# -----------------------------------------------------------
st.header("📊 Visualisation")
graph_placeholder = st.empty()

if st.session_state.graph is not None:

    # --- MODE ANIMATION ---
    if st.session_state.running and not st.session_state.paused:

        if st.session_state.step_index < len(st.session_state.steps):
            step = st.session_state.steps[st.session_state.step_index]

            fig = plot_kruskal_step(st.session_state.graph, step)
            graph_placeholder.plotly_chart(fig, use_container_width=True)

            time.sleep(speed)
            st.session_state.step_index += 1
            st.rerun()

        else:
            st.session_state.running = False
            st.session_state.finished = True
            st.rerun()

    # --- MODE PAUSE / FIN ---
    elif st.session_state.steps:

        step = st.session_state.steps[min(
            st.session_state.step_index,
            len(st.session_state.steps) - 1
        )]

        # Affichage final ou intermédiaire
        if st.session_state.finished:
            fig = plot_kruskal_mst(st.session_state.graph, step["mst_edges"])
        else:
            fig = plot_kruskal_step(st.session_state.graph, step)

        graph_placeholder.plotly_chart(fig, use_container_width=True)

        # Résultats finaux
        if st.session_state.finished:

            total_cost = sum(w for (_, _, w) in step["mst_edges"])
            st.success(f"🌳 Coût total de l’ACPM : **{total_cost:.2f}**")

            if st.session_state.start_time:
                elapsed = time.time() - st.session_state.start_time
                st.info(f"⏱️ Temps total d'exécution : **{elapsed:.2f} sec**")

    # --- MODE INITIAL : afficher le graphe statique ---
    else:
        fig = plot_graph_plotly(st.session_state.graph, is_test_graph=True)
        graph_placeholder.plotly_chart(fig, use_container_width=True)
        st.info("Clique sur ▶️ Démarrer pour lancer Kruskal.")

else:
    st.warning("Aucun graphe chargé.")

# -----------------------------------------------------------
# FOOTER
# -----------------------------------------------------------
st.divider()
st.markdown("""
### ℹ️ À propos de Kruskal

L’algorithme de Kruskal construit un **arbre couvrant minimal (MST)** en :

1. triant les arêtes par poids,  
2. ajoutant les arêtes les plus légères,  
3. évitant les cycles grâce à **union-find**,  
4. jusqu’à connecter tout le graphe.

Cette page te permet de suivre **chaque étape** de sa construction.
""")
