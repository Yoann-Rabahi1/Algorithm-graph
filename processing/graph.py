import numpy as np

def build_graph_from_matrix(matrice):
    graph = {}

    for i in matrice.index:
        graph[i] = []

        for j in matrice.columns:
            if i != j:
                graph[i].append((j, matrice.loc[i, j]))

    return graph
