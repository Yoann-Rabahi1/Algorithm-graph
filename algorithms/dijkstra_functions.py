import heapq
import plotly.graph_objects as go
import networkx as nx
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
    """Reconstruit le chemin de source à target"""
    path = []
    u = target

    while u is not None:
        path.append(u)
        u = prev[u]

    path.reverse()

    if path and path[0] == source:
        return path
    return []


# ---------------------------------------------------------
# Dijkstra étape par étape — VERSION COMPLÈTE
# ---------------------------------------------------------
def dijkstra_steps(G, start, end=None):
    """
    Générateur Dijkstra étape par étape.
    Sauvegarde toutes les distances à chaque itération pour la matrice.
    """
    dist = {start: 0}
    parent = {start: None}
    visited = set()
    pq = [(0, start)]
    
    # Historique des distances pour la matrice
    iterations = []
    
    # État initial
    iterations.append(dict(dist))

    while pq:
        current_dist, u = heapq.heappop(pq)

        if u in visited:
            continue
        visited.add(u)

        yield {
            "current": u,
            "dist": dict(dist),
            "parent": dict(parent),
            "visited": set(visited),
            "iterations": list(iterations)
        }

        # Pour OSMnx (MultiDiGraph), on utilise G[u] pour les voisins sortants
        if u not in G: 
            continue
        
        for v in G[u]:
            if v in visited: 
                continue
            
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
        
        # Sauvegarder l'état après traitement du nœud
        iterations.append(dict(dist))

    yield {
        "current": None, 
        "dist": dict(dist), 
        "parent": dict(parent), 
        "visited": set(visited),
        "iterations": list(iterations)
    }


def dijkstra_complete(G, start, end=None):
    """
    Version complète (non-itérative) de Dijkstra.
    Retourne dist, parent, et toutes les itérations pour la matrice.
    """
    dist = {start: 0}
    parent = {start: None}
    visited = set()
    pq = [(0, start)]
    
    iterations = []
    iterations.append(dict(dist))

    while pq:
        current_dist, u = heapq.heappop(pq)

        if u in visited:
            continue
        visited.add(u)

        if u not in G:
            continue
        
        for v in G[u]:
            if v in visited:
                continue
            
            edge_data = G.get_edge_data(u, v)
            if edge_data:
                if isinstance(edge_data, dict):
                    weight = min(d.get('length', 1) for d in edge_data.values())
                else:
                    weight = edge_data.get('length', 1)
                
                new_dist = current_dist + weight
                if new_dist < dist.get(v, float('inf')):
                    dist[v] = new_dist
                    parent[v] = u
                    heapq.heappush(pq, (new_dist, v))
        
        iterations.append(dict(dist))

    return dist, parent, visited, iterations


# ---------------------------------------------------------
# Étape Dijkstra — TOUS les nœuds
# ---------------------------------------------------------
def plot_dijkstra_step(G, step, start=None, end=None, is_test_graph=False):

    visited = step["visited"]
    current = step["current"]
    
    # Fonction pour obtenir les coordonnées (OSMnx ou graphe de test)
    def get_coords(node):
        if 'x' in G.nodes[node] and 'y' in G.nodes[node]:
            return G.nodes[node]['x'], G.nodes[node]['y']
        elif 'x' in G.nodes[node]:  # OSMnx utilise x=longitude, y=latitude
            return G.nodes[node]['x'], G.nodes[node]['y']
        else:
            return 0, 0

    edge_x, edge_y = [], []
    for u, v in G.edges():
        ux, uy = get_coords(u)
        vx, vy = get_coords(v)
        edge_x += [ux, vx, None]
        edge_y += [uy, vy, None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode="lines",
        line=dict(width=1, color="#ddd"),
        hoverinfo="none"
    )

    node_x, node_y, node_color, node_size, labels = [], [], [], [], []

    for n in G.nodes():
        nx_coord, ny_coord = get_coords(n)
        node_x.append(nx_coord)
        node_y.append(ny_coord)
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
# Étape Dijkstra — dynamique
# ---------------------------------------------------------
def plot_dijkstra_step_dynamic(G, step, start=None, end=None, is_test_graph=False):

    visited = step["visited"]
    current = step["current"]

    highlight = visited | {n for n in [start, end, current] if n is not None}
    
    # Fonction pour obtenir les coordonnées
    def get_coords(node):
        if 'x' in G.nodes[node] and 'y' in G.nodes[node]:
            return G.nodes[node]['x'], G.nodes[node]['y']
        else:
            return 0, 0

    all_edge_x, all_edge_y = [], []
    for u, v in G.edges():
        ux, uy = get_coords(u)
        vx, vy = get_coords(v)
        all_edge_x += [ux, vx, None]
        all_edge_y += [uy, vy, None]

    all_edge_trace = go.Scatter(
        x=all_edge_x, y=all_edge_y,
        mode="lines",
        line=dict(width=0.5, color="#e0e0e0"),
        hoverinfo="none"
    )

    node_x, node_y, node_color, node_size, labels = [], [], [], [], []

    for n in highlight:
        nx_coord, ny_coord = get_coords(n)
        node_x.append(nx_coord)
        node_y.append(ny_coord)
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
# Chemin final — VERSION AMÉLIORÉE
# ---------------------------------------------------------
def plot_final_path_dijkstra(G, step, start, end, is_test_graph=False):
    """
    Affiche le graphe final avec :
    - Chemin optimal en orange
    - Distances affichées sur les nœuds
    - Poids des arêtes du chemin
    """

    parent = step["parent"]
    visited = step["visited"]
    dist = step["dist"]

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

    valid_path = len(path) >= 2

    # Fonction pour obtenir les coordonnées
    def xy(n):
        if 'x' in G.nodes[n] and 'y' in G.nodes[n]:
            return G.nodes[n]['x'], G.nodes[n]['y']
        else:
            return 0, 0

    # --- Toutes les arêtes en arrière-plan ---
    all_edge_x, all_edge_y = [], []
    for u, v in G.edges():
        x0, y0 = xy(u)
        x1, y1 = xy(v)
        all_edge_x += [x0, x1, None]
        all_edge_y += [y0, y1, None]

    all_edge_trace = go.Scatter(
        x=all_edge_x, y=all_edge_y,
        mode="lines",
        line=dict(width=1.5, color="#A0A0A0"),
        hoverinfo="none"
    )

    # --- Arêtes du chemin optimal ---
    path_edge_x, path_edge_y = [], []
    if valid_path:
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            x0, y0 = xy(u)
            x1, y1 = xy(v)
            path_edge_x += [x0, x1, None]
            path_edge_y += [y0, y1, None]

    path_trace = go.Scatter(
        x=path_edge_x, y=path_edge_y,
        mode="lines",
        line=dict(width=7, color="orange"),
        hoverinfo="none"
    )

    # --- Poids des arêtes du chemin (optionnel) ---
    edge_labels = []
    if valid_path and is_test_graph:
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            if G.has_edge(u, v):
                x0, y0 = xy(u)
                x1, y1 = xy(v)
                edge_data = G.get_edge_data(u, v)
                if isinstance(edge_data, dict):
                    w = min(d.get('length', 1) for d in edge_data.values())
                else:
                    w = edge_data.get('length', 1)
                
                edge_labels.append(
                    go.Scatter(
                        x=[(x0 + x1) / 2],
                        y=[(y0 + y1) / 2],
                        text=[f"{w:.0f}"],
                        mode="text",
                        textfont=dict(size=14, color="darkred", family="Arial Black"),
                        hoverinfo="skip",
                        showlegend=False
                    )
                )

    # --- Nœuds avec distances ---
    node_x, node_y, node_color, node_size, labels = [], [], [], [], []

    for n in visited:
        if n not in G.nodes:
            continue

        x, y = xy(n)
        node_x.append(x)
        node_y.append(y)

        # Distance depuis le départ
        d = dist.get(n, math.inf)
        
        # Label avec nom du nœud et distance
        if is_test_graph:
            if d != math.inf:
                labels.append(f"{n}<br>{d:.0f}")
            else:
                labels.append(f"{n}<br>∞")
        else:
            labels.append(str(n))

        # Couleurs et tailles
        if n == start:
            node_color.append("green")
            node_size.append(60)
        elif n == end:
            node_color.append("red")
            node_size.append(60)
        elif n in path:
            node_color.append("orange")
            node_size.append(55)
        elif d != math.inf:
            node_color.append("#031E66")
            node_size.append(50)
        else:
            node_color.append("#444444")
            node_size.append(48)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text" if is_test_graph else "markers",
        text=labels if is_test_graph else None,
        textposition="middle center",
        marker=dict(
            size=node_size,
            color=node_color,
            line=dict(width=4, color="white")
        ),
        textfont=dict(size=12, color="white", family="Arial Black"),
        hoverinfo="text"
    )

    # --- Construction de la figure ---
    fig = go.Figure([all_edge_trace, path_trace, node_trace] + edge_labels)
    
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="lightblue",
        paper_bgcolor="lightblue",
        height=650
    )

    return fig