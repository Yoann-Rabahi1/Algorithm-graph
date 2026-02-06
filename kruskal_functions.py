import plotly.graph_objects as go

def kruskal_steps(G, weight="length"):
    """
    Générateur étape par étape pour Kruskal.
    Retourne :
    - current_edge : arête en cours d'examen
    - mst_edges : arêtes déjà ajoutées au MST
    - visited_edges : arêtes déjà traitées
    - parent, rank : structures union-find
    """

    # Tri des arêtes par poids
    edges = []
    for u, v, data in G.edges(data=True):
        w = data.get(weight, 1)
        edges.append((w, u, v))
    edges.sort()

    # Union-Find
    parent = {n: n for n in G.nodes()}
    rank = {n: 0 for n in G.nodes()}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(x, y):
        rx, ry = find(x), find(y)
        if rx == ry:
            return False
        if rank[rx] < rank[ry]:
            parent[rx] = ry
        elif rank[rx] > rank[ry]:
            parent[ry] = rx
        else:
            parent[ry] = rx
            rank[rx] += 1
        return True

    mst_edges = []
    visited_edges = []

    # Parcours des arêtes triées
    for w, u, v in edges:
        visited_edges.append((u, v, w))

        # Étape intermédiaire
        yield {
            "current_edge": (u, v, w),
            "mst_edges": list(mst_edges),
            "visited_edges": list(visited_edges),
            "parent": dict(parent),
            "rank": dict(rank)
        }

        # Ajout au MST si pas de cycle
        if union(u, v):
            mst_edges.append((u, v, w))

    # Étape finale
    yield {
        "current_edge": None,
        "mst_edges": list(mst_edges),
        "visited_edges": list(visited_edges),
        "parent": dict(parent),
        "rank": dict(rank)
    }


# ---------------------------------------------------------
# Affichage du MST final
# ---------------------------------------------------------
def plot_kruskal_mst(G, mst_edges):

    # Arrière-plan : toutes les arêtes
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

    # Labels des poids du MST
    weight_labels = []
    for u, v, w in mst_edges:
        x0, y0 = G.nodes[u]['x'], G.nodes[u]['y']
        x1, y1 = G.nodes[v]['x'], G.nodes[v]['y']
        weight_labels.append(
            go.Scatter(
                x=[(x0 + x1) / 2],
                y=[(y0 + y1) / 2],
                text=[str(w)],
                mode="text",
                textfont=dict(size=14, color="black", family="Arial Black"),
                hoverinfo="skip"
            )
        )

    # Arêtes MST
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

    # Nœuds + labels
    node_x, node_y, labels = [], [], []
    for n, data in G.nodes(data=True):
        node_x.append(data["x"])
        node_y.append(data["y"])
        labels.append(str(n))

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        text=labels,
        textposition="top center",
        marker=dict(
            size=22,
            color="black",
            line=dict(width=2, color="white")
        ),
        textfont=dict(size=12, color="white", family="Arial Black"),
        hoverinfo="text"
    )

    fig = go.Figure([bg_edges, mst_trace, node_trace] + weight_labels)
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


# ---------------------------------------------------------
# Affichage dynamique étape par étape
# ---------------------------------------------------------
def plot_kruskal_step(G, step):

    current = step["current_edge"]
    mst_edges = step["mst_edges"]
    visited = step["visited_edges"]

    # Arrière-plan
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

    # Poids des arêtes visitées
    weight_labels = []
    for u, v, w in visited:
        x0, y0 = G.nodes[u]['x'], G.nodes[u]['y']
        x1, y1 = G.nodes[v]['x'], G.nodes[v]['y']
        weight_labels.append(
            go.Scatter(
                x=[(x0 + x1) / 2],
                y=[(y0 + y1) / 2],
                text=[str(w)],
                mode="text",
                textfont=dict(size=14, color="black", family="Arial Black"),
                hoverinfo="skip"
            )
        )

    # Arêtes visitées (orange)
    vis_x, vis_y = [], []
    for u, v, w in visited:
        vis_x += [G.nodes[u]['x'], G.nodes[v]['x'], None]
        vis_y += [G.nodes[u]['y'], G.nodes[v]['y'], None]

    visited_trace = go.Scatter(
        x=vis_x, y=vis_y,
        mode="lines",
        line=dict(width=3, color="orange"),
        hoverinfo="none"
    )

    # Arêtes MST (vert)
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

    # Arête courante (jaune)
    if current is not None:
        u, v, w = current
        cur_trace = go.Scatter(
            x=[G.nodes[u]['x'], G.nodes[v]['x']],
            y=[G.nodes[u]['y'], G.nodes[v]['y']],
            mode="lines",
            line=dict(width=6, color="yellow"),
            hoverinfo="none"
        )
    else:
        cur_trace = go.Scatter(x=[], y=[])

    # Nœuds + labels
    node_x, node_y, labels = [], [], []
    for n, data in G.nodes(data=True):
        node_x.append(data["x"])
        node_y.append(data["y"])
        labels.append(str(n))

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        text=labels,
        textposition="top center",
        marker=dict(
            size=22,
            color="black",
            line=dict(width=2, color="white")
        ),
        textfont=dict(size=12, color="white", family="Arial Black"),
        hoverinfo="text"
    )

    fig = go.Figure([bg_edges, visited_trace, mst_trace, cur_trace, node_trace] + weight_labels)
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
