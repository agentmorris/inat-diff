"""
iNaturalist Difference Detection Library

A Python library for querying iNaturalist observations to detect species presence
patterns across regions and time periods.
"""

from .client import iNatClient
from .query import SpeciesQuery
from .exceptions import iNatAPIError, PlaceNotFoundError, TaxonNotFoundError

__version__ = "0.1.0"
__all__ = ["iNatClient", "SpeciesQuery", "iNatAPIError", "PlaceNotFoundError", "TaxonNotFoundError"]