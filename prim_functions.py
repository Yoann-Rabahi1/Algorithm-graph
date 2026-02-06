import heapq
import plotly.graph_objects as go

def prim_steps(G, start_node=None, weight="length"):
    """
    Générateur étape par étape pour Prim (MST).
    Le graphe est considéré comme non orienté pour Prim.
    yield dict:
      - current_edge: (u, v, w) arête choisie (celle qu'on ajoute au MST)
      - candidate_edge: (u, v, w) arête en cours d'examen (optionnel visuel)
      - mst_edges: liste des arêtes du MST déjà ajoutées
      - visited_nodes: noeuds déjà dans l'arbre
      - total_cost: coût total actuel
    """

    nodes = list(G.nodes())
    if not nodes:
        yield {
            "current_edge": None,
            "candidate_edge": None,
            "mst_edges": [],
            "visited_nodes": set(),
            "total_cost": 0.0
        }
        return

    if start_node is None:
        start_node = nodes[0]

    visited = set([start_node])
    mst_edges = []
    total_cost = 0.0

    # on push toutes les arêtes sortantes de start (Prim traite non orienté)
    pq = []
    def push_edges_from(u):
        # voisins sortants
        for v in G.successors(u):
            edges = G.get_edge_data(u, v)
            if edges:
                w = min(ed.get(weight, 1) for ed in edges.values())
                heapq.heappush(pq, (w, u, v))

        # voisins entrants (pour simuler non orienté)
        for v in G.predecessors(u):
            edges = G.get_edge_data(v, u)
            if edges:
                w = min(ed.get(weight, 1) for ed in edges.values())
                heapq.heappush(pq, (w, u, v))

    push_edges_from(start_node)

    # étape initiale
    yield {
        "current_edge": None,
        "candidate_edge": None,
        "mst_edges": list(mst_edges),
        "visited_nodes": set(visited),
        "total_cost": total_cost
    }

    while pq and len(visited) < len(nodes):
        w, u, v = heapq.heappop(pq)

        # candidate step (juste pour animation, optionnel)
        yield {
            "current_edge": None,
            "candidate_edge": (u, v, w),
            "mst_edges": list(mst_edges),
            "visited_nodes": set(visited),
            "total_cost": total_cost
        }

        # on veut une arête qui relie l'arbre à un nouveau noeud
        if v in visited and u in visited:
            continue

        # normaliser: u doit être dans visited, v doit être le nouveau
        if u not in visited and v in visited:
            u, v = v, u

        if u in visited and v not in visited:
            visited.add(v)
            mst_edges.append((u, v, w))
            total_cost += w

            # étape acceptation
            yield {
                "current_edge": (u, v, w),
                "candidate_edge": None,
                "mst_edges": list(mst_edges),
                "visited_nodes": set(visited),
                "total_cost": total_cost
            }

            push_edges_from(v)

    # étape finale
    yield {
        "current_edge": None,
        "candidate_edge": None,
        "mst_edges": list(mst_edges),
        "visited_nodes": set(visited),
        "total_cost": total_cost
    }


# ---------------------------------------------------------
# Affichage dynamique étape par étape (Prim)
# ---------------------------------------------------------
def plot_prim_step(G, step):
    current = step.get("current_edge")         # arête ajoutée
    candidate = step.get("candidate_edge")     # arête examinée
    mst_edges = step.get("mst_edges", [])
    visited_nodes = step.get("visited_nodes", set())

    # fond: toutes les arêtes
    all_edge_x, all_edge_y = [], []
    for u, v in G.edges():
        all_edge_x += [G.nodes[u]['x'], G.nodes[v]['x'], None]
        all_edge_y += [G.nodes[u]['y'], G.nodes[v]['y'], None]

    bg_edges = go.Scatter(
        x=all_edge_x, y=all_edge_y,
        mode="lines",
        line=dict(width=1.5, color="#A0A0A0"),
        hoverinfo="none"
    )

    # MST (vert)
    mst_x, mst_y = [], []
    for u, v, w in mst_edges:
        mst_x += [G.nodes[u]['x'], G.nodes[v]['x'], None]
        mst_y += [G.nodes[u]['y'], G.nodes[v]['y'], None]

    mst_trace = go.Scatter(
        x=mst_x, y=mst_y,
        mode="lines",
        line=dict(width=6, color="green"),
        hoverinfo="none"
    )

    # arête candidate (orange)
    if candidate is not None:
        u, v, w = candidate
        cand_trace = go.Scatter(
            x=[G.nodes[u]['x'], G.nodes[v]['x']],
            y=[G.nodes[u]['y'], G.nodes[v]['y']],
            mode="lines",
            line=dict(width=6, color="orange"),
            hoverinfo="none"
        )
    else:
        cand_trace = go.Scatter(x=[], y=[])

    # arête courante acceptée (jaune)
    if current is not None:
        u, v, w = current
        cur_trace = go.Scatter(
            x=[G.nodes[u]['x'], G.nodes[v]['x']],
            y=[G.nodes[u]['y'], G.nodes[v]['y']],
            mode="lines",
            line=dict(width=7, color="yellow"),
            hoverinfo="none"
        )
    else:
        cur_trace = go.Scatter(x=[], y=[])

        # noeuds, style Dijkstra amélioré
    node_x, node_y, labels, colors = [], [], [], []
    for n, data in G.nodes(data=True):
        node_x.append(data["x"])
        node_y.append(data["y"])
        labels.append(str(n))

        # bleu pour les noeuds déjà dans l'arbre
        if n in visited_nodes:
            colors.append("#1E90FF")  # bleu vif
        else:
            colors.append("#000000")  # noir

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        text=labels,
        textposition="top center",
        marker=dict(
            size=28,                     # plus gros
            color=colors,
            line=dict(width=3, color="white")  # bord blanc épais
        ),
        textfont=dict(
            size=14,
            color="white",
            family="Arial Black"
        ),
        hoverinfo="text"
    )


    fig = go.Figure([bg_edges, mst_trace, cand_trace, cur_trace, node_trace])
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=600,
        plot_bgcolor="lightblue",
        paper_bgcolor="lightblue"
    )
    return fig


# ---------------------------------------------------------
# Affichage MST final (Prim)
# ---------------------------------------------------------
def plot_dfs_final_path(G, step, start, end, is_test_graph=False):

    parent = step["parent"]
    visited = step["visited"]

    # Reconstruction du chemin final
    path = []
    node = end
    while node is not None:
        if node not in G.nodes:
            break
        path.append(node)
        node = parent.get(node)
    path.reverse()

    # Si pas de chemin → fallback
    if not path or path[0] != start:
        return plot_dfs_step(G, step, start, end, is_test_graph)

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

    # Arêtes du chemin final
    path_edge_x, path_edge_y = [], []
    for i in range(len(path) - 1):
        u, v = path[i], path[i + 1]
        path_edge_x += [G.nodes[u]['x'], G.nodes[v]['x'], None]
        path_edge_y += [G.nodes[u]['y'], G.nodes[v]['y'], None]

    path_trace = go.Scatter(
        x=path_edge_x, y=path_edge_y,
        mode="lines",
        line=dict(width=6, color="orange"),
        hoverinfo="none"
    )

    # --- NOEUDS (style harmonisé) ---
    node_x, node_y, node_color, node_size, labels = [], [], [], [], []

    for n in G.nodes():

        node_x.append(G.nodes[n]['x'])
        node_y.append(G.nodes[n]['y'])
        labels.append(str(n))

        if n == start:
            node_color.append("green")
            node_size.append(55)

        elif n == end:
            node_color.append("red")
            node_size.append(55)

        elif n in path:
            node_color.append("orange")
            node_size.append(50)

        elif n in visited:
            node_color.append("#1E3A8A")  # bleu foncé
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

    fig = go.Figure([bg_edges, path_trace, node_trace])
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=600,
        plot_bgcolor="lightblue",
        paper_bgcolor="lightblue"
    )

    return fig
