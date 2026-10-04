#!/usr/bin/env python3
import pyfiglet
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "wordmark-2.svg"

def main():
    # Generate ASCII art
    f = pyfiglet.Figlet(font='slant')
    
    lines1 = pyfiglet.figlet_format("THARUN", font="slant").split('\n')
    while lines1 and not lines1[-1].strip(): lines1.pop()
        
    lines2 = pyfiglet.figlet_format("TEJA", font="slant").split('\n')
    while lines2 and not lines2[-1].strip(): lines2.pop()

    W = 490
    BAR_H = 34
    
    # Calculate text dimensions
    CELL_W = 7
    CELL_H = 14
    FONT = 12
    
    width1 = (max(len(l) for l in lines1) if lines1 else 0) * CELL_W
    height1 = len(lines1) * CELL_H
    
    width2 = (max(len(l) for l in lines2) if lines2 else 0) * CELL_W
    height2 = len(lines2) * CELL_H
    
    import xml.etree.ElementTree as ET
    try:
        tree = ET.parse(ROOT / "TT-ascii-1.svg")
        root_svg = tree.getroot()
        H = float(root_svg.attrib["height"])
    except Exception:
        H = 773
    
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
    
    avail_h = H - BAR_H
    GAP = 40
    total_height = height1 + GAP + height2
    
    # Position THARUN
    start_y1 = BAR_H + (avail_h - total_height) / 2
    start_x1 = max(20, (W - width1) / 2)
    for i, line in enumerate(lines1):
        y = start_y1 + i * CELL_H
        out.append(f'<text x="{start_x1}" y="{y}" xml:space="preserve" style="white-space:pre;">{escape(line)}</text>')

    # Position TEJA
    start_y2 = start_y1 + height1 + GAP
    start_x2 = max(20, (W - width2) / 2)
    for i, line in enumerate(lines2):
        y = start_y2 + i * CELL_H
        out.append(f'<text x="{start_x2}" y="{y}" xml:space="preserve" style="white-space:pre;">{escape(line)}</text>')

    out += ["</g>", "</svg>", ""]
    OUT.write_text("\n".join(out), encoding="utf-8")
    print(f"wrote {OUT}")

if __name__ == "__main__":
    main()
