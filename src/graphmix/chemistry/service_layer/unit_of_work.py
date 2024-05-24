from graphmix.chemistry.chemical import Chemical
from graphmix.chemistry.chemical import NucleicAcid
from graphmix.core.sqlmodel.unit_of_work import SqlModelUnitOfWork


class ChemicalUnitOfWork(SqlModelUnitOfWork):
    model = Chemical


class NucleicAcidUnitOfWork(SqlModelUnitOfWork):
    model = NucleicAcid
