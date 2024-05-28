from requests_ratelimiter import LimiterSession

from graphmix.chemistry.chemical import Chemical
from graphmix.chemistry.units import Q_


def property_string() -> str:
    chemical_properties = (
        "MolecularWeight",
        "CanonicalSMILES",
        "MolecularFormula",
    )
    return ",".join(chemical_properties)


PROP_STRING = property_string()


def pubchem_uri(name: str) -> str:
    base = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
    end = f"property/{PROP_STRING}/JSON"
    return f"{base}/compound/name/{name}/{end}"


class PubChemService:
    session: LimiterSession
    timeout: float = 5

    def __init__(self, requests_per_second: float = 5, timeout: float = 5):
        self.session = LimiterSession(per_second=requests_per_second)
        self.timeout = timeout

    def do_request(self, uri: str) -> dict:
        r = self.session.get(uri, timeout=self.timeout)
        r.raise_for_status()
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
