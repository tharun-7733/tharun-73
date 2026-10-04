#!/usr/bin/env python3
"""Hand-authored neofetch-style info card -> info-card.svg

Edit the CONFIG block below with your own details.
STATIC=1 python scripts/make_info_card.py   # frozen frame for local previews
"""
import os
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "info-card.svg"
STATIC = os.environ.get("STATIC") == "1"

# ---------------- CONFIG: edit me ----------------
USER = "TT"
HOST = "github"
FIELDS = [
    ("Role",       ["Software Engineer"]),
    ("Now",        ["Building products & tools in public"]),
    ("Prev",       ["Internships / past roles go here"]),
    ("Stack",      ["Python, TypeScript, React, Node.js"]),
    ("Highlights", ["Shipped X to N users",
                   "Open-source contributions",
                   "Hackathon wins / awards"]),
    ("Reach me",   ["you@example.com"]),
]
# -------------------------------------------------

W = 490
LINE_H = 22
FONT = 13
KEY_W = 12                      # key column width in characters
C = dict(bg="#0d1117", bar="#161b22", text="#c9d1d9", dim="#8b949e",
         key="#58a6ff", user="#39d353")
STRIP = ["#f85149", "#d29922", "#39d353", "#58a6ff", "#bc8cff", "#39c5cf", "#c9d1d9", "#6e7681"]

rows = []        # each row: list[(text, colour)] or "STRIP"
rows.append([(USER, C["user"]), ("@", C["dim"]), (HOST, C["user"])])
rows.append([("-" * (len(USER) + len(HOST) + 1), C["dim"])])
for key, vals in FIELDS:
    rows.append([((key + ":").ljust(KEY_W), C["key"]), (vals[0], C["text"])])
    for extra in vals[1:]:
        rows.append([(" " * KEY_W, C["text"]), (extra, C["text"])])
rows.append([("", C["text"])])
rows.append("STRIP")

BAR_H = 34
TOP = BAR_H + 30
H = TOP + len(rows) * LINE_H + 10

if STATIC:
    css = ".l{opacity:1}"
else:
    css = ("@keyframes in{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:none}}"
           ".l{opacity:0;animation:in .45s ease-out forwards}")

out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
    f"<style>{css}</style>",
    f'<rect width="{W}" height="{H}" rx="10" fill="{C["bg"]}"/>',
    f'<path d="M0 10a10 10 0 0 1 10-10h{W-20}a10 10 0 0 1 10 10v{BAR_H-10}H0z" fill="{C["bar"]}"/>',
    f'<circle cx="20" cy="{BAR_H/2}" r="6" fill="#ff5f56"/>',
    f'<circle cx="40" cy="{BAR_H/2}" r="6" fill="#ffbd2e"/>',
    f'<circle cx="60" cy="{BAR_H/2}" r="6" fill="#27c93f"/>',
    f'<text x="{W/2}" y="{BAR_H/2+4}" text-anchor="middle" fill="{C["dim"]}" '
    f'font-family="ui-monospace,Menlo,Consolas,monospace" font-size="12">{USER}@{HOST}: ~ $ neofetch</text>',
    f'<g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,\'Courier New\',monospace" font-size="{FONT}">',
]

for i, row in enumerate(rows):
    y = TOP + i * LINE_H
    delay = 0.3 + i * 0.12
    if row == "STRIP":
        blocks = "".join(f'<rect x="{20 + j*22}" y="{y-12}" width="18" height="14" rx="3" fill="{c}"/>'
                         for j, c in enumerate(STRIP))
        out.append(f'<g class="l" style="animation-delay:{delay:.2f}s">{blocks}</g>')
        continue
    spans = "".join(f'<tspan fill="{col}">{escape(t)}</tspan>' for t, col in row)
    out.append(f'<text class="l" x="20" y="{y}" xml:space="preserve" style="white-space:pre;'
               f'animation-delay:{delay:.2f}s">{spans}</text>')

out += ["</g>", "</svg>", ""]
OUT.write_text("\n".join(out), encoding="utf-8")
print(f"wrote {OUT}")
