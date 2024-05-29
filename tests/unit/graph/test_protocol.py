from graphmix.chemistry.chemical import Chemical
from graphmix.chemistry.units import Q_
from graphmix.graph.protocol import Protocol
from graphmix.graph.solution import Solution
from graphmix.location import WellPlate


def test_with_entity():
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
    saline = Solution(name="saline").with_components(
        {
            nacl: Q_(1, "mg/mL"),
            water: Q_(100, "%"),
        }
    )

    protocol = Protocol(
        grids={"0": WellPlate[96]},
    ).with_entity(
        entity=saline,
        into="0",
        volume=Q_(100, "uL"),
    )

    assert protocol.nodes["saline"].final_volume == Q_(100, "uL")
    assert protocol.nodes["saline"].location == WellPlate[96][0]
    print(protocol.nodes["saline"].solution)
