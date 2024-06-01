from collections.abc import Generator
from collections.abc import Iterable

from pydantic import BaseModel

from graphmix.chemistry.units import Percent
from graphmix.chemistry.units import Volume
from graphmix.graph.builder.builder import ProtocolBuilder
from graphmix.graph.protocol import Node
from graphmix.graph.protocol import Protocol
from graphmix.graph.solution import Solution
from graphmix.location import LocationSet


class StandardCurveStep(BaseModel):
    ref: str
    factor: float
    source: str = "stock"


BCA_STANDARD_CURVE = (
    StandardCurveStep(ref="A", factor=1),
    StandardCurveStep(ref="B", factor=0.75),
    StandardCurveStep(ref="C", factor=0.5),
    StandardCurveStep(ref="D", source="B", factor=0.5),
    StandardCurveStep(ref="E", source="C", factor=0.5),
    StandardCurveStep(ref="F", source="E", factor=0.5),
    StandardCurveStep(ref="G", source="F", factor=0.5),
    StandardCurveStep(ref="H", source="G", factor=0.5),
    StandardCurveStep(ref="I", factor=0),
)
"""Manufacturer recommended standard curve for the BCA assay. Has 9 points."""


def dilution_factors(
    steps: Iterable[StandardCurveStep],
) -> Generator[float, None, None]:
    factor_dict = {
        "stock": 1,
    }
    for step in steps:
        if step.source not in factor_dict:
            raise ValueError(
                f"Step {step.ref} has an unknown source: {step.source}"
            )
        factor_dict[step.ref] = factor_dict[step.source] * step.factor
        yield factor_dict[step.ref]


RIBOGREEN_STANDARD_CURVE = (
    StandardCurveStep(ref="A", factor=1),
    StandardCurveStep(ref="B", factor=0.5),
    StandardCurveStep(ref="C", source="B", factor=0.2),
    StandardCurveStep(ref="D", source="C", factor=0.2),
    StandardCurveStep(ref="E", factor=0),
)
"""Manufacturer recommended standard curve for the RiboGreen™ assay. Has 5 points."""


def get_grid(
    grids: dict[str, LocationSet], grid: str | LocationSet
) -> LocationSet:
    return grid if isinstance(grid, LocationSet) else grids[grid]


class StandardCurveBuilder(ProtocolBuilder):
    name: str
    steps: tuple[StandardCurveStep, ...] | None = None
    diluent: Solution
    stock: Solution
    grids: dict[str, LocationSet]
    _proto: Protocol
    _curve_dict: dict[str, Solution]
    final_volume: Volume

    def __init__(
        self,
        name: str,
        final_volume: Volume,
        grids: dict[str, LocationSet],
        stock_grid: str | LocationSet,
        diluent_grid: str | LocationSet,
        out_grid: str | LocationSet,
        steps: tuple[StandardCurveStep, ...] | None = None,
    ):
        self.name = name
        self.steps = steps
        self.stock_grid = get_grid(grids, stock_grid)
        self.diluent_grid = get_grid(grids, diluent_grid)
        self.out_grid = get_grid(grids, out_grid)
        self.grids = grids
        self._proto = Protocol(
            name=self.name,
            grids=self.grids,
        )
        self._curve_dict = {}
        self.final_volume = final_volume

    def with_step(self, step: StandardCurveStep) -> "StandardCurveBuilder":
        if self.steps is None:
            self.steps = (step,)
        else:
            self.steps += (step,)
        return self

    def with_diluent(
        self, diluent: Solution, final_volume: Volume | None = None
    ) -> "StandardCurveBuilder":
        if final_volume is None:
            final_volume = self.diluent_grid.dead_volume
        self.diluent = diluent
        self._proto = self._proto.with_node(
            entity=self.diluent,
            volume=final_volume,
            into=self.diluent_grid,
        )
        self._curve_dict["diluent"] = self._proto.get_node(self.diluent)
        return self

    def with_stock(
        self, stock: Solution, final_volume: Volume | None = None
    ) -> "StandardCurveBuilder":
        if final_volume is None:
            final_volume = self.stock_grid.dead_volume
        self.stock = stock
        self._proto = self._proto.with_node(
            entity=self.stock,
            volume=final_volume,
            into=self.stock_grid,
        )
        self._curve_dict["stock"] = self._proto.get_node(self.stock)
        return self

    def _get_step_source(self, step: StandardCurveStep) -> Node:
        if step.factor == 0:
            return self._curve_dict["diluent"]
        return self._curve_dict.get(step.source)

    def _create_step(self, step: StandardCurveStep):
        source = self._get_step_source(step).solution
        created_solution = Solution(name=f"{self.name}_{step.ref}")
        source_percent = Percent(100 * step.factor, "%")
        diluent_percent = Percent(100, "%") - source_percent

        if source_percent == Percent(0, "%"):
            created_solution = created_solution.with_component(
                component=self.diluent, concentration=Percent(100, "%")
            )
            self._proto = self._proto.with_node(
                entity=created_solution,
                volume=self.final_volume,
                into=self.out_grid,
            ).with_edge(
                source=source,
                target=created_solution,
                weight=Percent(100, "%"),
            )
            self._curve_dict[step.ref] = self._proto.get_node(created_solution)
            return

        created_solution = created_solution.with_component(
            component=source, concentration=source_percent
        ).with_component(component=self.diluent, concentration=diluent_percent)

        self._proto = (
            self._proto.with_node(
                entity=created_solution,
                volume=self.final_volume,
                into=self.out_grid,
            )
            .with_edge(
                source=source,
                target=created_solution,
                weight=source_percent,
            )
            .with_edge(
                source=self.diluent,
                target=created_solution,
                weight=diluent_percent,
            )
        )
        self._curve_dict[step.ref] = self._proto.get_node(created_solution)

    def build(self) -> Protocol:
        for step in self.steps:
            self._create_step(step)
        return self._proto
