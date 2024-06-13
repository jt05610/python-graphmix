from collections.abc import Generator

import networkx as nx

from graphmix.chemistry.units import Volume
from graphmix.graph.model import DiGraph


def reverse_topological_sort(G: DiGraph) -> Generator[str, None, None]:
    """Reverse topological sort of the graph."""
    yield from reversed(tuple(nx.topological_sort(G)))


def edge_volume(
    G: DiGraph,
    source: str,
    target: str,
    target_final_volume: Volume,
    target_outgoing: Volume,
) -> float:
    """Determine the volume to transfer from the source to the target."""
    target_total_volume = target_outgoing + target_final_volume
    edge = G.edges[source, target]
    if not edge:
        return 0
    edge_weight = edge["weight"]
    return edge_weight * target_total_volume
