import heapq
import plotly.graph_objects as go
import networkx as nx


def dfs_steps(G, start, end=None):
    """
    Générateur DFS étape par étape.
    Explore tout le graphe des métropoles (non OSMnx).
    """

    visited = set()
    parent = {start: None}
    stack = [start]

    while stack:
        u = stack.pop()

        if u in visited:
            continue

        visited.add(u)

        yield {
            "current": u,
            "visited": set(visited),
            "parent": dict(parent)
        }

        # Pas d'arrêt prématuré
        # if end is not None and u == end:
        #     break

        # DFS = on empile les voisins dans l'ordre inverse
        neighbors = list(G.neighbors(u))
        neighbors.reverse()

        for v in neighbors:
            if v not in visited:
                parent[v] = u
                stack.append(v)

    # Étape finale
    yield {
        "current": None,
        "visited": set(visited),
        "parent": dict(parent)
    }


def plot_dfs_step(G, step, start=None, end=None, is_test_graph=False):

    visited = step["visited"]
    current = step["current"]

    highlight = visited | {n for n in [start, end, current] if n is not None}

    # Arrière-plan
    all_edge_x, all_edge_y = [], []
    for u, v in G.edges():
        all_edge_x += [G.nodes[u]['x'], G.nodes[v]['x'], None]
        all_edge_y += [G.nodes[u]['y'], G.nodes[v]['y'], None]

    all_edge_trace = go.Scatter(
        x=all_edge_x, y=all_edge_y,
        mode="lines",
        line=dict(width=0.5, color="#444"),
        hoverinfo="none"
    )

    # Nœuds
    node_x, node_y, node_color, node_size, labels = [], [], [], [], []

    for n in highlight:
        node_x.append(G.nodes[n]['x'])
        node_y.append(G.nodes[n]['y'])
        labels.append(str(n))

        if n == current:
            node_color.append("yellow")
            node_size.append(55)
        elif n == start:
            node_color.append("green")
            node_size.append(50)
        elif n == end:
            node_color.append("red")
            node_size.append(50)
        else:
            node_color.append("blue")
            node_size.append(45)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        text=labels if is_test_graph else None,
        textposition="middle center",
        marker=dict(size=node_size, color=node_color, line=dict(width=4, color="white")),
        textfont=dict(size=10, color="white", family="Arial Black"),
        hoverinfo="text"
    )

    fig = go.Figure([all_edge_trace, node_trace])
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=600,
        plot_bgcolor="black",
        paper_bgcolor="black"
    )

    return fig


def plot_dfs_final_path(G, step, start, end, is_test_graph=False):

    parent = step["parent"]
    visited = step["visited"]

    # Reconstruction du chemin
    path = []
    current = end

    while current is not None:
        if current not in G.nodes:
            break
        path.append(current)
        current = parent.get(current)

    path.reverse()

    # Si pas de chemin → fallback
    if not path or path[0] != start:
        return plot_dfs_step(G, step, start, end, is_test_graph)

    # Arrière-plan
    all_edge_x, all_edge_y = [], []
    for u, v in G.edges():
        all_edge_x += [G.nodes[u]['x'], G.nodes[v]['x'], None]
        all_edge_y += [G.nodes[u]['y'], G.nodes[v]['y'], None]

    all_edge_trace = go.Scatter(
        x=all_edge_x, y=all_edge_y,
        mode="lines",
        line=dict(width=0.5, color="#444"),
        hoverinfo="none"
    )

    # Chemin final
    path_edge_x, path_edge_y = [], []
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        path_edge_x += [G.nodes[u]['x'], G.nodes[v]['x'], None]
        path_edge_y += [G.nodes[u]['y'], G.nodes[v]['y'], None]

    path_trace = go.Scatter(
        x=path_edge_x, y=path_edge_y,
        mode="lines",
        line=dict(width=6, color="orange"),
        hoverinfo="none"
    )

    # Nœuds
    node_x, node_y, node_color, node_size, labels = [], [], [], [], []

    for n in visited:
        node_x.append(G.nodes[n]['x'])
        node_y.append(G.nodes[n]['y'])
        labels.append(str(n))

        if n == start:
            node_color.append("green")
            node_size.append(55)
        elif n == end:
            node_color.append("red")
            node_size.append(55)
        elif n in path:
            node_color.append("orange")
            node_size.append(50)
        else:
            node_color.append("blue")
            node_size.append(45)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        text=labels if is_test_graph else None,
        textposition="middle center",
        marker=dict(size=node_size, color=node_color, line=dict(width=4, color="white")),
        textfont=dict(size=10, color="white", family="Arial Black"),
        hoverinfo="text"
    )

    fig = go.Figure([all_edge_trace, path_trace, node_trace])
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=600,
        plot_bgcolor="black",
        paper_bgcolor="black"
    )

    return fig
