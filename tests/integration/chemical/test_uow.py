from sqlalchemy import text
from sqlmodel import Session

from graphmix.chemistry.service_layer.unit_of_work import ChemicalUnitOfWork
from graphmix.chemistry.units import Q_


# noinspection SqlResolve
def insert_chemical(
    session: Session, name: str, formula: str, molar_mass: Q_ | str
):
    if not isinstance(molar_mass, str):
        molar_mass = str(molar_mass)
    session.execute(
        text(
            "INSERT INTO chemical (name, formula, molar_mass) VALUES (:name, :formula, :molar_mass)"
        ),
        {"name": name, "formula": formula, "molar_mass": molar_mass},
    )


def test_chemical_uow_can_retrieve_a_chemical(sqlite_session_factory):
    session = sqlite_session_factory()
    session.commit()

    insert_chemical(session, "Water", "H2O", Q_("18.01528 g/mol"))
    uow = ChemicalUnitOfWork(sqlite_session_factory)
    with uow:
        chemical = uow.repo.get_by("name", "Water")
        assert chemical.name == "Water"
        assert chemical.formula == "H2O"
        assert chemical.molar_mass == Q_("18.01528 g/mol")
