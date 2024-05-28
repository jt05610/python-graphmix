import json

from graphmix.chemistry.chemical import Chemical
from graphmix.chemistry.units import Q_
from graphmix.graph.solution import Solution


def saline() -> Solution:
    nacl = Chemical(name="NaCl", formula="NaCl", molar_mass="58.44 g/mol")
    water = Chemical(name="water", formula="H2O", molar_mass="18.015 g/mol")
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
