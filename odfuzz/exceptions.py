"""This module contains the set of all ODfuzz exceptions."""


class ODfuzzException(Exception):
    """Base class for all ODfuzz exceptions."""
    pass


class ArgParserError(ODfuzzException):
    """An error occurred while parsing arguments."""
    pass


class BuilderError(ODfuzzException):
    """An error occurred while initializing queryable entities."""
    pass


class DispatcherError(ODfuzzException):
    """An error occurred while reading response from the server."""
    pass


class RestrictionsError(ODfuzzException):
    """An error occurred while initializing a restrictions object."""
    pass


class LoggersError(ODfuzzException):
    """An error occurred while creating directories."""
    pass
