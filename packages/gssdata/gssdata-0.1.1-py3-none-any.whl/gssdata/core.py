"""Core API functions for gssdata package."""

import pandas as pd

from gssdata.data import HISTORICAL_TRAJECTORIES, GSS_VARIABLES


def variables() -> list[str]:
    """
    List all available GSS variables.

    Returns:
        List of variable names (uppercase strings).

    Example:
        >>> import gssdata
        >>> vars = gssdata.variables()
        >>> "HOMOSEX" in vars
        True
    """
    return list(GSS_VARIABLES.keys())


def info(variable: str) -> dict:
    """
    Get metadata for a GSS variable.

    Args:
        variable: GSS variable name (case-insensitive).

    Returns:
        Dictionary with keys:
        - question: Full question text
        - responses: Dict mapping response codes to labels
        - first_year: First year variable was asked
        - description: Short description
        - liberal_response: Response code(s) considered "liberal"

    Raises:
        KeyError: If variable is not found.

    Example:
        >>> import gssdata
        >>> info = gssdata.info("HOMOSEX")
        >>> print(info["description"])
        Attitudes toward homosexual relations
    """
    variable = variable.upper()
    if variable not in GSS_VARIABLES:
        raise KeyError(f"Unknown variable: {variable}")
    return GSS_VARIABLES[variable].copy()


def trend(variable: str) -> pd.DataFrame:
    """
    Get time series trend for a GSS variable.

    Returns the percentage giving the "liberal" response by year.
    The liberal response is defined in the variable metadata.

    Args:
        variable: GSS variable name (case-insensitive).

    Returns:
        DataFrame with columns:
        - year: Survey year
        - pct: Percentage giving the liberal response

    Raises:
        KeyError: If variable is not found.

    Example:
        >>> import gssdata
        >>> df = gssdata.trend("HOMOSEX")
        >>> df[df["year"] == 2022]
           year  pct
        28 2022   61
    """
    variable = variable.upper()
    if variable not in HISTORICAL_TRAJECTORIES:
        raise KeyError(f"Unknown variable: {variable}")

    data = HISTORICAL_TRAJECTORIES[variable]
    df = pd.DataFrame([
        {"year": year, "pct": pct}
        for year, pct in sorted(data.items())
    ])
    return df
