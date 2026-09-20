"""Shared design tokens for the profile README assets.

Concept: the profile belongs to a developer, so the visual language borrows
from git itself -- commit graphs, diff markers, a terminal prompt -- rather
than generic dashboard chrome. One accent pair (violet / amber) carries every
asset so the set reads as one system rather than five unrelated charts.
"""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Theme:
    bg: str
    surface: str
    border: str
    text: str
    muted: str
    violet: str
    violet_dim: str
    amber: str


DARK = Theme(
    bg="#0B0E14",
    surface="#121722",
    border="#232B3A",
    text="#EDEFF4",
    muted="#8891A3",
    violet="#AA9BEF",
    violet_dim="#4E4670",
    amber="#F2B872",
)

LIGHT = Theme(
    bg="#FAFAF8",
    surface="#FFFFFF",
    border="#E3E0D8",
    text="#1B1E27",
    muted="#6B7280",
    violet="#8C7AE6",
    violet_dim="#DDD5F7",
    amber="#C9782E",
)

THEMES = {"dark": DARK, "light": LIGHT}

SANS = "'Segoe UI', system-ui, -apple-system, sans-serif"
MONO = "ui-monospace, 'SFMono-Regular', 'JetBrains Mono', Menlo, Consolas, monospace"
