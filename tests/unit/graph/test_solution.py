import json

import pytest

from graphmix.chemistry.chemical import Chemical
from graphmix.chemistry.units import Q_
from graphmix.graph.solution import Composition
from graphmix.graph.solution import DimensionalityError
from graphmix.graph.solution import Solution

nacl = Chemical(name="NaCl", formula="NaCl", molar_mass="58.44 g/mol")
water = Chemical(name="water", formula="H2O", molar_mass="18.015 g/mol")


def saline() -> Solution:
    return (
        Solution(name="saline")
        .with_component(nacl, Q_(1, "mg/mL"))
        .with_component(water, Q_(100, "%"))
    )


def test_solution_prepared_from_primitives():
    solution = saline()
    as_json = solution.model_dump_json()

    from_json = Solution(**json.loads(as_json))

    assert from_json.name == "saline"
    assert from_json.G.nodes == solution.G.nodes
    assert from_json.G.edges == solution.G.edges
    assert from_json.components == solution.components
    print(solution.composition)
    expected_composition = Composition(
        solutes={nacl: Q_(1, "mg/mL")}, solvents={water: Q_(100, "%")}
    )

    assert from_json.composition == expected_composition


def test_solution_prepared_from_solution():
    solution = saline()

    new_solution = (
        Solution(name="diluted_saline")
        .with_component(solution, Q_(50, "%"))
        .with_component(water, Q_(50, "%"))
    )
    expected_composition = Composition(
        solutes={nacl: Q_(0.5, "mg/mL")}, solvents={water: Q_(100, "%")}
    )
    assert new_solution.composition == expected_composition
    print(new_solution.G.nodes)
    assert len(new_solution.G.nodes) == 4

    another_dilution = (
        Solution(name="twice_diluted_saline")
        .with_component(new_solution, Q_(50, "%"))
        .with_component(water, Q_(50, "%"))
    )

    expected_composition = Composition(
        solutes={nacl: Q_(0.25, "mg/mL")}, solvents={water: Q_(100, "%")}
    )

    assert another_dilution.composition == expected_composition


def test_cant_prepare_from_solution_with_mass_conc():
    with pytest.raises(DimensionalityError):
        (
            Solution(name="diluted_saline")
            .with_component(saline(), Q_(50, "mg/mL"))
            .with_component(water, Q_(50, "%"))
        )
