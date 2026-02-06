import math
import plotly.graph_objects as go

import networkx as nx

def create_bellman_ford_graph():
    """
    Graphe Bellman-Ford réduit à 8 nœuds :
    - poids positifs et négatifs
    - aucun cycle négatif
    - coordonnées x,y pour affichage Plotly
    """

    G = nx.DiGraph()

    # --- Positions des nœuds ---
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

    # --- Arêtes pondérées ---
    edges = [
        # Ligne du haut
        ("A", "B", 4),
        ("B", "C", 2),
        ("C", "D", -3),

        # Ligne du bas
        ("E", "F", 3),
        ("F", "G", -2),
        ("G", "H", 4),

        # Connexions verticales
        ("A", "E", 5),
        ("B", "F", -1),
        ("C", "G", 3),
        ("D", "H", 2),

        # Connexions diagonales
        ("A", "F", 6),
        ("B", "G", 1),
        ("C", "H", 2),

        # Retour contrôlé (pas de cycle négatif)
        ("F", "B", 2),
        ("G", "C", 1),
    ]

    for u, v, w in edges:
        G.add_edge(u, v, length=w)

    return G


def bellman_ford_steps(G, source, weight="length"):
    """
    Générateur Bellman Ford.
    step dict:
      - phase: "init" | "relax" | "check" | "final"
      - iter: numéro d'itération (0..|V|-1)
      - edge: (u,v,w) arête testée
      - updated: bool (si relaxation a amélioré dist[v])
      - dist: dict
      - parent: dict
      - neg_cycle: bool (si détecté)
    Hypothèses:
      - G est un DiGraph ou MultiDiGraph ou Graph
      - poids dans data[weight], sinon 1
    """
    # distances
    dist = {n: math.inf for n in G.nodes()}
    parent = {n: None for n in G.nodes()}
    dist[source] = 0.0

    # on fabrique une liste d'arêtes (u, v, w)
    edges = []
    is_multi = hasattr(G, "is_multigraph") and G.is_multigraph()
    if is_multi:
        for u, v, k, data in G.edges(keys=True, data=True):
            w = float(data.get(weight, 1.0))
            edges.append((u, v, w))
    else:
        for u, v, data in G.edges(data=True):
            w = float(data.get(weight, 1.0))
            edges.append((u, v, w))

    yield {
        "phase": "init",
        "iter": 0,
        "edge": None,
        "updated": False,
        "dist": dict(dist),
        "parent": dict(parent),
        "neg_cycle": False
    }

    n = len(G.nodes())
    # relaxations
    for it in range(1, n):
        changed = False
        for (u, v, w) in edges:
            updated = False
            if dist[u] != math.inf and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u
                updated = True
                changed = True

            yield {
                "phase": "relax",
                "iter": it,
                "edge": (u, v, w),
                "updated": updated,
                "dist": dict(dist),
                "parent": dict(parent),
                "neg_cycle": False
            }

        if not changed:
            break

    # check negative cycle
    neg_cycle = False
    for (u, v, w) in edges:
        updated = False
        if dist[u] != math.inf and dist[u] + w < dist[v]:
            updated = True
            neg_cycle = True

        yield {
            "phase": "check",
            "iter": n,
            "edge": (u, v, w),
            "updated": updated,
            "dist": dict(dist),
            "parent": dict(parent),
            "neg_cycle": neg_cycle
        }

        if neg_cycle:
            break

    yield {
        "phase": "final",
        "iter": n,
        "edge": None,
        "updated": False,
        "dist": dict(dist),
        "parent": dict(parent),
        "neg_cycle": neg_cycle
    }


def plot_bellman_ford_step(G, step, source=None, target=None, show_all_nodes=False):
    """
    Version harmonisée avec le style global du projet :
    - Arêtes grises épaisses
    - Nœuds noirs / bleus / verts / rouges avec bord blanc
    - Arête courante colorée (jaune / vert / rouge)
    - Distances affichées proprement
    """

    def xy(n):
        d = G.nodes[n]
        return d["x"], d["y"]

    phase = step.get("phase")
    current_edge = step.get("edge")
    updated = step.get("updated", False)
    dist = step.get("dist", {})

    # --- ARRIÈRE-PLAN : arêtes ---
    ex, ey = [], []
    for u, v in G.edges():
        x0, y0 = xy(u)
        x1, y1 = xy(v)
        ex += [x0, x1, None]
        ey += [y0, y1, None]

    bg_edges = go.Scatter(
        x=ex, y=ey,
        mode="lines",
        line=dict(width=1.5, color="#A0A0A0"),
        hoverinfo="none"
    )

    # --- NŒUDS ---
    node_x, node_y, node_color, node_size, node_text = [], [], [], [], []

    nodes_to_draw = (
        list(G.nodes()) if show_all_nodes
        else [n for n in G.nodes() if dist.get(n, math.inf) != math.inf]
    )

    # Toujours inclure source et target
    if source not in nodes_to_draw:
        nodes_to_draw.append(source)
    if target not in nodes_to_draw:
        nodes_to_draw.append(target)

    for n in nodes_to_draw:
        x, y = xy(n)
        node_x.append(x)
        node_y.append(y)

        d = dist.get(n, math.inf)
        label = f"{n}<br>dist={d:.2f}" if d != math.inf else f"{n}<br>dist=∞"
        node_text.append(label)

        # Couleurs harmonisées
        if n == source:
            node_color.append("green")
            node_size.append(55)
        elif n == target:
            node_color.append("red")
            node_size.append(55)
        elif d != math.inf:
            node_color.append("#031E66")  # bleu foncé
            node_size.append(45)
        else:
            node_color.append("black")
            node_size.append(40)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        text=node_text,
        textposition="middle center",
        marker=dict(
            size=node_size,
            color=node_color,
            line=dict(width=4, color="white")
        ),
        textfont=dict(size=12, color="white", family="Arial Black"),
        hoverinfo="text"
    )

    # --- ARÊTE COURANTE ---
    ce = go.Scatter(x=[], y=[], mode="lines")

    if current_edge is not None:
        u, v, w = current_edge
        x0, y0 = xy(u)
        x1, y1 = xy(v)

        # Couleur selon état
        col = "yellow"
        if phase == "relax" and updated:
            col = "green"
        if phase == "check" and updated:
            col = "red"

        ce = go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            mode="lines",
            line=dict(width=7, color=col),
            hoverinfo="skip"
        )

    # --- FIGURE ---
    fig = go.Figure([bg_edges, ce, node_trace])
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


def plot_bellman_ford_final_path(G, step, source, target):
    """
    Affichage final du chemin Bellman-Ford :
    - chemin final en orange
    - source en vert
    - cible en rouge
    - nœuds atteignables en bleu foncé
    """

    dist = step["dist"]
    parent = step["parent"]

    # --- Reconstruction du chemin ---
    path = []
    node = target
    while node is not None:
        path.append(node)
        node = parent.get(node)
    path.reverse()

    # Si le chemin ne commence pas par la source → pas de chemin
    valid_path = (path[0] == source and dist[target] != math.inf)

    # --- Arrière-plan ---
    def xy(n):
        return G.nodes[n]["x"], G.nodes[n]["y"]

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
            node_color.append("#031E66")  # bleu foncé
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
