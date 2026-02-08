import streamlit as st
import math

# ============================================================
# 1) Vérification générale du graphe
# ============================================================

def validate_graph(G, source=None, target=None, weight_key="length"):
    """
    Vérifie que le graphe est valide pour n'importe quel algorithme.
    - graphe chargé
    - nœuds et arêtes présents
    - poids présents (si utilisés)
    - source et cible valides
    """

    if G is None:
        st.error("❌ Aucun graphe chargé.")
        st.stop()

    if len(G.nodes()) == 0:
        st.error("❌ Le graphe ne contient aucun nœud.")
        st.stop()

    if len(G.edges()) == 0:
        st.error("❌ Le graphe ne contient aucune arête.")
        st.stop()

    # Vérification des poids
    for u, v, data in G.edges(data=True):
        if weight_key not in data:
            st.error(f"❌ L'arête {u} → {v} n'a pas de poids '{weight_key}'.")
            st.stop()

    # Vérification source / cible
    if source is not None and source not in G.nodes():
        st.error(f"❌ Le nœud source '{source}' n'existe pas dans le graphe.")
        st.stop()

    if target is not None and target not in G.nodes():
        st.error(f"❌ Le nœud cible '{target}' n'existe pas dans le graphe.")
        st.stop()

    if source is not None and target is not None and source == target:
        st.error("❌ Le nœud de départ et d'arrivée doivent être différents.")
        st.stop()


# ============================================================
# 2) Vérification spécifique Dijkstra
# ============================================================

def validate_dijkstra(G, weight_key="length"):
    """
    Vérifie que Dijkstra peut être appliqué :
    - aucun poids négatif
    """

    for _, _, data in G.edges(data=True):
        if data.get(weight_key, 0) < 0:
            st.error("❌ Dijkstra ne supporte pas les poids négatifs. Utilisez Bellman‑Ford.")
            st.stop()


# ============================================================
# 3) Vérification spécifique Bellman-Ford
# ============================================================

def validate_bellman_ford(neg_cycle):
    """
    Vérifie qu'il n'y a pas de cycle négatif.
    """

    if neg_cycle:
        st.error("❌ Cycle négatif détecté : les distances ne sont pas fiables.")
        st.stop()


# ============================================================
# 4) Vérification du chemin final (Dijkstra / Bellman-Ford)
# ============================================================

def validate_final_distance(dist, target):
    """
    Vérifie que la distance finale est valide.
    """

    if target not in dist:
        st.error("❌ La distance finale n'a pas été calculée pour la cible.")
        st.stop()

    if dist[target] == math.inf:
        st.warning("⚠️ Aucun chemin trouvé vers la cible.")
        st.stop()


# ============================================================
# 5) Vérification des coordonnées pour Plotly
# ============================================================

def validate_coordinates(G):
    """
    Vérifie que tous les nœuds ont des coordonnées (x,y).
    """

    for n in G.nodes():
        if "x" not in G.nodes[n] or "y" not in G.nodes[n]:
            st.error(f"❌ Le nœud '{n}' n'a pas de coordonnées (x,y).")
            st.stop()

    for u, v in G.edges():
        if "x" not in G.nodes[u] or "x" not in G.nodes[v]:
            st.error(f"❌ Impossible d'afficher l'arête {u} → {v} : coordonnées manquantes.")
            st.stop()


# ============================================================
# 6) Vérification pour Kruskal / Prim
# ============================================================

def validate_mst_graph(G, weight_key="length"):
    """
    Vérifie que le graphe est valide pour un algorithme MST :
    - graphe connecté (optionnel)
    - poids présents
    """

    validate_graph(G, weight_key=weight_key)

    # Optionnel : vérifier la connexité
    # (Kruskal/Prim fonctionnent même sur graphes non connexes,
    # mais l'ACPM ne couvrira pas tout)
    if not G:
        st.error("❌ Graphe invalide pour un MST.")
        st.stop()


# ============================================================
# 7) Vérification pour DFS / BFS
# ============================================================

def validate_start_node(G, start):
    """
    Vérifie que le nœud de départ existe.
    """

    if start not in G.nodes():
        st.error(f"❌ Le nœud de départ '{start}' n'existe pas dans le graphe.")
        st.stop()
