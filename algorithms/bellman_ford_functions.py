import math
import plotly.graph_objects as go
import networkx as nx

# ============================================================
# 1) Création du graphe Bellman-Ford (inchangé)
# ============================================================

def create_bellman_ford_graph():
    G = nx.DiGraph()

    positions = {
        "A": (0, 4),
        "B": (3, 5),
        "C": (6, 4),
        "D": (9, 5),
        "E": (0, 2),
        "F": (3, 1),
        "G": (6, 2),
        "H": (9, 1),
    }

    for n, (x, y) in positions.items():
        G.add_node(n, x=x, y=y)

    edges = [
        ("A", "B", 4), ("B", "C", 2), ("C", "D", -3),
        ("E", "F", 3), ("F", "G", -2), ("G", "H", 4),
        ("A", "E", 5), ("B", "F", -1), ("C", "G", 3), ("D", "H", 2),
        ("A", "F", 6), ("B", "G", 1), ("C", "H", 2),
        ("F", "B", 2), ("G", "C", 1),
    ]

    for u, v, w in edges:
        G.add_edge(u, v, length=w)

    return G


# ============================================================
# 2) Bellman-Ford (version corrigée avec itération 0)
# ============================================================

def bellman_ford_run(G, source, weight="length"):
    """
    Version corrigée :
    - Sauvegarde l'état initial (itération 0)
    - EXACTEMENT |V|-1 itérations de relaxation
    - Détection de cycle négatif
    - Retourne toutes les itérations pour la matrice
    """

    dist = {n: math.inf for n in G.nodes()}
    parent = {n: None for n in G.nodes()}
    dist[source] = 0.0

    # Liste des arêtes (u, v, w)
    edges = []
    for u, v, data in G.edges(data=True):
        w = float(data.get(weight, 1.0))
        edges.append((u, v, w))

    iterations = []
    n = len(G.nodes())

    # --- Sauvegarde de l'état initial (itération 0) ---
    iterations.append(dict(dist))

    # --- Relaxations : EXACTEMENT n-1 fois ---
    for iteration_num in range(n - 1):
        # Pour chaque itération, on relaxe toutes les arêtes
        for u, v, w in edges:
            if dist[u] != math.inf and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u

        # Snapshot après cette itération
        iterations.append(dict(dist))

    # --- Détection cycle négatif ---
    neg_cycle = False
    for u, v, w in edges:
        if dist[u] != math.inf and dist[u] + w < dist[v]:
            neg_cycle = True
            break

    return dist, parent, neg_cycle, iterations


# ============================================================
# 3) Reconstruction du chemin final (version améliorée)
# ============================================================

def reconstruct_path(parent, source, target):
    """
    Reconstruit le chemin source -> target.
    Retourne [] si aucun chemin.
    """
    if source == target:
        return [source]

    path = []
    cur = target
    seen = set()
    max_steps = len(parent) + 1  # Sécurité contre les boucles infinies

    while cur is not None and len(path) < max_steps:
        if cur in seen:
            return []  # Détection de cycle
        seen.add(cur)
        path.append(cur)
        if cur == source:
            break
        cur = parent.get(cur)

    path.reverse()
    
    # Vérifier que le chemin commence bien à la source
    if not path or path[0] != source:
        return []
    
    return path


# ============================================================
# 4) Visualisation finale (version corrigée)
# ============================================================

def plot_bellman_ford_final_path(G, step, source, target):
    """
    Affiche le graphe final avec :
    - Toutes les arêtes en gris clair
    - Le chemin optimal en orange épais
    - Les distances correctes affichées sur chaque nœud
    - Source en vert, cible en rouge
    """

    dist = step["dist"]
    parent = step["parent"]

    # --- Reconstruction du chemin ---
    path = reconstruct_path(parent, source, target)
    valid_path = (len(path) >= 2 and dist[target] != math.inf)

    def xy(n):
        return G.nodes[n]["x"], G.nodes[n]["y"]

    # --- Toutes les arêtes en arrière-plan ---
    all_edge_x, all_edge_y = [], []
    for u, v in G.edges():
        x0, y0 = xy(u)
        x1, y1 = xy(v)
        all_edge_x += [x0, x1, None]
        all_edge_y += [y0, y1, None]

    bg_edges = go.Scatter(
        x=all_edge_x, y=all_edge_y,
        mode="lines",
        line=dict(width=1.5, color="#A0A0A0"),
        hoverinfo="none",
        name="Arêtes"
    )

    # --- Arêtes du chemin optimal ---
    path_x, path_y = [], []
    if valid_path:
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            x0, y0 = xy(u)
            x1, y1 = xy(v)
            path_x += [x0, x1, None]
            path_y += [y0, y1, None]

    path_trace = go.Scatter(
        x=path_x, y=path_y,
        mode="lines",
        line=dict(width=7, color="orange"),
        hoverinfo="none",
        name="Chemin optimal"
    )

    # --- Poids des arêtes (optionnel, sur les arêtes du chemin) ---
    edge_labels = []
    if valid_path:
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            if G.has_edge(u, v):
                x0, y0 = xy(u)
                x1, y1 = xy(v)
                w = G[u][v].get('length', 0)
                edge_labels.append(
                    go.Scatter(
                        x=[(x0 + x1) / 2],
                        y=[(y0 + y1) / 2],
                        text=[f"{w:+.0f}"],
                        mode="text",
                        textfont=dict(size=14, color="darkred", family="Arial Black"),
                        hoverinfo="skip",
                        showlegend=False
                    )
                )

    # --- Nœuds avec distances ---
    node_x, node_y, node_color, node_size, labels = [], [], [], [], []

    for n in G.nodes():
        x, y = xy(n)
        node_x.append(x)
        node_y.append(y)

        d = dist.get(n, math.inf)
        
        # Label avec nom du nœud et distance
        if d != math.inf:
            label = f"{n}<br>{d:.1f}"
        else:
            label = f"{n}<br>∞"
        labels.append(label)

        # Couleurs et tailles selon le rôle du nœud
        if n == source:
            node_color.append("green")
            node_size.append(60)
        elif n == target:
            node_color.append("red")
            node_size.append(60)
        elif valid_path and n in path:
            node_color.append("orange")
            node_size.append(52)
        elif d != math.inf:
            node_color.append("#031E66")
            node_size.append(48)
        else:
            node_color.append("#444444")
            node_size.append(45)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        text=labels,
        textposition="middle center",
        marker=dict(
            size=node_size,
            color=node_color,
            line=dict(width=4, color="white")
        ),
        textfont=dict(size=12, color="white", family="Arial Black"),
        hoverinfo="text",
        name="Nœuds"
    )

    # --- Construction de la figure ---
    fig = go.Figure([bg_edges, path_trace, node_trace] + edge_labels)
    
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