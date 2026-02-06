import plotly.graph_objects as go
import heapq

def plot_kruskal_mst(G, mst_edges):
    all_edge_x, all_edge_y = [], []
    for u, v in G.edges():
        x0, y0 = G.nodes[u]['x'], G.nodes[u]['y']
        x1, y1 = G.nodes[v]['x'], G.nodes[v]['y']
        all_edge_x += [x0, x1, None]
        all_edge_y += [y0, y1, None]

    all_edge_trace = go.Scatter(
        x=all_edge_x, y=all_edge_y,
        mode='lines',
        line=dict(width=0.5, color="#e0e0e0"),
        hoverinfo='none'
    )

    all_node_x, all_node_y = [], []
    for node, data in G.nodes(data=True):
        all_node_x.append(data['x'])
        all_node_y.append(data['y'])

    all_nodes_trace = go.Scatter(
        x=all_node_x, y=all_node_y,
        mode='markers',
        marker=dict(size=2, color="#f0f0f0"),
        hoverinfo='none'
    )

    mst_x, mst_y = [], []
    for u, v, w in mst_edges:
        x0, y0 = G.nodes[u]['x'], G.nodes[u]['y']
        x1, y1 = G.nodes[v]['x'], G.nodes[v]['y']
        mst_x += [x0, x1, None]
        mst_y += [y0, y1, None]

    mst_trace = go.Scatter(
        x=mst_x, y=mst_y,
        mode='lines',
        line=dict(width=6, color="green"),
        hoverinfo='none'
    )

    fig = go.Figure([all_edge_trace, all_nodes_trace, mst_trace])
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=600
    )
    return fig

def plot_kruskal_step(G, step):
    """
    step attendu:
      - current_edge: (u,v,w)
      - accepted: bool
      - mst_edges: [(u,v,w), ...]
    """
    current_edge = step.get("current_edge")
    accepted = step.get("accepted", False)
    mst_edges = step.get("mst_edges", [])

    # Fond: toutes les arêtes en gris clair
    all_edge_x, all_edge_y = [], []
    for u, v in G.edges():
        x0, y0 = G.nodes[u]['x'], G.nodes[u]['y']
        x1, y1 = G.nodes[v]['x'], G.nodes[v]['y']
        all_edge_x += [x0, x1, None]
        all_edge_y += [y0, y1, None]

    all_edge_trace = go.Scatter(
        x=all_edge_x, y=all_edge_y,
        mode='lines',
        line=dict(width=0.5, color="#e0e0e0"),
        hoverinfo='none'
    )

    # Tous les noeuds en gris clair
    all_node_x, all_node_y = [], []
    for node, data in G.nodes(data=True):
        all_node_x.append(data['x'])
        all_node_y.append(data['y'])

    all_nodes_trace = go.Scatter(
        x=all_node_x, y=all_node_y,
        mode='markers',
        marker=dict(size=2, color="#f0f0f0"),
        hoverinfo='none'
    )

    # MST courant en vert
    mst_x, mst_y = [], []
    for u, v, w in mst_edges:
        x0, y0 = G.nodes[u]['x'], G.nodes[u]['y']
        x1, y1 = G.nodes[v]['x'], G.nodes[v]['y']
        mst_x += [x0, x1, None]
        mst_y += [y0, y1, None]

    mst_trace = go.Scatter(
        x=mst_x, y=mst_y,
        mode='lines',
        line=dict(width=5, color="green"),
        hoverinfo='none'
    )

    # Arête courante (jaune si en cours, rouge si refusée, vert si acceptée)
    cur_trace = None
    if current_edge is not None:
        u, v, w = current_edge
        x0, y0 = G.nodes[u]['x'], G.nodes[u]['y']
        x1, y1 = G.nodes[v]['x'], G.nodes[v]['y']

        if accepted:
            c = "green"
        else:
            c = "red"

        cur_trace = go.Scatter(
            x=[x0, x1], y=[y0, y1],
            mode='lines',
            line=dict(width=7, color=c),
            hoverinfo='none'
        )

    traces = [all_edge_trace, all_nodes_trace, mst_trace]
    if cur_trace is not None:
        traces.append(cur_trace)

    fig = go.Figure(traces)
    fig.update_layout(
        showlegend=False,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        height=600
    )
    return fig

import math
from algorithm import UnionFind

def kruskal_steps_osmnx(G, weight="length"):
    edges = []
    for u, v, data in G.edges(keys=False, data=True):
        w = data.get(weight, math.inf)
        if w < math.inf:
            edges.append((u, v, w))

    edges.sort(key=lambda x: x[2])

    uf = UnionFind(G.nodes)
    mst_edges = []
    total_cost = 0.0

    for idx, (u, v, w) in enumerate(edges):
        accepted = uf.union(u, v)
        if accepted:
            mst_edges.append((u, v, w))
            total_cost += w

        yield {
            "idx": idx,
            "total_edges": len(edges),
            "current_edge": (u, v, w),
            "accepted": accepted,
            "mst_edges": list(mst_edges),
            "total_cost": total_cost,
        }

        if len(mst_edges) >= max(0, len(G.nodes) - 1):
            break
