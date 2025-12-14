import os
import osmnx as ox

custom_filter = '["railway"~"rail|subway|tram"]'

G_idf = ox.graph_from_place(
    "Île-de-France, France",
    custom_filter=custom_filter
)

print("Dossier courant :", os.getcwd())
print(f"Nombre de nœuds : {G_idf.number_of_nodes()}")
print(f"Nombre d’arêtes : {G_idf.number_of_edges()}")

ox.save_graphml(G_idf, "../data/idf_rail.graphml")
print("✅ Graphe ferroviaire sauvegardé")
