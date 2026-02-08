import streamlit as st
import time
import math

from graphs.download_graph import *
from algorithms.bellman_ford_functions import *

st.set_page_config(page_title="Bellman Ford", layout="wide")

st.title("🧭 Bellman Ford, plus courts chemins")

st.markdown("""
Bellman Ford calcule les plus courts chemins depuis une source.
Il supporte les poids négatifs et peut détecter un cycle négatif.
""")

# -----------------------------------------------------------
# SESSION STATE
# -----------------------------------------------------------
for key, default in {
    "graph": None,
    "node_list": [],
    "steps": [],
    "step_index": 0,
    "running": False,
    "paused": False,
    "finished": False,
    "start_node": None,
    "end_node": None,
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
        st.session_state.graph = create_bellman_ford_graph()
        st.session_state.node_list = list(st.session_state.graph.nodes())
        st.success("Graphe chargé !")
        st.rerun()

    if st.session_state.graph is not None:
        st.subheader("🎯 Source et cible")

        nodes = st.session_state.node_list

        # Sélection de la source
        start_idx = st.selectbox(
            "Source",
            range(len(nodes)),
            format_func=lambda i: str(nodes[i]),
            index=0
        )

        # Sélection de la cible, mais sans proposer la même valeur
        possible_targets = [i for i in range(len(nodes)) if i != start_idx]

        end_idx = st.selectbox(
            "Cible (ne peut pas être la source)",
            possible_targets,
            format_func=lambda i: str(nodes[i]),
            index=0
        )

        st.session_state.start_node = nodes[start_idx]
        st.session_state.end_node = nodes[end_idx]


        st.subheader("⚡ Vitesse")
        speed = st.slider("Délai entre étapes (sec)", 0.01, 1.0, 0.2, 0.01)

        st.subheader("👁️ Options")
        show_all = st.checkbox("Afficher tous les noeuds", value=False)

# -----------------------------------------------------------
# CONTROLS
# -----------------------------------------------------------
st.header("🎮 Contrôles")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    if st.button("▶️ Démarrer", disabled=st.session_state.running):
        if st.session_state.graph is None:
            st.error("Charge d'abord un graphe.")
        else:
            st.session_state.running = True
            st.session_state.paused = False
            st.session_state.finished = False
            st.session_state.step_index = 0
            st.session_state.start_time = time.time()

            st.session_state.steps = list(
                bellman_ford_steps(
                    st.session_state.graph,
                    st.session_state.start_node,
                    weight="length"
                )
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
# STATUS
# -----------------------------------------------------------
if st.session_state.steps:
    colA, colB, colC = st.columns(3)

    with colA:
        if st.session_state.finished:
            st.success("Terminé")
        elif st.session_state.paused:
            st.warning("En pause")
        elif st.session_state.running:
            st.info("En cours...")

    with colB:
        progress = st.session_state.step_index / len(st.session_state.steps)
        st.metric("Progression", f"{st.session_state.step_index}/{len(st.session_state.steps)}")
        st.progress(min(1.0, progress))

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

            fig = plot_bellman_ford_step(
                st.session_state.graph,
                step,
                source=st.session_state.start_node,
                target=st.session_state.end_node,
                show_all_nodes=show_all if "show_all" in locals() else False
            )
            graph_placeholder.plotly_chart(fig, use_container_width=True)

            time.sleep(speed)
            st.session_state.step_index += 1
            st.rerun()

        else:
            st.session_state.running = False
            st.session_state.finished = True
            st.rerun()

    # --- MODE PAUSE / INTERMÉDIAIRE ---
    elif st.session_state.steps and not st.session_state.finished:

        step = st.session_state.steps[min(
            st.session_state.step_index,
            len(st.session_state.steps) - 1
        )]

        fig = plot_bellman_ford_step(
            st.session_state.graph,
            step,
            source=st.session_state.start_node,
            target=st.session_state.end_node,
            show_all_nodes=show_all if "show_all" in locals() else False
        )
        graph_placeholder.plotly_chart(fig, use_container_width=True)

        # Infos d’étape
        phase = step.get("phase")
        if phase:
            st.info(f"Phase : {phase}, itération : {step.get('iter')}")

        if step.get("neg_cycle"):
            st.error("Cycle négatif détecté : distances non fiables.")

    # --- MODE FIN : AFFICHAGE DU CHEMIN FINAL ---
    elif st.session_state.finished:

        final_step = st.session_state.steps[-1]

        fig = plot_bellman_ford_final_path(
            st.session_state.graph,
            final_step,
            st.session_state.start_node,
            st.session_state.end_node
        )
        graph_placeholder.plotly_chart(fig, use_container_width=True)

        # Résultat numérique
        dist = final_step["dist"]
        tgt = st.session_state.end_node

        if final_step.get("neg_cycle"):
            st.error("Cycle négatif détecté : distances non fiables.")
        elif dist[tgt] == math.inf:
            st.warning("Aucun chemin vers la cible.")
        else:
            st.success(f"Distance minimale : {dist[tgt]:.2f}")

        # Temps total
        if st.session_state.start_time:
            elapsed = time.time() - st.session_state.start_time
            st.info(f"⏱️ Temps total d'exécution : {elapsed:.2f} sec")

    # --- MODE INITIAL ---
    else:
        st.info("Clique sur ▶️ Démarrer pour lancer Bellman‑Ford.")

else:
    st.warning("Aucun graphe chargé.")


st.divider()
st.markdown("""
### ℹ️ Bellman Ford
On relâche toutes les arêtes |V|-1 fois, puis on refait un tour pour détecter un cycle négatif.
""")
