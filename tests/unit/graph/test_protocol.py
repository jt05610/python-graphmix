from graphmix.chemistry.chemical import Chemical
from graphmix.chemistry.units import Q_
from graphmix.graph.protocol import Protocol
from graphmix.graph.solution import Solution
from graphmix.location import WellPlate


def saline() -> Solution:
    nacl = Chemical(
        name="NaCl",
        formula="NaCl",
        molar_mass=58.44,
    )
    water = Chemical(
        name="Water",
        formula="H2O",
        molar_mass=18.01528,
    )
    return Solution(name="saline").with_components(
        {
            nacl: Q_(1, "mg/mL"),
            water: Q_(100, "%"),
        }
    )


def h20() -> Solution:
    water = Chemical(
        name="Water",
        formula="H2O",
        molar_mass=18.01528,
    )
    return Solution(name="water").with_components(
        {
            water: Q_(100, "%"),
        }
    )


def test_with_entity():

    protocol = Protocol(
        grids={"0": WellPlate[96]},
    ).with_node(
        entity=saline(),
        into="0",
        volume=Q_(100, "uL"),
    )

    assert protocol.nodes["saline"].final_volume == Q_(100, "uL")
    assert protocol.nodes["saline"].location == WellPlate[96][0]
    print(protocol.nodes["saline"].solution)


def test_with_node_from():
    sal = saline()
    protocol = (
        Protocol(grids={"0": WellPlate[96]})
        .with_node(
            entity=sal,
            into="0",
            volume=Q_(100, "uL"),
        )
        .with_node(
            entity=h20(),
            into="0",
            volume=Q_(100, "uL"),
        )
        .with_node_from(
            name="diluted_saline",
            components={
                sal: Q_(50, "%"),
                "water": Q_(50, "%"),
            },
            into="0",
            final_volume=Q_(100, "uL"),
        )
    )
    assert len(protocol.nodes) == 3
    assert len(protocol.edges) == 2
    assert len(protocol.G.nodes) == 3


def test_dilution_with_mass_conc():
    sal = saline()
    water = h20()
    protocol = (
        Protocol(grids={"0": WellPlate[96]})
        .with_node(
            entity=sal,
            into="0",
            volume=Q_(100, "uL"),
        )
        .with_node(
            entity=water,
            into="0",
            volume=Q_(100, "uL"),
        )
        .with_dilution(
            species="NaCl",
            source=sal,
            diluent=water,
            final_volume=Q_(100, "uL"),
            final_concentration=Q_(0.5, "mg/mL"),
            into="0",
        )
    )
    for e in protocol.edges:
        print(e)
    assert len(protocol.nodes) == 3
    assert len(protocol.edges) == 2
    assert len(protocol.G.nodes) == 3
    assert protocol.nodes["saline_diluted_with_water"]["NaCl"] == Q_(
        0.5, "mg/mL"
    )
    assert protocol.edges[("saline", "saline_diluted_with_water")][
        "weight"
    ] == Q_(50, "%")
    assert protocol.edges[("water", "saline_diluted_with_water")][
        "weight"
    ] == Q_(50, "%")
