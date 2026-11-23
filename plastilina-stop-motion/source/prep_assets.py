#!/usr/bin/env python3
"""Asset preparation for the clay stop-motion test (Pillow + numpy only).

The image generator returns RGBA PNGs whose alpha carries a faint haze
(alpha 1-15) around the figure. Over the set plate that haze reads as a
coloured glow, so every cutout goes through the same cleanup:

  1. alpha levels: <= LO -> 0, >= HI -> 255 (kills the haze, makes the clay solid)
  2. connected components on the solid mask; keep the figures, drop specks
  3. one PNG per figure, cropped with a margin, RGB zeroed where alpha == 0

Pose sheets (several poses in one generation) are split left-to-right into
one file per drawing. Measurements used to register the drawings (height,
foot line, horizontal centre) are written next to the cutouts as JSON.

Usage:
  python3 source/prep_assets.py cutout <in.png> <out.png>
  python3 source/prep_assets.py sheet  <in.png> <out_dir> <name1,name2,...>
"""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

LO, HI = 24, 240          # alpha levels window
SOLID = 128               # alpha threshold that defines the figure
MARGIN = 24               # px kept around each crop


def clean_alpha(rgba: np.ndarray) -> np.ndarray:
    out = rgba.copy()
    a = rgba[..., 3].astype(np.float32)
    a = np.clip((a - LO) / (HI - LO), 0.0, 1.0) * 255.0
    out[..., 3] = np.round(a).astype(np.uint8)
    out[out[..., 3] == 0, :3] = 0
    return out


def label_components(mask: np.ndarray):
    """8-connected labelling via row runs + union-find. Returns (labels, comps)."""
    h, w = mask.shape
    parent = [0]

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[max(ra, rb)] = min(ra, rb)

    runs_prev = []
    all_runs = []  # (y, x0, x1, label)
    for y in range(h):
        row = mask[y]
        if not row.any():
            runs_prev = []
            continue
        d = np.diff(np.concatenate(([0], row.astype(np.int8), [0])))
        starts = np.where(d == 1)[0]
        ends = np.where(d == -1)[0]  # exclusive
        runs_cur = []
        for x0, x1 in zip(starts, ends):
            lab = None
            for (px0, px1, plab) in runs_prev:
                if px0 <= x1 and px1 >= x0:  # touches incl. diagonals
                    if lab is None:
                        lab = plab
                    else:
                        union(lab, plab)
            if lab is None:
                lab = len(parent)
                parent.append(lab)
            runs_cur.append((x0, x1, lab))
            all_runs.append((y, x0, x1, lab))
        runs_prev = runs_cur

    labels = np.zeros((h, w), dtype=np.int32)
    comps = {}
    for (y, x0, x1, lab) in all_runs:
        r = find(lab)
        labels[y, x0:x1] = r
        c = comps.setdefault(r, {"label": r, "area": 0, "x0": x0, "x1": x1, "y0": y, "y1": y})
        c["area"] += int(x1 - x0)
        c["x0"] = min(c["x0"], int(x0)); c["x1"] = max(c["x1"], int(x1))
        c["y0"] = min(c["y0"], y);       c["y1"] = max(c["y1"], y)
    return labels, sorted(comps.values(), key=lambda c: -c["area"])


def measure(rgba: np.ndarray) -> dict:
    a = rgba[..., 3] >= SOLID
    ys, xs = np.where(a)
    y_top, y_bot = int(ys.min()), int(ys.max())
    # foot line and horizontal centre measured on the bottom 3 % of the figure
    band = a[max(y_bot - int(0.03 * (y_bot - y_top)), 0): y_bot + 1]
    bx = np.where(band.any(axis=0))[0]
    return {
        "width": int(rgba.shape[1]), "height": int(rgba.shape[0]),
        "figure_top": y_top, "figure_bottom": y_bot,
        "figure_height": y_bot - y_top + 1,
        "figure_left": int(xs.min()), "figure_right": int(xs.max()),
        "center_x": float(xs.mean()),
        "feet_left": int(bx.min()), "feet_right": int(bx.max()),
    }


def crop_component(rgba, labels, comp, keep_labels):
    h, w = labels.shape
    x0 = max(comp["x0"] - MARGIN, 0); x1 = min(comp["x1"] + MARGIN, w)
    y0 = max(comp["y0"] - MARGIN, 0); y1 = min(comp["y1"] + 1 + MARGIN, h)
    tile = rgba[y0:y1, x0:x1].copy()
    lab = labels[y0:y1, x0:x1]
    solid_other = (lab != 0) & ~np.isin(lab, keep_labels)
    # soft edge pixels (alpha < SOLID) are unlabelled: keep those nearest to this figure only
    tile[solid_other] = 0
    return tile, (x0, y0)


def save(rgba: np.ndarray, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(rgba, "RGBA").save(path, optimize=True)


def cmd_cutout(src, dst):
    rgba = clean_alpha(np.array(Image.open(src).convert("RGBA")))
    labels, comps = label_components(rgba[..., 3] >= SOLID)
    main = comps[0]
    keep = [c["label"] for c in comps if c["area"] >= 0.002 * main["area"]]
    # drop specks: zero everything not near a kept component's bbox
    tile, _ = crop_component(rgba, labels, main, keep)
    m = measure(tile)
    save(tile, Path(dst))
    Path(dst).with_suffix(".json").write_text(json.dumps(m, indent=1))
    print(dst, m)


def cmd_sheet(src, out_dir, names):
    rgba = clean_alpha(np.array(Image.open(src).convert("RGBA")))
    labels, comps = label_components(rgba[..., 3] >= SOLID)
    biggest = comps[0]["area"]
    figures = [c for c in comps if c["area"] >= 0.25 * biggest]
    small = [c for c in comps if 0.002 * biggest <= c["area"] < 0.25 * biggest]
    figures.sort(key=lambda c: c["x0"])
    if len(figures) != len(names):
        sys.exit(f"expected {len(names)} figures, found {len(figures)}: {[(c['x0'], c['area']) for c in figures]}")
    report = {}
    for c, name in zip(figures, names):
        # attach detached bits (e.g. a hand) whose bbox centre lies inside this figure's bbox
        keep = [c["label"]] + [s["label"] for s in small
                               if c["x0"] <= (s["x0"] + s["x1"]) / 2 <= c["x1"]]
        tile, origin = crop_component(rgba, labels, c, keep)
        m = measure(tile)
        m["sheet_origin"] = origin
        out = Path(out_dir) / f"{name}.png"
        save(tile, out)
        report[name] = m
        print(out, m)
    (Path(out_dir) / f"{Path(src).stem}.json").write_text(json.dumps(report, indent=1))


if __name__ == "__main__":
    if sys.argv[1] == "cutout":
        cmd_cutout(sys.argv[2], sys.argv[3])
    elif sys.argv[1] == "sheet":
        cmd_sheet(sys.argv[2], sys.argv[3], sys.argv[4].split(","))
    else:
        sys.exit(__doc__)
