import heapq
import plotly.graph_objects as go
import networkx as nx

# ---------------------------------------------------------
# Affichage simple du graphe
# ---------------------------------------------------------
def plot_graph_plotly(G, is_test_graph=False):

    if all('x' in G.nodes[n] and 'y' in G.nodes[n] for n in G.nodes()):
        pos = {n: (G.nodes[n]['x'], G.nodes[n]['y']) for n in G.nodes()}
    else:
        pos = nx.spring_layout(G, seed=42)

    edge_x, edge_y, edge_labels = [], [], []

    for u, v, data in G.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]

        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

        if is_test_graph and "length" in data:
            edge_labels.append(
                go.Scatter(
                    x=[(x0 + x1) / 2],
                    y=[(y0 + y1) / 2],
                    text=[str(data["length"])],
                    mode="text",
                    textfont=dict(size=14, color="black"),
                    hoverinfo="skip"
                )
            )

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode="lines",
        line=dict(width=1, color="#BBBBBB"),
        hoverinfo="none"
    )

    node_x, node_y = [], []
    for n in G.nodes():
        x, y = pos[n]
        node_x.append(x)
        node_y.append(y)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text" if is_test_graph else "markers",
        text=[str(n) for n in G.nodes()] if is_test_graph else None,
        textposition="top center",
        marker=dict(
            size=22 if is_test_graph else 8,
            color="#1f77b4",
            line=dict(width=2 if is_test_graph else 0.5, color="black")
        ),
        hoverinfo="text"
    )

    fig = go.Figure([edge_trace, node_trace])
    for lbl in edge_labels:
        fig.add_trace(lbl)

    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        plot_bgcolor="white"
    )

    return fig




# ---------------------------------------------------------
# Graphe avec start / end
# ---------------------------------------------------------
def plot_graph_with_points(G, start_node, end_node, is_test_graph=False):

    # Récupération des positions
    if all('x' in G.nodes[n] and 'y' in G.nodes[n] for n in G.nodes()):
        pos = {n: (G.nodes[n]['x'], G.nodes[n]['y']) for n in G.nodes()}
    else:
        pos = nx.spring_layout(G, seed=42)

    edge_x, edge_y, edge_labels = [], [], []

    # --- Arêtes (même style que plot_final_path) ---
    for u, v, data in G.edges(data=True):
        x0, y0 = pos[u]
        x1, y1 = pos[v]

        edge_x += [x0, x1, None]
        edge_y += [y0, y1, None]

        if is_test_graph and "length" in data:
            edge_labels.append(
                go.Scatter(
                    x=[(x0 + x1) / 2],
                    y=[(y0 + y1) / 2],
                    text=[str(data["length"])],
                    mode="text",
                    textfont=dict(size=22, color="white"),
                    hoverinfo="skip"
                )
            )

    edge_trace = go.Scatter(
        x=edge_x, y=edge_y,
        mode="lines",
        line=dict(width=2, color="#e0e0e0"),  # même couleur que final_path
        hoverinfo="none"
    )

    # --- Nœuds (même style que plot_final_path) ---
    node_x, node_y, node_color, node_size, labels = [], [], [], [], []

    for n in G.nodes():
        x, y = pos[n]
        node_x.append(x)
        node_y.append(y)
        labels.append(str(n))

        if n == start_node:
            node_color.append("green")
            node_size.append(55)
        elif n == end_node:
            node_color.append("red")
            node_size.append(55)
        else:
            node_color.append("black")  # même style que final_path
            node_size.append(45)

    node_trace = go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text" if is_test_graph else "markers",
        text=labels if is_test_graph else None,
        textposition="middle center",
        marker=dict(
            size=node_size,
            color=node_color,
            line=dict(width=4, color="white")  # même outline que final_path
        ),
        textfont=dict(size=12, color="white", family="Arial Black"),
        hoverinfo="text"
    )

    # --- Construction de la figure ---
    fig = go.Figure([edge_trace, node_trace])

    for lbl in edge_labels:
        fig.add_trace(lbl)

    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=600,
        plot_bgcolor="lightblue"
    )

    return fig