#!/usr/bin/env python3
"""Generate the GitHub stats card and language-activity SVGs.

Reads GITHUB_USERNAME and GH_TOKEN from the environment (GH_TOKEN is optional
but strongly recommended -- unauthenticated requests are rate-limited to 60/hr
and this script can easily make dozens of calls).

Usage:
    GITHUB_USERNAME=you GH_TOKEN=ghp_xxx python generate_stats.py
"""
from __future__ import annotations

import argparse
import json
import os
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any

from theme import MONO, SANS, THEMES, Theme

API_ROOT = "https://api.github.com"
USER = os.getenv("GITHUB_USERNAME", "nikhilkeshavmali")
TOKEN = os.getenv("GH_TOKEN", "")


class GitHubError(RuntimeError):
    pass


def gh_request(path: str, *, retries: int = 3) -> Any:
    """GET a GitHub API path, with basic rate-limit / transient-error backoff."""
    url = f"{API_ROOT}{path}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "nikhil-profile-readme",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    if TOKEN:
        req.add_header("Authorization", f"Bearer {TOKEN}")

    last_error: Exception | None = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=20) as resp:
                return json.load(resp)
        except urllib.error.HTTPError as exc:
            last_error = exc
            if exc.code == 403 and exc.headers.get("X-RateLimit-Remaining") == "0":
                reset = int(exc.headers.get("X-RateLimit-Reset", time.time() + 60))
                wait = max(1, reset - int(time.time()))
                print(f"rate limited, sleeping {wait}s ...")
                time.sleep(min(wait, 60))
                continue
            if exc.code == 404:
                raise GitHubError(f"not found: {path}") from exc
            time.sleep(1.5 * (attempt + 1))
        except urllib.error.URLError as exc:
            last_error = exc
            time.sleep(1.5 * (attempt + 1))
    raise GitHubError(f"failed to fetch {path}: {last_error}")


def fetch_repos(user: str) -> list[dict[str, Any]]:
    repos: list[dict[str, Any]] = []
    page = 1
    while True:
        batch = gh_request(f"/users/{user}/repos?per_page=100&page={page}&type=owner&sort=updated")
        if not batch:
            break
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return repos


def fetch_language_totals(user: str, repos: list[dict[str, Any]]) -> Counter:
    totals: Counter = Counter()
    for repo in repos:
        if repo.get("fork"):
            continue
        try:
            langs = gh_request(f"/repos/{user}/{repo['name']}/languages")
            totals.update(langs)
        except GitHubError as exc:
            print(f"skipping {repo['name']}: {exc}")
        time.sleep(0.05)  # be polite, avoid secondary rate limits
    return totals


# --- hand-drawn line icons (24x24 viewbox, stroke-based, no external assets) ---

_ICON_REPO = (
    'M4 3.5h13a2 2 0 0 1 2 2v13.5a1 1 0 0 1-1.55.85L14 17l-3.45 2.85A1 1 0 0 1 9 19V6a2 2 0 0 1 2-2'
)
_ICON_FOLLOWERS = "M12 12a4 4 0 1 0 0-8 4 4 0 0 0 0 8ZM4.5 20a7.5 7.5 0 0 1 15 0"
_ICON_SCAN = "M4 8V5a1 1 0 0 1 1-1h3M17 4h3a1 1 0 0 1 1 1v3M20 16v3a1 1 0 0 1-1 1h-3M7 20H4a1 1 0 0 1-1-1v-3M4 12h16"

ICONS = {"repo": _ICON_REPO, "followers": _ICON_FOLLOWERS, "scan": _ICON_SCAN}


def _icon(name: str, x: float, y: float, theme: Theme) -> str:
    d = ICONS[name]
    return (
        f'<g transform="translate({x},{y})">'
        f'<rect x="0" y="0" width="36" height="36" rx="9" fill="{theme.violet_dim}"/>'
        f'<path d="{d}" transform="translate(6,6)" fill="none" stroke="{theme.violet}" '
        f'stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round"/>'
        f"</g>"
    )


def render_stats_card(theme: Theme, public_repos: str, followers: str, repo_count: str) -> str:
    rows = [
        ("repo", "Public repositories", public_repos),
        ("followers", "Followers", followers),
        ("scan", "Repositories scanned for languages", repo_count),
    ]
    row_svg = []
    for i, (icon, label, value) in enumerate(rows):
        y = 108 + i * 62
        row_svg.append(_icon(icon, 48, y, theme))
        row_svg.append(
            f'<text x="98" y="{y + 15}" fill="{theme.text}" font-family="{SANS}" font-size="15">{label}</text>'
        )
        row_svg.append(
            f'<text x="472" y="{y + 24}" text-anchor="end" fill="{theme.violet}" '
            f'font-family="{MONO}" font-size="24" font-weight="700">{value}</text>'
        )

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 300" role="img" aria-label="GitHub snapshot for {USER}">
<rect width="520" height="300" rx="18" fill="{theme.bg}" stroke="{theme.border}"/>
<text x="48" y="54" fill="{theme.text}" font-family="{SANS}" font-size="19" font-weight="700">GitHub snapshot</text>
<text x="48" y="76" fill="{theme.muted}" font-family="{MONO}" font-size="12">@{USER}</text>
<line x1="48" y1="90" x2="472" y2="90" stroke="{theme.border}"/>
{''.join(row_svg)}
</svg>
"""


def render_lang_card(theme: Theme, items: list[tuple[str, float]]) -> str:
    rows = []
    for i, (name, pct) in enumerate(items):
        y = 100 + i * 44
        bar_width = 330 * pct / 100
        rows.append(
            f'<text x="35" y="{y}" fill="{theme.muted}" font-family="{MONO}" font-size="12">{i + 1:02d}</text>'
            f'<text x="62" y="{y}" fill="{theme.text}" font-family="{SANS}" font-size="14" font-weight="600">{name}</text>'
            f'<text x="485" y="{y}" text-anchor="end" fill="{theme.muted}" '
            f'font-family="{MONO}" font-size="12">{pct:.1f}%</text>'
            f'<rect x="62" y="{y + 10}" width="330" height="6" rx="3" fill="{theme.border}"/>'
            f'<rect x="62" y="{y + 10}" width="{bar_width:.1f}" height="6" rx="3" fill="url(#langBar)"/>'
        )
    height = max(360, 100 + len(items) * 44 + 30)
    empty_state = (
        f'<text x="35" y="110" fill="{theme.muted}" font-family="{SANS}" font-size="13">'
        "No language data available</text>"
    )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 {height}" role="img" aria-label="Language activity for {USER}">
<defs>
  <linearGradient id="langBar" x1="0" x2="1">
    <stop offset="0" stop-color="{theme.violet}"/>
    <stop offset="1" stop-color="{theme.amber}"/>
  </linearGradient>
</defs>
<rect width="520" height="{height}" rx="18" fill="{theme.bg}" stroke="{theme.border}"/>
<text x="35" y="50" fill="{theme.text}" font-family="{SANS}" font-size="19" font-weight="700">Language activity</text>
<line x1="35" y1="66" x2="485" y2="66" stroke="{theme.border}"/>
{''.join(rows) if rows else empty_state}
</svg>
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out-dir", default="assets", help="Directory to write SVGs into")
    args = parser.parse_args()

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        profile = gh_request(f"/users/{USER}")
        repos = fetch_repos(USER)
        lang_totals = fetch_language_totals(USER, repos)
        total = sum(lang_totals.values()) or 1
        items = [(lang, count / total * 100) for lang, count in lang_totals.most_common(6)]
        public_repos = str(profile.get("public_repos", "—"))
        followers = str(profile.get("followers", "—"))
        repo_count = str(len(repos))
    except GitHubError as exc:
        print(f"GitHub API update failed: {exc}")
        public_repos = followers = repo_count = "—"
        items = []

    for mode, theme in THEMES.items():
        (out_dir / f"card-stats-{mode}.svg").write_text(
            render_stats_card(theme, public_repos, followers, repo_count), encoding="utf-8"
        )

    # metrics.languages.svg has no light/dark pair in the README, so keep dark only
    (out_dir / "metrics.languages.svg").write_text(
        render_lang_card(THEMES["dark"], items), encoding="utf-8"
    )

    print(f"wrote card-stats-dark.svg, card-stats-light.svg, metrics.languages.svg to {out_dir}/")


if __name__ == "__main__":
    main()