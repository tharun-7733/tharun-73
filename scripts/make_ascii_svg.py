#!/usr/bin/env python3
"""Convert source-prepped.png into a self-typing monochrome ASCII SVG (TT-ascii.svg)."""
import sys
from html import escape
from pathlib import Path

import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "source-prepped.png"
OUT = ROOT / "TT-ascii.svg"

RAMP = " .`:-=+*cs#%@"      # bright (sparse) -> dark (dense); leading space = blank
COLS = 100                  # characters per row
CELL_W, CELL_H = 6.0, 11.0  # character cell size in px
FONT_SIZE = 10
FILL = "#c9d1d9"            # one light-gray colour (monochrome)
BG = "#0d1117"
PAD = 12
GAMMA = 0.9                 # <1 brightens shadows a little
THRESHOLD = 0.06            # darkness below this -> blank
ROW_STAGGER = 0.05          # seconds between rows
ROW_DUR = 0.45              # seconds per row wipe


def main() -> None:
    img = Image.open(SRC).convert("L")
    w, h = img.size
    rows = max(1, round(COLS * (h / w) * (CELL_W / CELL_H)))
    img = img.resize((COLS, rows), Image.LANCZOS)

    dark = 1.0 - np.asarray(img, dtype=np.float32) / 255.0
    dark = np.clip(dark, 0, 1) ** GAMMA

    lines = []
    for r in range(rows):
        chars = []
        for c in range(COLS):
            d = dark[r, c]
            chars.append(" " if d < THRESHOLD else RAMP[min(int(d * len(RAMP)), len(RAMP) - 1)])
        lines.append("".join(chars).rstrip())

    width = COLS * CELL_W + 2 * PAD
    height = rows * CELL_H + 2 * PAD

    defs, body = [], []
    for i, line in enumerate(lines):
        if not line:
            continue
        begin = f"{0.3 + i * ROW_STAGGER:.2f}s"
        tw = len(line) * CELL_W
        y_top = i * CELL_H
        defs.append(
            f'<clipPath id="c{i}"><rect x="0" y="{y_top:.1f}" width="0" height="{CELL_H + 1:.1f}">'
            f'<animate attributeName="width" from="0" to="{tw:.1f}" begin="{begin}" '
            f'dur="{ROW_DUR}s" fill="freeze"/></rect></clipPath>'
        )
        body.append(
            f'<text x="0" y="{(i + 1) * CELL_H - 2:.1f}" textLength="{tw:.1f}" lengthAdjust="spacing" '
            f'xml:space="preserve" style="white-space:pre" clip-path="url(#c{i})">{escape(line)}</text>'
        )
        # block cursor riding the wipe edge
        body.append(
            f'<rect x="0" y="{y_top:.1f}" width="{CELL_W}" height="{CELL_H}" fill="{FILL}" opacity="0">'
            f'<animate attributeName="x" from="0" to="{tw:.1f}" begin="{begin}" dur="{ROW_DUR}s" fill="freeze"/>'
            f'<animate attributeName="opacity" values="1;1;0" keyTimes="0;0.97;1" begin="{begin}" '
            f'dur="{ROW_DUR}s" fill="freeze"/></rect>'
        )

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.0f} {height:.0f}" '
        f'width="{width:.0f}" height="{height:.0f}">\n'
        f'<rect width="100%" height="100%" rx="10" fill="{BG}"/>\n'
        f'<defs>{"".join(defs)}</defs>\n'
        f'<g transform="translate({PAD},{PAD})" fill="{FILL}" '
        f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,\'Courier New\',monospace" '
        f'font-size="{FONT_SIZE}">\n' + "\n".join(body) + "\n</g>\n</svg>\n"
    )
    OUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT} ({COLS}x{rows} chars, {len(svg) // 1024} KB)")


if __name__ == "__main__":
    main()
