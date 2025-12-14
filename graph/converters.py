import osmnx as ox
import networkx as nx
import numpy as np


def reduce_to_cities(G, cities):
    """
    G : graphe OSMnx (networkx)
    cities : dict { "Paris": (lat, lon), ... }

    Retourne :
    - G_reduced : graphe networkx pondéré entre villes
    """

    city_nodes = {}

    # Associer chaque ville au nœud OSM le plus proche
    for city, (lat, lon) in cities.items():
        node = ox.distance.nearest_nodes(G, X=lon, Y=lat)
        city_nodes[city] = node

    G_reduced = nx.Graph()

    # Ajouter les villes comme nœuds
    for city in city_nodes:
        G_reduced.add_node(city)

    # Calcul des distances réelles entre villes
    for city1, node1 in city_nodes.items():
        for city2, node2 in city_nodes.items():
            if city1 == city2:
                continue

            try:
                dist = nx.shortest_path_length(
                    G, node1, node2, weight="length"
                )
                G_reduced.add_edge(city1, city2, weight=dist)

            except nx.NetworkXNoPath:
                pass

    return G_reduced

def graph_to_adj_list(G):
    """
    G : graphe networkx pondéré

    Retour :
    adj : dict {node: [(neighbor, weight), ...]}
    """

    adj = {}

    for u in G.nodes:
        adj[u] = []

        for v, data in G[u].items():
            weight = data.get("weight", 1)
            adj[u].append((v, weight))

    return adj



def graph_to_adj_matrix(G):
    """
    G : graphe networkx pondéré

    Retour :
    - matrix : np.ndarray
    - nodes  : liste des nœuds (index → ville)
    """

    nodes = list(G.nodes)
    index = {node: i for i, node in enumerate(nodes)}

    n = len(nodes)
    matrix = np.zeros((n, n))

    for u, v, data in G.edges(data=True):
        i, j = index[u], index[v]
        w = data.get("weight", 1)

        matrix[i, j] = w
        matrix[j, i] = w  # graphe non orienté

    return matrix, nodes
