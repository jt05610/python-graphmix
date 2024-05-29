from pydantic import BaseModel

from graphmix.chemistry.units import Percent
from graphmix.chemistry.units import Volume
from graphmix.graph.model import DiGraph
from graphmix.graph.solution import Solution
from graphmix.location import Location
from graphmix.location import LocationSet


class Node(Solution, Location):
    final_volume: Volume

    @property
    def solution(self) -> Solution:
        return Solution(**self.model_dump())

    @property
    def location(self) -> Location:
        return Location(**self.model_dump())


class Protocol(BaseModel):
    grids: dict[str, LocationSet] = {}
    nodes: dict[str, Node] = {}
    G: DiGraph = DiGraph()

    def with_entity(
        self,
        entity: Solution,
        volume: Volume,
        into: LocationSet | str | Location,
    ) -> "Protocol":
        if isinstance(into, str):
            into = next(self.grids[into])
        elif isinstance(into, LocationSet):
            into = next(into)
        new_node = Node(
            final_volume=volume,
            **into.model_dump(),
            **entity.model_dump(),
        )
        self.add_node(new_node)
        return self

    def add_node(self, node: Node) -> "Protocol":
        self.nodes[node.name] = node
        self.G.add_node(node)
        return self

    def get_node(self, n: Node | Solution | str) -> Node:
        match n:
            case Node():
                return n
            case Solution():
                return self.nodes[n.name]
            case str():
                return self.nodes[n]

    def with_node_from(
        self,
        name: str,
        components: dict[Node | Solution | str, Percent],
        into: LocationSet | str,
        final_volume: Volume,
    ) -> "Protocol":
        if isinstance(into, str):
            into = self.grids[into]
        position = next(into)
        node_compositions = {
            self.get_node(component): percent
            for component, percent in components.items()
        }
        new_node = Node(
            name=name,
            final_volume=final_volume,
            **position.model_dump(),
        ).with_components(node_compositions)
        self.add_node(new_node)
        for node, percent in node_compositions.items():
            self.G.add_edge(node, new_node, weight=percent)
        return self

    @property
    def edges(self):
        return self.G.edges
