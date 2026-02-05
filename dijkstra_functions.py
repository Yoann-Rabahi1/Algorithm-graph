import heapq
import plotly.graph_objects as go
import networkx as nx

import heapq
import math


def dijkstra_osmnx(G, source, target=None, weight="length"):
    """
    Dijkstra adapté à un graphe OSMnx (MultiDiGraph).
    
    Parameters
    ----------
    G : networkx.MultiDiGraph
    source : int
        Node ID de départ
    target : int, optional
        Node ID d'arrivée
    weight : str
        Attribut utilisé comme poids (ex: 'length')

    Returns
    -------
    dist : dict
        Distance minimale depuis source
    prev : dict
        Prédécesseur de chaque node
    """

    # Initialisation
    dist = {node: math.inf for node in G.nodes}
    prev = {node: None for node in G.nodes}
    dist[source] = 0

    # File de priorité
    pq = [(0, source)]

    while pq:
        current_dist, u = heapq.heappop(pq)

        # Optimisation
        if current_dist > dist[u]:
            continue

        # Arrêt anticipé
        if target is not None and u == target:
            break

        # Parcours des voisins sortants
        for v in G.successors(u):
            # Plusieurs arêtes possibles u -> v
            edges = G.get_edge_data(u, v)

            # poids minimal entre u et v
            min_weight = min(
                edge_data.get(weight, math.inf)
                for edge_data in edges.values()
            )

            alt = dist[u] + min_weight

            if alt < dist[v]:
                dist[v] = alt
                prev[v] = u
                heapq.heappush(pq, (alt, v))

    return dist, prev


def reconstruct_path(prev, source, target):
    path = []
    u = target

    while u is not None:
        path.append(u)
        u = prev[u]

    path.reverse()

    if path[0] == source:
        return path
    return []


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
            node_size.append(55)
        elif n == start:
            node_color.append("green")
            node_size.append(50)
        elif n == end:
            node_color.append("red")
            node_size.append(50)
        else:
            node_color.append("blue")
            node_size.append(48)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        text=labels if is_test_graph else None,
        textposition="middle center",
        marker=dict(size=node_size, color=node_color, line=dict(width=2, color="white")),
        textfont=dict(size=11, color="white", family="Arial Black"),
        hoverinfo="text"
    )

    fig = go.Figure([all_edge_trace, node_trace])
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="lightblue",
        height=600
    )
    return fig


# ---------------------------------------------------------
# Chemin final
# ---------------------------------------------------------


def plot_final_path_dijkstra(G, step, start, end, is_test_graph=False):

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
        line=dict(width=3, color="#e0e0e0"),
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
            node_size.append(55)
        elif n == end:
            node_color.append("red")
            node_size.append(55)
        elif n in path:
            node_color.append("lightgreen")
            node_size.append(55)
        else:
            node_color.append("black")
            node_size.append(55)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        text=labels if is_test_graph else None,
        textposition="middle center",
        marker=dict(
            size=node_size,
            color=node_color,
            line=dict(width=4, color="white")
        ),
        textfont=dict(size=11, color="white", family="Arial Black"),
        hoverinfo="text"
    )

    fig = go.Figure([all_edge_trace, path_trace, node_trace])
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="lightblue",
        height=600
    )

    return fig
