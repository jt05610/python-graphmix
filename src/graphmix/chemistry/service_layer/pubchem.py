import time

import requests

from graphmix.chemistry.chemical import Chemical
from graphmix.chemistry.units import Q_

chemical_properties = (
    "MolecularWeight",
    "CanonicalSMILES",
    "MolecularFormula",
)


def property_string() -> str:
    return ",".join(chemical_properties)


def pubchem_uri(name: str) -> str:
    base = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
    end = f"property/{property_string()}/JSON"
    return f"{base}/compound/name/{name}/{end}"


class PubChemService:
    last_request_time: float = 0
    second_delay: float
    timeout: int = 5

    def __init__(self, requests_per_second: int = 5, timeout: int = 5):
        self.second_delay = 1 / requests_per_second

    def do_request(self, uri: str) -> dict:
        elapsed_time = time.time() - self.last_request_time
        if elapsed_time < self.second_delay:
            time.sleep(self.second_delay - elapsed_time)
        r = requests.get(uri, timeout=5)
        r.raise_for_status()
        self.last_request_time = time.time()
        return r.json()

    def lookup(self, name: str) -> Chemical:
        uri = pubchem_uri(name)

        data = self.do_request(uri)
        properties = data["PropertyTable"]["Properties"][0]
        smiles = properties.get("CanonicalSMILES", None)
        formula = properties.get("MolecularFormula", None)
        molar_mass = Q_(float(properties.get("MolecularWeight", 0.0)), "g/mol")
        return Chemical(
            name=name,
            smiles=smiles,
            formula=formula,
            molar_mass=molar_mass,
        )
