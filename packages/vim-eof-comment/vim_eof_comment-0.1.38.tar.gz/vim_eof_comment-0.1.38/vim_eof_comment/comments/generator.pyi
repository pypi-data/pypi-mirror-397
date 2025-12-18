from typing import Iterator, NoReturn

from ..types.typeddict import IndentMap as IndentMap
from .types import GeneratedEOFComments as GeneratedEOFComments
from .types import IndentMapDict as IndentMapDict

_formats: GeneratedEOFComments
_DEFAULT: IndentMapDict

class Comments:
    """Vim EOF comments class."""
    __DEFAULT: IndentMapDict
    __formats: GeneratedEOFComments
    comments: GeneratedEOFComments
    langs: IndentMapDict
    def __init__(self, mappings: IndentMapDict | None = None) -> None:
        """
        Creates a new Vim EOF comment object.

        Parameters
        ----------
        mappings : IndentMapDict, optional, default=None
            The ``str`` to ``IndentMap`` dictionary.
        """
    def __iter__(self) -> Iterator[str]:
        """Iterate through comment langs."""
    def __is_available(self, lang: str) -> bool:
        """Checks if a given lang is available within the class."""
    def __fill_langs(self, langs: IndentMapDict) -> NoReturn:
        """Fill languages dict."""
    def get_defaults(self) -> IndentMapDict:
        """
        Retrieve the default comment dictionary.

        Returns
        -------
        IndentMapDict
        """
    def generate(self) -> GeneratedEOFComments:
        """
        Generate the comments list.

        Returns
        -------
        comments : GeneratedEOFComments
            The customly generated comments dictionary.
        """
    def get_ft(self, ext: str) -> str | None:
        """
        Get the comment string by filetype (or None if it doesn't exist).

        Parameters
        ----------
        ext : str
            The file extension to be fetched.

        Returns
        -------
        ``str`` or ``None``
        """

# vim: set ts=4 sts=4 sw=4 et ai si sta:
