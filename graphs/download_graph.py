import osmnx as ox
import networkx as nx

def get_graph(place: str, network_type="drive"):
    """
    Télécharge un graphe depuis OpenStreetMap et ajoute les attributs x/y
    """
    G = ox.graph_from_place(place, network_type=network_type)
    G = G.to_undirected()

    return G


def get_osm_info(place: str, network_type="drive"):
    """
    Récupère des infos sur un graphe OSM (sans sauvegarde)
    """
    try:
        G = get_graph(place, network_type)
        return {
            "nodes": len(G.nodes()),
            "edges": len(G.edges()),
            "name": place
        }
    except Exception as e:
        return {
            "nodes": "?",
            "edges": "?",
            "name": place,
            "error": str(e)
        }


def create_french_cities_graph():
    """Crée le graphe des villes françaises avec les distances"""
    G = nx.MultiDiGraph()
    
    positions = {
        'Rennes': (0, 50),
        'Nantes': (10, 30),
        'Bordeaux': (0, 0),
        'Caen': (30, 70),
        'Paris': (40, 50),
        'Dijon': (50, 30),
        'Lyon': (50, 0),
        'Lille': (60, 80),
        'Nancy': (80, 50),
        'Grenoble': (70, 0)
    }
    
    for city, (x, y) in positions.items():
        G.add_node(city, x=x, y=y)
    
    edges = [
        ('Rennes', 'Caen', 75),
        ('Rennes', 'Nantes', 45),
        ('Rennes', 'Bordeaux', 130),
        ('Nantes', 'Bordeaux', 90),
        ('Nantes', 'Paris', 110),
        ('Caen', 'Paris', 50),
        ('Caen', 'Lille', 65),
        ('Paris', 'Lille', 70),
        ('Paris', 'Dijon', 60),
        ('Paris', 'Bordeaux', 150),
        ('Bordeaux', 'Lyon', 100),
        ('Dijon', 'Lyon', 70),
        ('Dijon', 'Nancy', 75),
        ('Dijon', 'Grenoble', 75),
        ('Lyon', 'Grenoble', 40),
        ('Lille', 'Paris', 120),
        ('Lille', 'Nancy', 100),
        ('Nancy', 'Grenoble', 80),
        ('Nancy', 'Dijon', 90),
    ]
    
    for u, v, length in edges:
        G.add_edge(u, v, 0, length=length)
        G.add_edge(v, u, 0, length=length)
    
    return G