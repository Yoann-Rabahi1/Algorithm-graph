import heapq
import math


def dijkstra_osmnx(G, source, target=None, weight="length"):
    """
    Dijkstra adapté à un graphe OSMnx (MultiDiGraph).
    
    Parameters
    ----------
    G : networkx.MultiDiGraph
    source : int
        Node ID de départ
    target : int, optional
        Node ID d'arrivée
    weight : str
        Attribut utilisé comme poids (ex: 'length')

    Returns
    -------
    dist : dict
        Distance minimale depuis source
    prev : dict
        Prédécesseur de chaque node
    """

    # Initialisation
    dist = {node: math.inf for node in G.nodes}
    prev = {node: None for node in G.nodes}
    dist[source] = 0

    # File de priorité
    pq = [(0, source)]

    while pq:
        current_dist, u = heapq.heappop(pq)

        # Optimisation
        if current_dist > dist[u]:
            continue

        # Arrêt anticipé
        if target is not None and u == target:
            break

        # Parcours des voisins sortants
        for v in G.successors(u):
            # Plusieurs arêtes possibles u -> v
            edges = G.get_edge_data(u, v)

            # poids minimal entre u et v
            min_weight = min(
                edge_data.get(weight, math.inf)
                for edge_data in edges.values()
            )

            alt = dist[u] + min_weight

            if alt < dist[v]:
                dist[v] = alt
                prev[v] = u
                heapq.heappush(pq, (alt, v))

    return dist, prev


def reconstruct_path(prev, source, target):
    path = []
    u = target

    while u is not None:
        path.append(u)
        u = prev[u]

    path.reverse()

    if path[0] == source:
        return path
    return []
