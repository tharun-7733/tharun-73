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
COLS = 75                  # characters per row
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

    BAR_H = 34
    width = COLS * CELL_W + 2 * PAD
    height = rows * CELL_H + 2 * PAD + BAR_H

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
        f'<path d="M0 10a10 10 0 0 1 10-10h{width-20:.0f}a10 10 0 0 1 10 10v{BAR_H-10}H0z" fill="#161b22"/>\n'
        f'<circle cx="20" cy="{BAR_H/2}" r="6" fill="#ff5f56"/>\n'
        f'<circle cx="40" cy="{BAR_H/2}" r="6" fill="#ffbd2e"/>\n'
        f'<circle cx="60" cy="{BAR_H/2}" r="6" fill="#27c93f"/>\n'
        f'<text x="{width/2:.0f}" y="{BAR_H/2+4}" text-anchor="middle" fill="#8b949e" '
        f'font-family="ui-monospace,Menlo,Consolas,monospace" font-size="12">THARUN@github: ~$ ./portrait.sh</text>\n'
        f'<defs>{"".join(defs)}</defs>\n'
        f'<g transform="translate({PAD},{PAD + BAR_H})" fill="{FILL}" '
        f'font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,\'Courier New\',monospace" '
        f'font-size="{FONT_SIZE}">\n' + "\n".join(body) + "\n</g>\n</svg>\n"
    )
    OUT.write_text(svg, encoding="utf-8")
    print(f"wrote {OUT} ({COLS}x{rows} chars, {len(svg) // 1024} KB)")


if __name__ == "__main__":
    main()
