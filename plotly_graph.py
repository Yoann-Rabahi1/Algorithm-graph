import plotly.graph_objects as go
import heapq

# ---------------------------------------------------------
# Affichage simple du graphe (tous les nœuds visibles)
# ---------------------------------------------------------
def plot_graph_plotly(G):
    """
    Affiche le graphe complet avec tous les nœuds et arêtes
    """
    nodes = G.nodes(data=True)

    edge_x = []
    edge_y = []

    for u, v, data in G.edges(data=True):
        x0, y0 = G.nodes[u]['x'], G.nodes[u]['y']
        x1, y1 = G.nodes[v]['x'], G.nodes[v]['y']
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        line=dict(width=1, color="#888"),
        hoverinfo='none',
        mode='lines'
    )

    node_x = []
    node_y = []

    for node, data in nodes:
        node_x.append(data['x'])
        node_y.append(data['y'])

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode='markers',
        hoverinfo='text',
        marker=dict(color='blue', size=4)
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
# Dijkstra étape par étape (générateur) - Version OSMnx
# ---------------------------------------------------------
def dijkstra_steps(G, source, target=None):
    """
    Générateur qui yield chaque étape de l'algorithme de Dijkstra
    Compatible avec les MultiDiGraph d'OSMnx
    """
    import math
    
    dist = {node: float('inf') for node in G.nodes()}
    dist[source] = 0
    visited = set()
    pq = [(0, source)]
    parent = {}

    while pq:
        d, u = heapq.heappop(pq)

        if u in visited:
            continue

        visited.add(u)

        yield {
            "current": u,
            "dist": dist.copy(),
            "visited": visited.copy(),
            "parent": parent.copy()
        }

        # Arrêt si on a atteint la cible
        if target is not None and u == target:
            break

        # Parcours des voisins (successors pour DiGraph)
        for v in G.successors(u):
            # Gestion des MultiDiGraph : plusieurs arêtes possibles
            edges = G.get_edge_data(u, v)
            
            # Trouver le poids minimal parmi toutes les arêtes u->v
            min_weight = min(
                edge_data.get('length', 1)
                for edge_data in edges.values()
            )
            
            if dist[u] + min_weight < dist[v]:
                dist[v] = dist[u] + min_weight
                parent[v] = u
                heapq.heappush(pq, (dist[v], v))

    # Étape finale
    yield {
        "current": None,
        "dist": dist,
        "visited": visited,
        "parent": parent
    }


# ---------------------------------------------------------
# Affichage du graphe avec seulement start/end visibles
# ---------------------------------------------------------
def plot_graph_with_points(G, start=None, end=None):
    """
    Affiche le graphe complet en arrière-plan avec les points de départ et d'arrivée
    """
    # Arêtes (tout le graphe)
    edge_x = []
    edge_y = []

    for u, v in G.edges():
        x0, y0 = G.nodes[u]['x'], G.nodes[u]['y']
        x1, y1 = G.nodes[v]['x'], G.nodes[v]['y']
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line=dict(width=0.5, color="#ddd"),
        hoverinfo='none'
    )

    # Tous les nœuds (en gris très clair)
    all_node_x = []
    all_node_y = []
    
    for node, data in G.nodes(data=True):
        all_node_x.append(data['x'])
        all_node_y.append(data['y'])
    
    all_nodes_trace = go.Scatter(
        x=all_node_x,
        y=all_node_y,
        mode='markers',
        marker=dict(size=2, color="#eee"),
        hoverinfo='none'
    )

    # Points de départ et d'arrivée (en surbrillance)
    point_x = []
    point_y = []
    point_color = []
    point_text = []

    if start is not None:
        point_x.append(G.nodes[start]['x'])
        point_y.append(G.nodes[start]['y'])
        point_color.append("green")
        point_text.append("Départ")

    if end is not None:
        point_x.append(G.nodes[end]['x'])
        point_y.append(G.nodes[end]['y'])
        point_color.append("red")
        point_text.append("Arrivée")

    point_trace = go.Scatter(
        x=point_x,
        y=point_y,
        mode='markers+text',
        marker=dict(size=14, color=point_color, line=dict(width=2, color='white')),
        text=point_text,
        textposition="top center",
        textfont=dict(size=12, color='black'),
        hoverinfo='none'
    )

    fig = go.Figure([edge_trace, all_nodes_trace, point_trace])
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=600
    )
    return fig


# ---------------------------------------------------------
# Affichage d'une étape de Dijkstra (tous les nœuds)
# ---------------------------------------------------------
def plot_dijkstra_step(G, step, start=None, end=None):
    """
    Affiche tous les nœuds avec coloration selon leur état
    """
    visited = step["visited"]
    parent = step["parent"]
    current = step["current"]

    edge_x = []
    edge_y = []

    for u, v in G.edges():
        x0, y0 = G.nodes[u]['x'], G.nodes[u]['y']
        x1, y1 = G.nodes[v]['x'], G.nodes[v]['y']
        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode='lines',
        line=dict(width=1, color="#ddd"),
        hoverinfo='none'
    )

    node_x = []
    node_y = []
    node_color = []
    node_size = []

    for node, data in G.nodes(data=True):
        node_x.append(data['x'])
        node_y.append(data['y'])

        if node == current:
            node_color.append("yellow")
            node_size.append(10)
        elif node == start:
            node_color.append("green")
            node_size.append(10)
        elif node == end:
            node_color.append("red")
            node_size.append(10)
        elif node in visited:
            node_color.append("blue")
            node_size.append(6)
        else:
            node_color.append("lightgray")
            node_size.append(4)

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers',
        marker=dict(size=node_size, color=node_color),
        hoverinfo='none'
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
# Affichage dynamique (seulement nœuds visités)
# ---------------------------------------------------------
def plot_dijkstra_step_dynamic(G, step, start=None, end=None):
    """
    Affiche le graphe complet en arrière-plan avec seulement les nœuds visités en surbrillance
    """
    visited = step["visited"]
    parent = step["parent"]
    current = step["current"]
    
    # Ensemble des nœuds à mettre en surbrillance
    nodes_to_highlight = visited.copy()
    if start is not None:
        nodes_to_highlight.add(start)
    if end is not None:
        nodes_to_highlight.add(end)
    if current is not None:
        nodes_to_highlight.add(current)
    
    # TOUTES les arêtes du graphe (en gris très clair)
    all_edge_x = []
    all_edge_y = []
    
    for u, v in G.edges():
        x0, y0 = G.nodes[u]['x'], G.nodes[u]['y']
        x1, y1 = G.nodes[v]['x'], G.nodes[v]['y']
        all_edge_x += [x0, x1, None]
        all_edge_y += [y0, y1, None]
    
    all_edge_trace = go.Scatter(
        x=all_edge_x, y=all_edge_y,
        mode='lines',
        line=dict(width=0.5, color="#e0e0e0"),
        hoverinfo='none'
    )
    
    # TOUS les nœuds du graphe (en gris très clair)
    all_node_x = []
    all_node_y = []
    
    for node, data in G.nodes(data=True):
        all_node_x.append(data['x'])
        all_node_y.append(data['y'])
    
    all_nodes_trace = go.Scatter(
        x=all_node_x,
        y=all_node_y,
        mode='markers',
        marker=dict(size=2, color="#f0f0f0"),
        hoverinfo='none'
    )
    
    # Arêtes visitées (celles qui connectent des nœuds visités) - en couleur
    visited_edge_x = []
    visited_edge_y = []
    
    for u, v in G.edges():
        if u in nodes_to_highlight and v in nodes_to_highlight:
            x0, y0 = G.nodes[u]['x'], G.nodes[u]['y']
            x1, y1 = G.nodes[v]['x'], G.nodes[v]['y']
            visited_edge_x += [x0, x1, None]
            visited_edge_y += [y0, y1, None]
    
    visited_edge_trace = go.Scatter(
        x=visited_edge_x, y=visited_edge_y,
        mode='lines',
        line=dict(width=2, color="#aaa"),
        hoverinfo='none'
    )
    
    # Nœuds visités (en surbrillance)
    node_x = []
    node_y = []
    node_color = []
    node_size = []
    
    for node in nodes_to_highlight:
        data = G.nodes[node]
        node_x.append(data['x'])
        node_y.append(data['y'])
        
        # Coloration selon le rôle du nœud
        if node == current:
            node_color.append("yellow")
            node_size.append(14)
        elif node == start:
            node_color.append("green")
            node_size.append(14)
        elif node == end:
            node_color.append("red")
            node_size.append(14)
        elif node in visited:
            node_color.append("blue")
            node_size.append(8)
        else:
            node_color.append("gray")
            node_size.append(6)
    
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers',
        marker=dict(size=node_size, color=node_color, line=dict(width=1, color='white')),
        hoverinfo='none'
    )
    
    fig = go.Figure([all_edge_trace, all_nodes_trace, visited_edge_trace, node_trace])
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=600
    )
    return fig


# ---------------------------------------------------------
# Affichage du chemin final
# ---------------------------------------------------------
def plot_final_path(G, step, start, end):
    """
    Affiche le graphe complet avec le chemin final trouvé par Dijkstra
    """
    visited = step["visited"]
    parent = step["parent"]
    
    # Reconstruire le chemin
    path = []
    current_node = end
    while current_node is not None:
        path.append(current_node)
        current_node = parent.get(current_node)
    path.reverse()
    
    # Vérifier que le chemin est valide
    if len(path) == 0 or path[0] != start:
        # Pas de chemin trouvé, afficher juste les nœuds visités
        return plot_dijkstra_step_dynamic(G, step, start, end)
    
    # TOUTES les arêtes du graphe (en gris très clair)
    all_edge_x = []
    all_edge_y = []
    
    for u, v in G.edges():
        x0, y0 = G.nodes[u]['x'], G.nodes[u]['y']
        x1, y1 = G.nodes[v]['x'], G.nodes[v]['y']
        all_edge_x += [x0, x1, None]
        all_edge_y += [y0, y1, None]
    
    all_edge_trace = go.Scatter(
        x=all_edge_x, y=all_edge_y,
        mode='lines',
        line=dict(width=0.5, color="#e0e0e0"),
        hoverinfo='none'
    )
    
    # TOUS les nœuds du graphe (en gris très clair)
    all_node_x = []
    all_node_y = []
    
    for node, data in G.nodes(data=True):
        all_node_x.append(data['x'])
        all_node_y.append(data['y'])
    
    all_nodes_trace = go.Scatter(
        x=all_node_x,
        y=all_node_y,
        mode='markers',
        marker=dict(size=2, color="#f0f0f0"),
        hoverinfo='none'
    )
    
    # Arêtes du chemin (en vert épais)
    path_edge_x = []
    path_edge_y = []
    
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        x0, y0 = G.nodes[u]['x'], G.nodes[u]['y']
        x1, y1 = G.nodes[v]['x'], G.nodes[v]['y']
        path_edge_x += [x0, x1, None]
        path_edge_y += [y0, y1, None]
    
    path_edge_trace = go.Scatter(
        x=path_edge_x, y=path_edge_y,
        mode='lines',
        line=dict(width=6, color="green"),
        hoverinfo='none'
    )
    
    # Nœuds visités (en surbrillance)
    visited_node_x = []
    visited_node_y = []
    visited_node_color = []
    visited_node_size = []
    
    for node in visited:
        data = G.nodes[node]
        visited_node_x.append(data['x'])
        visited_node_y.append(data['y'])
        
        if node == start:
            visited_node_color.append("green")
            visited_node_size.append(16)
        elif node == end:
            visited_node_color.append("red")
            visited_node_size.append(16)
        elif node in path:
            visited_node_color.append("lightgreen")
            visited_node_size.append(10)
        else:
            visited_node_color.append("lightblue")
            visited_node_size.append(6)
    
    visited_node_trace = go.Scatter(
        x=visited_node_x,
        y=visited_node_y,
        mode='markers',
        marker=dict(size=visited_node_size, color=visited_node_color, line=dict(width=1, color='white')),
        hoverinfo='none'
    )
    
    fig = go.Figure([all_edge_trace, all_nodes_trace, path_edge_trace, visited_node_trace])
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=600
    )
    return fig