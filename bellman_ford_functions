import math
import plotly.graph_objects as go

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
    Visualisation Plotly:
    - fond: arêtes gris clair + noeuds gris clair
    - arête courante: jaune, si updated -> vert, si check updated -> rouge
    - noeud source: vert, target: rouge
    - noeuds connus (dist != inf) en bleu
    """
    # positions: attend x/y sur les noeuds (comme ton graphe villes)
    def xy(n):
        d = G.nodes[n]
        return d["x"], d["y"]

    phase = step.get("phase")
    current_edge = step.get("edge")
    updated = step.get("updated", False)
    dist = step.get("dist", {})

    # background edges
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
        hoverinfo="none",
        opacity=0.4
    )

    # background nodes
    all_x, all_y = [], []
    for n in G.nodes():
        x, y = xy(n)
        all_x.append(x)
        all_y.append(y)

    bg_nodes = go.Scatter(
        x=all_x, y=all_y,
        mode="markers",
        marker=dict(size=8, color="#EAEAEA"),
        hoverinfo="none",
        opacity=0.9
    )

    # highlight nodes
    hx, hy, hcolor, htext, hsize = [], [], [], [], []
    nodes_to_draw = list(G.nodes()) if show_all_nodes else [n for n in G.nodes() if dist.get(n, math.inf) != math.inf]

    # toujours inclure source/target même si inf
    if source is not None and source not in nodes_to_draw:
        nodes_to_draw.append(source)
    if target is not None and target not in nodes_to_draw:
        nodes_to_draw.append(target)

    for n in nodes_to_draw:
        x, y = xy(n)
        hx.append(x)
        hy.append(y)

        dn = dist.get(n, math.inf)
        label = f"{n}"
        if dn != math.inf:
            label += f"<br>dist={dn:.2f}"
        else:
            label += "<br>dist=∞"
        htext.append(label)

        if n == source:
            hcolor.append("green")
            hsize.append(14)
        elif n == target:
            hcolor.append("red")
            hsize.append(14)
        elif dn != math.inf:
            hcolor.append("blue")
            hsize.append(10)
        else:
            hcolor.append("gray")
            hsize.append(8)

    nodes = go.Scatter(
        x=hx, y=hy,
        mode="markers",
        marker=dict(size=hsize, color=hcolor, line=dict(width=1, color="white")),
        hoverinfo="text",
        text=htext
    )

    # current edge highlight
    ce = go.Scatter(x=[], y=[], mode="lines")
    if current_edge is not None:
        u, v, w = current_edge
        x0, y0 = xy(u)
        x1, y1 = xy(v)

        # couleur selon phase et updated
        col = "yellow"
        width = 6
        if phase == "relax" and updated:
            col = "green"
        if phase == "check" and updated:
            col = "red"

        ce = go.Scatter(
            x=[x0, x1],
            y=[y0, y1],
            mode="lines",
            line=dict(width=width, color=col),
            hoverinfo="skip"
        )

    fig = go.Figure([bg_edges, bg_nodes, ce, nodes])
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
