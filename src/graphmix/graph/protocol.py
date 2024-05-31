import networkx as nx
from pydantic import BaseModel
from pydantic import Field

from graphmix.chemistry.chemical import Chemical
from graphmix.chemistry.math import dilution
from graphmix.chemistry.units import Concentration
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
    G: DiGraph = Field(default_factory=DiGraph, frozen=False)

    def with_node(
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
        self.G.add_node(node.name)
        return self

    def add_edge(
        self, source: Node, target: Node, weight: Percent
    ) -> "Protocol":
        self.G.add_edge(source.name, target.name, weight=weight)
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
        for component, percent in components.items():
            self.add_edge(
                self.get_node(component),
                new_node,
                weight=percent,
            )
        return self

    def with_dilution(
        self,
        species: Chemical | str,
        source: Node | Solution | str,
        diluent: Node | Solution | str,
        final_volume: Volume,
        final_concentration: Concentration,
        into: LocationSet | str,
    ) -> "Protocol":
        v1 = dilution(
            c1=self.get_node(source).composition.of(species),
            v2=final_volume,
            c2=final_concentration,
        )
        weight = Percent(v1 / final_volume, "%")
        diluent_weight = Percent(100, "%") - weight
        if isinstance(into, str):
            into = self.grids[into]
        position = next(into)
        new_node = Node(
            name=f"{source.name}_diluted_with_{diluent.name}",
            final_volume=final_volume,
            **position.model_dump(),
        ).with_components(
            {
                self.get_node(source): weight,
                self.get_node(diluent): diluent_weight,
            }
        )
        self.add_node(new_node)
        self.add_edge(
            self.get_node(source),
            new_node,
            weight=weight,
        )
        self.add_edge(
            self.get_node(diluent),
            new_node,
            weight=diluent_weight,
        )
        return self

    @property
    def edges(self):
        return self.G.edges

    def write_latex(self, path: str) -> None:
        nx.drawing.write_latex(self.G, path)
