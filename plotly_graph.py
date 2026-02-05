import heapq
import plotly.graph_objects as go
import networkx as nx


# ---------------------------------------------------------
# Affichage simple du graphe
# ---------------------------------------------------------
def plot_graph_plotly(G, is_test_graph=False):

    if all('x' in G.nodes[n] and 'y' in G.nodes[n] for n in G.nodes()):
        pos = {n: (G.nodes[n]['x'], G.nodes[n]['y']) for n in G.nodes()}
    else:
        pos = nx.spring_layout(G, seed=42)

    edge_x, edge_y, edge_labels = [], [], []

    for u, v, data in G.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]

        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

        if is_test_graph and "length" in data:
            edge_labels.append(
                go.Scatter(
                    x=[(x0 + x1) / 2],
                    y=[(y0 + y1) / 2],
                    text=[str(data["length"])],
                    mode="text",
                    textfont=dict(size=14, color="black"),
                    hoverinfo="skip"
                )
            )

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode="lines",
        line=dict(width=1, color="#BBBBBB"),
        hoverinfo="none"
    )

    node_x, node_y = [], []
    for n in G.nodes():
        x, y = pos[n]
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text" if is_test_graph else "markers",
        text=[str(n) for n in G.nodes()] if is_test_graph else None,
        textposition="top center",
        marker=dict(
            size=22 if is_test_graph else 8,
            color="#1f77b4",
            line=dict(width=2 if is_test_graph else 0.5, color="black")
        ),
        hoverinfo="text"
    )

    fig = go.Figure([edge_trace, node_trace])
    for lbl in edge_labels:
        fig.add_trace(lbl)

    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="white"
    )

    return fig


# ---------------------------------------------------------
# Dijkstra étape par étape — VERSION FINALE
# ---------------------------------------------------------
def dijkstra_steps(G, start, end=None):
    dist = {start: 0}
    parent = {start: None}
    visited = set()
    pq = [(0, start)]

    while pq:
        current_dist, u = heapq.heappop(pq)

        if u in visited:
            continue
        visited.add(u)

        yield {
            "current": u,
            "dist": dict(dist),
            "parent": dict(parent),
            "visited": set(visited)
        }

        # Pour OSMnx (MultiDiGraph), on utilise G[u] pour les voisins sortants
        if u not in G: continue
        
        for v in G[u]:
            if v in visited: continue
            
            edge_data = G.get_edge_data(u, v)
            if edge_data:
                # On prend la plus courte arête entre u et v
                if isinstance(edge_data, dict):
                    weight = min(d.get('length', 1) for d in edge_data.values())
                else:
                    weight = edge_data.get('length', 1)
                
                new_dist = current_dist + weight
                if new_dist < dist.get(v, float('inf')):
                    dist[v] = new_dist
                    parent[v] = u
                    heapq.heappush(pq, (new_dist, v))

    yield {"current": None, "dist": dict(dist), "parent": dict(parent), "visited": set(visited)}


# ---------------------------------------------------------
# Graphe avec start / end
# ---------------------------------------------------------
def plot_graph_with_points(G, start_node, end_node, is_test_graph=False):

    if all('x' in G.nodes[n] and 'y' in G.nodes[n] for n in G.nodes()):
        pos = {n: (G.nodes[n]['x'], G.nodes[n]['y']) for n in G.nodes()}
    else:
        pos = nx.spring_layout(G, seed=42)

    edge_x, edge_y, edge_labels = [], [], []

    for u, v, data in G.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]

        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

        if is_test_graph and "length" in data:
            edge_labels.append(
                go.Scatter(
                    x=[(x0 + x1) / 2],
                    y=[(y0 + y1) / 2],
                    text=[str(data["length"])],
                    mode="text",
                    textfont=dict(size=14, color="black"),
                    hoverinfo="skip"
                )
            )

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode="lines",
        line=dict(width=1, color="#BBBBBB"),
        hoverinfo="none"
    )

    node_x, node_y, node_color = [], [], []

    for n in G.nodes():
        x, y = pos[n]
        node_x.append(x)
        node_y.append(y)

        if n == start_node:
            node_color.append("green")
        elif n == end_node:
            node_color.append("red")
        else:
            node_color.append("#1f77b4")

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text" if is_test_graph else "markers",
        text=[str(n) for n in G.nodes()] if is_test_graph else None,
        textposition="top center",
        marker=dict(
            size=22 if is_test_graph else 10,
            color=node_color,
            line=dict(width=2 if is_test_graph else 0.5, color="black")
        ),
        hoverinfo="text"
    )

    fig = go.Figure([edge_trace, node_trace])
    for lbl in edge_labels:
        fig.add_trace(lbl)

    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="white"
    )

    return fig


# ---------------------------------------------------------
# Étape Dijkstra – TOUS les nœuds
# ---------------------------------------------------------
def plot_dijkstra_step(G, step, start=None, end=None, is_test_graph=False):

    visited = step["visited"]
    current = step["current"]

    edge_x, edge_y = [], []
    for u, v in G.edges():
        edge_x += [G.nodes[u]['x'], G.nodes[v]['x'], None]
        edge_y += [G.nodes[u]['y'], G.nodes[v]['y'], None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode="lines",
        line=dict(width=1, color="#ddd"),
        hoverinfo="none"
    )

    node_x, node_y, node_color, node_size, labels = [], [], [], [], []

    for n in G.nodes():
        node_x.append(G.nodes[n]['x'])
        node_y.append(G.nodes[n]['y'])
        labels.append(str(n))

        if n == current:
            node_color.append("yellow")
            node_size.append(45)
        elif n == start:
            node_color.append("green")
            node_size.append(40)
        elif n == end:
            node_color.append("red")
            node_size.append(40)
        elif n in visited:
            node_color.append("blue")
            node_size.append(38)
        else:
            node_color.append("lightgray")
            node_size.append(35)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        text=labels if is_test_graph else None,
        textposition="middle center",
        marker=dict(size=node_size, color=node_color, line=dict(width=2, color="white")),
        textfont=dict(size=9, color="white", family="Arial Black"),
        hoverinfo="text"
    )

    fig = go.Figure([edge_trace, node_trace])
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=600
    )
    return fig


# ---------------------------------------------------------
# Étape Dijkstra – dynamique
# ---------------------------------------------------------
def plot_dijkstra_step_dynamic(G, step, start=None, end=None, is_test_graph=False):

    visited = step["visited"]
    current = step["current"]

    highlight = visited | {n for n in [start, end, current] if n is not None}

    all_edge_x, all_edge_y = [], []
    for u, v in G.edges():
        all_edge_x += [G.nodes[u]['x'], G.nodes[v]['x'], None]
        all_edge_y += [G.nodes[u]['y'], G.nodes[v]['y'], None]

    all_edge_trace = go.Scatter(
        x=all_edge_x, y=all_edge_y,
        mode="lines",
        line=dict(width=0.5, color="#e0e0e0"),
        hoverinfo="none"
    )

    node_x, node_y, node_color, node_size, labels = [], [], [], [], []

    for n in highlight:
        node_x.append(G.nodes[n]['x'])
        node_y.append(G.nodes[n]['y'])
        labels.append(str(n))

        if n == current:
            node_color.append("yellow")
            node_size.append(45)
        elif n == start:
            node_color.append("green")
            node_size.append(40)
        elif n == end:
            node_color.append("red")
            node_size.append(40)
        else:
            node_color.append("blue")
            node_size.append(38)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        text=labels if is_test_graph else None,
        textposition="middle center",
        marker=dict(size=node_size, color=node_color, line=dict(width=2, color="white")),
        textfont=dict(size=9, color="white", family="Arial Black"),
        hoverinfo="text"
    )

    fig = go.Figure([all_edge_trace, node_trace])
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=600
    )
    return fig


# ---------------------------------------------------------
# Chemin final
# ---------------------------------------------------------
def plot_final_path(G, step, start, end, is_test_graph=False):

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

    if not path or path[0] != start:
        return plot_dijkstra_step_dynamic(G, step, start, end, is_test_graph)

    all_edge_x, all_edge_y = [], []
    for u, v in G.edges():
        all_edge_x += [G.nodes[u]['x'], G.nodes[v]['x'], None]
        all_edge_y += [G.nodes[u]['y'], G.nodes[v]['y'], None]

    all_edge_trace = go.Scatter(
        x=all_edge_x, y=all_edge_y,
        mode="lines",
        line=dict(width=0.5, color="#e0e0e0"),
        hoverinfo="none"
    )

    path_edge_x, path_edge_y = [], []
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        path_edge_x += [G.nodes[u]['x'], G.nodes[v]['x'], None]
        path_edge_y += [G.nodes[u]['y'], G.nodes[v]['y'], None]

    path_trace = go.Scatter(
        x=path_edge_x, y=path_edge_y,
        mode="lines",
        line=dict(width=6, color="green"),
        hoverinfo="none"
    )

    node_x, node_y, node_color, node_size, labels = [], [], [], [], []

    for n in visited:
        if n not in G.nodes:
            continue

        node_x.append(G.nodes[n]['x'])
        node_y.append(G.nodes[n]['y'])
        labels.append(str(n))

        if n == start:
            node_color.append("green")
            node_size.append(45)
        elif n == end:
            node_color.append("red")
            node_size.append(45)
        elif n in path:
            node_color.append("lightgreen")
            node_size.append(40)
        else:
            node_color.append("lightblue")
            node_size.append(35)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        text=labels if is_test_graph else None,
        textposition="middle center",
        marker=dict(
            size=node_size,
            color=node_color,
            line=dict(width=2, color="white")
        ),
        textfont=dict(size=9, color="white", family="Arial Black"),
        hoverinfo="text"
    )

    fig = go.Figure([all_edge_trace, path_trace, node_trace])
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=600
    )

    return fig
