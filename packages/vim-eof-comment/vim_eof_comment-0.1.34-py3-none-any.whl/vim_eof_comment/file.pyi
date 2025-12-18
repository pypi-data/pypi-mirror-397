from io import TextIOWrapper

from .types.typeddict import BatchPairDict as BatchPairDict
from .types.typeddict import BatchPathDict as BatchPathDict
from .types.typeddict import LineBool as LineBool
from .util import die as die
from .util import error as error

def bootstrap_paths(paths: tuple[str], exts: tuple[str]) -> list[BatchPairDict]:
    """
    Bootstraps all the matching paths in current dir and below.

    Parameters
    ----------
    paths : array_like
        A list of specified file paths.
    exts : array_like
        A list of specified file extensions.

    Returns
    -------
    result : array_like
        A list of BatchPairDict type objects.
    """
def open_batch_paths(paths: list[BatchPairDict]) -> dict[str, BatchPathDict]:
    """
    Return a list of TextIO objects given file path strings.

    Parameters
    ----------
    paths : List[BatchPairDict]
        A list of BatchPairDict type objects.

    Returns
    -------
    result : Dict[str, BatchPathDict]
        A string to BatchPathDict dictionary.
    """
def modify_file(file: TextIOWrapper, comments: dict[str, str], ext: str, newline: bool, has_nwl: bool, matching: bool) -> str:
    """
    Modifies a file containing a bad EOF comment.

    Parameters
    ----------
    file : TextIOWrapper
        The file object to be read.
    comments : Dict[str, str]
        A filetype-to-comment dictionary.
    ext : str
        The filetype extension given by the user.
    newline : bool
        Flag to whether add a newline before the comment.
    has_nwl : bool
        Indicates whether the file already has a newline at the end
        (not counting LF/CRLF line endings).
    matching : bool
        Indicates whether the file already has a matching EOF comment.

    Returns
    -------
    str
        The modified contents of the given file.
    """
def get_last_line(file: TextIOWrapper) -> LineBool:
    """
    Returns the last line of a file and indicates whether it already has a newline.

    Parameters
    ----------
    file : TextIOWrapper
        The file to retrieve the last line data from.

    Returns
    -------
    last_line : LineBool
        An object containing both the last line in a string and a boolean indicating a newline.
    """

# vim: set ts=4 sts=4 sw=4 et ai si sta:
