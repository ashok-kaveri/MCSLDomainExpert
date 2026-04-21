"""Minimal compatibility shim for `langchain_core.messages`."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass
class HumanMessage:
    content: str
