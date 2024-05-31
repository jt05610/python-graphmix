from __future__ import annotations

from collections.abc import Iterable

from pydantic import BaseModel
from pydantic import Field

from graphmix.chemistry.chemical import Chemical
from graphmix.chemistry.units import Q_
from graphmix.chemistry.units import MassConcentration
from graphmix.chemistry.units import Percent
from graphmix.graph.model import DiGraph


class DimensionalityError(Exception):
    def __init__(self, expected: str, for_: str, got: str):
        self.expected = expected
        self.for_ = for_
        self.got = got

    def __str__(self):
        return (
            f"Expected dimensionality {self.expected} for {self.for_}, "
            f"got {self.got}"
        )


class Composition(BaseModel):
    solutes: dict[Chemical, MassConcentration] = {}
    solvents: dict[Chemical, Percent] = {}

    @property
    def all(self) -> dict:
        return {**self.solutes, **self.solvents}

    @property
    def by_name(self) -> dict[str, MassConcentration | Percent]:
        return {chem.name: conc for chem, conc in self.all.items()}

    def of(self, chem: Chemical | str) -> MassConcentration | Percent:
        if isinstance(chem, str):
            if chem in self.by_name:
                return self.by_name[chem]

        return self.all[chem]


class Solution(BaseModel):
    name: str
    G: DiGraph = Field(default_factory=DiGraph)
    components: dict[str, Chemical | Solution] = {}

    def __getitem__(self, key: str) -> Q_:
        return self.composition.of(key)

    def __hash__(self):
        return hash(self.name)

    def add_entity(self, entity: Chemical | Solution):
        self.components[entity.name] = entity
        self.G.add_node(entity.name)
        return self

    def with_component(
        self,
        component: Chemical | Solution,
        concentration: Q_,
    ):
        if isinstance(component, Solution):
            if concentration.units != "percent":
                raise DimensionalityError(
                    "percent", component.name, concentration.units
                )
        self.add_entity(component)
        self.G.add_edge(component.name, self.name, concentration=concentration)
        return self

    def with_components(self, components: dict[Chemical | Solution, Q_]):
        for component, concentration in components.items():
            self.with_component(component, concentration)
        return self

    def _component_data(self, node: str) -> tuple[Chemical | Solution, Q_]:
        return (
            self.components[node],
            self.G.edges[node, self.name]["concentration"],
        )

    def iter_nodes(self) -> Iterable[tuple[Chemical | str | Solution, Q_]]:
        for node in self.components.keys():
            if node == self.name:
                continue
            component, concentration = self._component_data(node)
            yield component, concentration

    @property
    def composition(self) -> Composition:
        composition = Composition()
        for component, concentration in self.iter_nodes():
            if isinstance(component, Solution):
                sub_composition = component.composition
                for solvent, conc in sub_composition.solvents.items():
                    if solvent in composition.solvents:
                        composition.solvents[solvent] += conc * concentration
                        continue
                    composition.solvents[solvent] = conc * concentration
                for solute, conc in sub_composition.solutes.items():
                    solute_concentration = conc * concentration
                    if solute in composition.solutes:
                        composition.solutes[solute] += solute_concentration
                        continue
                    composition.solutes[solute] = solute_concentration
                continue
            if concentration.units.dimensionality == "[mass] / [length] ** 3":
                composition.solutes[component] = concentration
            if concentration.units == "percent":
                if component in composition.solvents:
                    composition.solvents[component] += concentration
                    continue
                composition.solvents[component] = concentration
        return composition
