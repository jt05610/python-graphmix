import networkx as nx
from pydantic import BaseModel
from pydantic import Field

from graphmix.chemistry.chemical import Chemical
from graphmix.chemistry.dilution import dilution
from graphmix.chemistry.units import Concentration
from graphmix.chemistry.units import Percent
from graphmix.chemistry.units import Volume
from graphmix.graph.model import DiGraph
from graphmix.graph.node import Node
from graphmix.graph.solution import Solution
from graphmix.location import Location
from graphmix.location import LocationSet


class Protocol(BaseModel):
    grids: dict[str, LocationSet] = {}
    nodes: dict[str, Node] = {}
    chemicals: dict[str, Chemical] = {}
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
            solution=entity,
            location=into,
        )
        self.add_node(new_node)
        self.chemicals.update(dict(entity.chemicals))
        return self

    def with_edge(
        self, source: str | Solution, target: str | Solution, weight: Percent
    ) -> "Protocol":
        source = self.get_node(source)
        target = self.get_node(target)
        self.add_edge(source, target, weight)
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
        solution = Solution(name=name).with_components(node_compositions)
        new_node = Node(
            solution=solution,
            final_volume=final_volume,
            location=position,
        )
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
        if isinstance(species, str):
            species = self.chemicals[species]
        v1 = dilution(
            c1=self.get_node(source).solution.composition.of(species),
            v2=final_volume,
            c2=final_concentration,
        )
        weight = Percent(v1 / final_volume, "%")
        diluent_weight = Percent(100, "%") - weight
        if isinstance(into, str):
            into = self.grids[into]
        position = next(into)
        solution = Solution(
            name=f"{source.name}_diluted_with_{diluent.name}"
        ).with_component(species, final_concentration)
        new_node = Node(
            final_volume=final_volume,
            location=position,
            solution=solution,
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

    @property
    def inputs(self) -> tuple[Node, ...]:
        return tuple(
            self.get_node(n) for n, deg in self.G.in_degree if not deg
        )

    @property
    def outputs(self) -> tuple[Node, ...]:
        return tuple(
            self.get_node(n) for n, deg in self.G.out_degree if not deg
        )
