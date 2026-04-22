"""Small Streamlit compatibility shim for tests.

If the real Streamlit package is installed outside the repository root, this
module delegates to it. Otherwise it exposes a tiny no-op surface that is
enough for unit tests that import the dashboard module without launching the UI.
"""
from __future__ import annotations

from importlib.machinery import PathFinder
from importlib.util import module_from_spec
from pathlib import Path
import sys
from types import ModuleType
from typing import Any


def _load_real_streamlit() -> ModuleType | None:
    repo_root = str(Path(__file__).resolve().parent)
    search_path = [
        path
        for path in sys.path
        if path and Path(path).resolve() != Path(repo_root).resolve()
    ]
    spec = PathFinder.find_spec("streamlit", search_path)
    if not spec or not spec.loader:
        return None
    current_module = sys.modules.get(__name__)
    module = module_from_spec(spec)
    try:
        # Register the real package before execution so Streamlit's internal
        # imports like `from streamlit import logger` resolve to the real module.
        sys.modules[__name__] = module
        spec.loader.exec_module(module)
        return module
    except Exception:
        if current_module is not None:
            sys.modules[__name__] = current_module
        else:
            sys.modules.pop(__name__, None)
        return None


_real_streamlit = _load_real_streamlit()
if _real_streamlit is not None:
    globals().update(_real_streamlit.__dict__)
    IS_SHIM = False
else:
    IS_SHIM = True

    class _SessionState(dict):
        def __getattr__(self, name: str) -> Any:
            try:
                return self[name]
            except KeyError as exc:
                raise AttributeError(name) from exc

        def __setattr__(self, name: str, value: Any) -> None:
            self[name] = value


    class _Block:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb) -> bool:
            return False

        def __call__(self, *args, **kwargs):
            return None

        def __getattr__(self, _name: str):
            return _noop


    class _Progress(_Block):
        def progress(self, *args, **kwargs):
            return None


    session_state = _SessionState()
    sidebar = _Block()


    def _noop(*args, **kwargs):
        return None


    def cache_data(*args, **kwargs):
        if args and callable(args[0]) and len(args) == 1 and not kwargs:
            return args[0]

        def decorator(func):
            return func

        return decorator


    def set_page_config(**kwargs):
        return None


    def tabs(labels):
        return [_Block() for _ in labels]


    def columns(spec):
        count = spec if isinstance(spec, int) else len(spec)
        return [_Block() for _ in range(count)]


    def expander(*args, **kwargs):
        return _Block()


    def spinner(*args, **kwargs):
        return _Block()


    def container(*args, **kwargs):
        return _Block()


    def empty():
        return _Block()


    def progress(*args, **kwargs):
        return _Progress()


    def button(*args, **kwargs):
        return False


    def checkbox(label, value=False, **kwargs):
        return value


    def toggle(label, value=False, **kwargs):
        return value


    def selectbox(label, options, index=0, **kwargs):
        if not options:
            return None
        return options[index] if 0 <= index < len(options) else options[0]


    def radio(label, options, index=0, **kwargs):
        if not options:
            return None
        return options[index] if 0 <= index < len(options) else options[0]


    def multiselect(label, options, default=None, **kwargs):
        return list(default or [])


    def text_input(label, value="", key=None, **kwargs):
        return value


    def text_area(label, value="", key=None, **kwargs):
        return value


    def number_input(label, value=0, **kwargs):
        return value


    def slider(label, min_value=None, max_value=None, value=None, **kwargs):
        return value


    def date_input(label, value=None, **kwargs):
        return value


    def file_uploader(*args, **kwargs):
        return None


    def stop():
        return None


    def rerun():
        return None


    def __getattr__(name: str):
        return _noop
