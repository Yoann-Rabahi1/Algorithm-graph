import heapq
import plotly.graph_objects as go

# ---------------------------------------------------------
# Générateur étape par étape pour Prim
# ---------------------------------------------------------
def prim_steps(G, start_node=None, weight="length"):
    """
    Générateur étape par étape pour Prim (MST).
    Le graphe est considéré comme non orienté pour Prim.
    """

    nodes = list(G.nodes())
    if not nodes:
        yield {
            "current_edge": None,
            "candidate_edge": None,
            "mst_edges": [],
            "visited_nodes": set(),
            "total_cost": 0.0
        }
        return

    if start_node is None:
        start_node = nodes[0]

    visited = set([start_node])
    mst_edges = []
    total_cost = 0.0

    pq = []

    def push_edges_from(u):
        # voisins sortants
        for v in G.successors(u):
            edges = G.get_edge_data(u, v)
            if edges:
                w = min(ed.get(weight, 1) for ed in edges.values())
                heapq.heappush(pq, (w, u, v))

        # voisins entrants (non orienté)
        for v in G.predecessors(u):
            edges = G.get_edge_data(v, u)
            if edges:
                w = min(ed.get(weight, 1) for ed in edges.values())
                heapq.heappush(pq, (w, u, v))

    push_edges_from(start_node)

    # étape initiale
    yield {
        "current_edge": None,
        "candidate_edge": None,
        "mst_edges": list(mst_edges),
        "visited_nodes": set(visited),
        "total_cost": total_cost
    }

    while pq and len(visited) < len(nodes):
        w, u, v = heapq.heappop(pq)

        # étape candidate
        yield {
            "current_edge": None,
            "candidate_edge": (u, v, w),
            "mst_edges": list(mst_edges),
            "visited_nodes": set(visited),
            "total_cost": total_cost
        }

        # ignorer si déjà dans l'arbre
        if u in visited and v in visited:
            continue

        # normalisation
        if u not in visited and v in visited:
            u, v = v, u

        if u in visited and v not in visited:
            visited.add(v)
            mst_edges.append((u, v, w))
            total_cost += w

            # étape acceptation
            yield {
                "current_edge": (u, v, w),
                "candidate_edge": None,
                "mst_edges": list(mst_edges),
                "visited_nodes": set(visited),
                "total_cost": total_cost
            }

            push_edges_from(v)

    # étape finale
    yield {
        "current_edge": None,
        "candidate_edge": None,
        "mst_edges": list(mst_edges),
        "visited_nodes": set(visited),
        "total_cost": total_cost
    }


# ---------------------------------------------------------
# Affichage dynamique étape par étape (Prim)
# ---------------------------------------------------------
def plot_prim_step(G, step):

    current = step.get("current_edge")
    candidate = step.get("candidate_edge")
    mst_edges = step.get("mst_edges", [])
    visited_nodes = step.get("visited_nodes", set())

    # --- Arrière-plan ---
    all_edge_x, all_edge_y = [], []
    for u, v in G.edges():
        all_edge_x += [G.nodes[u]['x'], G.nodes[v]['x'], None]
        all_edge_y += [G.nodes[u]['y'], G.nodes[v]['y'], None]

    bg_edges = go.Scatter(
        x=all_edge_x, y=all_edge_y,
        mode="lines",
        line=dict(width=1.5, color="#A0A0A0"),
        hoverinfo="none"
    )

    # --- MST (vert) ---
    mst_x, mst_y = [], []
    for u, v, w in mst_edges:
        mst_x += [G.nodes[u]['x'], G.nodes[v]['x'], None]
        mst_y += [G.nodes[u]['y'], G.nodes[v]['y'], None]

    mst_trace = go.Scatter(
        x=mst_x, y=mst_y,
        mode="lines",
        line=dict(width=6, color="green"),
        hoverinfo="none"
    )

    # --- Arête candidate (orange) ---
    if candidate is not None:
        u, v, w = candidate
        cand_trace = go.Scatter(
            x=[G.nodes[u]['x'], G.nodes[v]['x']],
            y=[G.nodes[u]['y'], G.nodes[v]['y']],
            mode="lines",
            line=dict(width=6, color="orange"),
            hoverinfo="none"
        )
    else:
        cand_trace = go.Scatter(x=[], y=[])

    # --- Arête courante acceptée (jaune) ---
    if current is not None:
        u, v, w = current
        cur_trace = go.Scatter(
            x=[G.nodes[u]['x'], G.nodes[v]['x']],
            y=[G.nodes[u]['y'], G.nodes[v]['y']],
            mode="lines",
            line=dict(width=7, color="yellow"),
            hoverinfo="none"
        )
    else:
        cur_trace = go.Scatter(x=[], y=[])

    # --- Nœuds (style harmonisé) ---
    node_x, node_y, labels, colors = [], [], [], []
    for n, data in G.nodes(data=True):
        node_x.append(data["x"])
        node_y.append(data["y"])
        labels.append(str(n))

        if n in visited_nodes:
            colors.append("#1E90FF")  # bleu vif
        else:
            colors.append("black")

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        text=labels,
        textposition="top center",
        marker=dict(
            size=28,
            color=colors,
            line=dict(width=3, color="white")
        ),
        textfont=dict(size=14, color="white", family="Arial Black"),
        hoverinfo="text"
    )

    fig = go.Figure([bg_edges, mst_trace, cand_trace, cur_trace, node_trace])
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=600,
        plot_bgcolor="lightblue",
        paper_bgcolor="lightblue"
    )

    return fig
