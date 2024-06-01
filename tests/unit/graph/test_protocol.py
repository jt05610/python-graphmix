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


def dilution_protocol() -> Protocol:
    sal = saline()
    water = h20()
    return (
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
            species=sal.components["NaCl"],
            source=sal,
            diluent=water,
            final_volume=Q_(100, "uL"),
            final_concentration=Q_(0.5, "mg/mL"),
            into="0",
        )
    )


def test_dilution_with_mass_conc():
    protocol = dilution_protocol()
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


def test_write_latex(tmp_path):
    latex_path = tmp_path / "protocol.tex"
    proto = dilution_protocol()
    proto.write_latex(latex_path)
    expected = """\\documentclass{report}
\\usepackage{tikz}
\\usepackage{subcaption}

\\begin{document}
\\begin{figure}
  \\begin{tikzpicture}
      \\draw
        (0.0:2) node (saline){saline}
        (120.0:2) node (water){water}
        (240.0:2) node (saline_diluted_with_water){saline_diluted_with_water};
      \\begin{scope}[->]
        \\draw (saline) to (saline_diluted_with_water);
        \\draw (water) to (saline_diluted_with_water);
      \\end{scope}
    \\end{tikzpicture}
\\end{figure}
\\end{document}"""
    with latex_path.open() as f:
        assert f.read() == expected


def test_protocol_inputs_outputs():
    protocol = dilution_protocol()

    assert len(protocol.inputs) == 2
    assert len(protocol.outputs) == 1
