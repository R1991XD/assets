#!/usr/bin/env python3
"""Replacement faces for the close-up (PP), built like stop-motion replacement pieces.

Two generations of the same close-up exist: the base (eyes open, closed smile) and an expression
pass (eyes closed in a happy squint, open smile, stronger blush) generated with the base as
reference. Instead of cutting between the two whole images (which would make the beanie, hair and
coat "boil"), every state is the base with only local regions swapped in from the expression pass:

  pp_s0  base                     eyes open, closed smile
  pp_s1  base + eyes/brows        blink (happy closed eyes)
  pp_s2  base + mouth             open smile, eyes open
  pp_s3  base + eyes/brows/mouth/cheeks   happy squint, open smile, blush

The expression pass is first aligned to the base by phase correlation on regions that must not
change (beanie, coat). Masks are feathered ellipses in base pixel coordinates.

Usage: python3 source/build_pp_faces.py
"""
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
GEN = ROOT / "source" / "generations"
OUT = ROOT / "assets" / "pp"
LO, HI = 24, 240  # same alpha cleanup as prep_assets.py

# feature ellipses in base pixel coordinates: (cx, cy, rx, ry)
EYES = [(543, 1000, 112, 96), (896, 983, 102, 92)]
BROWS = [(535, 828, 112, 58), (900, 812, 104, 62)]
MOUTH = [(736, 1246, 178, 108)]
CHEEKS = [(436, 1158, 96, 80), (1004, 1124, 82, 78)]
FEATHER = 14  # px gaussian on the mask edge


def load(name):
    return np.array(Image.open(GEN / name).convert("RGBA")).astype(np.float32)


def luminance(x):
    return (0.299 * x[..., 0] + 0.587 * x[..., 1] + 0.114 * x[..., 2]) * (x[..., 3] / 255)


def phase_shift(a, b):
    """Integer (dy, dx) that moves b onto a."""
    a, b = a - a.mean(), b - b.mean()
    w = np.outer(np.hanning(a.shape[0]), np.hanning(a.shape[1]))
    r = np.fft.ifft2(np.fft.fft2(a * w) * np.conj(np.fft.fft2(b * w)) /
                     (np.abs(np.fft.fft2(a * w) * np.conj(np.fft.fft2(b * w))) + 1e-9)).real
    y, x = np.unravel_index(np.argmax(r), r.shape)
    return (y - a.shape[0] if y > a.shape[0] // 2 else y,
            x - a.shape[1] if x > a.shape[1] // 2 else x)


def ellipse_mask(shape, ellipses):
    h, w = shape
    y, x = np.mgrid[0:h, 0:w]
    m = np.zeros(shape, bool)
    for cx, cy, rx, ry in ellipses:
        m |= ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1
    img = Image.fromarray((m * 255).astype(np.uint8), "L").filter(ImageFilter.GaussianBlur(FEATHER))
    return np.asarray(img, np.float32)[..., None] / 255


def clean(rgba):
    out = rgba.copy()
    out[..., 3] = np.clip((rgba[..., 3] - LO) / (HI - LO), 0, 1) * 255
    out[out[..., 3] <= 0, :3] = 0
    return out


def main():
    base, expr = load("07_pp_base_raw.png"), load("09_pp_expression_raw.png")
    la, lb = luminance(base), luminance(expr)
    shifts = [phase_shift(la[y0:y1], lb[y0:y1]) for y0, y1 in ((40, 700), (1500, 2040))]
    dy, dx = max(set(shifts), key=shifts.count)
    expr = np.roll(expr, shift=(dy, dx), axis=(0, 1))
    print(f"expression pass aligned by dy={dy} dx={dx} (beanie/coat estimates: {shifts})")
    states = {
        "pp_s0": [],
        "pp_s1": EYES + BROWS,
        "pp_s2": MOUTH,
        "pp_s3": EYES + BROWS + MOUTH + CHEEKS,
    }
    OUT.mkdir(parents=True, exist_ok=True)
    for name, regions in states.items():
        if regions:
            m = ellipse_mask(base.shape[:2], regions)
            img = base * (1 - m) + expr * m
        else:
            img = base
        img = clean(img)
        Image.fromarray(np.clip(img + 0.5, 0, 255).astype(np.uint8), "RGBA").save(OUT / f"{name}.png", optimize=True)
        print("wrote", (OUT / f"{name}.png").relative_to(ROOT))


if __name__ == "__main__":
    main()
