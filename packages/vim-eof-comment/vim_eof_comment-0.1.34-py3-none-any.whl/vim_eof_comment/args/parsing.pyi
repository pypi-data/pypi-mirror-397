from argparse import ArgumentParser, Namespace

from ..types.typeddict import IndentHandler as IndentHandler
from ..types.typeddict import ParserSpec as ParserSpec
from ..util import die as die

def bootstrap_args(parser: ArgumentParser, specs: list[ParserSpec]) -> Namespace:
    """
    Bootstraps the program arguments.

    Parameters
    ----------
    parser : argparse.ArgumentParser
        The ``argparse.ArgumentParser`` object.
    specs : List[vim_eof_comment.types.typeddict.ParserSpec]
        A list containing ``ParserSpec`` objects.

    Returns
    -------
    namespace : argparse.Namespace
        The generated argparse Namespace object.
    """
def arg_parser_init() -> tuple[ArgumentParser, Namespace]:
    """
    Generate the argparse namespace.

    Returns
    -------
    parser : argparse.ArgumentParser
        The generated ``argparse.ArgumentParser`` object.
    namespace : argparse.Namespace
        The generated ``argparse.Namespace`` object.
    """
def indent_handler(indent: str) -> list[IndentHandler]:
    """
    Parse indent levels defined by the user.

    Parameters
    ----------
    indent : str
        The ``-i`` option argument string.

    Returns
    -------
    maps : List[vim_eof_comment.types.typeddict.IndentHandler]
        A list of ``IndentHandler`` objects.
    """

# vim: set ts=4 sts=4 sw=4 et ai si sta:
