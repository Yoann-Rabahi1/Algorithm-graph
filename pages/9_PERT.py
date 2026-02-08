import streamlit as st
import time
import pandas as pd

from algorithms.pert_functions import (
    build_pert_graph, 
    pert_compute_steps, 
    pert_compute_complete,
    plot_pert_step,
    plot_pert_final
)

st.set_page_config(page_title="PERT", layout="wide")

st.title("📌 PERT — Chemin critique et ordonnancement de projet")

st.markdown("""
Cette page implémente la méthode PERT (Program Evaluation and Review Technique) :

- **Forward pass** : calcul des dates au plus tôt (ES, EF)
- **Backward pass** : calcul des dates au plus tard (LS, LF)
- **Marges** : calcul du slack (marge totale)
- **Chemin critique** : identification des tâches critiques (marge = 0)
- **Matrice complète** : tableau de toutes les dates et marges
- **Visualisation finale** : graphe avec chemin critique en rouge
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
    "project_duration": None,
    "computed": False,
    "result": None,
    "elapsed": None
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# -----------------------------------------------------------
# SIDEBAR
# -----------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Configuration")

    st.subheader("🔥 Charger un exemple PERT")
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
        st.session_state.computed = False
        st.success("PERT chargé")
        st.rerun()

    st.subheader("⚡ Vitesse")
    speed = st.slider("Délai entre étapes (sec)", 0.01, 1.0, 0.2, 0.01)

# -----------------------------------------------------------
# CONTROLS
# -----------------------------------------------------------
st.header("🎮 Contrôles")

col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    if st.button("▶️ Animation", disabled=st.session_state.running):
        if st.session_state.graph is None:
            st.error("Charge un exemple PERT d'abord.")
        else:
            st.session_state.running = True
            st.session_state.paused = False
            st.session_state.finished = False
            st.session_state.computed = False
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
    if st.button("⚡ Calcul Direct", disabled=st.session_state.graph is None):
        st.session_state.start_time = time.time()
        
        try:
            result = pert_compute_complete(st.session_state.graph)
            st.session_state.result = result
            st.session_state.computed = True
            st.session_state.elapsed = time.time() - st.session_state.start_time
            st.rerun()
        except Exception as e:
            st.error(f"Erreur PERT: {e}")

with col3:
    if st.button("⏸️ Pause", disabled=not st.session_state.running or st.session_state.paused):
        st.session_state.paused = True
        st.rerun()

with col4:
    if st.button("▶️ Reprendre", disabled=not st.session_state.paused):
        st.session_state.paused = False
        st.rerun()

with col5:
    if st.button("⏩ Étape", disabled=not st.session_state.paused):
        st.session_state.step_index += 1
        st.rerun()

with col6:
    if st.button("⏹️ Reset"):
        st.session_state.running = False
        st.session_state.paused = False
        st.session_state.finished = False
        st.session_state.computed = False
        st.session_state.step_index = 0
        st.session_state.steps = []
        st.session_state.project_duration = None
        st.session_state.result = None
        st.rerun()

# -----------------------------------------------------------
# STATUS (Animation)
# -----------------------------------------------------------
if st.session_state.steps:
    colA, colB, colC = st.columns(3)

    with colA:
        if st.session_state.finished:
            st.success("✅ PERT terminé")
        elif st.session_state.paused:
            st.warning("⏸️ En pause")
        elif st.session_state.running:
            st.info("▶️ En cours...")

    with colB:
        progress = st.session_state.step_index / len(st.session_state.steps)
        st.metric("Progression", f"{st.session_state.step_index}/{len(st.session_state.steps)}")
        st.progress(progress)

    with colC:
        if st.session_state.start_time:
            elapsed = time.time() - st.session_state.start_time
            st.metric("Temps écoulé", f"{elapsed:.2f} sec")

# -----------------------------------------------------------
# STATUS (Calcul direct)
# -----------------------------------------------------------
if st.session_state.computed:
    colA, colB, colC = st.columns(3)

    with colA:
        st.success("✅ Calcul terminé")

    with colB:
        num_tasks = len(st.session_state.graph.nodes()) if st.session_state.graph else 0
        st.metric("Tâches", f"{num_tasks}")

    with colC:
        st.metric("Temps écoulé", f"{st.session_state.elapsed:.4f} sec")

# -----------------------------------------------------------
# TABLEAU DES DATES ET MARGES
# -----------------------------------------------------------
if st.session_state.computed and st.session_state.result:
    
    st.header("📊 Tableau des dates et marges")
    
    st.markdown("""
    **Légende :** 
    - **ES** (Earliest Start) : Date de début au plus tôt
    - **EF** (Earliest Finish) : Date de fin au plus tôt
    - **LS** (Latest Start) : Date de début au plus tard
    - **LF** (Latest Finish) : Date de fin au plus tard
    - **Marge** : LS - ES (ou LF - EF)
    - **Critique** : Tâche sur le chemin critique (marge = 0)
    """)
    
    result = st.session_state.result
    
    # Construire le tableau
    tasks_data = []
    for node in sorted(st.session_state.graph.nodes()):
        duration = st.session_state.graph.nodes[node].get("duration", 0)
        es = result["ES"].get(node, 0)
        ef = result["EF"].get(node, 0)
        ls = result["LS"].get(node, 0)
        lf = result["LF"].get(node, 0)
        slack = result["slack"].get(node, 0)
        is_critical = node in result["critical_nodes"]
        
        tasks_data.append({
            "Tâche": node,
            "Durée": f"{duration:.0f}",
            "ES": f"{es:.0f}",
            "EF": f"{ef:.0f}",
            "LS": f"{ls:.0f}",
            "LF": f"{lf:.0f}",
            "Marge": f"{slack:.0f}",
            "Critique": "✓" if is_critical else ""
        })
    
    df_tasks = pd.DataFrame(tasks_data)
    
    # Afficher avec styling
    st.dataframe(df_tasks, use_container_width=True, hide_index=True)
    
    # Informations projet
    st.info(f"""
    📌 **Durée totale du projet** : {result['project_duration']:.0f}  
    📌 **Nombre de tâches critiques** : {len(result['critical_nodes'])}  
    📌 **Tâches critiques** : {', '.join(sorted(result['critical_nodes']))}
    """)

# -----------------------------------------------------------
# VISUALISATION FINALE
# -----------------------------------------------------------
if st.session_state.computed and st.session_state.result:
    
    st.header("🗺️ Visualisation finale")
    
    fig = plot_pert_final(st.session_state.graph, st.session_state.result)
    st.plotly_chart(fig, use_container_width=True)
    
    # Analyse du chemin critique
    st.subheader("📋 Analyse du chemin critique")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.success(f"✅ **Durée minimale du projet** : {result['project_duration']:.0f}")
        
        critical_path = sorted(list(result['critical_nodes']))
        st.info(f"🛤️ **Chemin critique** : {' → '.join(critical_path)}")
    
    with col2:
        num_critical = len(result['critical_nodes'])
        num_total = len(st.session_state.graph.nodes())
        st.metric("Tâches critiques", f"{num_critical}/{num_total}")
        
        num_critical_edges = len(result['critical_edges'])
        num_total_edges = len(st.session_state.graph.edges())
        st.metric("Arêtes critiques", f"{num_critical_edges}/{num_total_edges}")
    
    # Tâches avec marge
    st.markdown("### Tâches avec marge de manœuvre")
    
    non_critical_tasks = []
    for node in sorted(st.session_state.graph.nodes()):
        if node not in result['critical_nodes']:
            slack = result['slack'].get(node, 0)
            duration = st.session_state.graph.nodes[node].get("duration", 0)
            non_critical_tasks.append({
                "Tâche": node,
                "Durée": f"{duration:.0f}",
                "Marge disponible": f"{slack:.0f}",
                "% de flexibilité": f"{(slack/duration*100):.1f}%" if duration > 0 else "N/A"
            })
    
    if non_critical_tasks:
        df_non_critical = pd.DataFrame(non_critical_tasks)
        st.dataframe(df_non_critical, use_container_width=True, hide_index=True)
    else:
        st.warning("⚠️ Toutes les tâches sont critiques ! Aucune marge de manœuvre.")

# -----------------------------------------------------------
# GRAPHE DE DÉPENDANCES
# -----------------------------------------------------------
if st.session_state.computed and st.session_state.result:
    
    st.header("🔗 Graphe de dépendances")
    
    # Construire tableau des dépendances
    deps_data = []
    for node in sorted(st.session_state.graph.nodes()):
        preds = list(st.session_state.graph.predecessors(node))
        succs = list(st.session_state.graph.successors(node))
        
        deps_data.append({
            "Tâche": node,
            "Prédécesseurs": ", ".join(sorted(preds)) if preds else "—",
            "Successeurs": ", ".join(sorted(succs)) if succs else "—",
            "Critique": "✓" if node in result['critical_nodes'] else ""
        })
    
    df_deps = pd.DataFrame(deps_data)
    st.dataframe(df_deps, use_container_width=True, hide_index=True)

# -----------------------------------------------------------
# VISUALISATION (Animation)
# -----------------------------------------------------------
if not st.session_state.computed:
    st.header("🔄 Animation")
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
                st.info("Clique sur ▶️ Animation ou ⚡ Calcul Direct.")
    else:
        st.warning("Aucun PERT chargé.")

# -----------------------------------------------------------
# FOOTER
# -----------------------------------------------------------
st.divider()
st.markdown("""
### ℹ️ À propos de PERT

La méthode PERT (Program Evaluation and Review Technique) est une technique d'ordonnancement de projet :

1. **Forward pass** : Calcul des dates au plus tôt
   - ES (Earliest Start) : date de début au plus tôt
   - EF (Earliest Finish) : date de fin au plus tôt = ES + durée

2. **Backward pass** : Calcul des dates au plus tard
   - LF (Latest Finish) : date de fin au plus tard
   - LS (Latest Start) : date de début au plus tard = LF - durée

3. **Calcul des marges** : Marge = LS - ES = LF - EF
   - Marge = 0 → tâche **critique**
   - Marge > 0 → tâche non-critique avec flexibilité

4. **Chemin critique** : Séquence de tâches critiques qui détermine la durée minimale du projet

**Complexité** : O(|V| + |E|)  
**Avantage** : Identifie les tâches critiques et les marges de manœuvre  
**Usage** : Gestion de projet, planification, optimisation des ressources
""")