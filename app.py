import streamlit as st

st.set_page_config(page_title="Visualisation d'Algorithmes de Graphes", layout="wide")

# -----------------------------------------------------------
# TITRE PRINCIPAL
# -----------------------------------------------------------
st.title("🧭 Plateforme Interactive de Visualisation d'Algorithmes de Graphes")

st.markdown("""
Bienvenue dans cette application interactive dédiée à l’exploration visuelle des **algorithmes fondamentaux de théorie des graphes**.

Ici, tu peux :

- Charger des **graphes réels** depuis OpenStreetMap  
- Utiliser des **graphes de test pédagogiques**  
- Visualiser **pas à pas** le fonctionnement des algorithmes  
- Comprendre intuitivement leurs mécanismes internes  
- Comparer les résultats entre différentes méthodes  

Cette plateforme a été conçue pour être **pédagogique**, **intuitive** et **visuellement cohérente**.
""")

st.divider()

# -----------------------------------------------------------
# SECTION : COMMENT UTILISER L’INTERFACE
# -----------------------------------------------------------
st.header("🛠️ Comment utiliser l’interface")

st.markdown("""
Chaque page dédiée à un algorithme suit la même structure :

---

### 1️⃣ **Chargement du graphe (barre latérale)**  
Dans la colonne de gauche, tu peux choisir :

- **Graphe de test** : un petit réseau de villes françaises  
- **Graphe OSM** : un graphe réel téléchargé depuis OpenStreetMap  

Une fois chargé, l’application affiche :

- le nombre de nœuds  
- le nombre d’arêtes  
- la possibilité de choisir un **nœud de départ** (pour Dijkstra, Prim, BFS, DFS)  
- un réglage de **vitesse d’animation**

---

### 2️⃣ **Contrôles de l’algorithme (zone principale)**

Chaque algorithme propose les mêmes boutons :

- ▶️ **Démarrer** : lance l’animation pas à pas  
- ⏸️ **Pause** : met l’animation en pause  
- ▶️ **Reprendre** : continue l’animation  
- ⏩ **Étape** : avance d’une étape (mode pause)  
- ⏹️ **Reset** : réinitialise l’algorithme  
- ⚡ **Calcul Direct** : exécute l’algorithme instantanément (si disponible)

---

### 3️⃣ **Visualisation graphique**

L’algorithme est représenté avec :

- des **nœuds colorés** selon leur état  
- des **arêtes mises en évidence** (explorées, sélectionnées, finales)  
- un **fond bleu clair** pour une lecture agréable  
- des **tailles de nœuds adaptées** :
  - grands pour les graphes de test  
  - petits pour les graphes OSMnx  

Chaque étape met en avant :

- le nœud courant  
- les arêtes candidates  
- les arêtes retenues  
- les distances / clés / poids selon l’algorithme  

---

### 4️⃣ **Résultats finaux**

À la fin d’un calcul (direct ou animé), tu obtiens :

- le **chemin optimal** (Dijkstra, Bellman–Ford, BFS, DFS)  
- l’**arbre couvrant minimal** (Prim / Kruskal)  
- la **matrice des distances** (Dijkstra, Floyd–Warshall, Bellman–Ford)  
- la **matrice des clés** (Prim)  
- un **tableau détaillé** des arêtes sélectionnées  
- un **graphe final clair et lisible**

---
""")

st.divider()

# -----------------------------------------------------------
# SECTION : DESCRIPTION DES ALGORITHMES
# -----------------------------------------------------------
st.header("📚 Présentation des algorithmes disponibles")

st.markdown("""
## 🔵 Dijkstra — Plus court chemin
- Trouve le **chemin le plus court** entre deux nœuds.  
- Animation détaillée : distances, nœud courant, relaxation, matrice des distances.  
- Idéal pour comprendre la logique des files de priorité.

👉 Page : **Dijkstra**

---

## 🟢 Prim — Arbre couvrant minimal (ACPM)
- Construit un arbre couvrant minimal en partant d’un nœud.  
- Animation détaillée : clés, parents, file de priorité, arêtes ajoutées.  
- Matrice des clés disponible pour les graphes de test.

👉 Page : **Prim**

---

## 🟣 Kruskal — Arbre couvrant minimal (ACPM)
- Construit un ACPM en triant les arêtes par poids.  
- Animation détaillée : union-find, arêtes triées, arêtes retenues.  
- Très visuel et intuitif.

👉 Page : **Kruskal**

---

## 🟠 Bellman–Ford — Plus court chemin avec poids négatifs
- Trouve les plus courts chemins même en présence de **poids négatifs**.  
- Détecte les **cycles négatifs**.  
- Animation étape par étape des relaxations.

👉 Page : **Bellman–Ford**

---

## 🔴 Floyd–Warshall — Tous les plus courts chemins
- Calcule les distances minimales **entre tous les couples de nœuds**.  
- Produit une **matrice complète des distances**.  
- Très utile pour les graphes denses.

👉 Page : **Floyd–Warshall**

---

## 🟡 BFS — Parcours en largeur
- Explore un graphe **niveau par niveau**.  
- Idéal pour les graphes non pondérés.  
- Animation simple et intuitive.

👉 Page : **BFS**

---

## 🟤 DFS — Parcours en profondeur
- Explore un graphe en allant **le plus loin possible** avant de revenir en arrière.  
- Très utile pour la détection de cycles, composantes connexes, etc.

👉 Page : **DFS**

---

## 🔷 PERT / CPM — Gestion de projet
- Analyse des tâches, dépendances et durées.  
- Calcul du **chemin critique**.  
- Visualisation du graphe PERT et des marges.

👉 Page : **PERT / CPM**

---
""")

st.divider()

# -----------------------------------------------------------
# SECTION : CONSEILS D’UTILISATION
# -----------------------------------------------------------
st.header("💡 Conseils pour bien explorer les algorithmes")

st.markdown("""
### ✔️ Utilise d’abord les **graphes de test**
Ils sont petits, lisibles, et parfaits pour comprendre les animations.

### ✔️ Passe ensuite aux **graphes OSM**
Tu verras comment les algorithmes se comportent sur des réseaux réels.

### ✔️ Joue avec la **vitesse d’animation**
Ralentis pour comprendre, accélère pour parcourir rapidement.

### ✔️ Compare les algorithmes
- Dijkstra / Bellman–Ford / Floyd–Warshall → plus courts chemins  
- Prim / Kruskal → arbres couvrants minimaux  
- BFS / DFS → exploration structurelle  
- PERT → gestion de projet  

### ✔️ Utilise le **Calcul Direct**
Pour vérifier rapidement un résultat ou comparer avec l’animation.

""")

st.divider()

# -----------------------------------------------------------
# SECTION : NAVIGATION
# -----------------------------------------------------------
st.header("🧭 Navigation")

st.markdown("""
Tu peux accéder aux algorithmes via le menu **à gauche** :

- **Dijkstra**  
- **Prim**  
- **Kruskal**  
- **Bellman–Ford**  
- **Floyd–Warshall**  
- **BFS**  
- **DFS**  
- **PERT / CPM**  

Chaque page est indépendante et suit la même logique d’utilisation.
""")

st.success("Tu es prêt à explorer les algorithmes de graphes de manière interactive ! 🚀")
