"""Minimal compatibility shim for `langchain_core.documents`."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Document:
    page_content: str
    metadata: dict = field(default_factory=dict)
