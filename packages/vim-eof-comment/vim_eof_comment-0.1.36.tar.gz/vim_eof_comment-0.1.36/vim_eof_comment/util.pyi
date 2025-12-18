from typing import Callable, NoReturn, TextIO

from .types.typeddict import IndentHandler as IndentHandler
from .types.typeddict import IndentMap as IndentMap

def error(*msg, end: str = '\n', sep: str = ' ', flush: bool = False) -> NoReturn:
    '''
    Prints to stderr.

    Parameters
    ----------
    *msg
        The data to be printed to stderr.
    end : str, default="\\n", optional
        The string to be printed when finishing all the data printing.
    sep : str, default=" ", optional
        The string to be printed between each data element to be printed.
    flush : bool, default=False, optional
        Forcefully makes the output file to be flushed.

    See Also
    --------
    print : This function is essentially being wrapped around here.
    '''
def die(*msg, code: int = 0, end: str = '\n', sep: str = ' ', flush: bool = False, func: Callable[[TextIO], None] | None = None) -> NoReturn:
    '''
    Kills program execution.

    Summons sys.exit() with a provided code and optionally prints code to stderr or stdout
    depending on the provuded exit code.

    Parameters
    ----------
    *msg : optional
        Data to be printed.
    code : int, default=0
        The exit code.
    end : str, default="\\n", optional
        The string to be printed when finishing all the data printing.
    sep : str, default=" ", optional
        The string to be printed between each data element to be printed.
    flush : bool, default=False, optional
        Forcefully makes the output file to be flushed.
    func : Callable[[TextIO], None], optional
        A function to be called with a TextIO object if provided.

    See Also
    --------
    vim_eof_comment.util.error : Function to be used if exit code is not 0.
    '''
def verbose_print(*msg, verbose: bool | None = None, **kwargs) -> NoReturn:
    """
    Only prints the given data if verbose mode is activated.

    Parameters
    ----------
    *msg
        Data to be printed.
    verbose : bool or None, default=None
        Flag to signal whether to execute this function or not.
    **kwargs
        Extra arguments for the ``print()`` function.

    See Also
    --------
    print : This function is essentially being wrapped around here.
    """
def version_print(version: str) -> NoReturn:
    """
    Print project version, then exit.

    version : str
        The version string.

    See Also
    --------
    vim_eof_comment.util.die : The function used for this function.
    """
def gen_indent_maps(maps: list[IndentHandler]) -> dict[str, IndentMap] | None:
    """
    Generate a dictionary from the custom indent maps.

    Parameters
    ----------
    maps : List[IndentHandler]
        A list of IndentHandler objects.

    Returns
    -------
    map_d : Dict[str, IndentMap]
        The generated indent map dictionary.

    Raises
    ------
    ValueError : This will happen if any element of the only parameter
                  is less or equal to one.
    """

# vim: set ts=4 sts=4 sw=4 et ai si sta:
