from io import TextIOWrapper
from typing import Any, TypedDict

class ParserSpec(TypedDict):
    """A ``TypedDict`` container."""
    opts: tuple[str]
    kwargs: dict[str, Any]

class CommentMap(TypedDict):
    """A ``TypedDict`` container."""
    level: int

class IndentMap(TypedDict):
    """A ``TypedDict`` container."""
    level: int
    expandtab: bool

class IndentHandler(TypedDict):
    """A ``TypedDict`` container."""
    ext: str
    level: str
    expandtab: bool

class IOWrapperBool(TypedDict):
    """A ``TypedDict`` container."""
    file: TextIOWrapper
    has_nwl: bool

class LineBool(TypedDict):
    """A ``TypedDict`` container."""
    line: str
    has_nwl: bool

class BatchPathDict(TypedDict):
    """A ``TypedDict`` container."""
    file: TextIOWrapper
    ext: str

class BatchPairDict(TypedDict):
    """A ``TypedDict`` container."""
    fpath: str
    ext: str

class EOFCommentSearch(TypedDict):
    """A ``TypedDict`` container."""
    state: IOWrapperBool
    lang: str
    match: bool

# vim: set ts=4 sts=4 sw=4 et ai si sta:
