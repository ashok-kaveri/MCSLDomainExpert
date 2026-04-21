"""Pipeline package compatibility helpers.

The test suite patches modules via dotted paths such as
``pipeline.user_story_writer._get_claude`` before importing the submodule.
Python only resolves those patch targets if the package exposes the submodule
as an attribute. Keep that behavior via lazy imports so existing call sites
continue to work without eagerly importing the full pipeline.
"""
from __future__ import annotations

from importlib import import_module

_LAZY_SUBMODULES = {
    "automation_writer",
    "bug_reporter",
    "card_processor",
    "release_analyser",
    "slack_client",
    "trello_client",
    "user_story_writer",
}


def __getattr__(name: str):
    if name in _LAZY_SUBMODULES:
        module = import_module(f"{__name__}.{name}")
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = sorted(_LAZY_SUBMODULES)
