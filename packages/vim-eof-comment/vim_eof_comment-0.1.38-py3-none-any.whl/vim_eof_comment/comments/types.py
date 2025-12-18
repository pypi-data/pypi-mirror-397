# -*- coding: utf-8 -*-
# Copyright (c) 2025 Guennadi Maximov C. All Rights Reserved.
"""
Per-filetype modeline comment class.

Copyright (c) 2025 Guennadi Maximov C. All Rights Reserved.
"""
from typing import TypedDict

from ..types.typeddict import IndentMap


class GeneratedEOFComments(TypedDict):
    """A ``TypedDict`` object containing all the file-extension to comment elements."""

    C: str
    H: str
    bash: str
    c: str
    cc: str
    cpp: str
    css: str
    fish: str
    h: str
    hh: str
    hpp: str
    htm: str
    html: str
    lua: str
    markdown: str
    md: str
    py: str
    pyi: str
    sh: str
    xml: str
    zsh: str


class IndentMapDict(TypedDict):
    """A ``TypedDict`` object with ``IndentMap`` values."""

    C: IndentMap
    H: IndentMap
    bash: IndentMap
    c: IndentMap
    cc: IndentMap
    cpp: IndentMap
    css: IndentMap
    fish: IndentMap
    h: IndentMap
    hh: IndentMap
    hpp: IndentMap
    htm: IndentMap
    html: IndentMap
    lua: IndentMap
    markdown: IndentMap
    md: IndentMap
    py: IndentMap
    pyi: IndentMap
    sh: IndentMap
    xml: IndentMap
    zsh: IndentMap

# vim: set ts=4 sts=4 sw=4 et ai si sta:
