from collections.abc import Callable

import networkx as nx
from matplotlib import pyplot as plt

from graphmix.graph.model import DiGraph


def plot_graph(
    G: DiGraph,
    node_color: str = "#0d9488",
    font_color: str = "#ccfbf1",
    font_size: int = 8,
    node_size: int = 500,
    edge_colors: str = "#042f2e",
    edge_attr: str = "concentration",
    line_width: float = 1.1,
    alpha: float = 0.8,
    ax: plt.Axes = None,
    layout: Callable[[DiGraph], dict] = nx.kamada_kawai_layout,
) -> plt.Axes:
    if ax is None:
        ax = plt.gca()
    ax.set_axis_off()
    base_opts = {
        "G": G,
        "ax": ax,
        "pos": nx.rescale_layout_dict(layout(G), scale=2),
    }

    node_opts = {
        "node_size": node_size,
        "node_color": node_color,
        "edgecolors": edge_colors,
        "linewidths": line_width,
        "alpha": alpha,
        **base_opts,
    }

    node_label_opts = {
        "font_size": font_size,
        "font_color": font_color,
        **base_opts,
    }

    edge_opts = {
        "edge_color": edge_colors,
        "width": line_width,
        "node_size": node_size,
        **base_opts,
    }

    edge_label_opts = {
        "edge_labels": nx.get_edge_attributes(G, edge_attr),
        "font_size": font_size,
        **base_opts,
    }

    nx.draw_networkx_nodes(**node_opts)
    nx.draw_networkx_labels(**node_label_opts)
    nx.draw_networkx_edges(**edge_opts)
    nx.draw_networkx_edge_labels(**edge_label_opts)
    return ax
