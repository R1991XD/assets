#!/usr/bin/env python3
"""X-sheet -> HyperFrames project (index.html + compositions/camina.html + compositions/saluda.html).

Stop-motion logic, not interpolation: every exposure is its own timed <img> clip that shows ONE
drawing, unchanged, for a whole number of frames (2 = on twos). Nothing is tweened: the
set-light flicker jumps with tl.set once per exposure, and each cel PNG carries its own contact
shadow and projected silhouette shadow (baked here), like a puppet photographed on the set.
Every visible element is graded media (HyperFrames media-treatment: warmth, grain, vignette).

Registration (what an animator does with a puppet on a set):
  * scale  - each generation sheet gets one scale, a geometric blend of "same standing height" and
             "same eye-bead size" as the master, so neither body nor head pops between sheets;
  * ground - the lowest point of every drawing sits on ground_y;
  * x      - the planted boot is locked between consecutive drawings (heel strike -> flat -> toe),
             so the feet never skate; between steps the body advances step_transition_advance px.

Usage:  python3 source/build_xsheet.py
Edit source/xsheet.json (timing, order, placement) and rebuild. The HTML it writes is plain
HyperFrames and can also be edited directly in Studio (a rebuild overwrites those edits).
"""
import json
import math
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

ROOT = Path(__file__).resolve().parent.parent
CELS = ROOT / "assets" / "nico"
SRC = ROOT / "source"
X = json.loads((SRC / "xsheet.json").read_text())
EPS = 0.0002  # clips open 0.2 ms before their first frame so float error can never drop a frame

# drawing -> (generation sheet, ground contact, planted foot)
DRAWINGS = {
    "walk_n1_contact": ("A", "heel", "near"), "walk_n2_down": ("A", "flat", "near"),
    "walk_n3_passing": ("A", "flat", "near"), "walk_n4_up": ("A", "toe", "near"),
    "walk_n1_contact_alt": ("B", "heel", "near"), "walk_n2_down_alt": ("B", "flat", "near"),
    "walk_n3_passing_alt": ("B", "flat", "near"), "walk_n4_up_alt": ("B", "toe", "near"),
    "walk_f1_contact": ("C", "heel", "far"), "walk_f2_down": ("C", "flat", "far"),
    "walk_f3_passing": ("C", "flat", "far"), "walk_f4_up": ("C", "toe", "far"),
    "nico_master": ("M", "stand", "both"),
    "wave_1_anticip": ("W", "stand", "both"), "wave_2_out": ("W", "stand", "both"),
    "wave_3_in": ("W", "stand", "both"), "wave_4_blink": ("W", "stand", "both"),
}
# per sheet: standing-equivalent figure height and eye-bead height (px), measured on the cutouts
SHEET_REF = {"M": (1993, 77.0), "A": (1053, 44.75), "B": (1033, 45.0),
             "C": (1052, 44.75), "W": (1123, 41.5)}


def sheet_scale(sheet):
    h_t = X["standing_height"]
    e_t = SHEET_REF["M"][1] * h_t / SHEET_REF["M"][0]
    h, e = SHEET_REF[sheet]
    return math.sqrt((h_t / h) * (e_t / e))


def measure(name):
    solid = np.array(Image.open(CELS / f"{name}.png"))[..., 3] >= 128
    h, w = solid.shape
    bottom = np.full(w, -1)
    for x in np.where(solid.any(axis=0))[0]:
        bottom[x] = np.where(solid[:, x])[0].max()
    g = int(bottom.max())
    touch = np.where(bottom >= g - 6)[0]
    runs = [(int(r[0]), int(r[-1])) for r in np.split(touch, np.where(np.diff(touch) > 3)[0] + 1) if len(r)]
    ys, xs = np.where(solid)
    bx = np.where(solid[g - 30: g + 1].any(axis=0))[0]
    return {"w": w, "h": h, "ground": g, "touch": runs, "top": int(ys.min()),
            "cx": float(xs.mean()), "feet": (int(bx.min()), int(bx.max()))}


def lock_points(prev, cur, mp, mc):
    """Drawing-space x of the same ground point in two consecutive drawings (None: new step)."""
    tp, cp = prev[1], cur[1]
    if tp == "stand" and cp == "stand":
        return sum(mp["feet"]) / 2, sum(mc["feet"]) / 2
    if cp == "stand":  # the last planted boot becomes the near boot of the standing pose
        r, near = mp["touch"][-1], mc["touch"][0]
        return (r[0] + r[1]) / 2, (near[0] + near[1]) / 2
    if prev[2] != cur[2]:
        return None
    rp, rc = mp["touch"][-1], mc["touch"][-1]
    if tp == "heel" and cp == "flat":
        return (rp[0] + rp[1]) / 2, rc[0]      # heel stays where it struck
    if tp == "flat" and cp == "flat":
        return rp[0], rc[0]                    # sole stays put
    if tp == "flat" and cp == "toe":
        return rp[1], rc[1]                    # roll onto the toe
    return (rp[0] + rp[1]) / 2, (rc[0] + rc[1]) / 2


def flicker(n):
    """Deterministic set-light drift, one value per exposure (stops)."""
    amp, state, out, v = X["light_flicker"]["amplitude"], X["light_flicker"]["seed"], [], 0.0
    for _ in range(n):
        state = (1103515245 * state + 12345) % 2**31
        r = state / 2**31 * 2 - 1
        v = 0.45 * v + 0.55 * r
        out.append(round(amp * v, 4))
    return out


def g_start(frame):
    return 0.0 if frame == 0 else round(frame / X["fps"] - EPS, 4)


def ellipse_alpha(h, w, cx, cy, rw, rh, core, falloff, angle=0.0):
    """Soft elliptical shadow (optionally rotated, degrees): gaussian core, 0 at the edge."""
    y, x = np.mgrid[0:h, 0:w]
    t = math.radians(angle)
    dx, dy = x + 0.5 - cx, y + 0.5 - cy
    u, v = dx * math.cos(t) + dy * math.sin(t), -dx * math.sin(t) + dy * math.cos(t)
    r = np.sqrt((u / rw) ** 2 + (v / rh) ** 2)
    a = core * np.exp(-2.2 * (r / falloff) ** 2) * np.clip((1 - r) / 0.25, 0, 1)
    return np.clip(a, 0, 1)


def projected_shadow(fig_alpha, g, fig_h, k, pad_l, W, H):
    """The pose's own silhouette laid on the ground toward the left/back (low sun, upper right):
    a point h px above the ground lands kx*h to the left and ky*h further back (up on screen)."""
    kx, ky = k["length"], k["rise"]
    # PIL maps every output pixel (X, Y) back to the drawing: x = X - kx/ky*Y + c, y = Y/ky + f
    data = (1, -kx / ky, -pad_l + kx * g / ky, 0, 1 / ky, g - g / ky)
    src = Image.fromarray((fig_alpha * 255).astype(np.uint8), "L")
    proj = src.transform((W, H), Image.AFFINE, data, resample=Image.BILINEAR)
    proj = proj.filter(ImageFilter.GaussianBlur(k["blur"] * fig_h))
    a = np.asarray(proj, np.float32) / 255
    rows = np.arange(H, dtype=np.float32)[:, None]
    dist = np.clip((g - rows) / ky / fig_h, 0, 1)          # 0 at the boots, 1 at the head's shadow
    return np.clip(a * k["alpha"] * (1 - k["fade"] * dist), 0, 1)


def bake_cel(name, m):
    """Cutout + its contact and cast shadow on one transparent canvas -> assets/cels/<name>.png.
    Returns the padding added on the left and top (drawing px) and the new size."""
    out = ROOT / "assets" / "cels" / f"{name}.png"
    cfg = X["shadows"]
    g = m["ground"]
    fig_h = g - m["top"]
    fx0, fx1 = m["feet"]
    feet_c = (fx0 + fx1) / 2
    c, k = cfg["contact"], cfg["cast"]
    contact = (feet_c + c["offset_x"] * fig_h, g + c["offset_y"] * fig_h,
               ((fx1 - fx0) * 1.15 + c["width_extra"] * fig_h) / 2, c["height"] * fig_h / 2)
    margin = math.ceil(3 * k["blur"] * fig_h) + 4
    pad_l = math.ceil(k["length"] * fig_h) + margin
    W = pad_l + max(m["w"], math.ceil(contact[0] + contact[2])) + margin
    H = max(m["h"], math.ceil(contact[1] + contact[3])) + margin
    fig = np.array(Image.open(CELS / f"{name}.png").convert("RGBA")).astype(np.float32) / 255
    a = 1 - (1 - ellipse_alpha(H, W, contact[0] + pad_l, contact[1], contact[2], contact[3],
                               c["alpha"], c["falloff"], c.get("angle", 0))) \
          * (1 - projected_shadow(fig[..., 3], g, fig_h, k, pad_l, W, H))
    canvas = np.zeros((H, W, 4), np.float32)
    canvas[..., :3] = np.array(cfg["color"], np.float32) / 255
    canvas[..., 3] = a
    sub = canvas[0: m["h"], pad_l: pad_l + m["w"]]
    fa = fig[..., 3:4]
    oa = fa + sub[..., 3:4] * (1 - fa)
    rgb = (fig[..., :3] * fa + sub[..., :3] * sub[..., 3:4] * (1 - fa)) / np.maximum(oa, 1e-6)
    sub[..., :3], sub[..., 3:4] = rgb, oa
    img = (np.clip(canvas, 0, 1) * 255 + 0.5).astype(np.uint8)
    img[img[..., 3] == 0, :3] = 0
    out.parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(img, "RGBA").save(out, optimize=True)
    return pad_l, 0, W, H


def grading_attr(patch):
    return (f"data-color-grading='{json.dumps(patch, separators=(',', ':'))}'"
            if patch else "")


def place():
    ground, cache, placed, frame = X["ground_y"], {}, [], 0
    luz = flicker(len(X["exposures"]))
    for i, ex in enumerate(X["exposures"]):
        name, info = ex["drawing"], DRAWINGS[ex["drawing"]]
        m = cache.setdefault(name, measure(name))
        s = sheet_scale(info[0])
        top = ground - m["ground"] * s
        if i == 0:
            left = X["start_center_x"] - m["cx"] * s
        else:
            q = placed[-1]
            lk = lock_points(DRAWINGS[q["name"]], info, q["m"], m)
            if lk is None:
                left = q["left"] + q["m"]["cx"] * q["s"] + X["step_transition_advance"] - m["cx"] * s
            else:
                left = q["left"] + lk[0] * q["s"] - lk[1] * s
        placed.append({"k": i + 1, "name": name, "s": s, "m": m, "left": left, "top": top,
                       "frame": frame, "frames": ex["frames"], "note": ex.get("note", ""), "luz": luz[i]})
        frame += ex["frames"]
    xf = X.get("xsheet_frames", X["frames"])
    assert frame == xf, f"x-sheet covers {frame} frames, expected {xf}"
    return placed


def write(placed):
    W, H = X["canvas"]
    total = X["frames"] / X["fps"]                     # whole film
    xframes = X.get("xsheet_frames", X["frames"])       # part driven by the exposure sheet
    hosts, k, baked = [], 0, {}
    cel_grading = grading_attr(X["grading"].get("cels"))
    for sc in X["scenes"]:
        group = placed[k: k + sc["exposures"]]
        k += sc["exposures"]
        f0, f1 = group[0]["frame"], group[-1]["frame"] + group[-1]["frames"]
        h_start = g_start(f0)
        h_end = total if f1 >= X["frames"] else g_start(f1)
        assert f1 <= xframes
        h_dur = round(h_end - h_start, 4)
        cels, expo = [], []
        for j, p in enumerate(group):
            st = round(g_start(p["frame"]) - h_start, 4) if j else 0.0
            nxt = round(g_start(group[j + 1]["frame"]) - h_start, 4) if j + 1 < len(group) else h_dur
            cid = f"{sc['id']}-{p['k']:02d}"
            note = f" · {p['note']}" if p["note"] else ""
            pad_l, pad_t, cw, ch = baked.setdefault(p["name"], bake_cel(p["name"], p["m"]))
            s = p["s"]
            cels.append(
                f'    <!-- frames {p["frame"] + 1}-{p["frame"] + p["frames"]} ({p["frames"]} f){note} -->\n'
                f'    <img id="{cid}" class="clip {sc["id"]}-cel" src="assets/cels/{p["name"]}.png" alt="Nico · {p["name"]}"'
                f' data-start="{st:g}" data-duration="{round(nxt - st, 4):g}" data-track-index="1"\n'
                f'      {cel_grading}\n'
                f'      style="left: {p["left"] - pad_l * s:.1f}px; top: {p["top"] - pad_t * s:.1f}px;'
                f' width: {cw * s:.1f}px; height: {ch * s:.1f}px; --hf-color-grading-exposure: 0" />')
            expo.append({"id": cid, "t": st, "luz": p["luz"]})
        tpl = (SRC / "scene.template.html").read_text()
        html = (tpl.replace("{{ID}}", sc["id"]).replace("{{LABEL}}", sc["label"])
                .replace("{{W}}", str(W)).replace("{{H}}", str(H)).replace("{{CELS}}", "\n".join(cels))
                .replace("{{EXPOSURES_JSON}}", json.dumps(expo, separators=(",", ":"))))
        (ROOT / "compositions").mkdir(exist_ok=True)
        (ROOT / "compositions" / f"{sc['id']}.html").write_text(html)
        hosts.append(
            f'      <div\n        id="{sc["id"]}"\n        data-composition-id="{sc["id"]}"\n'
            f'        data-composition-src="compositions/{sc["id"]}.html"\n'
            f'        data-start="{h_start:g}"\n        data-duration="{h_dur:g}"\n'
            f'        data-track-index="1"\n        data-track-kind="graphics"\n'
            f'        data-width="{W}"\n        data-height="{H}"\n      ></div>')
    f0 = xframes
    for sc in X.get("extra_scenes", []):
        h_start = g_start(f0)
        h_end = total if f0 + sc["frames"] >= X["frames"] else g_start(f0 + sc["frames"])
        hosts.append(
            f'      <!-- {sc["label"]}: frames {f0 + 1}-{f0 + sc["frames"]} -->\n'
            f'      <div\n        id="{sc["id"]}"\n        data-composition-id="{sc["id"]}"\n'
            f'        data-composition-src="compositions/{sc["id"]}.html"\n'
            f'        data-start="{h_start:g}"\n        data-duration="{round(h_end - h_start, 4):g}"\n'
            f'        data-track-index="1"\n        data-track-kind="graphics"\n'
            f'        data-width="{W}"\n        data-height="{H}"\n      ></div>')
        f0 += sc["frames"]
    plate_attr = (grading_attr(X["grading"].get("plate"))
                  + '\n        style="--hf-color-grading-exposure: 0"')
    luz = [[g_start(p["frame"]), p["luz"]] for p in placed]
    idx = ((SRC / "index.template.html").read_text()
           .replace("{{W}}", str(W)).replace("{{H}}", str(H)).replace("{{DUR}}", f"{total:g}")
           .replace("{{XDUR}}", f"{g_start(xframes) if xframes < X['frames'] else total:g}")
           .replace("{{HOST_IDS}}", ", ".join(f"#{sc['id']}" for sc in X["scenes"] + X.get("extra_scenes", [])))
           .replace("{{FPS}}", str(X["fps"])).replace("{{FRAMES}}", str(X["frames"]))
           .replace("{{PLATE_GRADING}}", plate_attr).replace("{{HOSTS}}", "\n".join(hosts))
           .replace("{{LUZ_JSON}}", json.dumps(luz, separators=(",", ":"))))
    (ROOT / "index.html").write_text(idx)


if __name__ == "__main__":
    placed = place()
    write(placed)
    print(f"wrote index.html + {len(X['scenes'])} scenes ({len(placed)} exposures, {X['frames']} frames)")
    for p in placed:
        print(f"  {p['k']:2d} f{p['frame']:2d}+{p['frames']} {p['name']:20s} s={p['s']:.4f}"
              f" body_x={p['left'] + p['m']['cx'] * p['s']:7.1f} top={p['top']:6.1f} luz={p['luz']:+.4f}")
