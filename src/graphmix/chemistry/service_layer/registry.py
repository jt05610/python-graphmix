import logging
from pathlib import Path

from graphmix.chemistry.chemical import Chemical
from graphmix.chemistry.service_layer.pubchem import PubChemService
from graphmix.chemistry.service_layer.unit_of_work import ChemicalUnitOfWork
from graphmix.chemistry.service_layer.unit_of_work import session_factory

logger = logging.getLogger(__name__)


class ChemicalRegistry:
    """
    A registry for storing and retrieving chemical information. Uses a local
    database to store chemicals, and queries PubChem if a chemical is not
    found.
    """

    uow: ChemicalUnitOfWork
    pubchem: PubChemService

    def __init__(
        self,
        uow: ChemicalUnitOfWork | None = None,
        path: str | None = None,
    ):
        if uow is None:
            uow = ChemicalUnitOfWork(session_factory=session_factory(path))
        self.uow = uow
        self.pubchem = PubChemService()

    def get_chemical(self, name: str) -> Chemical:
        """
        Get a chemical by name. If the chemical is not found in the local
        database, query PubChem for the chemical information.
        """
        with self.uow:
            chemical = self.uow.repo.get_by("name", name.lower())
            if chemical is not None:
                return chemical
            logger.info(
                f"Chemical {name} not found in local database, querying PubChem"
            )
            chemical = self.pubchem.lookup(name)
            if chemical is None:
                logger.error(f"Chemical {name} not found in PubChem")
                raise ValueError(f"Chemical {name} not found")
            self.uow.repo.add(chemical)
            self.uow.session.expunge(chemical)
            self.uow.commit()
            return chemical

    def add_chemical(self, chemical: Chemical):
        """
        Add a chemical to the local database.
        """
        with self.uow:
            if self.uow.repo.get_by("name", chemical.name) is not None:
                raise ValueError(f"Chemical {chemical.name} already exists")
            chemical.name = chemical.name.lower()
            self.uow.repo.add(chemical)
            self.uow.commit()

    def Chemical(self, name: str) -> Chemical:
        return self.get_chemical(name)

    @property
    def path(self) -> Path:
        return self.uow.path
