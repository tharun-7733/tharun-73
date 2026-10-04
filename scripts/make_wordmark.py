#!/usr/bin/env python3
import pyfiglet
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "wordmark.svg"

def main():
    # Generate ASCII art
    f = pyfiglet.Figlet(font='isometric1') # Or 'slant' or '3d' - actually the picture shows a slanted blocky font.
    # The font in the picture looks like 'starwars' or 'slant' or 'speed'. Let's try 'speed' or 'slant'.
    # Actually, the picture has:
    #   cSSSSSSSS     +*SSSSS   CCSSSSSS  *+CCCCC
    # This looks like the 'larry3d' or '3d' or 'isometric' font. Let's just use 'slant' or 'starwars'. 
    # Or even better, a generic blocky font. Let's use 'slant'.
    
    text = pyfiglet.figlet_format("THARUN\nTEJA", font="slant")
    lines = text.split('\n')
    # strip empty lines at the end
    while lines and not lines[-1].strip():
        lines.pop()

    W = 490
    BAR_H = 34
    
    # Calculate text dimensions
    CELL_W = 7
    CELL_H = 14
    FONT = 12
    max_len = max(len(l) for l in lines) if lines else 0
    text_width = max_len * CELL_W
    text_height = len(lines) * CELL_H
    
    # We want it to fit in the window nicely, center it.
    H = max(300, text_height + 100 + BAR_H)
    
    C = dict(bg="#0d1117", bar="#161b22", text="#c9d1d9", dim="#8b949e")

    out = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
        f'<rect width="{W}" height="{H}" rx="10" fill="{C["bg"]}"/>',
        f'<path d="M0 10a10 10 0 0 1 10-10h{W-20}a10 10 0 0 1 10 10v{BAR_H-10}H0z" fill="{C["bar"]}"/>',
        f'<circle cx="20" cy="{BAR_H/2}" r="6" fill="#ff5f56"/>',
        f'<circle cx="40" cy="{BAR_H/2}" r="6" fill="#ffbd2e"/>',
        f'<circle cx="60" cy="{BAR_H/2}" r="6" fill="#27c93f"/>',
        f'<text x="{W/2}" y="{BAR_H/2+4}" text-anchor="middle" fill="{C["dim"]}" '
        f'font-family="ui-monospace,Menlo,Consolas,monospace" font-size="12">THARUN@github: ~$ ./wordmark.sh --3d</text>',
        f'<g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,\'Courier New\',monospace" font-size="{FONT}" fill="{C["text"]}">',
    ]
    
    start_y = BAR_H + 40
    start_x = (W - text_width) / 2
    if start_x < 20: start_x = 20
    
    for i, line in enumerate(lines):
        y = start_y + i * CELL_H
        out.append(f'<text x="{start_x}" y="{y}" xml:space="preserve" style="white-space:pre;">{escape(line)}</text>')

    out += ["</g>", "</svg>", ""]
    OUT.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {OUT}")

if __name__ == "__main__":
    main()
