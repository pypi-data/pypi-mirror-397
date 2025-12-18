class _VersionInfo:
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
    _all_versions: list[tuple[int, int, int]]
    def __init__(self, all_versions: list[tuple[int, int, int]]) -> None:
        """
        Initialize _VersionInfo object.

        Parameters
        ----------
        all_versions : List[Tuple[int, int, int]]
        """
    def __str__(self) -> str:
        """
        Representate this object as a string.

        Returns
        -------
        str
            The string representation of the instance.
        """
    def __repr__(self) -> str:
        """Generate printable representation of the class instance."""
    def __eq__(self, b) -> bool:
        """Compare between two ``_VersionInfo`` instances."""

version_info: _VersionInfo
# vim: set ts=4 sts=4 sw=4 et ai si sta:
