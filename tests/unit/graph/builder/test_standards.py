import math

from graphmix.chemistry.units import Q_
from graphmix.graph.builder import standards
from graphmix.location import WellPlate


def test_standard_curve_builder(saline, water):
    bld = (
        standards.StandardCurveBuilder(
            name="BCA",
            final_volume=Q_(100, "uL"),
            grids={"0": WellPlate[96].with_dead_volume(Q_(10, "uL"))},
            stock_grid="0",
            diluent_grid="0",
            out_grid="0",
            steps=standards.BCA_STANDARD_CURVE,
        )
        .with_stock(saline)
        .with_diluent(water)
    )
    proto = bld.build()
    assert len(proto.inputs) == 2

    starting_concentration = proto.nodes["saline"].solution.composition.of(
        "NaCl"
    )
    expected = tuple(
        f * starting_concentration
        for f in standards.dilution_factors(standards.BCA_STANDARD_CURVE)
    )
    actual_concentrations = tuple(
        proto.nodes[f"BCA_{step.ref}"].solution.composition.of("NaCl", "mg/mL")
        for step in standards.BCA_STANDARD_CURVE
    )

    for actual, expect in zip(actual_concentrations, expected, strict=False):
        assert math.isclose(
            actual.to("mg/mL").magnitude,
            expect.to("mg/mL").magnitude,
            rel_tol=1e-3,
        )
