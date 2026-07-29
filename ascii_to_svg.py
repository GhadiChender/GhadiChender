#!/usr/bin/env python3
"""ascii_to_svg.py — render a neofetch-style terminal profile card as SVG.

Left pane: ASCII art generated from an image (luminance -> char ramp,
brightness-bucketed colors). Right pane: system-info style profile lines.
Outputs dark.svg and light.svg.
"""
from PIL import Image, ImageEnhance
import html

IMG = "assets/ninja.jpg"

# ---------------- ASCII grid ----------------
COLS, ROWS = 92, 46
RAMP = " .`':;~-=+*x#%@"      # dark -> bright
THRESH = 0.042                # below this luminance -> empty background
GAMMA = 0.40                  # lift shadows so the figure fills densely

# geometry
FS_A = 11.0                   # ascii font size
CW_A, CH_A = 6.6, 13.0        # ascii cell size
FS_I = 12.5                   # info font size
CW_I, CH_I = 7.5, 19.0        # info cell / line height
PAD = 26
TITLE_H = 46

ASCII_W = COLS * CW_A + 24    # inner pane padding 12 each side
ASCII_H = ROWS * CH_A + 24
INFO_X_OFF = 30               # gap between panes

W = int(PAD + ASCII_W + INFO_X_OFF + 520 + PAD)
H = int(TITLE_H + PAD + ASCII_H + PAD)

MONO = "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"

THEMES = {
    "dark": {
        "bg": "#0b0f19", "pane": "#0a1226", "pane_border": "#1e293b",
        "title": "#94a3b8", "divider": "#1e293b",
        "key": "#22d3ee", "dots": "#334155", "val": "#e2e8f0",
        "head": "#c084fc", "sect": "#f472b6", "note": "#4ade80",
        "buckets": ["#312e81", "#4338ca", "#0369a1", "#0ea5e9", "#22d3ee", "#a5f3fc"],
        "grad": ("#a855f7", "#22d3ee"),
        "lights": ["#ff5f56", "#ffbd2e", "#27c93f"],
        "tab": "#64748b",
    },
    "light": {
        "bg": "#ffffff", "pane": "#f8fafc", "pane_border": "#e2e8f0",
        "title": "#64748b", "divider": "#e2e8f0",
        "key": "#0284c7", "dots": "#cbd5e1", "val": "#0f172a",
        "head": "#7c3aed", "sect": "#db2777", "note": "#15803d",
        "buckets": ["#c7d2fe", "#a5b4fc", "#818cf8", "#4f46e5", "#312e81", "#0f172a"],
        "grad": ("#7c3aed", "#0891b2"),
        "lights": ["#ff5f56", "#ffbd2e", "#27c93f"],
        "tab": "#94a3b8",
    },
}

# ---------------- profile content ----------------
USER = "ghadi"
HOST = "GhadiChender"
TITLE = f"{USER}@chender — ~ ./profile.sh --live"
TAB = "NINJA.MAP"

INFO = [
    ("head", f"{USER}@{HOST}"),
    ("rule", None),
    ("kv", ("Subject", "Ghadi Chender")),
    ("kv", ("Role", "Full-Stack Engineer · AI Builder")),
    ("kv", ("Origin", "Beirut, Lebanon")),
    ("kv", ("Base", "Jeddah, Saudi Arabia")),
    ("kv", ("Education", "BSc Computer Engineering")),
    ("kv", ("Status", "Building · Automating · Shipping")),
    ("kv", ("ToolChain", "Claude Code, Git, Docker, AWS")),
    ("gap", None),
    ("kv", ("Core.Lang", "TypeScript, Python, Solidity, C++")),
    ("kv", ("Core.Frontend", "React 18, Next.js, Expo, Tailwind")),
    ("kv", ("Core.Backend", "NestJS, Node.js, Flask, Prisma")),
    ("kv", ("Core.AI", "Claude API, RAG, pgvector, vLLM")),
    ("kv", ("Core.Database", "PostgreSQL, Redis, SQL Server")),
    ("kv", ("Core.Infra", "ECS Fargate, Terraform, CI/CD")),
    ("gap", None),
    ("kv", ("Human.Langs", "AR · EN · FR · TR")),
    ("gap", None),
    ("sect", "Contact"),
    ("kv", ("Grid.Mail", "ghadichender@outlook.com")),
    ("kv", ("Grid.Site", "asco-ai.sa")),
    ("kv", ("Grid.GitHub", "GhadiChender")),
    ("gap", None),
    ("sect", "Live.Stats"),
    ("kv", ("Commits.Y1", "2,677 across 15 repos")),
    ("kv", ("Ship.Rate", "~7.3 commits / day")),
    ("note", "▓ live cards + snake below ↓"),
    ("gap", None),
    ("palette", None),
]


def ascii_grid():
    img = Image.open(IMG).convert("L")
    img = ImageEnhance.Contrast(img).enhance(1.35)
    w, h = img.size
    # crop to pane aspect (in square-pixel terms), biased toward the top (face)
    target = (COLS * CW_A) / (ROWS * CH_A) * (CH_A / CW_A) * (CW_A / CH_A)
    target = (COLS * CW_A) / (ROWS * CH_A)
    crop_h = int(w / target)
    if crop_h <= h:
        y0 = int((h - crop_h) * 0.22)
        img = img.crop((0, y0, w, y0 + crop_h))
    else:
        crop_w = int(h * target)
        x0 = (w - crop_w) // 2
        img = img.crop((x0, 0, x0 + crop_w, h))
    img = img.resize((COLS, ROWS), Image.LANCZOS)
    px = img.load()
    grid = []
    for r in range(ROWS):
        row = []
        for c in range(COLS):
            v = px[c, r] / 255.0
            if v < THRESH:
                v = 0.0
            else:
                v = ((v - THRESH) / (1 - THRESH)) ** GAMMA
            row.append(v)
        grid.append(row)
    return grid


def runs(row_vals, n_buckets):
    """yield (start_col, text, bucket) runs of equal bucket; skip spaces."""
    out = []
    cur = None
    for c, v in enumerate(row_vals):
        ci = min(int(v * len(RAMP)), len(RAMP) - 1) if v > 0 else 0
        ch = RAMP[ci]
        b = min(int(v * n_buckets), n_buckets - 1) if ch != " " else None
        if ch == " ":
            cur = None
            continue
        if cur is not None and cur[2] == b:
            cur[1].append(ch)
        else:
            cur = [c, [ch], b]
            out.append(cur)
    return [(s, "".join(chs), b) for s, chs, b in out]


def esc(s):
    return html.escape(s, quote=True)


def build(theme_name):
    t = THEMES[theme_name]
    p = []
    p.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" aria-label="Ghadi Chender terminal profile card">'
    )
    g0, g1 = t["grad"]
    p.append(
        f'<defs><linearGradient id="bd" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{g0}"/><stop offset="1" stop-color="{g1}"/>'
        f"</linearGradient></defs>"
    )
    # terminal body
    p.append(
        f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="16" '
        f'fill="{t["bg"]}" stroke="url(#bd)" stroke-width="2.5"/>'
    )
    # title bar
    for i, col in enumerate(t["lights"]):
        p.append(f'<circle cx="{28 + i*22}" cy="{TITLE_H/2 + 2}" r="6.5" fill="{col}"/>')
    p.append(
        f'<text x="{W/2}" y="{TITLE_H/2 + 6}" text-anchor="middle" '
        f'font-family="{MONO}" font-size="12" fill="{t["title"]}">{esc(TITLE)}</text>'
    )
    p.append(
        f'<line x1="14" y1="{TITLE_H}" x2="{W-14}" y2="{TITLE_H}" '
        f'stroke="{t["divider"]}" stroke-width="1"/>'
    )
    # ascii pane
    ax, ay = PAD, TITLE_H + PAD - 6
    p.append(
        f'<rect x="{ax}" y="{ay}" width="{ASCII_W}" height="{ASCII_H}" rx="10" '
        f'fill="{t["pane"]}" stroke="{t["pane_border"]}" stroke-width="1"/>'
    )
    p.append(
        f'<text x="{ax+14}" y="{ay+16}" font-family="{MONO}" font-size="9.5" '
        f'letter-spacing="2" fill="{t["tab"]}">{TAB}</text>'
    )
    grid = ascii_grid()
    bcols = t["buckets"]
    ox, oy = ax + 12, ay + 20
    p.append(f'<g font-family="{MONO}" font-size="{FS_A}" xml:space="preserve">')
    for r, row in enumerate(grid):
        y = oy + (r + 1) * CH_A - 3
        segs = runs(row, len(bcols))
        if not segs:
            continue
        line = "".join(
            f'<tspan x="{ox + s*CW_A:.1f}" fill="{bcols[b]}">{esc(txt)}</tspan>'
            for s, txt, b in segs
        )
        p.append(f'<text y="{y:.1f}">{line}</text>')
    p.append("</g>")
    # info pane
    ix = ax + ASCII_W + INFO_X_OFF
    iw = W - PAD - ix
    y = ay + 26
    p.append(f'<g font-family="{MONO}" font-size="{FS_I}" xml:space="preserve">')
    for kind, data in INFO:
        if kind == "gap":
            y += CH_I * 0.55
            continue
        if kind == "palette":
            sw, gapx = 34, 8
            for i, col in enumerate(t["buckets"] + [t["head"], t["sect"]]):
                p.append(
                    f'<rect x="{ix + i*(sw+gapx)}" y="{y - 12:.1f}" width="{sw}" '
                    f'height="16" rx="4" fill="{col}"/>'
                )
            y += CH_I
            continue
        if kind == "head":
            p.append(
                f'<text x="{ix}" y="{y:.1f}" font-size="15" font-weight="bold" '
                f'fill="{t["head"]}">{esc(data)}</text>'
            )
            y += CH_I
            continue
        if kind == "rule":
            p.append(
                f'<line x1="{ix}" y1="{y - 12:.1f}" x2="{ix+iw}" y2="{y - 12:.1f}" '
                f'stroke="{t["divider"]}" stroke-width="1"/>'
            )
            y += CH_I * 0.35
            continue
        if kind == "sect":
            p.append(
                f'<text x="{ix}" y="{y:.1f}" font-weight="bold" fill="{t["sect"]}">'
                f'── {esc(data)} ──</text>'
            )
            y += CH_I
            continue
        if kind == "note":
            p.append(f'<text x="{ix}" y="{y:.1f}" fill="{t["note"]}">{esc(data)}</text>')
            y += CH_I
            continue
        k, v = data
        total = int(iw / CW_I)
        ndots = max(2, total - len(k) - len(v) - 2)
        p.append(
            f'<text x="{ix}" y="{y:.1f}">'
            f'<tspan fill="{t["key"]}" font-weight="bold">{esc(k)}</tspan>'
            f'<tspan x="{ix + (len(k)+1)*CW_I:.1f}" fill="{t["dots"]}">{"." * ndots}</tspan>'
            f'<tspan x="{ix + iw:.1f}" text-anchor="end" fill="{t["val"]}"> {esc(v)}</tspan>'
            f"</text>"
        )
        y += CH_I
    p.append("</g>")
    p.append("</svg>")
    return "\n".join(p)


if __name__ == "__main__":
    for name in ("dark", "light"):
        svg = build(name)
        with open(f"{name}.svg", "w") as f:
            f.write(svg)
        print(f"{name}.svg written ({len(svg)//1024} KB), card {W}x{H}")
