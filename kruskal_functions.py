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

