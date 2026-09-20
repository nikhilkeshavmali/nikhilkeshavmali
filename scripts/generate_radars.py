from pathlib import Path
import math

OUT = Path("assets")
OUT.mkdir(exist_ok=True)

def radar(filename, labels, values, dark=True):
    bg = "#0d1117" if dark else "#ffffff"
    fg = "#f0f6fc" if dark else "#24292f"
    muted = "#8b949e" if dark else "#57606a"
    grid = "#30363d" if dark else "#d0d7de"
    accent = "#AA9BEF"
    cx, cy, r, n = 210, 205, 145, len(labels)
    def point(i, radius):
        a = -math.pi/2 + 2*math.pi*i/n
        return cx + radius*math.cos(a), cy + radius*math.sin(a)
    rings=[]; axes=[]; texts=[]
    for level in range(1,6):
        rr=r*level/5
        pts=" ".join(f"{point(i,rr)[0]:.1f},{point(i,rr)[1]:.1f}" for i in range(n))
        rings.append(f'<polygon points="{pts}" fill="none" stroke="{grid}" stroke-width="1"/>')
    for i,label in enumerate(labels):
        x,y=point(i,r); axes.append(f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="{grid}"/>')
        lx,ly=point(i,r+22); anchor="middle" if abs(lx-cx)<40 else ("end" if lx<cx else "start")
        texts.append(f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" fill="{muted}" font-family="sans-serif" font-size="12">{label}</text>')
    pts=" ".join(f"{point(i,r*v/100)[0]:.1f},{point(i,r*v/100)[1]:.1f}" for i,v in enumerate(values))
    svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 420 420"><rect width="420" height="420" rx="20" fill="{bg}"/>{''.join(rings)}{''.join(axes)}<polygon points="{pts}" fill="{accent}" fill-opacity=".20" stroke="{accent}" stroke-width="3"/>{''.join(texts)}<text x="210" y="35" text-anchor="middle" fill="{fg}" font-family="sans-serif" font-size="16" font-weight="700">Nikhil Mali</text><text x="210" y="57" text-anchor="middle" fill="{accent}" font-family="sans-serif" font-size="11">FOCUS RADAR</text></svg>'''
    (OUT/filename).write_text(svg,encoding="utf-8")

radar("radar-dark.svg", ["Frontend","Backend","APIs","Databases","AI/ML","DevOps"], [90,86,88,82,76,68], True)
radar("radar-light.svg", ["Frontend","Backend","APIs","Databases","AI/ML","DevOps"], [90,86,88,82,76,68], False)
radar("radar-langs-dark.svg", ["JavaScript","Python","TypeScript","SQL","HTML/CSS","Other"], [88,86,62,78,90,55], True)
radar("radar-langs-light.svg", ["JavaScript","Python","TypeScript","SQL","HTML/CSS","Other"], [88,86,62,78,90,55], False)
