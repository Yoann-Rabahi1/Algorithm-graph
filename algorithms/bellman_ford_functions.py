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
# 2) Bellman-Ford (version propre, EXACTEMENT n-1 itérations)
# ============================================================

def bellman_ford_run(G, source, weight="length"):
    """
    Version propre et standard :
    - EXACTEMENT |V|-1 itérations
    - pas d'early break
    - distances correctes
    - parent correct
    - détection cycle négatif
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

    # --- Relaxations : EXACTEMENT n-1 fois ---
    for _ in range(n - 1):
        for u, v, w in edges:
            if dist[u] != math.inf and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u

        # snapshot de l'itération
        iterations.append(dict(dist))

    # --- Détection cycle négatif ---
    neg_cycle = False
    for u, v, w in edges:
        if dist[u] != math.inf and dist[u] + w < dist[v]:
            neg_cycle = True
            break

    return dist, parent, neg_cycle, iterations


# ============================================================
# 3) Reconstruction du chemin final
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

    while cur is not None:
        if cur in seen:
            return []  # sécurité
        seen.add(cur)
        path.append(cur)
        if cur == source:
            break
        cur = parent.get(cur)

    path.reverse()
    if not path or path[0] != source:
        return []
    return path


# ============================================================
# 4) Visualisation finale (inchangée mais propre)
# ============================================================

def plot_bellman_ford_final_path(G, step, source, target):
    """
    Affiche le graphe final :
    - chemin final en orange
    - source en vert
    - cible en rouge
    - nœuds atteignables en bleu foncé
    """

    dist = step["dist"]
    parent = step["parent"]

    # --- Reconstruction du chemin ---
    path = reconstruct_path(parent, source, target)
    valid_path = (len(path) >= 2 and dist[target] != math.inf)

    def xy(n):
        return G.nodes[n]["x"], G.nodes[n]["y"]

    # --- Arrière-plan ---
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
        hoverinfo="none"
    )

    # --- Arêtes du chemin final ---
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
        hoverinfo="none"
    )

    # --- Nœuds ---
    node_x, node_y, node_color, node_size, labels = [], [], [], [], []

    for n in G.nodes():
        x, y = xy(n)
        node_x.append(x)
        node_y.append(y)

        d = dist.get(n, math.inf)
        label = f"{n}<br>dist={d:.2f}" if d != math.inf else f"{n}<br>dist=∞"
        labels.append(label)

        if n == source:
            node_color.append("green")
            node_size.append(55)
        elif n == target:
            node_color.append("red")
            node_size.append(55)
        elif valid_path and n in path:
            node_color.append("orange")
            node_size.append(50)
        elif d != math.inf:
            node_color.append("#031E66")
            node_size.append(45)
        else:
            node_color.append("black")
            node_size.append(40)

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
        hoverinfo="text"
    )

    fig = go.Figure([bg_edges, path_trace, node_trace])
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
