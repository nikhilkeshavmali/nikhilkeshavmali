"""A small, hand-tuned git commit-graph, drawn as decoration for the banner.

Three lanes (main / feature / hotfix) that branch and merge, in the style of
`git log --graph`. Coordinates are hand-placed rather than randomised so the
composition stays intentional -- this is meant to read as a *shape*, not a
literal, accurate graph.
"""
from __future__ import annotations

from theme import Theme

# (x, lane) pairs for the main lane's commits; lane 0 = main.
MAIN_COMMITS = [560, 610, 660, 760, 820, 870, 960, 1010, 1060, 1110]
# feature branch: splits off after the 3rd main commit, rejoins before the 6th
FEATURE_SPLIT_X, FEATURE_JOIN_X = MAIN_COMMITS[2], MAIN_COMMITS[5]
FEATURE_COMMITS = [740, 770, 800]
# hotfix branch: short-lived, splits after the 7th, rejoins at the 10th
HOTFIX_SPLIT_X, HOTFIX_JOIN_X = MAIN_COMMITS[6], MAIN_COMMITS[9]
HOTFIX_COMMITS = [1035]

LANE_OFFSET = 46  # vertical distance from the main lane to a side lane


def render(theme: Theme, cy: float, *, highlight_index: int = 6) -> str:
    """Render the graph centered on ``cy``. One commit (``highlight_index``
    into MAIN_COMMITS) is drawn in the amber accent as a focal point."""
    feature_y = cy - LANE_OFFSET
    hotfix_y = cy + LANE_OFFSET

    parts: list[str] = []

    # main lane, full width
    x_first, x_last = MAIN_COMMITS[0], MAIN_COMMITS[-1]
    parts.append(f'<path d="M{x_first} {cy} H{x_last}" stroke="{theme.violet_dim}" stroke-width="2" fill="none"/>')

    # feature branch: split down, run, merge back up
    parts.append(
        f'<path d="M{FEATURE_SPLIT_X} {cy} '
        f'C {FEATURE_SPLIT_X + 30} {cy} {FEATURE_SPLIT_X + 30} {feature_y} {FEATURE_SPLIT_X + 60} {feature_y} '
        f'H {FEATURE_JOIN_X - 60} '
        f'C {FEATURE_JOIN_X - 30} {feature_y} {FEATURE_JOIN_X - 30} {cy} {FEATURE_JOIN_X} {cy}" '
        f'stroke="{theme.violet}" stroke-width="2" fill="none" opacity=".55"/>'
    )

    # hotfix branch: split up, run, merge back down
    parts.append(
        f'<path d="M{HOTFIX_SPLIT_X} {cy} '
        f'C {HOTFIX_SPLIT_X + 25} {cy} {HOTFIX_SPLIT_X + 25} {hotfix_y} {HOTFIX_SPLIT_X + 50} {hotfix_y} '
        f'H {HOTFIX_JOIN_X - 50} '
        f'C {HOTFIX_JOIN_X - 25} {hotfix_y} {HOTFIX_JOIN_X - 25} {cy} {HOTFIX_JOIN_X} {cy}" '
        f'stroke="{theme.violet}" stroke-width="2" fill="none" opacity=".4"/>'
    )

    # commit dots
    for i, x in enumerate(MAIN_COMMITS):
        is_highlight = i == highlight_index
        r = 5 if is_highlight else 3.5
        fill = theme.amber if is_highlight else theme.violet
        parts.append(f'<circle cx="{x}" cy="{cy}" r="{r}" fill="{theme.bg}" stroke="{fill}" stroke-width="2"/>')
        if is_highlight:
            parts.append(f'<circle cx="{x}" cy="{cy}" r="1.6" fill="{fill}"/>')

    for x in FEATURE_COMMITS:
        parts.append(f'<circle cx="{x}" cy="{feature_y}" r="3" fill="{theme.bg}" stroke="{theme.violet}" stroke-width="1.6" opacity=".7"/>')

    for x in HOTFIX_COMMITS:
        parts.append(f'<circle cx="{x}" cy="{hotfix_y}" r="3" fill="{theme.bg}" stroke="{theme.violet}" stroke-width="1.6" opacity=".55"/>')

    return "".join(parts)
