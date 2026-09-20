from pathlib import Path
import os, json, urllib.request
from collections import Counter

OUT=Path("assets"); OUT.mkdir(exist_ok=True)
USER=os.getenv("GITHUB_USERNAME","nikhilkeshavmali")
TOKEN=os.getenv("GH_TOKEN","")

def gh(path):
    req=urllib.request.Request(f"https://api.github.com{path}",headers={"Accept":"application/vnd.github+json","User-Agent":"nikhil-profile"})
    if TOKEN: req.add_header("Authorization",f"Bearer {TOKEN}")
    with urllib.request.urlopen(req,timeout=20) as r: return json.load(r)

def stats_card(public_repos,followers,repo_count):
    bg,fg,muted,accent="#0d1117","#f0f6fc","#8b949e","#AA9BEF"
    rows=[]
    for i,(a,b) in enumerate([("Public repos",public_repos),("Followers",followers),("Repositories scanned",repo_count)]):
        y=112+i*54; rows.append(f'<text x="48" y="{y}" fill="{muted}" font-family="sans-serif" font-size="15">{a}</text><text x="470" y="{y}" text-anchor="end" fill="{fg}" font-family="monospace" font-size="18" font-weight="700">{b}</text>')
    d=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 290"><rect width="520" height="290" rx="18" fill="{bg}" stroke="#30363d"/><text x="48" y="52" fill="{fg}" font-family="sans-serif" font-size="20" font-weight="700">GitHub snapshot</text><text x="48" y="76" fill="{accent}" font-family="monospace" font-size="11">@{USER}</text>{"".join(rows)}</svg>'
    l=d.replace("#0d1117","#ffffff").replace("#f0f6fc","#24292f").replace("#8b949e","#57606a").replace("#30363d","#d0d7de")
    (OUT/"card-stats-dark.svg").write_text(d); (OUT/"card-stats-light.svg").write_text(l)

def lang_card(items):
    bg,fg,muted,accent="#0d1117","#f0f6fc","#8b949e","#AA9BEF"; rows=[]
    for i,(name,pct) in enumerate(items):
        y=92+i*45; w=360*pct/100
        rows.append(f'<text x="35" y="{y}" fill="{muted}" font-family="sans-serif" font-size="13">{name}</text><text x="485" y="{y}" text-anchor="end" fill="{muted}" font-family="monospace" font-size="12">{pct:.1f}%</text><rect x="35" y="{y+10}" width="360" height="6" rx="3" fill="#30363d"/><rect x="35" y="{y+10}" width="{w:.1f}" height="6" rx="3" fill="{accent}"/>')
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 520 380"><rect width="520" height="380" rx="18" fill="{bg}" stroke="#30363d"/><text x="35" y="48" fill="{fg}" font-family="sans-serif" font-size="20" font-weight="700">Language activity</text>{"".join(rows)}</svg>'
    (OUT/"metrics.languages.svg").write_text(svg)

try:
    repos=gh(f"/users/{USER}/repos?per_page=100&type=owner&sort=updated")
    profile=gh(f"/users/{USER}")
    langs=Counter()
    for repo in repos:
        if repo.get("fork"): continue
        try: langs.update(gh(f"/repos/{USER}/{repo['name']}/languages"))
        except Exception: pass
    total=sum(langs.values()) or 1
    items=[(k,v/total*100) for k,v in langs.most_common(6)]
    stats_card(profile.get("public_repos","—"),profile.get("followers","—"),len(repos)); lang_card(items)
except Exception as e:
    print("GitHub API update failed:",e)
    stats_card("—","—","—"); lang_card([])
