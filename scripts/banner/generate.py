from pathlib import Path

OUT = Path("assets")
OUT.mkdir(exist_ok=True)

def make(dark=True):
    bg = "#0d1117" if dark else "#f6f8fa"
    fg = "#f0f6fc" if dark else "#24292f"
    muted = "#8b949e" if dark else "#57606a"
    grid = "#21262d" if dark else "#d0d7de"
    accent = "#AA9BEF"
    dots = "".join(f'<circle cx="{x}" cy="{y}" r="1" fill="{grid}" opacity=".45"/>' for x in range(40,1160,55) for y in range(28,240,42))
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1200 270">
<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{accent}"/><stop offset="1" stop-color="#7c6ee6" stop-opacity=".55"/></linearGradient></defs>
<rect width="1200" height="270" rx="24" fill="{bg}"/>{dots}
<path d="M-20 220 C220 110 350 300 570 175 S900 40 1220 145" fill="none" stroke="url(#g)" stroke-width="3" opacity=".65"/>
<path d="M-20 238 C220 128 350 318 570 193 S900 58 1220 163" fill="none" stroke="{accent}" stroke-width="1" opacity=".18"/>
<text x="70" y="92" fill="{accent}" font-family="monospace" font-size="18" font-weight="700">~/nikhil</text>
<text x="70" y="142" fill="{fg}" font-family="monospace" font-size="39" font-weight="800">Full Stack Developer</text>
<text x="70" y="180" fill="{muted}" font-family="monospace" font-size="18">React • MERN • Python • Django • AI</text>
<rect x="70" y="204" width="340" height="2" rx="1" fill="{accent}" opacity=".75"/>
<text x="1080" y="72" fill="{accent}" font-family="monospace" font-size="14">01</text>
<text x="1080" y="92" fill="{muted}" font-family="monospace" font-size="12">BUILD</text>
</svg>'''
    (OUT / ("banner-dark.svg" if dark else "banner-light.svg")).write_text(svg, encoding="utf-8")

make(True)
make(False)
