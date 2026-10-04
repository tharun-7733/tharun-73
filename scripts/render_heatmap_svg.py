#!/usr/bin/env python3
"""Render data/contributions.json as an animated 53x7 heatmap -> contrib-heatmap.svg"""
import json
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "contributions.json"
OUT = ROOT / "contrib-heatmap.svg"

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#69f0a0"]
CELL, GAP = 12, 3
STEP = CELL + GAP
W = 860
LEFT, TOP = 44, 40
BG, DIM, TEXT = "#0d1117", "#8b949e", "#c9d1d9"
MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]


def level_for(d: dict, max_count: int) -> int:
    """GitHub gives levels 0-4; promote the very busiest days to a neon level 5."""
    lv = d["level"]
    if lv == 4 and max_count and d["count"] >= 0.8 * max_count:
        return 5
    return lv


def main() -> None:
    data = json.loads(SRC.read_text())
    days, st = data["days"], data["stats"]
    max_count = max(d["count"] for d in days)

    first = date.fromisoformat(days[0]["date"])
    start = first - timedelta(days=(first.weekday() + 1) % 7)   # Sunday on/before first day
    n_weeks = (date.fromisoformat(days[-1]["date"]) - start).days // 7 + 1

    cells, month_labels, last_month = [], [], None
    for d in days:
        dt = date.fromisoformat(d["date"])
        row = (dt.weekday() + 1) % 7
        col = (dt - start).days // 7
        x, y = LEFT + col * STEP, TOP + row * STEP
        lv = level_for(d, max_count)
        delay = (col + row) * 0.012
        tip = f'{d["count"]} contribution{"s" if d["count"] != 1 else ""} on {d["date"]}'
        cells.append(
            f'<rect class="c" x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="3" '
            f'fill="{PALETTE[lv]}" style="animation-delay:{delay:.3f}s"><title>{tip}</title></rect>'
        )
        if row == 0 and dt.month != last_month:
            month_labels.append(f'<text x="{x}" y="{TOP - 10}">{MONTHS[dt.month - 1]}</text>')
            last_month = dt.month

    day_labels = "".join(
        f'<text x="{LEFT - 10}" y="{TOP + r * STEP + 10}" text-anchor="end">{name}</text>'
        for r, name in ((1, "Mon"), (3, "Wed"), (5, "Fri"))
    )

    grid_bottom = TOP + 7 * STEP
    legend_y = grid_bottom + 14
    lx = W - 20 - (len(PALETTE) * STEP + 80)
    legend = [f'<text x="{lx}" y="{legend_y + 10}">Less</text>']
    for i, col in enumerate(PALETTE):
        legend.append(f'<rect x="{lx + 32 + i * STEP}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="3" fill="{col}"/>')
    legend.append(f'<text x="{lx + 38 + len(PALETTE) * STEP}" y="{legend_y + 10}">More</text>')

    footer = (f'{st["total"]:,} contributions in the last year  ·  '
              f'current streak {st["current_streak"]}d  ·  longest {st["longest_streak"]}d  ·  '
              f'best day {st["best_day"]["count"]}')
    H = legend_y + 40
    nl = "\n"

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">
<style>
@keyframes drop{{from{{opacity:0;transform:translateY(-8px)}}to{{opacity:1;transform:none}}}}
.c{{opacity:0;animation:drop .5s ease-out forwards}}
text{{font:11px ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;fill:{DIM}}}
.f{{font-size:12px;fill:{TEXT}}}
</style>
<rect width="{W}" height="{H}" rx="10" fill="{BG}"/>
{"".join(month_labels)}
{day_labels}
{nl.join(cells)}
{nl.join(legend)}
<text class="f" x="{LEFT}" y="{legend_y + 10}">{footer}</text>
</svg>
'''
    OUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT} ({n_weeks} weeks, {len(cells)} days)")


if __name__ == "__main__":
    main()
