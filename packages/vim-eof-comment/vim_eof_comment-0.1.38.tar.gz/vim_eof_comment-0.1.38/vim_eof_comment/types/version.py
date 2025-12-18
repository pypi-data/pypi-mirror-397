# -*- coding: utf-8 -*-
# Copyright (c) 2025 Guennadi Maximov C. All Rights Reserved.
"""
Custom vim-eof-comment versioning objects.

Copyright (c) 2025 Guennadi Maximov C. All Rights Reserved.
"""
from typing import List, Tuple


class _VersionInfo():
    """
    A sys-inspired version_info object type.

    Attributes
    ----------
    major : int
        The major component of the version.
    minor : int
        The minor component of the version.
    patch : int
        The patch component of the version.
    """

    major: int
    minor: int
    patch: int
    _all_versions: List[Tuple[int, int, int]]

    def __init__(self, all_versions: List[Tuple[int, int, int]]):
        """
        Initialize _VersionInfo object.

        Parameters
        ----------
        all_versions : List[Tuple[int, int, int]]
        """
        self._all_versions = all_versions.copy()

        all_versions = all_versions.copy()[::-1]
        self.major = all_versions[0][0]
        self.minor = all_versions[0][1]
        self.patch = all_versions[0][2]

    def __str__(self) -> str:
        """
        Representate this object as a string.

        Returns
        -------
        str
            The string representation of the instance.
        """
        return f"{self.major}.{self.minor}.{self.patch}"

    def __repr__(self) -> str:
        """Generate printable representation of the class instance."""
        return self.__str__()

    def __eq__(self, b) -> bool:
        """Compare between two ``_VersionInfo`` instances."""
        if not isinstance(b, _VersionInfo):
            return False

        b: _VersionInfo = b
        return self.major == b.major and self.minor == b.minor and self.patch == b.patch


version_info: _VersionInfo = _VersionInfo([
    (0, 1, 1),
    (0, 1, 2),
    (0, 1, 3),
    (0, 1, 4),
    (0, 1, 5),
    (0, 1, 6),
    (0, 1, 7),
    (0, 1, 8),
    (0, 1, 9),
    (0, 1, 10),
    (0, 1, 11),
    (0, 1, 12),
    (0, 1, 13),
    (0, 1, 14),
    (0, 1, 15),
    (0, 1, 16),
    (0, 1, 17),
    (0, 1, 18),
    (0, 1, 19),
    (0, 1, 20),
    (0, 1, 21),
    (0, 1, 22),
    (0, 1, 23),
    (0, 1, 24),
    (0, 1, 25),
    (0, 1, 26),
    (0, 1, 27),
    (0, 1, 28),
    (0, 1, 29),
    (0, 1, 30),
    (0, 1, 31),
    (0, 1, 32),
    (0, 1, 33),
    (0, 1, 34),
    (0, 1, 35),
    (0, 1, 36),
    (0, 1, 37),
    (0, 1, 38),
])

# vim: set ts=4 sts=4 sw=4 et ai si sta:
