"""Minimal compatibility shim for `chromadb`."""
from __future__ import annotations


class _Collection:
    def delete(self, **kwargs):
        return None


class PersistentClient:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def delete_collection(self, *args, **kwargs):
        return None

    def get_collection(self, *args, **kwargs):
        return _Collection()
