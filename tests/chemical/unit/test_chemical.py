from graphmix.chemistry.chemical import Chemical
from graphmix.chemistry.units import Q_


def test_chemical_sqlmodel_works_with_quantity():
    water = Chemical(
        name="Water",
        formula="H2O",
        molar_mass="18.01528 g/mol",
    )
    assert water.molar_mass == Q_("18.01528 g/mol")

    # make sure it works when no unit is passed with molar mass
    water = Chemical(
        name="Water",
        formula="H2O",
        molar_mass=18.01528,
    )
    assert water.molar_mass == Q_("18.01528 g/mol")
