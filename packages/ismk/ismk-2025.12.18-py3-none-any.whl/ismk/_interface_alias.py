"""Alias helpers to bridge legacy SMK interface packages to the ismk namespace."""

from importlib import import_module
from types import ModuleType
from typing import Iterable
import sys


def alias_package(alias: str, target: str, submodules: Iterable[str]) -> ModuleType:
    """Expose a target package under an alias and mirror selected submodules."""
    expanded_submodules = set()
    for sub in submodules:
        parts = sub.split(".")
        for idx in range(1, len(parts) + 1):
            expanded_submodules.add(".".join(parts[:idx]))

    target_mod = import_module(target)
    alias_mod = sys.modules.get(alias, ModuleType(alias))
    sys.modules[alias] = alias_mod

    alias_mod.__dict__.update(target_mod.__dict__)
    if hasattr(target_mod, "__path__"):
        alias_mod.__path__ = target_mod.__path__
    alias_mod.__file__ = getattr(target_mod, "__file__", None)
    alias_mod.__package__ = alias
    alias_mod.__spec__ = target_mod.__spec__
    alias_mod.__all__ = getattr(target_mod, "__all__", None)

    for sub in sorted(expanded_submodules):
        target_name = f"{target}.{sub}"
        alias_name = f"{alias}.{sub}"
        try:
            submod = import_module(target_name)
        except ModuleNotFoundError:
            continue
        sys.modules[alias_name] = submod

        top_level = sub.split(".")[0]
        top_alias = f"{alias}.{top_level}"
        if top_alias in sys.modules:
            setattr(alias_mod, top_level, sys.modules[top_alias])

    return alias_mod
