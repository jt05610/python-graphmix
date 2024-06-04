from __future__ import annotations

from collections.abc import Callable
from collections.abc import Generator

import networkx as nx
from pydantic import BaseModel
from pydantic import Field

from graphmix.chemistry.chemical import Chemical
from graphmix.chemistry.units import Q_
from graphmix.chemistry.units import MassConcentration
from graphmix.chemistry.units import MolarConcentration
from graphmix.chemistry.units import Percent
from graphmix.graph.model import DiGraph


def chain_functions(*funcs: Callable[[Q_], Q_]) -> Callable[[Q_], Q_]:
    def chain(x: Q_) -> Q_:
        for f in funcs:
            x = f(x)
        return x

    return chain


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
        return {
            chem.name if isinstance(chem, Chemical) else chem: conc
            for chem, conc in self.all.items()
        }

    def of(
        self,
        chem: Chemical | str,
        to_unit: str | None = None,
        compact: bool = False,
    ) -> MassConcentration | MolarConcentration | Percent:
        if isinstance(chem, str):
            idx = self.by_name
        else:
            idx = self.all
        ret = idx.get(chem, Q_(0, "mg/mL" if to_unit is None else to_unit))
        if to_unit is not None:
            test_q = Q_(1, to_unit)
            if test_q.dimensionality != ret.dimensionality:
                if (
                    test_q.dimensionality == "[mass] / [length] ** 3"
                    and ret.dimensionality == "[substance] / [length] ** 3"
                ):
                    ret = ret * chem.molar_mass
            ret = ret.to(to_unit)
        if compact:
            ret = ret.to_compact()
        return ret

    def __eq__(self, other: Composition) -> bool:
        for k, v in self.all.items():
            if v != other.of(k):
                return False
        return True


class Solution(BaseModel):
    name: str
    G: DiGraph = Field(default_factory=DiGraph, frozen=False)
    components: dict[str, Chemical | Solution] = {}

    def __getitem__(self, key: str) -> Q_:
        return self.composition.of(key)

    def __hash__(self):
        return hash(self.name)

    @property
    def chemicals(self) -> Generator[tuple[str, Chemical], None, None]:
        for k, v in self.components.items():
            if isinstance(v, Chemical):
                yield k, v

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
        if isinstance(component, Solution):
            self.G = nx.compose(self.G, component.G)
            self.components.update(dict(component.chemicals))

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

    def in_edges(
        self, node: str
    ) -> Generator[tuple[str, str, Q_ | float], None, None]:
        for source, _, conc in self.G.in_edges(node, data="concentration"):
            match conc.units:
                case "percent":
                    yield source, node, conc.to("%").magnitude / 100
                case _:
                    yield source, node, conc

    @property
    def composition(self) -> Composition:
        makeup = {}

        def traverse(node: str, factor: float = 1.0):
            traversed = False
            for source, _, conc in self.in_edges(node):
                traversed = True
                traverse(source, conc * factor)
            if not traversed:
                if node not in makeup:
                    makeup[node] = factor
                else:
                    makeup[node] += factor

        traverse(self.name)

        composition = Composition()
        chem_dict = dict(self.chemicals)
        for k, v in makeup.items():
            chem = chem_dict[k]
            if isinstance(v, float):
                composition.solvents[chem] = Percent(100 * v, "%")
                continue
            composition.solutes[chem] = v
        return composition

    def dilute_with(self, solvent: Chemical, ratio: float) -> Solution:
        if not 0 < ratio < 1:
            raise ValueError("Dilution ratio must be between 0 and 1")

        return (
            Solution(name=f"{self.name} d/ {solvent.name}")
            .with_component(self, Q_(ratio * 100, "%"))
            .with_component(solvent, Q_((1 - ratio) * 100, "%"))
        )
