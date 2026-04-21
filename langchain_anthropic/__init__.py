"""Minimal compatibility shim for `langchain_anthropic`.

Delegates to the real package when available outside the repo. Otherwise it
provides a lightweight `ChatAnthropic` stub so unit tests can patch or import
pipeline modules without the dependency installed.
"""
from __future__ import annotations

from importlib.machinery import PathFinder
from importlib.util import module_from_spec
from pathlib import Path
import sys


def _load_real_module():
    repo_root = Path(__file__).resolve().parents[1]
    search_path = [
        path
        for path in sys.path
        if path and Path(path).resolve() != repo_root
    ]
    spec = PathFinder.find_spec("langchain_anthropic", search_path)
    if not spec or not spec.loader:
        return None
    current_module = sys.modules.get(__name__)
    module = module_from_spec(spec)
    try:
        # Register the real package before execution so its internal relative
        # imports like `langchain_anthropic._version` resolve normally.
        sys.modules[__name__] = module
        spec.loader.exec_module(module)
        return module
    except Exception:
        if current_module is not None:
            sys.modules[__name__] = current_module
        else:
            sys.modules.pop(__name__, None)
        return None


_real_module = _load_real_module()
if _real_module is not None:
    globals().update(_real_module.__dict__)
else:
    class ChatAnthropic:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def invoke(self, messages):
            raise RuntimeError("langchain_anthropic is not installed")
