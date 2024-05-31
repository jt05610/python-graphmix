from graphmix.chemistry.units import Concentration
from graphmix.chemistry.units import Volume


def dilution(
    c1: Concentration | None = None,
    v1: Volume | None = None,
    c2: Concentration | None = None,
    v2: Volume | None = None,
) -> Concentration | Volume:
    """
    Calculate the missing value in a dilution equation. Must provide 3 out of 4
    values. If two concentrations are provided, they must have the same
    dimensionality.

    Args:
        c1: Initial concentration.
        v1: Initial volume.
        c2: Final concentration.
        v2: Final volume.

    Returns:
        The missing value.

    Raises:
        ValueError: If the input is invalid.
    """
    match (c1, v1, c2, v2):
        case (None, _, _, _):
            return c2 * v2 / v1
        case (_, None, _, _):
            if c1.dimensionality != c2.dimensionality:
                raise ValueError(
                    "Concentrations must have the same dimensionality"
                )
            return c2 * v2 / c1
        case (_, _, None, _):
            return c1 * v1 / v2
        case (_, _, _, None):
            if c1.dimensionality != c2.dimensionality:
                raise ValueError(
                    "Concentrations must have the same dimensionality"
                )
            return c1 * v1 / c2
        case _:
            raise ValueError("Invalid input")
