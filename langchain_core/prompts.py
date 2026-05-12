"""Minimal PromptTemplate shim for local tests without langchain-core."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PromptTemplate:
    input_variables: list[str]
    template: str

    def format(self, **kwargs: object) -> str:
        return self.template.format(**kwargs)
