import osmnx as ox

def load_data(path):
    return ox.load_graphml(path)