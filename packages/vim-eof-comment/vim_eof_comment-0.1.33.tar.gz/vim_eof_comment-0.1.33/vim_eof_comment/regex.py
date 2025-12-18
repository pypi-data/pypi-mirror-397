# -*- coding: utf-8 -*-
# Copyright (c) 2025 Guennadi Maximov C. All Rights Reserved.
"""EOF comments checker regex matching utilities.

Copyright (c) 2025 Guennadi Maximov C. All Rights Reserved.
"""
from re import compile

from .util import verbose_print


def matches(s: str, verbose: bool) -> bool:
    """Check if given string matches any of the given patterns."""
    pats = (
        "vim:([a-zA-Z]+(=[a-zA-Z0-9_]*)?:)+",
        "vim:\\sset(\\s[a-zA-Z]+(=[a-zA-Z0-9_]*)?)*\\s[a-zA-Z]+(=[a-zA-Z0-9_]*)?:"
    )
    for pattern in [compile(pat) for pat in pats]:
        match = pattern.search(s)
        if match is not None:
            verbose_print(
                f"- Match: `{s}` (match str: `{match.string}`)\n",
                f"  - Group: `{match.group()}`\n",
                verbose=verbose,
                sep=""
            )
            return True

    return False
# vim: set ts=4 sts=4 sw=4 et ai si sta:
