from __future__ import annotations

from collections.abc import Iterable

from pydantic import BaseModel

from graphmix.chemistry.chemical import Chemical
from graphmix.chemistry.units import Q_
from graphmix.chemistry.units import MassConcentration
from graphmix.chemistry.units import MolarConcentration
from graphmix.chemistry.units import Percent
from graphmix.chemistry.units import Volume
from graphmix.graph.graph import DiGraph


class Composition(BaseModel):
    solutes: dict[Chemical | str, MassConcentration | MolarConcentration] = {}
    solvents: dict[Chemical | str, Percent] = {}

    def concentration_of(
        self, node: str
    ) -> MassConcentration | MolarConcentration:
        return self.nodes[node].concentration


class Solution(BaseModel):
    name: str
    G: DiGraph = DiGraph()
    components: dict[str, Chemical | Solution] = {}

    def add_entity(self, entity: Chemical):
        self.components[entity.name] = entity
        self.G.add_node(entity.name)
        return self

    def with_component(
        self,
        solute: Chemical,
        concentration: MassConcentration | MolarConcentration | Volume,
    ):
        if isinstance(solute, Chemical):
            self.add_entity(solute)
        self.G.add_edge(solute.name, "root", concentration=concentration)
        return self

    def with_components(self, components: dict[Chemical, Q_]):
        for component, concentration in components.items():
            self.with_component(component, concentration)
        return self

    def _component_data(self, node: str) -> tuple[Chemical, Q_]:
        return (
            self.components[node],
            self.G.edges[node, "root"]["concentration"],
        )

    def iter_nodes(
        self,
    ) -> Iterable[
        tuple[
            str,
            tuple[
                Chemical | str,
                MassConcentration | MolarConcentration | Percent,
            ],
        ]
    ]:
        for node in self.G.nodes:
            if node == "root":
                continue
            component, concentration = self._component_data(node)
            if (
                concentration.units.dimensionality == "[mass] / [length] **3"
                or concentration.units.dimensionality
                == "[substance] / [length] **3"
            ):
                label = "solutes"
            else:
                label = "solvents"
            yield label, (component, concentration)

    @property
    def composition(self) -> Composition:
        composition = Composition()
        for label, (component, concentration) in self.iter_nodes():
            getattr(composition, label)[component] = concentration
        return composition
