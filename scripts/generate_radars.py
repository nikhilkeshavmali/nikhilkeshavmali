#!/usr/bin/env python3
"""Generate the two radar-chart SVG pairs (skills + languages) used in the README.

Edit SKILL_AXES / LANG_AXES below to change what's plotted -- these values are
illustrative self-assessments, not derived from any data source, so keep them
honest and update them as your focus shifts.

Usage:
    python generate_radar.py [--out-dir assets]
"""
from __future__ import annotations

import argparse
import math
from dataclasses import dataclass
from pathlib import Path

ACCENT = "#AA9BEF"

SKILL_AXES: list[tuple[str, int]] = [
    ("Frontend", 90),
    ("Backend", 86),
    ("APIs", 88),
    ("Databases", 82),
    ("AI/ML", 76),
    ("DevOps", 68),
]

LANG_AXES: list[tuple[str, int]] = [
    ("JavaScript", 88),
    ("Python", 86),
    ("TypeScript", 62),
    ("SQL", 78),
    ("HTML/CSS", 90),
    ("Other", 55),
]


@dataclass(frozen=True)
class Theme:
    bg: str
    fg: str
    muted: str
    grid: str


THEMES = {
    "dark": Theme(bg="#0d1117", fg="#f0f6fc", muted="#8b949e", grid="#30363d"),
    "light": Theme(bg="#ffffff", fg="#24292f", muted="#57606a", grid="#d0d7de"),
}


def _axis_point(cx: float, cy: float, radius: float, index: int, count: int) -> tuple[float, float]:
    angle = -math.pi / 2 + 2 * math.pi * index / count
    return cx + radius * math.cos(angle), cy + radius * math.sin(angle)


def render_radar(theme: Theme, title: str, axes: list[tuple[str, int]]) -> str:
    if not axes:
        raise ValueError("radar chart needs at least one axis")

    cx, cy, r = 210, 205, 145
    n = len(axes)
    labels = [label for label, _ in axes]
    values = [max(0, min(100, value)) for _, value in axes]  # clamp to a sane 0-100 range

    rings = []
    for level in range(1, 6):
        ring_r = r * level / 5
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (_axis_point(cx, cy, ring_r, i, n) for i in range(n)))
        rings.append(f'<polygon points="{pts}" fill="none" stroke="{theme.grid}" stroke-width="1"/>')

    axes_lines = []
    texts = []
    for i, label in enumerate(labels):
        x, y = _axis_point(cx, cy, r, i, n)
        axes_lines.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="{theme.grid}"/>')
        lx, ly = _axis_point(cx, cy, r + 22, i, n)
        anchor = "middle" if abs(lx - cx) < 40 else ("end" if lx < cx else "start")
        texts.append(
            f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" '
            f'fill="{theme.muted}" font-family="sans-serif" font-size="12">{label}</text>'
        )

    poly_pts = " ".join(
        f"{x:.1f},{y:.1f}"
        for x, y in (_axis_point(cx, cy, r * v / 100, i, n) for i, v in enumerate(values))
    )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 420">
<rect width="420" height="420" rx="20" fill="{theme.bg}"/>
{''.join(rings)}
{''.join(axes_lines)}
<polygon points="{poly_pts}" fill="{ACCENT}" fill-opacity=".20" stroke="{ACCENT}" stroke-width="3"/>
{''.join(texts)}
<text x="210" y="35" text-anchor="middle" fill="{theme.fg}" font-family="sans-serif" font-size="16" font-weight="700">{title}</text>
<text x="210" y="57" text-anchor="middle" fill="{ACCENT}" font-family="sans-serif" font-size="11">FOCUS RADAR</text>
</svg>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", default="assets", help="Directory to write SVGs into")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    charts = [
        ("radar", "Nikhil Mali", SKILL_AXES),
        ("radar-langs", "Nikhil Mali", LANG_AXES),
    ]

    for stem, title, axes in charts:
        for mode, theme in THEMES.items():
            svg = render_radar(theme, title, axes)
            path = out_dir / f"{stem}-{mode}.svg"
            path.write_text(svg, encoding="utf-8")
            print(f"wrote {path}")


if __name__ == "__main__":
    main()