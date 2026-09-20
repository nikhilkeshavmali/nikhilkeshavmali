#!/usr/bin/env python3
"""Generate the light/dark profile banner SVGs used at the top of the README.

Usage:
    python generate_banner.py [--out-dir assets]
"""
from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

ACCENT = "#AA9BEF"
ACCENT_DIM = "#7c6ee6"


@dataclass(frozen=True)
class Theme:
    bg: str
    fg: str
    muted: str
    grid: str


THEMES = {
    "dark": Theme(bg="#0d1117", fg="#f0f6fc", muted="#8b949e", grid="#21262d"),
    "light": Theme(bg="#f6f8fa", fg="#24292f", muted="#57606a", grid="#d0d7de"),
}


def _dot_grid(grid_color: str) -> str:
    dots = [
        f'<circle cx="{x}" cy="{y}" r="1" fill="{grid_color}" opacity=".45"/>'
        for x in range(40, 1160, 55)
        for y in range(28, 240, 42)
    ]
    return "".join(dots)


def render_banner(theme: Theme) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 270">
<defs>
  <linearGradient id="g" x1="0" x2="1">
    <stop offset="0" stop-color="{ACCENT}"/>
    <stop offset="1" stop-color="{ACCENT_DIM}" stop-opacity=".55"/>
  </linearGradient>
</defs>
<rect width="1200" height="270" rx="24" fill="{theme.bg}"/>
{_dot_grid(theme.grid)}
<path d="M-20 220 C220 110 350 300 570 175 S900 40 1220 145" fill="none" stroke="url(#g)" stroke-width="3" opacity=".65"/>
<path d="M-20 238 C220 128 350 318 570 193 S900 58 1220 163" fill="none" stroke="{ACCENT}" stroke-width="1" opacity=".18"/>
<text x="70" y="92" fill="{ACCENT}" font-family="monospace" font-size="18" font-weight="700">~/nikhil</text>
<text x="70" y="142" fill="{theme.fg}" font-family="monospace" font-size="39" font-weight="800">Full Stack Developer</text>
<text x="70" y="180" fill="{theme.muted}" font-family="monospace" font-size="18">React • MERN • Python • Django • AI</text>
<rect x="70" y="204" width="340" height="2" rx="1" fill="{ACCENT}" opacity=".75"/>
<text x="1080" y="72" fill="{ACCENT}" font-family="monospace" font-size="14">01</text>
<text x="1080" y="92" fill="{theme.muted}" font-family="monospace" font-size="12">BUILD</text>
</svg>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", default="assets", help="Directory to write SVGs into")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    for mode, theme in THEMES.items():
        svg = render_banner(theme)
        path = out_dir / f"banner-{mode}.svg"
        path.write_text(svg, encoding="utf-8")
        print(f"wrote {path}")


if __name__ == "__main__":
    main()