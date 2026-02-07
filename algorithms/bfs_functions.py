from collections import deque
import plotly.graph_objects as go


def bfs_steps(G, start, end=None):
    """
    BFS pondéré : les voisins sont ajoutés dans la file
    en fonction du poids croissant des arêtes.
    """

    visited = set()
    visit_order = []
    parent = {start: None}
    queue = deque([start])

    while queue:
        u = queue.popleft()

        if u in visited:
            continue

        visited.add(u)
        visit_order.append(u)

        yield {
            "current": u,
            "visited": set(visited),
            "visit_order": list(visit_order),
            "parent": dict(parent)
        }

        # --- tri des voisins par poids croissant ---
        neighbors = []
        for v in G.neighbors(u):
            w = G[u][v].get("length", 1)  # poids par défaut
            neighbors.append((w, v))

        neighbors.sort(key=lambda x: x[0])  # tri par poids

        # ajout dans la file
        for w, v in neighbors:
            if v not in visited and v not in queue:
                parent[v] = u
                queue.append(v)

    # Étape finale
    yield {
        "current": None,
        "visited": set(visited),
        "visit_order": list(visit_order),
        "parent": dict(parent)
    }



def plot_bfs_step(G, step, start=None, end=None, is_test_graph=False):

    visited = step["visited"]
    current = step["current"]

    # Arrière-plan
    all_edge_x, all_edge_y = [], []
    for u, v in G.edges():
        all_edge_x += [G.nodes[u]['x'], G.nodes[v]['x'], None]
        all_edge_y += [G.nodes[u]['y'], G.nodes[v]['y'], None]

    bg_edges = go.Scatter(
        x=all_edge_x, y=all_edge_y,
        mode="lines",
        line=dict(width=0.5, color="#444"),
        hoverinfo="none"
    )

    # --- NOEUDS ---
    node_x, node_y, node_color, node_size, labels = [], [], [], [], []

    for n in G.nodes():

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

        elif n in visited:
            node_color.append("#031E66")  # bleu foncé
            node_size.append(45)

        else:
            node_color.append("black")
            node_size.append(40)

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
        textfont=dict(size=12, color="white", family="Arial Black"),
        hoverinfo="text"
    )

    fig = go.Figure([bg_edges, node_trace])
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=600,
        plot_bgcolor="lightblue",
    )

    return fig
