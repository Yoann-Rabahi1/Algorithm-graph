import math
import plotly.graph_objects as go

def floyd_warshall_steps(G, weight="length"):
    """
    Générateur étape par étape Floyd-Warshall.

    Hypothèses:
    - G est un graphe avec attributs noeuds x/y (pour l'affichage ailleurs)
    - Les arêtes ont un poids (par défaut: "length"), sinon poids = 1
    - On traite le graphe comme ORIENTÉ si G est DiGraph/MultiDiGraph
      (si tu veux non orienté, ajoute aussi dist[j][i] = w)
    """

    nodes = list(G.nodes())
    n = len(nodes)
    idx = {nodes[i]: i for i in range(n)}

    # dist et next (reconstruction de chemin)
    dist = [[math.inf] * n for _ in range(n)]
    nxt = [[None] * n for _ in range(n)]

    for i in range(n):
        dist[i][i] = 0.0
        nxt[i][i] = nodes[i]

    # init depuis les arêtes (MultiGraph compatible)
    for u, v, data in G.edges(data=True):
        w = data.get(weight, 1.0)
        if w is None:
            w = 1.0
        iu, iv = idx[u], idx[v]
        if float(w) < dist[iu][iv]:
            dist[iu][iv] = float(w)
            nxt[iu][iv] = v

    # yield étape initiale
    yield {
        "phase": "init",
        "k": None, "i": None, "j": None,
        "updated": False,
        "dist": [row[:] for row in dist],
        "nxt": [row[:] for row in nxt],
    }

    # floyd-warshall
    for k in range(n):
        for i in range(n):
            dik = dist[i][k]
            if dik == math.inf:
                continue
            for j in range(n):
                dkj = dist[k][j]
                if dkj == math.inf:
                    continue

                old = dist[i][j]
                new = dik + dkj
                updated = False

                if new < old:
                    dist[i][j] = new
                    nxt[i][j] = nxt[i][k]  # premier saut i -> ...
                    updated = True

                # yield chaque comparaison (animation fine)
                yield {
                    "phase": "relax",
                    "k": k, "i": i, "j": j,
                    "updated": updated,
                    "dist_ij_old": old,
                    "dist_ij_new": dist[i][j],
                    "dist": [row[:] for row in dist],
                    "nxt": [row[:] for row in nxt],
                }

    yield {
        "phase": "done",
        "k": n - 1 if n > 0 else None,
        "i": None, "j": None,
        "updated": False,
        "dist": [row[:] for row in dist],
        "nxt": [row[:] for row in nxt],
    }


def floyd_warshall_complete(G, weight="length"):
    """
    Version complète (non-itérative) de Floyd-Warshall.
    Retourne les matrices finales dist et nxt, plus toutes les itérations pour la matrice.
    """
    nodes = list(G.nodes())
    n = len(nodes)
    idx = {nodes[i]: i for i in range(n)}

    # Initialisation
    dist = [[math.inf] * n for _ in range(n)]
    nxt = [[None] * n for _ in range(n)]

    for i in range(n):
        dist[i][i] = 0.0
        nxt[i][i] = nodes[i]

    # Init depuis les arêtes
    for u, v, data in G.edges(data=True):
        w = data.get(weight, 1.0)
        if w is None:
            w = 1.0
        iu, iv = idx[u], idx[v]
        if float(w) < dist[iu][iv]:
            dist[iu][iv] = float(w)
            nxt[iu][iv] = v

    # Sauvegarder toutes les matrices intermédiaires (pour affichage)
    all_matrices = []
    all_matrices.append([row[:] for row in dist])  # Matrice initiale (k=-1)

    # Floyd-Warshall
    for k in range(n):
        for i in range(n):
            for j in range(n):
                if dist[i][k] + dist[k][j] < dist[i][j]:
                    dist[i][j] = dist[i][k] + dist[k][j]
                    nxt[i][j] = nxt[i][k]
        
        # Sauvegarder après chaque k
        all_matrices.append([row[:] for row in dist])

    return dist, nxt, all_matrices


def reconstruct_path_from_step(step, nodes, src_node, dst_node):
    """
    Reconstruit le chemin src -> dst à partir de la matrice nxt (dans un step final ou courant).
    Retourne une liste de noeuds [src, ..., dst] ou [] si pas de chemin.
    """
    nxt = step["nxt"]
    idx = {nodes[i]: i for i in range(len(nodes))}

    if src_node not in idx or dst_node not in idx:
        return []

    i = idx[src_node]
    j = idx[dst_node]

    if nxt[i][j] is None:
        return []

    path = [src_node]
    cur = src_node
    guard = 0

    while cur != dst_node and guard < len(nodes) + 5:
        cur_i = idx[cur]
        cur = nxt[cur_i][j]
        if cur is None:
            return []
        path.append(cur)
        guard += 1

    if path[-1] != dst_node:
        return []
    return path


def reconstruct_path_from_nxt(nxt, nodes, src_node, dst_node):
    """
    Reconstruit le chemin src -> dst à partir de la matrice nxt.
    Version alternative qui prend directement nxt au lieu d'un step.
    """
    idx = {nodes[i]: i for i in range(len(nodes))}

    if src_node not in idx or dst_node not in idx:
        return []

    i = idx[src_node]
    j = idx[dst_node]

    if nxt[i][j] is None:
        return []

    path = [src_node]
    cur = src_node
    guard = 0

    while cur != dst_node and guard < len(nodes) + 5:
        cur_i = idx[cur]
        cur = nxt[cur_i][j]
        if cur is None:
            return []
        path.append(cur)
        guard += 1

    if path[-1] != dst_node:
        return []
    return path


def plot_floyd_warshall_final(G, dist, nxt, nodes, source, target):
    """
    Affiche le graphe final avec le chemin optimal de source à target.
    
    Args:
        G: Le graphe NetworkX
        dist: Matrice des distances finales
        nxt: Matrice des successeurs
        nodes: Liste des nœuds
        source: Nœud source
        target: Nœud cible
    """
    
    # Reconstruction du chemin
    path = reconstruct_path_from_nxt(nxt, nodes, source, target)
    
    idx = {nodes[i]: i for i in range(len(nodes))}
    valid_path = len(path) >= 2 and dist[idx[source]][idx[target]] != math.inf

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

    # --- Poids des arêtes du chemin ---
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

    for n in nodes:
        x, y = xy(n)
        node_x.append(x)
        node_y.append(y)

        # Distance depuis la source
        i_src = idx[source]
        i_node = idx[n]
        d = dist[i_src][i_node]
        
        # Label avec nom du nœud et distance
        if d != math.inf:
            label = f"{n}<br>{d:.1f}"
        else:
            label = f"{n}<br>∞"
        labels.append(label)

        # Couleurs et tailles
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