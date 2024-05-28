from graphmix.chemistry.adapters.repository import ChemicalRepository
from graphmix.chemistry.chemical import Chemical


def test_chemical_repo(sqlite_session_factory):
    chemical = Chemical(
        name="Water", formula="H2O", molar_mass="18.01528 g/mol"
    )

    with sqlite_session_factory() as session:
        repo = ChemicalRepository(session)
        repo.add(chemical)
        session.commit()
        assert repo.get(chemical.id) == chemical
        assert repo.get_by("name", "Water") == chemical

        assert repo.list() == [chemical]

        repo.delete(chemical.id)
        session.commit()

        assert repo.list() == []

        assert repo.get(chemical.id) is None
