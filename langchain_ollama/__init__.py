"""Minimal compatibility shim for `langchain_ollama`."""
from __future__ import annotations


class OllamaEmbeddings:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
