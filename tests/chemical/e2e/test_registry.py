from graphmix.chemistry.service_layer.registry import ChemicalRegistry
from graphmix.chemistry.service_layer.unit_of_work import ChemicalUnitOfWork
from graphmix.chemistry.units import Q_


def test_chemical_registry_adds_chemical_when_not_known(
    sqlite_session_factory,
):
    uow = ChemicalUnitOfWork(sqlite_session_factory)

    reg = ChemicalRegistry(uow)

    water = reg.chem("water")

    assert water.name == "water"
    assert water.formula == "H2O"
    assert water.molar_mass == Q_("18.015 g/mol")
