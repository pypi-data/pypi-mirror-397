"""
gssdata - Python client for General Social Survey data.

Simple API for accessing GSS time series and variable metadata.

Example:
    >>> import gssdata
    >>> df = gssdata.trend("HOMOSEX")
    >>> print(df.head())
       year  pct
    0  1973   11
    1  1974   13
    ...
"""

from gssdata.core import info, trend, variables

__version__ = "0.1.1"
__all__ = ["trend", "variables", "info"]
