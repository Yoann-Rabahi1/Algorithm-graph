import networkx as nx
import plotly.graph_objects as go

def build_pert_graph(tasks):
    """
    tasks: list de dict
      { "id": "A", "duration": 4, "pred": [] }
    retourne un DiGraph avec duration sur les noeuds
    """
    G = nx.DiGraph()
    for t in tasks:
        G.add_node(t["id"], duration=float(t["duration"]))
    for t in tasks:
        for p in t.get("pred", []):
            G.add_edge(p, t["id"])
    return G


def topological_levels(G):
    """
    donne une "profondeur" par noeud pour positionner en colonnes
    level[n] = longueur max en nb d'arcs depuis une source
    """
    level = {n: 0 for n in G.nodes()}
    for n in nx.topological_sort(G):
        for succ in G.successors(n):
            level[succ] = max(level[succ], level[n] + 1)
    return level


def pert_compute_steps(G):
    """
    Générateur étapes PERT.
    Etapes:
      1) forward pass (ES, EF)
      2) backward pass (LS, LF)
      3) final (slack, critical path)
    yield dict:
      phase: "forward" | "backward" | "final"
      current: noeud traité
      ES, EF, LS, LF, slack
      critical_nodes: set
      critical_edges: set((u,v))
    """
    if not nx.is_directed_acyclic_graph(G):
        raise ValueError("Le graphe PERT doit être un DAG (pas de cycle).")

    dur = {n: float(G.nodes[n].get("duration", 0.0)) for n in G.nodes()}

    ES = {n: 0.0 for n in G.nodes()}
    EF = {n: 0.0 for n in G.nodes()}

    order = list(nx.topological_sort(G))

    # -------- forward pass --------
    for n in order:
        preds = list(G.predecessors(n))
        ES[n] = max((EF[p] for p in preds), default=0.0)
        EF[n] = ES[n] + dur[n]

        yield {
            "phase": "forward",
            "current": n,
            "ES": dict(ES),
            "EF": dict(EF),
            "LS": {},
            "LF": {},
            "slack": {},
            "critical_nodes": set(),
            "critical_edges": set()
        }

    project_duration = max(EF.values(), default=0.0)

    # -------- backward pass --------
    LS = {n: 0.0 for n in G.nodes()}
    LF = {n: 0.0 for n in G.nodes()}

    for n in reversed(order):
        succs = list(G.successors(n))
        LF[n] = min((LS[s] for s in succs), default=project_duration)
        LS[n] = LF[n] - dur[n]

        yield {
            "phase": "backward",
            "current": n,
            "ES": dict(ES),
            "EF": dict(EF),
            "LS": dict(LS),
            "LF": dict(LF),
            "slack": {},
            "critical_nodes": set(),
            "critical_edges": set()
        }

    # -------- slack + critical --------
    slack = {n: LS[n] - ES[n] for n in G.nodes()}
    critical_nodes = {n for n in G.nodes() if abs(slack[n]) < 1e-9}

    critical_edges = set()
    for u, v in G.edges():
        # edge critique si u et v critiques et EF[u] == ES[v]
        if u in critical_nodes and v in critical_nodes and abs(EF[u] - ES[v]) < 1e-9:
            critical_edges.add((u, v))

    yield {
        "phase": "final",
        "current": None,
        "ES": dict(ES),
        "EF": dict(EF),
        "LS": dict(LS),
        "LF": dict(LF),
        "slack": dict(slack),
        "critical_nodes": set(critical_nodes),
        "critical_edges": set(critical_edges),
        "project_duration": project_duration
    }


def pert_compute_complete(G):
    """
    Version complète (non-itérative) de PERT.
    Retourne ES, EF, LS, LF, slack, critical_nodes, critical_edges, project_duration
    """
    if not nx.is_directed_acyclic_graph(G):
        raise ValueError("Le graphe PERT doit être un DAG (pas de cycle).")

    dur = {n: float(G.nodes[n].get("duration", 0.0)) for n in G.nodes()}

    ES = {n: 0.0 for n in G.nodes()}
    EF = {n: 0.0 for n in G.nodes()}

    order = list(nx.topological_sort(G))

    # Forward pass
    for n in order:
        preds = list(G.predecessors(n))
        ES[n] = max((EF[p] for p in preds), default=0.0)
        EF[n] = ES[n] + dur[n]

    project_duration = max(EF.values(), default=0.0)

    # Backward pass
    LS = {n: 0.0 for n in G.nodes()}
    LF = {n: 0.0 for n in G.nodes()}

    for n in reversed(order):
        succs = list(G.successors(n))
        LF[n] = min((LS[s] for s in succs), default=project_duration)
        LS[n] = LF[n] - dur[n]

    # Slack + critical
    slack = {n: LS[n] - ES[n] for n in G.nodes()}
    critical_nodes = {n for n in G.nodes() if abs(slack[n]) < 1e-9}

    critical_edges = set()
    for u, v in G.edges():
        if u in critical_nodes and v in critical_nodes and abs(EF[u] - ES[v]) < 1e-9:
            critical_edges.add((u, v))

    return {
        "ES": ES,
        "EF": EF,
        "LS": LS,
        "LF": LF,
        "slack": slack,
        "critical_nodes": critical_nodes,
        "critical_edges": critical_edges,
        "project_duration": project_duration
    }


def plot_pert_step(G, step):
    """
    Visualisation Plotly style "animation"
    - noeud courant en jaune
    - noeuds critiques en rouge (ou autre), le reste en noir
    - arêtes critiques en rouge, le reste gris
    """
    level = topological_levels(G)

    # positions (x par level, y par index dans la colonne)
    cols = {}
    for n, lv in level.items():
        cols.setdefault(lv, []).append(n)
    for lv in cols:
        cols[lv].sort()

    pos = {}
    for lv, nodes in cols.items():
        for i, n in enumerate(nodes):
            pos[n] = (lv * 2.0, -i * 1.2)

    current = step.get("current")
    crit_nodes = step.get("critical_nodes", set())
    crit_edges = step.get("critical_edges", set())

    ES = step.get("ES", {})
    EF = step.get("EF", {})
    LS = step.get("LS", {})
    LF = step.get("LF", {})
    slack = step.get("slack", {})

    # edges
    ex_bg, ey_bg = [], []
    ex_crit, ey_crit = [], []

    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        if (u, v) in crit_edges:
            ex_crit += [x0, x1, None]
            ey_crit += [y0, y1, None]
        else:
            ex_bg += [x0, x1, None]
            ey_bg += [y0, y1, None]

    edge_bg = go.Scatter(
        x=ex_bg, y=ey_bg,
        mode="lines",
        line=dict(width=2, color="#A0A0A0"),
        hoverinfo="none"
    )

    edge_crit = go.Scatter(
        x=ex_crit, y=ey_crit,
        mode="lines",
        line=dict(width=5, color="red"),
        hoverinfo="none"
    )

    # nodes
    nxs, nys, texts, colors = [], [], [], []
    for n in G.nodes():
        x, y = pos[n]
        nxs.append(x)
        nys.append(y)

        d = G.nodes[n].get("duration", 0)
        t = f"{n}<br>d={d}"
        if ES:
            t += f"<br>ES={ES.get(n, 0):.0f} EF={EF.get(n, 0):.0f}"
        if LS:
            t += f"<br>LS={LS.get(n, 0):.0f} LF={LF.get(n, 0):.0f}"
        if slack:
            t += f"<br>slack={slack.get(n, 0):.0f}"
        texts.append(t)

        if n == current:
            colors.append("yellow")
        elif n in crit_nodes:
            colors.append("red")
        else:
            colors.append("black")

    nodes = go.Scatter(
        x=nxs, y=nys,
        mode="markers",
        marker=dict(size=22, color=colors, line=dict(width=2, color="white")),
        hoverinfo="text",
        text=texts
    )

    fig = go.Figure([edge_bg, edge_crit, nodes])
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=650,
        plot_bgcolor="lightblue",
        paper_bgcolor="lightblue"
    )
    return fig


def plot_pert_final(G, result):
    """
    Visualisation finale améliorée du PERT avec :
    - Chemin critique en rouge épais
    - Tâches critiques en rouge
    - Tâches non-critiques en bleu avec marge affichée
    - Informations complètes sur chaque nœud
    """
    level = topological_levels(G)

    # positions (x par level, y par index dans la colonne)
    cols = {}
    for n, lv in level.items():
        cols.setdefault(lv, []).append(n)
    for lv in cols:
        cols[lv].sort()

    pos = {}
    for lv, nodes in cols.items():
        for i, n in enumerate(nodes):
            pos[n] = (lv * 2.0, -i * 1.2)

    crit_nodes = result.get("critical_nodes", set())
    crit_edges = result.get("critical_edges", set())

    ES = result.get("ES", {})
    EF = result.get("EF", {})
    LS = result.get("LS", {})
    LF = result.get("LF", {})
    slack = result.get("slack", {})

    # --- Arêtes ---
    ex_bg, ey_bg = [], []
    ex_crit, ey_crit = [], []

    for u, v in G.edges():
        x0, y0 = pos[u]
        x1, y1 = pos[v]
        if (u, v) in crit_edges:
            ex_crit += [x0, x1, None]
            ey_crit += [y0, y1, None]
        else:
            ex_bg += [x0, x1, None]
            ey_bg += [y0, y1, None]

    edge_bg = go.Scatter(
        x=ex_bg, y=ey_bg,
        mode="lines",
        line=dict(width=2, color="#A0A0A0"),
        hoverinfo="none",
        name="Arêtes normales"
    )

    edge_crit = go.Scatter(
        x=ex_crit, y=ey_crit,
        mode="lines",
        line=dict(width=7, color="red"),
        hoverinfo="none",
        name="Chemin critique"
    )

    # --- Nœuds avec informations détaillées ---
    nxs, nys, texts, colors, sizes = [], [], [], [], []
    
    for n in G.nodes():
        x, y = pos[n]
        nxs.append(x)
        nys.append(y)

        d = G.nodes[n].get("duration", 0)
        es = ES.get(n, 0)
        ef = EF.get(n, 0)
        ls = LS.get(n, 0)
        lf = LF.get(n, 0)
        s = slack.get(n, 0)
        
        # Label détaillé
        t = f"<b>{n}</b><br>"
        t += f"Durée: {d:.0f}<br>"
        t += f"ES: {es:.0f} | EF: {ef:.0f}<br>"
        t += f"LS: {ls:.0f} | LF: {lf:.0f}<br>"
        t += f"Marge: {s:.0f}"
        
        texts.append(t)

        # Couleurs selon criticité
        if n in crit_nodes:
            colors.append("red")
            sizes.append(60)
        else:
            colors.append("#031E66")
            sizes.append(55)

    nodes = go.Scatter(
        x=nxs, y=nys,
        mode="markers",
        marker=dict(
            size=sizes, 
            color=colors, 
            line=dict(width=4, color="white")
        ),
        hoverinfo="text",
        text=texts,
        name="Tâches"
    )

    # --- Labels des tâches (nom + durée) ---
    label_x, label_y, label_texts = [], [], []
    for n in G.nodes():
        x, y = pos[n]
        label_x.append(x)
        label_y.append(y)
        d = G.nodes[n].get("duration", 0)
        label_texts.append(f"{n}<br>d={d:.0f}")

    labels = go.Scatter(
        x=label_x, y=label_y,
        mode="text",
        text=label_texts,
        textposition="middle center",
        textfont=dict(size=12, color="white", family="Arial Black"),
        hoverinfo="skip",
        showlegend=False
    )

    fig = go.Figure([edge_bg, edge_crit, nodes, labels])
    
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=650,
        plot_bgcolor="lightblue",
        paper_bgcolor="lightblue"
    )
    
    return fig