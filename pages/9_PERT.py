import streamlit as st
import time

from pert_functions import build_pert_graph, pert_compute_steps, plot_pert_step

st.set_page_config(page_title="PERT", layout="wide")

st.title("📌 PERT, chemin critique")

st.markdown("""
Cette page affiche PERT étape par étape:

- forward pass (ES, EF)
- backward pass (LS, LF)
- marges (slack)
- chemin critique
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
    "start_time": None,
    "project_duration": None
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# -----------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")

    st.subheader("📥 Charger un exemple PERT")
    if st.button("Charger exemple", type="primary"):
        tasks = [
            {"id": "A", "duration": 4, "pred": []},
            {"id": "B", "duration": 3, "pred": ["A"]},
            {"id": "C", "duration": 2, "pred": ["A"]},
            {"id": "D", "duration": 5, "pred": ["B"]},
            {"id": "E", "duration": 1, "pred": ["B", "C"]},
            {"id": "F", "duration": 2, "pred": ["D", "E"]},
        ]
        st.session_state.graph = build_pert_graph(tasks)
        st.success("PERT chargé")
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
            st.error("Charge un exemple PERT d'abord.")
        else:
            st.session_state.running = True
            st.session_state.paused = False
            st.session_state.finished = False
            st.session_state.step_index = 0
            st.session_state.start_time = time.time()

            try:
                st.session_state.steps = list(pert_compute_steps(st.session_state.graph))
            except Exception as e:
                st.session_state.running = False
                st.session_state.steps = []
                st.error(f"Erreur PERT: {e}")
                st.stop()

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
        st.session_state.project_duration = None
        st.rerun()

# -----------------------------------------------------------
# STATUS
# -----------------------------------------------------------
if st.session_state.steps:
    colA, colB, colC = st.columns(3)

    with colA:
        if st.session_state.finished:
            st.success("PERT terminé")
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

    # MODE ANIMATION
    if st.session_state.running and not st.session_state.paused:

        if st.session_state.step_index < len(st.session_state.steps):
            step = st.session_state.steps[st.session_state.step_index]
            fig = plot_pert_step(st.session_state.graph, step)
            graph_placeholder.plotly_chart(fig, use_container_width=True)

            time.sleep(speed)
            st.session_state.step_index += 1
            st.rerun()

        else:
            st.session_state.running = False
            st.session_state.finished = True
            st.rerun()

    # MODE PAUSE / FIN
    else:
        if st.session_state.steps:
            step = st.session_state.steps[min(
                st.session_state.step_index,
                len(st.session_state.steps) - 1
            )]

            fig = plot_pert_step(st.session_state.graph, step)
            graph_placeholder.plotly_chart(fig, use_container_width=True)

            phase = step.get("phase", "")
            st.info(f"Phase: {phase}")

            if phase == "final":
                pdur = step.get("project_duration", None)
                if pdur is not None:
                    st.success(f"Durée totale projet: {pdur:.0f}")

                crit = sorted(list(step.get("critical_nodes", set())))
                st.write(f"Nœuds critiques: {crit}")

        else:
            st.info("Clique sur ▶️ Démarrer.")
else:
    st.warning("Aucun PERT chargé.")

st.divider()
st.markdown("""
### ℹ️ PERT
PERT calcule les dates au plus tôt, au plus tard, la marge, puis déduit le chemin critique (marge = 0).
""")
