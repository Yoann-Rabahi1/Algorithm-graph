import math
import plotly.graph_objects as go

def bellman_ford_run(G, source, weight="length"):
    """
    Calcule Bellman Ford en une seule fois.
    Retour:
      - dist: dict node -> distance
      - parent: dict node -> parent
      - neg_cycle: bool
      - iterations: liste de snapshots dist (après chaque itération)
    """
    dist = {n: math.inf for n in G.nodes()}
    parent = {n: None for n in G.nodes()}
    dist[source] = 0.0

    # Liste des arêtes (u, v, w)
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

    iterations = []
    n = len(G.nodes())

    # Relax |V|-1 fois
    for _ in range(n - 1):
        changed = False
        for u, v, w in edges:
            if dist[u] != math.inf and dist[u] + w < dist[v]:
                dist[v] = dist[u] + w
                parent[v] = u
                changed = True
        iterations.append(dict(dist))
        if not changed:
            break

    # Détection cycle négatif
    neg_cycle = False
    for u, v, w in edges:
        if dist[u] != math.inf and dist[u] + w < dist[v]:
            neg_cycle = True
            break

    return dist, parent, neg_cycle, iterations


def reconstruct_path(parent, source, target):
    """
    Reconstruit le chemin source -> target à partir de parent.
    Retourne une liste de noeuds [source, ..., target] ou [] si impossible.
    """
    if source == target:
        return [source]

    path = []
    cur = target
    seen = set()

    while cur is not None:
        if cur in seen:
            # boucle, sécurité
            return []
        seen.add(cur)
        path.append(cur)
        if cur == source:
            break
        cur = parent.get(cur)

    path.reverse()
    if not path or path[0] != source:
        return []
    return path


def plot_bellman_result(G, source=None, target=None, path=None, dist=None):
    """
    Affiche le graphe + surligne:
      - source (vert), target (rouge)
      - chemin final (vert épais)
      - noeuds atteignables (bleu léger)
    """
    def xy(n):
        d = G.nodes[n]
        return d["x"], d["y"]

    # Background edges
    ex, ey = [], []
    for u, v in G.edges():
        x0, y0 = xy(u)
        x1, y1 = xy(v)
        ex += [x0, x1, None]
        ey += [y0, y1, None]

    bg_edges = go.Scatter(
        x=ex, y=ey,
        mode="lines",
        line=dict(width=1.2, color="#A0A0A0"),
        hoverinfo="skip",
        opacity=0.35
    )

    # Background nodes
    nx, ny = [], []
    for n in G.nodes():
        x, y = xy(n)
        nx.append(x)
        ny.append(y)

    bg_nodes = go.Scatter(
        x=nx, y=ny,
        mode="markers",
        marker=dict(size=7, color="#EAEAEA"),
        hoverinfo="skip"
    )

    # Nodes reached
    reached_trace = go.Scatter(x=[], y=[], mode="markers")
    if dist is not None:
        rx, ry, rtext = [], [], []
        for n in G.nodes():
            if dist.get(n, math.inf) != math.inf:
                x, y = xy(n)
                rx.append(x)
                ry.append(y)
                rtext.append(f"{n}<br>dist={dist[n]:.2f}")
        reached_trace = go.Scatter(
            x=rx, y=ry,
            mode="markers",
            marker=dict(size=9, color="royalblue", line=dict(width=1, color="white")),
            hoverinfo="text",
            text=rtext,
            opacity=0.85
        )

    # Path highlight
    path_trace = go.Scatter(x=[], y=[], mode="lines")
    if path and len(path) >= 2:
        px, py = [], []
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            x0, y0 = xy(u)
            x1, y1 = xy(v)
            px += [x0, x1, None]
            py += [y0, y1, None]

        path_trace = go.Scatter(
            x=px, y=py,
            mode="lines",
            line=dict(width=7, color="green"),
            hoverinfo="skip",
            opacity=0.95
        )

    # Source & target
    st_x, st_y, st_c, st_t, st_s = [], [], [], [], []
    for n, col, label, size in [
        (source, "green", "SOURCE", 16),
        (target, "red", "CIBLE", 16)
    ]:
        if n is None:
            continue
        x, y = xy(n)
        st_x.append(x)
        st_y.append(y)
        st_c.append(col)
        st_t.append(label)
        st_s.append(size)

    st_trace = go.Scatter(
        x=st_x, y=st_y,
        mode="markers+text",
        marker=dict(size=st_s, color=st_c, line=dict(width=2, color="white")),
        text=st_t,
        textposition="top center",
        hoverinfo="skip"
    )

    fig = go.Figure([bg_edges, bg_nodes, reached_trace, path_trace, st_trace])
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False, fixedrange=True),
        yaxis=dict(visible=False, fixedrange=True),
        height=650,
        plot_bgcolor="lightblue",
        paper_bgcolor="lightblue"
    )
    return fig
