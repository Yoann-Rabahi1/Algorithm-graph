import heapq
import plotly.graph_objects as go

# ---------------------------------------------------------
# Générateur étape par étape pour Prim
# ---------------------------------------------------------
def prim_steps(G, start, weight="length"):
    """
    Générateur étape par étape pour Prim.
    Renvoie à chaque étape :
    - current_node : nœud en cours de traitement
    - current_edge : arête choisie à cette étape
    - mst_edges : arêtes déjà ajoutées au MST
    - visited : nœuds déjà intégrés au MST
    - key : valeur minimale pour connecter chaque nœud
    - parent : parent de chaque nœud dans le MST
    - queue : file de priorité (clé, u, v)
    """

    # Initialisation
    visited = set()
    mst_edges = []

    key = {n: float("inf") for n in G.nodes()}
    parent = {n: None for n in G.nodes()}

    key[start] = 0

    # File de priorité : (clé, u, v)
    # u = parent, v = node
    queue = [(0, None, start)]

    def get_weight(u, v):
        data = G.get_edge_data(u, v)
        if isinstance(data, dict):
            return min(d.get(weight, 1) for d in data.values())
        return data.get(weight, 1)

    # Boucle principale
    while queue:
        queue.sort(key=lambda x: x[0])
        k, u, v = queue.pop(0)

        # Étape : avant d'ajouter v
        yield {
            "current_node": v,
            "current_edge": (u, v, k) if u is not None else None,
            "mst_edges": list(mst_edges),
            "visited": set(visited),
            "key": dict(key),
            "parent": dict(parent),
            "queue": list(queue)
        }

        if v in visited:
            continue

        visited.add(v)

        if u is not None:
            mst_edges.append((u, v, k))

        # Mise à jour des voisins
        for w in G.neighbors(v):
            if w not in visited:
                w_weight = get_weight(v, w)
                if w_weight < key[w]:
                    key[w] = w_weight
                    parent[w] = v
                    queue.append((w_weight, v, w))

        # Étape après mise à jour
        yield {
            "current_node": v,
            "current_edge": (u, v, k) if u is not None else None,
            "mst_edges": list(mst_edges),
            "visited": set(visited),
            "key": dict(key),
            "parent": dict(parent),
            "queue": list(queue)
        }

    # Étape finale
    yield {
        "current_node": None,
        "current_edge": None,
        "mst_edges": list(mst_edges),
        "visited": set(visited),
        "key": dict(key),
        "parent": dict(parent),
        "queue": []
    }


# ---------------------------------------------------------
# Affichage dynamique étape par étape (Prim)
# ---------------------------------------------------------
def plot_prim_step(G, step, is_test_graph=False):

    def xy(n):
        if n in G.nodes and 'x' in G.nodes[n] and 'y' in G.nodes[n]:
            return G.nodes[n]['x'], G.nodes[n]['y']
        return None, None

    mst_edges = step["mst_edges"]
    visited = step["visited"]
    current = step["current_edge"]

    # --- Arrière-plan ---
    all_x, all_y = [], []
    for u, v in G.edges():
        x0, y0 = xy(u)
        x1, y1 = xy(v)
        if x0 is None or x1 is None:
            continue
        all_x += [x0, x1, None]
        all_y += [y0, y1, None]

    bg = go.Scatter(
        x=all_x, y=all_y,
        mode="lines",
        line=dict(width=1.5, color="#A0A0A0"),
        hoverinfo="none"
    )

    # --- Arêtes MST ---
    mst_x, mst_y = [], []
    for u, v, w in mst_edges:
        x0, y0 = xy(u)
        x1, y1 = xy(v)
        if x0 is None or x1 is None:
            continue
        mst_x += [x0, x1, None]
        mst_y += [y0, y1, None]

    mst_trace = go.Scatter(
        x=mst_x, y=mst_y,
        mode="lines",
        line=dict(width=6, color="green"),
        hoverinfo="none"
    )

    # --- Arête courante ---
    if current is not None:
        u, v, w = current
        x0, y0 = xy(u)
        x1, y1 = xy(v)
        if x0 is not None and x1 is not None:
            cur_trace = go.Scatter(
                x=[x0, x1],
                y=[y0, y1],
                mode="lines",
                line=dict(width=6, color="yellow"),
                hoverinfo="none"
            )
        else:
            cur_trace = go.Scatter(x=[], y=[])
    else:
        cur_trace = go.Scatter(x=[], y=[])

    # --- Nœuds ---
    node_x, node_y, node_color, node_size = [], [], [], []

    for n in G.nodes():
        x, y = xy(n)
        if x is None:
            continue

        node_x.append(x)
        node_y.append(y)

        if n in visited:
            node_color.append("#1E90FF")
        else:
            node_color.append("black")

        if is_test_graph:
            node_size.append(45)
        else:
            node_size.append(10)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers",
        marker=dict(size=node_size, color=node_color, line=dict(width=3, color="white")),
        hoverinfo="text"
    )

    fig = go.Figure([bg, mst_trace, cur_trace, node_trace])
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="lightblue",
        height=600
    )
    return fig


def plot_prim_mst(G, mst_edges, is_test_graph=False):

    def xy(n):
        if n in G.nodes and 'x' in G.nodes[n] and 'y' in G.nodes[n]:
            return G.nodes[n]['x'], G.nodes[n]['y']
        return None, None

    # --- Arrière-plan ---
    all_x, all_y = [], []
    for u, v in G.edges():
        x0, y0 = xy(u)
        x1, y1 = xy(v)
        if x0 is None or x1 is None:
            continue
        all_x += [x0, x1, None]
        all_y += [y0, y1, None]

    bg = go.Scatter(
        x=all_x, y=all_y,
        mode="lines",
        line=dict(width=1.5, color="#A0A0A0"),
        hoverinfo="none"
    )

    # --- Arêtes MST ---
    mst_x, mst_y = [], []
    for u, v, w in mst_edges:
        x0, y0 = xy(u)
        x1, y1 = xy(v)
        if x0 is None or x1 is None:
            continue
        mst_x += [x0, x1, None]
        mst_y += [y0, y1, None]

    mst_trace = go.Scatter(
        x=mst_x, y=mst_y,
        mode="lines",
        line=dict(width=6, color="green"),
        hoverinfo="none"
    )

    # --- Nœuds ---
    node_x, node_y, node_color, node_size = [], [], [], []

    for n in G.nodes():
        x, y = xy(n)
        if x is None:
            continue

        node_x.append(x)
        node_y.append(y)

        if n in {u for u, v, w in mst_edges} | {v for u, v, w in mst_edges}:
            node_color.append("green")
        else:
            node_color.append("black")

        node_size.append(45 if is_test_graph else 10)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers",
        marker=dict(size=node_size, color=node_color, line=dict(width=3, color="white")),
        hoverinfo="text"
    )

    fig = go.Figure([bg, mst_trace, node_trace])
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="lightblue",
        height=600
    )
    return fig
