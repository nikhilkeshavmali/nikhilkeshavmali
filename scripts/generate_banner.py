#!/usr/bin/env python3
"""Generate the light/dark profile banner SVGs used at the top of the README.

Usage:
    python generate_banner.py [--out-dir assets]
"""
from __future__ import annotations

import argparse
from pathlib import Path

import gitgraph
from theme import MONO, SANS, THEMES, Theme

WIDTH, HEIGHT = 1200, 270
GRAPH_CENTER_Y = HEIGHT / 2 + 6


def render_banner(theme: Theme) -> str:
    graph = gitgraph.render(theme, cy=GRAPH_CENTER_Y, highlight_index=6)

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-label="Nikhil Mali, full-stack developer">
<rect width="{WIDTH}" height="{HEIGHT}" rx="20" fill="{theme.bg}"/>
<rect x="1" y="1" width="{WIDTH - 2}" height="{HEIGHT - 2}" rx="19" fill="none" stroke="{theme.border}"/>

{graph}

<text x="64" y="96" fill="{theme.violet}" font-family="{MONO}" font-size="16">nikhil@dev</text>
<text x="169" y="96" fill="{theme.muted}" font-family="{MONO}" font-size="16">~ % whoami</text>

<text x="64" y="152" fill="{theme.text}" font-family="{SANS}" font-size="44" font-weight="700" letter-spacing="-0.5">Nikhil Mali</text>

<text x="64" y="186" fill="{theme.muted}" font-family="{SANS}" font-size="17">Full-stack developer building with React, MERN, Python and Django</text>
<rect x="64" y="204" width="110" height="2" rx="1" fill="{theme.violet}" opacity=".6"/>
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
