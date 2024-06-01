import json

import pytest
from matplotlib import pyplot as plt

from graphmix.chemistry.units import Q_
from graphmix.graph.drawing import plot_graph
from graphmix.graph.solution import Composition
from graphmix.graph.solution import DimensionalityError
from graphmix.graph.solution import Solution


def test_solution_prepared_from_primitives(saline, nacl, h2o):
    solution = saline
    as_json = solution.model_dump_json()

    from_json = Solution(**json.loads(as_json))

    assert from_json.name == "saline"
    assert from_json.G.nodes == solution.G.nodes
    assert from_json.G.edges == solution.G.edges
    assert from_json.components == solution.components
    expected_composition = Composition(
        solutes={nacl: Q_(1, "mg/mL")}, solvents={h2o: Q_(100, "%")}
    )

    assert from_json.composition == expected_composition


def test_solution_prepared_from_solution(saline, h2o, nacl):
    solution = saline

    new_solution = (
        Solution(name="diluted_saline")
        .with_component(solution, Q_(50, "%"))
        .with_component(h2o, Q_(50, "%"))
    )
    expected_composition = Composition(
        solutes={nacl: Q_(0.5, "mg/mL")}, solvents={h2o: Q_(100, "%")}
    )

    plot_graph(new_solution.G, edge_attr="concentration")
    plt.savefig("test.svg")
    assert new_solution.composition == expected_composition
    assert len(new_solution.G.nodes) == 4

    another_dilution = (
        Solution(name="twice_diluted_saline")
        .with_component(new_solution, Q_(50, "%"))
        .with_component(h2o, Q_(50, "%"))
    )

    expected_composition = Composition(
        solutes={nacl: Q_(0.25, "mg/mL")}, solvents={h2o: Q_(100, "%")}
    )

    assert another_dilution.composition == expected_composition


def test_cant_prepare_from_solution_with_mass_conc(saline, h2o):
    with pytest.raises(DimensionalityError):
        (
            Solution(name="diluted_saline")
            .with_component(saline, Q_(50, "mg/mL"))
            .with_component(h2o, Q_(50, "%"))
        )
