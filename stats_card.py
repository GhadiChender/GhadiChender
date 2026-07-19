#!/usr/bin/env python3
"""stats_card.py — render the year-in-review stats strip as SVG (dark + light).

Numbers are counted via the GitHub API (author-filtered commits since one year
ago, default branches, owned + org + collaborator repos) — not the profile
calendar, which lags behind reality.
"""

W, H = 1233, 178
TITLE_H = 42
MONO = "ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace"
TITLE = "ghadi@chender — ~ ./stats.sh --last-year"

METRICS = [
    ("2,677", "COMMITS.Y1", "shipped in the last 365 days"),
    ("95", "PEAK.DAY", "commits in a single day"),
    ("188", "ACTIVE.DAYS", "days with code shipped"),
    ("31d", "BEST.STREAK", "longest daily run"),
    ("15", "REPOS", "committed across"),
]

THEMES = {
    "dark": {
        "bg": "#0b0f19", "title": "#94a3b8", "divider": "#1e293b",
        "num": ["#22d3ee", "#c084fc", "#4ade80", "#f472b6", "#0ea5e9"],
        "label": "#e2e8f0", "sub": "#475569",
        "grad": ("#a855f7", "#22d3ee"),
        "lights": ["#ff5f56", "#ffbd2e", "#27c93f"],
    },
    "light": {
        "bg": "#ffffff", "title": "#64748b", "divider": "#e2e8f0",
        "num": ["#0284c7", "#7c3aed", "#15803d", "#db2777", "#0369a1"],
        "label": "#0f172a", "sub": "#94a3b8",
        "grad": ("#7c3aed", "#0891b2"),
        "lights": ["#ff5f56", "#ffbd2e", "#27c93f"],
    },
}


def build(name):
    t = THEMES[name]
    p = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" aria-label="Ghadi Chender — year in review stats">',
        f'<defs><linearGradient id="bd" x1="0" y1="0" x2="1" y2="1">'
        f'<stop offset="0" stop-color="{t["grad"][0]}"/><stop offset="1" stop-color="{t["grad"][1]}"/>'
        f"</linearGradient></defs>",
        f'<rect x="2" y="2" width="{W-4}" height="{H-4}" rx="16" '
        f'fill="{t["bg"]}" stroke="url(#bd)" stroke-width="2.5"/>',
    ]
    for i, col in enumerate(t["lights"]):
        p.append(f'<circle cx="{28 + i*22}" cy="{TITLE_H/2 + 2}" r="6.5" fill="{col}"/>')
    p.append(
        f'<text x="{W/2}" y="{TITLE_H/2 + 6}" text-anchor="middle" '
        f'font-family="{MONO}" font-size="12" fill="{t["title"]}">{TITLE}</text>'
    )
    p.append(
        f'<line x1="14" y1="{TITLE_H}" x2="{W-14}" y2="{TITLE_H}" '
        f'stroke="{t["divider"]}" stroke-width="1"/>'
    )
    n = len(METRICS)
    cw = (W - 40) / n
    for i, (num, label, sub) in enumerate(METRICS):
        cx = 20 + cw * (i + 0.5)
        if i:
            p.append(
                f'<line x1="{20 + cw*i:.0f}" y1="{TITLE_H + 22}" x2="{20 + cw*i:.0f}" '
                f'y2="{H - 24}" stroke="{t["divider"]}" stroke-width="1"/>'
            )
        p.append(
            f'<text x="{cx:.0f}" y="{TITLE_H + 62}" text-anchor="middle" font-family="{MONO}" '
            f'font-size="36" font-weight="bold" fill="{t["num"][i]}">{num}</text>'
        )
        p.append(
            f'<text x="{cx:.0f}" y="{TITLE_H + 88}" text-anchor="middle" font-family="{MONO}" '
            f'font-size="12.5" font-weight="bold" letter-spacing="1" fill="{t["label"]}">{label}</text>'
        )
        p.append(
            f'<text x="{cx:.0f}" y="{TITLE_H + 108}" text-anchor="middle" font-family="{MONO}" '
            f'font-size="10.5" fill="{t["sub"]}">{sub}</text>'
        )
    p.append("</svg>")
    return "\n".join(p)


if __name__ == "__main__":
    for name in ("dark", "light"):
        svg = build(name)
        with open(f"stats-{name}.svg", "w") as f:
            f.write(svg)
        print(f"stats-{name}.svg written")
