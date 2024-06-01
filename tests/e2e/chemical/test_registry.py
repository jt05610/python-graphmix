from graphmix.chemistry.service_layer.registry import ChemicalRegistry
from graphmix.chemistry.service_layer.unit_of_work import ChemicalUnitOfWork
from graphmix.chemistry.units import Q_


def test_chemical_registry_adds_chemical_when_not_known(
    sqlite_session_factory,
):
    uow = ChemicalUnitOfWork(sqlite_session_factory)

    reg = ChemicalRegistry(uow)

    water = reg.Chemical("water")
    assert water.name == "water"
    assert water.formula == "H2O"
    assert water.molar_mass == Q_("18.015 g/mol")


def test_registry_path(sqlite_session_factory, tmp_path):
    tmp_db = tmp_path / "test.db"

    assert not tmp_db.exists()
    reg = ChemicalRegistry(path=tmp_db)
    assert reg.path.exists()
    assert tmp_db.exists()
