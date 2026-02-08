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
        if n in G.nodes and "x" in G.nodes[n] and "y" in G.nodes[n]:
            return G.nodes[n]["x"], G.nodes[n]["y"]
        return None, None

    mst_edges = step["mst_edges"]
    visited = step["visited"]
    current = step["current_edge"]

    fig = go.Figure()

    # --- Arrière-plan ---
    for u, v in G.edges():
        x0, y0 = xy(u)
        x1, y1 = xy(v)
        if x0 is None or x1 is None:
            continue
        fig.add_trace(go.Scatter(
            x=[x0, x1], y=[y0, y1],
            mode="lines",
            line=dict(width=1.5, color="#A0A0A0"),
            hoverinfo="none"
        ))

    # --- Arêtes MST ---
    for u, v, w in mst_edges:
        x0, y0 = xy(u)
        x1, y1 = xy(v)
        if x0 is None or x1 is None:
            continue

        fig.add_trace(go.Scatter(
            x=[x0, x1], y=[y0, y1],
            mode="lines",
            line=dict(width=6, color="green"),
            hoverinfo="text" if is_test_graph else "none",
            text=[f"{u} → {v} : {w:.1f}"] if is_test_graph else None
        ))

        # Poids uniquement pour graphe de test
        if is_test_graph:
            xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
            fig.add_annotation(
                x=xm, y=ym,
                text=f"{w:.1f}",
                showarrow=False,
                font=dict(size=16, color="black"),
                bgcolor="white",
                opacity=0.8
            )

    # --- Arête courante ---
    if current is not None:
        u, v, w = current
        x0, y0 = xy(u)
        x1, y1 = xy(v)
        if x0 is not None and x1 is not None:

            fig.add_trace(go.Scatter(
                x=[x0, x1], y=[y0, y1],
                mode="lines",
                line=dict(width=6, color="yellow"),
                hoverinfo="text" if is_test_graph else "none",
                text=[f"{u} → {v} : {w:.1f}"] if is_test_graph else None
            ))

            # Poids de l’arête courante (test graph uniquement)
            if is_test_graph:
                xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
                fig.add_annotation(
                    x=xm, y=ym,
                    text=f"{w:.1f}",
                    showarrow=False,
                    font=dict(size=18, color="black"),
                    bgcolor="yellow",
                    opacity=0.9
                )

    # --- Nœuds ---
    node_x, node_y, node_text, node_color, node_size = [], [], [], [], []

    for n in G.nodes():
        x, y = xy(n)
        if x is None:
            continue

        node_x.append(x)
        node_y.append(y)
        node_text.append(str(n))

        node_color.append("#1E90FF" if n in visited else "black")
        node_size.append(45 if is_test_graph else 10)

    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        text=node_text if is_test_graph else None,
        textposition="top center",
        marker=dict(size=node_size, color=node_color, line=dict(width=3, color="white")),
        hoverinfo="text"
    ))

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
        if n in G.nodes and "x" in G.nodes[n] and "y" in G.nodes[n]:
            return G.nodes[n]["x"], G.nodes[n]["y"]
        return None, None

    fig = go.Figure()

    # --- Arrière-plan ---
    for u, v in G.edges():
        x0, y0 = xy(u)
        x1, y1 = xy(v)
        if x0 is None or x1 is None:
            continue
        fig.add_trace(go.Scatter(
            x=[x0, x1], y=[y0, y1],
            mode="lines",
            line=dict(width=1.5, color="#A0A0A0"),
            hoverinfo="none"
        ))

    # --- Arêtes MST ---
    for u, v, w in mst_edges:
        x0, y0 = xy(u)
        x1, y1 = xy(v)
        if x0 is None or x1 is None:
            continue

        fig.add_trace(go.Scatter(
            x=[x0, x1], y=[y0, y1],
            mode="lines",
            line=dict(width=6, color="green"),
            hoverinfo="text" if is_test_graph else "none",
            text=[f"{u} → {v} : {w:.1f}"] if is_test_graph else None
        ))

        # Poids uniquement pour graphe de test
        if is_test_graph:
            xm, ym = (x0 + x1) / 2, (y0 + y1) / 2
            fig.add_annotation(
                x=xm, y=ym,
                text=f"{w:.1f}",
                showarrow=False,
                font=dict(size=16, color="black"),
                bgcolor="white",
                opacity=0.8
            )

    # --- Nœuds ---
    node_x, node_y, node_text, node_color, node_size = [], [], [], [], []

    mst_nodes = {u for u, v, w in mst_edges} | {v for u, v, w in mst_edges}

    for n in G.nodes():
        x, y = xy(n)
        if x is None:
            continue

        node_x.append(x)
        node_y.append(y)
        node_text.append(str(n))

        node_color.append("green" if n in mst_nodes else "black")
        node_size.append(45 if is_test_graph else 10)

    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        text=node_text if is_test_graph else None,
        textposition="top center",
        marker=dict(size=node_size, color=node_color, line=dict(width=3, color="white")),
        hoverinfo="text"
    ))

    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="lightblue",
        height=600
    )

    return fig
