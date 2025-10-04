"""Custom exceptions for iNaturalist API interactions."""


class iNatAPIError(Exception):
    """Base exception for iNaturalist API errors."""
    pass


class PlaceNotFoundError(iNatAPIError):
    """Raised when a requested place/region cannot be found."""
    pass


class TaxonNotFoundError(iNatAPIError):
    """Raised when a requested taxon cannot be found."""
    pass


class InvalidTimeFormatError(iNatAPIError):
    """Raised when time period format is invalid."""
    pass