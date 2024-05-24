from graphmix.chemistry.chemical import Chemical
from graphmix.chemistry.service_layer.pubchem import PubChemService
from graphmix.chemistry.service_layer.unit_of_work import ChemicalUnitOfWork


class ChemicalRegistry:
    """
    A registry for storing and retrieving chemical information. Uses a local
    database to store chemicals, and queries PubChem if a chemical is not
    found.
    """

    uow: ChemicalUnitOfWork
    pubchem: PubChemService

    def __init__(self, uow: ChemicalUnitOfWork):
        self.uow = uow
        self.pubchem = PubChemService()

    def get_chemical(self, name: str) -> Chemical:
        """
        Get a chemical by name. If the chemical is not found in the local
        database, query PubChem for the chemical information.
        """
        with self.uow:
            chemical = self.uow.repo.get(name)
            if chemical is not None:
                return chemical
            chemical = self.pubchem.lookup(name)
            self.uow.repo.add(chemical)
            self.uow.commit()
            return chemical

    def add_chemical(self, chemical: Chemical):
        """
        Add a chemical to the local database.
        """
        with self.uow:
            if self.uow.repo.get(chemical.name) is not None:
                raise ValueError(f"Chemical {chemical.name} already exists")
            self.uow.repo.add(chemical)
            self.uow.commit()
