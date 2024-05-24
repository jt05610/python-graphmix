from sqlmodel import Session

from graphmix.chemistry.chemical import Chemical
from graphmix.core.sqlmodel.repository import SqlModelRepository


class ChemicalRepository(SqlModelRepository[Chemical]):
    model = Chemical

    def __init__(self, session: Session):
        super().__init__(self.model, session)
