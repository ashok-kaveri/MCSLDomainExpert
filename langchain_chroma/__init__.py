"""Minimal compatibility shim for `langchain_chroma`."""
from __future__ import annotations


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
