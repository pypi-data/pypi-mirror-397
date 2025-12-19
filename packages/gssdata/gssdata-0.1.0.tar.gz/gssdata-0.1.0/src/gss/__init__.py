"""
gss - Python client for General Social Survey data.

Simple API for accessing GSS time series and variable metadata.

Example:
    >>> import gss
    >>> df = gss.trend("HOMOSEX")
    >>> print(df.head())
       year  pct
    0  1973   11
    1  1974   13
    ...
"""

from gss.core import info, trend, variables

__version__ = "0.1.0"
__all__ = ["trend", "variables", "info"]
