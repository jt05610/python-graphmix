from graphmix.chemistry.units import Q_
from graphmix.graph.protocol import Protocol
from graphmix.location import WellPlate


def test_with_entity(saline):

    protocol = Protocol(
        grids={"0": WellPlate[96]},
    ).with_node(
        entity=saline,
        into="0",
        volume=Q_(100, "uL"),
    )

    assert protocol.nodes["saline"].final_volume == Q_(100, "uL")
    assert protocol.nodes["saline"].location == WellPlate[96][0]


def test_with_node_from(saline, water):
    sal = saline
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


def test_dilution_with_mass_conc(dilution_protocol, diluted_solution_name):
    protocol = dilution_protocol
    assert len(protocol.nodes) == 3
    assert len(protocol.edges) == 2
    assert len(protocol.G.nodes) == 3
    assert protocol.nodes[diluted_solution_name]["NaCl"] == Q_(0.5, "mg/mL")
    assert protocol.edges[("saline", diluted_solution_name)]["weight"] == Q_(
        50, "%"
    )
    assert protocol.edges[("water", diluted_solution_name)]["weight"] == Q_(
        50, "%"
    )


def test_write_latex(tmp_path, dilution_protocol, diluted_solution_name):
    latex_path = tmp_path / "protocol.tex"
    proto = dilution_protocol
    proto.write_latex(latex_path)
    expected = f"""\\documentclass{{report}}
\\usepackage{{tikz}}
\\usepackage{{subcaption}}

\\begin{{document}}
\\begin{{figure}}
  \\begin{{tikzpicture}}
      \\draw
        (0.0:2) node (saline){{saline}}
        (120.0:2) node (water){{water}}
        (240.0:2) node ({diluted_solution_name}){{{diluted_solution_name}}};
      \\begin{{scope}}[->]
        \\draw (saline) to ({diluted_solution_name});
        \\draw (water) to ({diluted_solution_name});
      \\end{{scope}}
    \\end{{tikzpicture}}
\\end{{figure}}
\\end{{document}}"""
    with latex_path.open() as f:
        assert f.read() == expected


def test_protocol_inputs_outputs(dilution_protocol):
    protocol = dilution_protocol

    assert len(protocol.inputs) == 2
    assert len(protocol.outputs) == 1
