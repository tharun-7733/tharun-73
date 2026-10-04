#!/usr/bin/env python3
"""Prep a photo for ASCII conversion.

1. Remove the background (rembg)
2. Boost local contrast (OpenCV CLAHE)
3. Composite onto pure white so the background becomes blank ASCII

Usage: python scripts/prep_photo.py source-photo.jpg [out.png]
"""
import sys
from pathlib import Path

import cv2
import numpy as np
from PIL import Image
from rembg import remove

ROOT = Path(__file__).resolve().parent.parent


def main(src: str, out: str | None = None) -> None:
    out_path = Path(out) if out else ROOT / "source-prepped.png"

    img = Image.open(src).convert("RGB")
    cut = remove(img)                      # RGBA with transparent background
    rgba = np.array(cut)
    alpha = rgba[..., 3].astype(np.float32) / 255.0

    # crop to the subject's bounding box (+ small margin)
    ys, xs = np.where(alpha > 0.1)
    pad = 10
    y0, y1 = max(ys.min() - pad, 0), min(ys.max() + pad, alpha.shape[0])
    x0, x1 = max(xs.min() - pad, 0), min(xs.max() + pad, alpha.shape[1])
    rgba = rgba[y0:y1, x0:x1]
    alpha = alpha[y0:y1, x0:x1]

    gray = cv2.cvtColor(rgba[..., :3], cv2.COLOR_RGB2GRAY)
    clahe = cv2.createCLAHE(clipLimit=1.5, tileGridSize=(8, 8))
    gray = clahe.apply(gray).astype(np.float32)

    comp = gray * alpha + 255.0 * (1.0 - alpha)      # background -> white
    Image.fromarray(comp.clip(0, 255).astype(np.uint8), "L").save(out_path)
    print(f"wrote {out_path}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit("usage: prep_photo.py <photo> [out.png]")
    main(*sys.argv[1:3])
