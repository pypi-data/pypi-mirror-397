# -*- coding: utf-8 -*-
# Copyright (c) 2025 Guennadi Maximov C. All Rights Reserved.
"""
EOF comments checker utilities.

Copyright (c) 2025 Guennadi Maximov C. All Rights Reserved.
"""
from sys import exit as Exit
from sys import stderr as STDERR
from sys import stdout as STDOUT
from typing import Callable, Dict, List, NoReturn, TextIO

from .types.typeddict import IndentHandler, IndentMap


def error(*msg, end: str = "\n", sep: str = " ", flush: bool = False) -> NoReturn:
    r"""
    Prints to stderr.

    Parameters
    ----------
    *msg
        The data to be printed to stderr.
    end : str, default="\n", optional
        The string to be printed when finishing all the data printing.
    sep : str, default=" ", optional
        The string to be printed between each data element to be printed.
    flush : bool, default=False, optional
        Forcefully makes the output file to be flushed.

    See Also
    --------
    print : This function is essentially being wrapped around here.
    """
    try:
        end = str(end)
    except KeyboardInterrupt:
        Exit(1)
    except Exception:
        end = "\n"

    try:
        sep = str(sep)
    except KeyboardInterrupt:
        Exit(1)
    except Exception:
        sep = " "

    try:
        flush = bool(flush)
    except KeyboardInterrupt:
        Exit(1)
    except Exception:
        flush = False

    print(*msg, end=end, sep=sep, flush=flush, file=STDERR)


def die(
        *msg,
        code: int = 0,
        end: str = "\n",
        sep: str = " ",
        flush: bool = False,
        func: Callable[[TextIO], None] | None = None,
) -> NoReturn:
    r"""
    Kills program execution.

    Summons sys.exit() with a provided code and optionally prints code to stderr or stdout
    depending on the provuded exit code.

    Parameters
    ----------
    *msg : optional
        Data to be printed.
    code : int, default=0
        The exit code.
    end : str, default="\n", optional
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
    """
    try:
        code = int(code)
    except Exception:
        code = 1

    try:
        end = str(end)
    except Exception:
        end = "\n"
        code = 1

    try:
        sep = str(sep)
    except Exception:
        sep = " "
        code = 1

    try:
        flush = bool(flush)
    except Exception:
        flush = False
        code = 1

    if func is not None and callable(func):
        func(STDERR if code != 0 else STDOUT)

    if msg and len(msg) > 0:
        if code == 0:
            print(*msg, end=end, sep=sep, flush=flush)
        else:
            error(*msg, end=end, sep=sep, flush=flush)

    Exit(code)


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
    end: str = kwargs.get("end", "\n")
    sep: str = kwargs.get("sep", " ")
    flush: bool = kwargs.get("flush", False)

    if verbose is None or not verbose:
        return

    print(*msg, end=end, sep=sep, flush=flush)


def version_print(version: str) -> NoReturn:
    """
    Print project version, then exit.

    version : str
        The version string.

    See Also
    --------
    vim_eof_comment.util.die : The function used for this function.
    """
    die(f"vim-eof-comment-{version}", code=0)


def gen_indent_maps(maps: List[IndentHandler]) -> Dict[str, IndentMap] | None:
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
    if len(maps) == 0:
        return None

    map_d: Dict[str, IndentMap] = dict()
    for mapping in maps:
        mapping_len = len(mapping)
        if mapping_len <= 1:
            raise ValueError(f"One of the custom mappings is not formatted properly! (`{mapping}`)")

        ext, level = mapping["ext"], mapping["level"]
        if ext in map_d.keys():
            continue

        mapping_len = mapping_len if mapping_len <= 3 else 3
        map_d[ext] = {
            "level": level,
            "expandtab": True if mapping_len == 2 else mapping["expandtab"],
        }

    return map_d

# vim: set ts=4 sts=4 sw=4 et ai si sta:
