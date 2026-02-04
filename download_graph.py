import osmnx as ox
import pickle
import os
from pathlib import Path

# Créer le dossier data s'il n'existe pas
DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)


def get_graph(place: str, network_type="drive"):
    """
    Télécharge un graphe depuis OpenStreetMap
    """
    G = ox.graph_from_place(place, network_type=network_type)
    return G


def save_graph(G, filename):
    """
    Sauvegarde le graphe dans le dossier data
    """
    filepath = DATA_DIR / filename
    with open(filepath, 'wb') as f:
        pickle.dump(G, f)
    print(f"Graphe sauvegardé dans {filepath}")
    return filepath



def load_graph(filename):
    path = os.path.join("data", filename)

    # 1) Si c'est un fichier GraphML → OSMnx
    if filename.endswith(".graphml"):
        return ox.load_graphml(path)

    # 2) Si c'est un pickle → pickle
    if filename.endswith(".pkl") or filename.endswith(".pickle"):
        with open(path, "rb") as f:
            return pickle.load(f)

    # 3) Sinon → essayer automatiquement
    try:
        # Essai pickle
        with open(path, "rb") as f:
            return pickle.load(f)
    except Exception:
        pass

    try:
        # Essai graphml
        return ox.load_graphml(path)
    except Exception:
        pass

    raise ValueError(f"Format de fichier non reconnu : {filename}")



def list_saved_graphs():
    """
    Liste tous les graphes sauvegardés dans le dossier data
    """
    if not DATA_DIR.exists():
        return []
    
    # Chercher tous les fichiers (pas de .pkl nécessairement)
    graph_files = [f.name for f in DATA_DIR.iterdir() if f.is_file()]
    return sorted(graph_files)


def get_graph_info(filename):
    """
    Récupère les informations sur un graphe sauvegardé
    """
    try:
        G = load_graph(filename)
        return {
            "nodes": len(G.nodes()),
            "edges": len(G.edges()),
            "name": filename
        }
    except Exception as e:
        return {
            "nodes": "?",
            "edges": "?",
            "name": filename,
            "error": str(e)
        }


def download_and_save(place: str, filename=None, network_type="drive"):
    """
    Télécharge et sauvegarde un graphe
    Si filename n'est pas fourni, utilise le nom du lieu
    """
    print(f"Téléchargement du graphe de {place}...")
    G = get_graph(place, network_type)
    
    if filename is None:
        # Créer un nom de fichier à partir du nom du lieu
        filename = place.replace(", ", "_").replace(" ", "_").lower()
    
    save_graph(G, filename)
    return G


def delete_graph(filename):
    """
    Supprime un graphe sauvegardé
    """
    filepath = DATA_DIR / filename
    if filepath.exists():
        filepath.unlink()
        print(f"Graphe {filename} supprimé")
        return True
    return False