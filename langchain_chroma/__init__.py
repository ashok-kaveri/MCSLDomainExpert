"""Compatibility shim for `langchain_chroma`."""
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
    spec = PathFinder.find_spec("langchain_chroma", search_path)
    if not spec or not spec.loader:
        return None
    current_module = sys.modules.get(__name__)
    module = module_from_spec(spec)
    try:
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
    class _Collection:
        def get(self, **kwargs):
            return {"ids": []}

        def delete(self, **kwargs):
            return None


    class Chroma:
        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs
            self._collection = _Collection()

        def add_documents(self, *args, **kwargs):
            return None

        def delete(self, *args, **kwargs):
            return None

        def similarity_search(self, *args, **kwargs):
            return []
