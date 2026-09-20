#!/usr/bin/env python3
"""Generate the GitHub stats card and language-activity SVGs.

Reads GITHUB_USERNAME and GH_TOKEN from the environment (GH_TOKEN is optional
but strongly recommended -- unauthenticated requests are rate-limited to 60/hr
and this script can easily make dozens of calls).

Usage:
    GITHUB_USERNAME=you GH_TOKEN=ghp_xxx python generate_stats.py
"""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Any

API_ROOT = "https://api.github.com"
OUT_DIR = Path("assets")
USER = os.getenv("GITHUB_USERNAME", "nikhilkeshavmali")
TOKEN = os.getenv("GH_TOKEN", "")

ACCENT = "#AA9BEF"


@dataclass(frozen=True)
class Theme:
    bg: str
    fg: str
    muted: str
    border: str


THEMES = {
    "dark": Theme(bg="#0d1117", fg="#f0f6fc", muted="#8b949e", border="#30363d"),
    "light": Theme(bg="#ffffff", fg="#24292f", muted="#57606a", border="#d0d7de"),
}


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


def render_stats_card(theme: Theme, public_repos: str, followers: str, repo_count: str) -> str:
    rows = []
    for i, (label, value) in enumerate(
        [("Public repos", public_repos), ("Followers", followers), ("Repositories scanned", repo_count)]
    ):
        y = 112 + i * 54
        rows.append(
            f'<text x="48" y="{y}" fill="{theme.muted}" font-family="sans-serif" font-size="15">{label}</text>'
            f'<text x="470" y="{y}" text-anchor="end" fill="{theme.fg}" '
            f'font-family="monospace" font-size="18" font-weight="700">{value}</text>'
        )
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 290">
<rect width="520" height="290" rx="18" fill="{theme.bg}" stroke="{theme.border}"/>
<text x="48" y="52" fill="{theme.fg}" font-family="sans-serif" font-size="20" font-weight="700">GitHub snapshot</text>
<text x="48" y="76" fill="{ACCENT}" font-family="monospace" font-size="11">@{USER}</text>
{''.join(rows)}
</svg>
"""


def render_lang_card(theme: Theme, items: list[tuple[str, float]]) -> str:
    rows = []
    for i, (name, pct) in enumerate(items):
        y = 92 + i * 45
        bar_width = 360 * pct / 100
        rows.append(
            f'<text x="35" y="{y}" fill="{theme.muted}" font-family="sans-serif" font-size="13">{name}</text>'
            f'<text x="485" y="{y}" text-anchor="end" fill="{theme.muted}" '
            f'font-family="monospace" font-size="12">{pct:.1f}%</text>'
            f'<rect x="35" y="{y + 10}" width="360" height="6" rx="3" fill="{theme.border}"/>'
            f'<rect x="35" y="{y + 10}" width="{bar_width:.1f}" height="6" rx="3" fill="{ACCENT}"/>'
        )
    height = max(380, 92 + len(items) * 45 + 30)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 {height}">
<rect width="520" height="{height}" rx="18" fill="{theme.bg}" stroke="{theme.border}"/>
<text x="35" y="48" fill="{theme.fg}" font-family="sans-serif" font-size="20" font-weight="700">Language activity</text>
{''.join(rows) if rows else f'<text x="35" y="100" fill="{theme.muted}" font-family="sans-serif" font-size="13">No language data available</text>'}
</svg>
"""


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

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
        (OUT_DIR / f"card-stats-{mode}.svg").write_text(
            render_stats_card(theme, public_repos, followers, repo_count), encoding="utf-8"
        )

    # metrics.languages.svg has no light/dark pair in the README, so keep dark only
    (OUT_DIR / "metrics.languages.svg").write_text(
        render_lang_card(THEMES["dark"], items), encoding="utf-8"
    )

    print(f"wrote card-stats-dark.svg, card-stats-light.svg, metrics.languages.svg to {OUT_DIR}/")


if __name__ == "__main__":
    main()