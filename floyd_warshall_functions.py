import math

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
