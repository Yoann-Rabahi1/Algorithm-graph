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
def plot_kruskal_mst(G, mst_edges, is_test_graph=False):

    # Fonction sécurisée pour récupérer les coordonnées
    def xy(n):
        if n in G.nodes and 'x' in G.nodes[n] and 'y' in G.nodes[n]:
            return G.nodes[n]['x'], G.nodes[n]['y']
        return None, None

    # --- Arrière-plan ---
    all_edge_x, all_edge_y = [], []
    for u, v in G.edges():
        x0, y0 = xy(u)
        x1, y1 = xy(v)
        if x0 is None or x1 is None:
            continue
        all_edge_x += [x0, x1, None]
        all_edge_y += [y0, y1, None]

    bg_edges = go.Scatter(
        x=all_edge_x, y=all_edge_y,
        mode="lines",
        line=dict(width=1.5, color="#A0A0A0"),
        hoverinfo="none"
    )

    # --- Arêtes MST ---
    mst_x, mst_y = [], []
    weight_labels = []

    for u, v, w in mst_edges:
        x0, y0 = xy(u)
        x1, y1 = xy(v)
        if x0 is None or x1 is None:
            continue

        mst_x += [x0, x1, None]
        mst_y += [y0, y1, None]

        if is_test_graph:
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

    mst_trace = go.Scatter(
        x=mst_x, y=mst_y,
        mode="lines",
        line=dict(width=6, color="green"),
        hoverinfo="none"
    )

    # --- Nœuds ---
    node_x, node_y, labels, node_color, node_size = [], [], [], [], []

    for n in G.nodes():
        x, y = xy(n)
        if x is None:
            continue

        node_x.append(x)
        node_y.append(y)
        labels.append(str(n))

        node_color.append("black" if n not in {u for u, v, w in mst_edges} else "green")

        node_size.append(22 if is_test_graph else 10)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text" if is_test_graph else "markers",
        text=labels if is_test_graph else None,
        textposition="top center",
        marker=dict(size=node_size, color=node_color, line=dict(width=2, color="white")),
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
def plot_kruskal_step(G, step, is_test_graph=False):

    current = step["current_edge"]
    mst_edges = step["mst_edges"]
    visited = step["visited_edges"]

    # Fonction sécurisée
    def xy(n):
        if n in G.nodes and 'x' in G.nodes[n] and 'y' in G.nodes[n]:
            return G.nodes[n]['x'], G.nodes[n]['y']
        return None, None

    # --- Arrière-plan ---
    all_edge_x, all_edge_y = [], []
    for u, v in G.edges():
        x0, y0 = xy(u)
        x1, y1 = xy(v)
        if x0 is None or x1 is None:
            continue
        all_edge_x += [x0, x1, None]
        all_edge_y += [y0, y1, None]

    bg_edges = go.Scatter(
        x=all_edge_x, y=all_edge_y,
        mode="lines",
        line=dict(width=1.5, color="#A0A0A0"),
        hoverinfo="none"
    )

    # --- Arêtes visitées ---
    vis_x, vis_y = [], []
    weight_labels = []

    for u, v, w in visited:
        x0, y0 = xy(u)
        x1, y1 = xy(v)
        if x0 is None or x1 is None:
            continue

        vis_x += [x0, x1, None]
        vis_y += [y0, y1, None]

        if is_test_graph:
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

    visited_trace = go.Scatter(
        x=vis_x, y=vis_y,
        mode="lines",
        line=dict(width=3, color="orange"),
        hoverinfo="none"
    )

    # --- Arêtes MST ---
    mst_x, mst_y = [], []
    for u, v, w in mst_edges:
        x0, y0 = xy(u)
        x1, y1 = xy(v)
        if x0 is None or x1 is None:
            continue
        mst_x += [x0, x1, None]
        mst_y += [y0, y1, None]

    mst_trace = go.Scatter(
        x=mst_x, y=mst_y,
        mode="lines",
        line=dict(width=6, color="green"),
        hoverinfo="none"
    )

    # --- Arête courante ---
    if current is not None:
        u, v, w = current
        x0, y0 = xy(u)
        x1, y1 = xy(v)
        if x0 is not None and x1 is not None:
            cur_trace = go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                mode="lines",
                line=dict(width=6, color="yellow"),
                hoverinfo="none"
            )
        else:
            cur_trace = go.Scatter(x=[], y=[])
    else:
        cur_trace = go.Scatter(x=[], y=[])

    # --- Nœuds ---
    node_x, node_y, labels, colors, node_size = [], [], [], [], []

    visited_nodes = {u for u, v, w in mst_edges} | {v for u, v, w in mst_edges}

    for n in G.nodes():
        x, y = xy(n)
        if x is None:
            continue

        node_x.append(x)
        node_y.append(y)
        labels.append(str(n))

        colors.append("#1E90FF" if n in visited_nodes else "black")

        node_size.append(28 if is_test_graph else 10)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text" if is_test_graph else "markers",
        text=labels if is_test_graph else None,
        textposition="top center",
        marker=dict(size=node_size, color=colors, line=dict(width=3, color="white")),
        textfont=dict(size=14, color="white", family="Arial Black"),
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
