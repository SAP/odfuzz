"""This module contains the set of all ODfuzz exceptions."""


class ODfuzzException(Exception):
    """Base class for all ODfuzz exceptions."""
    pass


class ArgParserError(ODfuzzException):
    """An error occurred while parsing arguments"""
    pass
