def at_least_ismk_version(version: str) -> bool:
    """Check if the current SMK version is at least the specified version.

    There is no need to check for a maximum version as SMK itself will ensure
    that only compatible interfaces can be installed along with it.
    """
    from ismk import __version__ as ismk_version
    from packaging.version import parse

    ismk_version = parse(ismk_version)
    return ismk_version >= parse(version)
