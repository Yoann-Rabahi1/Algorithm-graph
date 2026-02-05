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

#va nous permettre de détécter les cycles éfficacement 
class UnionFind:
    def __init__(self, nodes):
        self.parent = {node: node for node in nodes}
        self.rank = {node: 0 for node in nodes}

    def find(self, u):
        if self.parent[u] != u:
            self.parent[u] = self.find(self.parent[u])
        return self.parent[u]

    def union(self, u, v):
        ru = self.find(u)
        rv = self.find(v)

        if ru == rv:
            return False

        if self.rank[ru] < self.rank[rv]:
            self.parent[ru] = rv
        elif self.rank[ru] > self.rank[rv]:
            self.parent[rv] = ru
        else:
            self.parent[rv] = ru
            self.rank[ru] += 1

        return True

def kruskal_osmnx(G, weight="length"):
    """
    Kruskal adapté à un graphe OSMnx (MultiDiGraph).
    Le graphe est traité comme non orienté.

    Parameters
    ----------
    G : networkx.MultiDiGraph
    weight : str
        Attribut utilisé comme poids (ex: 'length')

    Returns
    -------
    mst_edges : list
        Liste des arêtes sélectionnées (u, v, w)
    total_cost : float
        Coût total de l'arbre couvrant minimal
    """

    # 1. Liste des arêtes (u, v, poids minimal)
    edges = []

    for u, v, data in G.edges(keys=False, data=True):
        w = data.get(weight, math.inf)
        if w < math.inf:
            edges.append((u, v, w))

    # 2. Tri des arêtes par poids croissant
    edges.sort(key=lambda x: x[2])

    # 3. Initialisation Union-Find
    uf = UnionFind(G.nodes)

    mst_edges = []
    total_cost = 0.0

    # 4. Parcours des arêtes
    for u, v, w in edges:
        if uf.union(u, v):
            mst_edges.append((u, v, w))
            total_cost += w

    return mst_edges, total_cost




def prim_osmnx(G, start, weight="length"):
    """
    Prim adapté à un graphe OSMnx (MultiDiGraph).
    Le graphe est traité comme non orienté.

    Parameters
    ----------
    G : networkx.MultiDiGraph
    start : int
        Node ID de départ
    weight : str
        Attribut utilisé comme poids (ex: 'length')

    Returns
    -------
    mst_edges : list
        Liste des arêtes sélectionnées (u, v, w)
    total_cost : float
        Coût total de l'arbre couvrant minimal
    """

    visited = set([start])
    mst_edges = []
    total_cost = 0.0

    # File de priorité : (poids, u, v)
    pq = []

    # Initialisation : arêtes sortantes du sommet de départ
    for v in G.neighbors(start):
        edges = G.get_edge_data(start, v)
        w = min(
            edge_data.get(weight, math.inf)
            for edge_data in edges.values()
        )
        heapq.heappush(pq, (w, start, v))

    # Boucle principale
    while pq and len(visited) < len(G.nodes):
        w, u, v = heapq.heappop(pq)

        if v in visited:
            continue

        # Ajout de l'arête au MST
        visited.add(v)
        mst_edges.append((u, v, w))
        total_cost += w

        # Ajout des nouvelles arêtes candidates
        for x in G.neighbors(v):
            if x not in visited:
                edges = G.get_edge_data(v, x)
                w_new = min(
                    edge_data.get(weight, math.inf)
                    for edge_data in edges.values()
                )
                heapq.heappush(pq, (w_new, v, x))

    return mst_edges, total_cost
