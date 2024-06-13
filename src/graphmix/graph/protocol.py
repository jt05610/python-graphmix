from collections.abc import Generator

import networkx as nx
from pydantic import BaseModel
from pydantic import Field

from graphmix.chemistry.chemical import Chemical
from graphmix.chemistry.dilution import dilution
from graphmix.chemistry.units import Q_
from graphmix.chemistry.units import Concentration
from graphmix.chemistry.units import Percent
from graphmix.chemistry.units import Volume
from graphmix.graph.analysis import edge_volume
from graphmix.graph.analysis import reverse_topological_sort
from graphmix.graph.model import DiGraph
from graphmix.graph.node import Node
from graphmix.graph.solution import Solution
from graphmix.location import Location
from graphmix.location import LocationSet


class Protocol(BaseModel):
    grids: dict[str, LocationSet] = {}
    nodes: dict[str, Node] = {}
    chemicals: dict[str, Chemical] = {}
    G: DiGraph = Field(default_factory=DiGraph)
    initial_volumes: dict[str, Volume] = {}
    outgoing_volumes: dict[str, Volume] = {}

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
        return self

    @property
    def reverse_topo_nodes(self) -> Generator[Node, None, None]:
        for n in reverse_topological_sort(self.G):
            yield self.nodes[n]

    def _update_volumes(self):
        for node in self.reverse_topo_nodes:
            if len(self.G.in_edges(node.name)) == 0:
                self.initial_volumes[node.name] = (
                    node.final_volume + self.outgoing_volumes[node.name]
                )
                continue
            for u, v in self.G.in_edges(node.name):
                vol = edge_volume(
                    self.G,
                    u,
                    v,
                    self.nodes[v].final_volume,
                    self.outgoing_volumes[v],
                )
                self.outgoing_volumes[u] += vol
                self.G.edges[u, v]["volume"] = vol

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
        self.chemicals.update(dict(node.solution.chemicals))
        self.initial_volumes[node.name] = Q_(0, "uL")
        self.outgoing_volumes[node.name] = Q_(0, "uL")
        return self

    def add_edge(
        self, source: Node, target: Node, weight: Percent
    ) -> "Protocol":
        as_prop = weight.to("dimensionless").magnitude
        self.G.add_edge(source.name, target.name, weight=as_prop)
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
        name: str | None = None,
    ) -> "Protocol":
        if isinstance(species, str):
            species = self.chemicals[species]
        source_node = self.get_node(source)
        c1 = source_node.solution.composition.of(species)
        v1 = dilution(
            c1=c1,
            v2=final_volume,
            c2=final_concentration,
        )
        dilution_factor = (
            (final_concentration / c1).to("dimensionless").magnitude
        )
        dil = self.get_node(diluent).solution
        solution = source_node.solution.dilute_with(
            name=name,
            solvent=dil,
            ratio=dilution_factor,
        )

        weight = Percent(v1 / final_volume, "%")
        diluent_weight = Percent(100, "%") - weight
        if isinstance(into, str):
            into = self.grids[into]
        position = next(into)
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

    def solve(self) -> "Protocol":
        self._update_volumes()
        return self
