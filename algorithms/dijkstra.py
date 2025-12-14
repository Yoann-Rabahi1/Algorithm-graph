import osmnx as ox

def dijkstra_rail_idf(start_node, end_node, G):
    """
    Calcule le plus court chemin entre start_node et end_node sur un graphe ferroviaire OSMnx.
    
    Params:
        start_node: nœud de départ
        end_node: nœud d'arrivée
        G: graphe OSMnx (rails)
    
    Returns:
        path: liste des nœuds du plus court chemin
        distances: dict avec la distance minimale depuis start_node pour chaque nœud
    """
    # Initialisation
    distances = {node: float('inf') for node in G.nodes}
    predecessors = {node: None for node in G.nodes}
    distances[start_node] = 0
    visited = set()

    while len(visited) < len(G.nodes):
        # Sélection du nœud non visité avec la distance minimale
        min_node = min(
            (node for node in G.nodes if node not in visited),
            key=lambda n: distances[n],
            default=None
        )
        if min_node is None or distances[min_node] == float('inf'):
            break  # Plus de nœuds atteignables

        visited.add(min_node)
        if min_node == end_node:
            break

        # Parcours des voisins
        for neighbor, edges in G[min_node].items():
            # Prend la plus courte arête si plusieurs arêtes existent
            edge_length = min(edge_data.get('length', 1.0) for edge_data in edges.values())
            new_dist = distances[min_node] + edge_length
            if new_dist < distances[neighbor]:
                distances[neighbor] = new_dist
                predecessors[neighbor] = min_node

    # Reconstruction du chemin
    path = []
    current = end_node
    while current is not None:
        path.insert(0, current)
        current = predecessors[current]

    return path, distances
