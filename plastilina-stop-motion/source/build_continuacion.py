#!/usr/bin/env python3
"""Continuation of the shot: push-in -> close-up (PP) -> pull-out to the aerial village + lettering.

Writes compositions/acercamiento.html, compositions/primer-plano.html, compositions/alejamiento.html
and the derived assets they use. Run after source/build_xsheet.py (it reuses the exact positions of
Nico computed by the exposure sheet) and source/build_pp_faces.py.

Stop-motion rules kept from the first part:
  * drawings are held exposures (one timed <img> per exposure), never interpolated;
  * the camera moves like a motion-control rig photographed on twos: it jumps to a new position
    once every 2 frames (tl.set), following an eased path, and never glides between frames;
  * every photographed step gets its own small set-light exposure offset (flicker);
  * the clay lettering grows a little on every step, like an animator laying a plasticine coil,
    and its surface "boils" (new noise seed per step).

Usage: python3 source/build_continuacion.py
"""
import json
import math
import re
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

import build_xsheet as bx

ROOT = bx.ROOT
C = json.loads((ROOT / "source" / "continuacion.json").read_text())
LETRAS = json.loads((ROOT / "source" / "letras.json").read_text())
FPS = bx.X["fps"]
W, H = bx.X["canvas"]
EPS = bx.EPS


def t_local(frame):
    return 0.0 if frame == 0 else round(frame / FPS - EPS, 4)


def ease(u, kind):
    if kind == "in":
        return u * u
    if kind == "out":
        return 1 - (1 - u) ** 2
    return 2 * u * u if u < 0.5 else 1 - (-2 * u + 2) ** 2 / 2   # in-out


def flicker_values(n, seed):
    amp, state, v, out = bx.X["light_flicker"]["amplitude"], seed, 0.0, []
    for _ in range(n):
        state = (1103515245 * state + 12345) % 2**31
        v = 0.45 * v + 0.55 * (state / 2**31 * 2 - 1)
        out.append(round(amp * v, 4))
    return out


def exposures_html(scene, items, cls, boxes, grading, frames_total, z=2, track=1):
    """items: [(image_path, frames, note)] -> timed <img> clips laid end to end."""
    html, f = [], 0
    starts = []
    for _, n, _ in items:
        starts.append(f)
        f += n
    assert f == frames_total, f"{scene}: exposures cover {f} frames, expected {frames_total}"
    for k, ((src, n, note), f0) in enumerate(zip(items, starts)):
        st = t_local(f0)
        end = frames_total / FPS if k + 1 == len(items) else t_local(starts[k + 1])
        x, y, w, h = boxes[src]
        note = f" · {note}" if note else ""
        html.append(
            f'      <!-- frames {f0 + 1}-{f0 + n} ({n} f){note} -->\n'
            f'      <img id="{scene}-{k + 1:02d}" class="clip {cls}" src="{src}" alt="" data-start="{st:g}"'
            f' data-duration="{round(end - st, 4):g}" data-track-index="{track}"\n'
            f'        {grading}\n'
            f'        style="left: {x:.1f}px; top: {y:.1f}px; width: {w:.1f}px; height: {h:.1f}px;'
            f' z-index: {z}; --hf-color-grading-exposure: 0" />')
    return "\n".join(html)


# ---------------------------------------------------------------- positions from the x-sheet
def wide_positions():
    """Cel boxes (with baked shadow) and face/feet anchors of the standing drawings, wide-shot px."""
    boxes = {}
    for scene in ("saluda",):
        html = (ROOT / "compositions" / f"{scene}.html").read_text()
        for m in re.finditer(r'src="(assets/cels/[^"]+)".*?style="left: ([-\d.]+)px; top: ([-\d.]+)px;'
                             r' width: ([\d.]+)px; height: ([\d.]+)px', html, re.S):
            boxes[m.group(1)] = tuple(float(v) for v in m.groups()[1:])
    anchors = {}
    for p in bx.place():
        fx0, fx1 = p["m"]["feet"]
        anchors[p["name"]] = {"s": p["s"], "left": p["left"], "top": p["top"],
                              "feet": (p["left"] + (fx0 + fx1) / 2 * p["s"], bx.X["ground_y"])}
    return boxes, anchors


def face_point(name, anchors):
    """Midpoint between the eye beads, measured once on the cutouts (drawing px)."""
    eyes = C["eye_midpoints"][name]
    a = anchors[name]
    return a["left"] + eyes[0] * a["s"], a["top"] + eyes[1] * a["s"]


# ---------------------------------------------------------------- derived assets
def make_assets(anchors):
    plate = Image.open(ROOT / "assets" / "plate" / "plato.jpg").convert("RGB")
    # PP background: the set right behind his head, seen through a longer lens, far out of focus.
    # The point behind his eyes in the wide shot lands where the eyes sit in the close-up.
    mag = C["primer_plano"]["fondo_aumento"]
    ex, ey = face_point("nico_master", anchors)
    sx, sy = C["primer_plano"]["ojos_en_pantalla"]
    cx, cy = ex - (sx - W / 2) / mag, ey - (sy - H / 2) / mag
    bw, bh = W / mag, H / mag
    crop = plate.crop((round(cx - bw / 2), round(cy - bh / 2), round(cx + bw / 2), round(cy + bh / 2)))
    crop = crop.resize((W, H), Image.LANCZOS).filter(ImageFilter.GaussianBlur(C["primer_plano"]["fondo_desenfoque"]))
    crop.save(ROOT / "assets" / "pp" / "pp_fondo.jpg", quality=92)
    # aerial village at full generated resolution (displayed at 1920x1080, zoomed in during the pull-out)
    (ROOT / "assets" / "pueblo").mkdir(exist_ok=True)
    Image.open(ROOT / "source" / "generations" / "08_aerial_raw.jpg").convert("RGB").save(
        ROOT / "assets" / "pueblo" / "aereo.jpg", quality=94)
    # wide set with feathered borders, so it melts into the aerial view when it gets smaller than the frame
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    fx, fy = W * C["alejamiento"]["fundido_borde"], H * C["alejamiento"]["fundido_borde"]
    rx = np.clip(np.minimum(x + 0.5, W - x - 0.5) / fx, 0, 1)
    ry = np.clip(np.minimum(y + 0.5, H - y - 0.5) / fy, 0, 1)
    a = (0.5 - 0.5 * np.cos(np.pi * rx)) * (0.5 - 0.5 * np.cos(np.pi * ry))
    rgba = np.dstack([np.asarray(plate, np.uint8), (a * 255 + 0.5).astype(np.uint8)])
    Image.fromarray(rgba, "RGBA").save(ROOT / "assets" / "pueblo" / "plato_fundido.png", optimize=True)
    # lens vignette fixed to the frame
    (ROOT / "assets" / "fx").mkdir(exist_ok=True)
    nx, ny = (x + 0.5 - W / 2) / (W / 2), (y + 0.5 - H / 2) / (H / 2)
    r = np.sqrt(nx ** 2 * 0.82 + ny ** 2 * 1.0)
    v = C["vineta"]
    va = np.clip((r - v["inicio"]) / (v["fin"] - v["inicio"]), 0, 1) ** v["curva"] * v["opacidad"]
    vig = np.zeros((H, W, 4), np.uint8)
    vig[..., :3] = v["color"]
    vig[..., 3] = (va * 255 + 0.5).astype(np.uint8)
    Image.fromarray(vig, "RGBA").save(ROOT / "assets" / "fx" / "vineta.png", optimize=True)


# ---------------------------------------------------------------- scene writers
def scene_doc(scene, css, body, script):
    return f"""<template>
  <style>
    #root {{
      position: absolute;
      inset: 0;
      overflow: hidden;
      background: #24170f;
    }}
{css}
  </style>
  <div id="root" data-composition-id="{scene}" data-width="{W}" data-height="{H}">
{body}
  </div>
  <script>
    const tl = gsap.timeline({{ paused: true }});
{script}
    window.__timelines["{scene}"] = tl;
  </script>
</template>
"""


def camera_steps(frames, every=2):
    return list(range(0, frames, every))


def write_acercamiento(boxes, anchors, grading_media, grading_cels, seed):
    c = C["acercamiento"]
    scene, frames = "acercamiento", c["frames"]
    fx, fy = face_point("nico_master", anchors)
    zend = c["zoom_final"]
    # pure zoom around a fixed point F that brings the face to the centre of frame at zend
    F = ((zend * fx - W / 2) / (zend - 1), (zend * fy - H / 2) / (zend - 1))
    steps = camera_steps(frames)
    cam = []
    for i, f in enumerate(steps):
        u = ease((i + 1) / len(steps), "in")            # accelerate into the cut to the close-up
        z = math.exp(u * math.log(zend))
        cam.append([t_local(f), round(F[0] * (1 - z), 2), round(F[1] * (1 - z), 2), round(z, 5)])
    luz = [[t_local(f), v] for f, v in zip(steps, flicker_values(len(steps), seed))]
    items = [(f"assets/cels/{n}.png", k, note) for n, k, note in c["cels"]]
    cels = exposures_html(scene, items, "acercamiento-cel", boxes, grading_cels, frames)
    css = f"""    #acercamiento-camara {{
      position: absolute;
      left: 0;
      top: 0;
      width: {W}px;
      height: {H}px;
    }}
    #acercamiento-plato,
    .acercamiento-cel {{
      position: absolute;
    }}"""
    body = f"""    <!-- camera: a motion-control push-in photographed on twos (moved once per 2 frames) -->
    <div id="acercamiento-camara" data-layout-allow-overflow>
      <img id="acercamiento-plato" class="clip" src="assets/plate/plato.jpg" alt="Plató" data-start="0"
        data-duration="{frames / FPS:g}" data-track-index="0"
        {grading_media}
        style="left: 0; top: 0; width: {W}px; height: {H}px; z-index: 1; --hf-color-grading-exposure: 0" />
{cels}
    </div>"""
    script = f"""    // [time, x, y, scale] of the camera for every photographed step
    const camara = {json.dumps(cam, separators=(",", ":"))};
    for (const [t, x, y, s] of camara) tl.set("#acercamiento-camara", {{ x, y, scale: s, transformOrigin: "0 0" }}, t);
    // set-light flicker, one value per photographed step, on every graded image
    const luz = {json.dumps(luz, separators=(",", ":"))};
    for (const [t, v] of luz) tl.set("#acercamiento-plato, .acercamiento-cel", {{ "--hf-color-grading-exposure": v }}, t);"""
    (ROOT / "compositions" / f"{scene}.html").write_text(scene_doc(scene, css, body, script))
    return F


def write_primer_plano(grading_media, grading_cels, seed):
    c = C["primer_plano"]
    scene, frames = "primer-plano", c["frames"]
    s = c["escala"]
    ex, ey = c["ojos_en_imagen"]                       # eye midpoint in the PP image (px)
    sx, sy = c["ojos_en_pantalla"]                     # where the eyes sit on screen
    left, top = sx - ex * s, sy - ey * s
    pw, ph = Image.open(ROOT / "assets" / "pp" / "pp_s0.png").size
    box = (left, top, pw * s, ph * s)
    boxes = {f"assets/pp/{n}.png": box for n, _, _ in c["caras"]}
    items = [(f"assets/pp/{n}.png", k, note) for n, k, note in c["caras"]]
    caras = exposures_html(scene, items, "primer-plano-cara", boxes, grading_cels, frames)
    steps = camera_steps(frames)
    zend, par = c["zoom_final"], c["paralaje_fondo"]
    cam, fondo = [], []
    for i, f in enumerate(steps):
        u = ease(i / max(len(steps) - 1, 1), "out")    # keeps the push of the cut, then settles
        z = 1 + (zend - 1) * u
        zb = 1 + (z - 1) * par                          # background is far: it grows less (parallax)
        cam.append([t_local(f), round(sx * (1 - z), 2), round(sy * (1 - z), 2), round(z, 5)])
        fondo.append([t_local(f), round(sx * (1 - zb), 2), round(sy * (1 - zb), 2), round(zb, 5)])
    luz = [[t_local(f), v] for f, v in zip(steps, flicker_values(len(steps), seed))]
    css = f"""    #primer-plano-fondo-capa,
    #primer-plano-camara {{
      position: absolute;
      left: 0;
      top: 0;
      width: {W}px;
      height: {H}px;
    }}
    #primer-plano-fondo,
    .primer-plano-cara {{
      position: absolute;
    }}"""
    body = f"""    <!-- background: the set behind his head through a longer lens, far out of focus (moves less: parallax) -->
    <div id="primer-plano-fondo-capa" data-layout-allow-overflow>
      <img id="primer-plano-fondo" class="clip" src="assets/pp/pp_fondo.jpg" alt="" data-start="0"
        data-duration="{frames / FPS:g}" data-track-index="0"
        {grading_media}
        style="left: 0; top: 0; width: {W}px; height: {H}px; z-index: 1; --hf-color-grading-exposure: 0" />
    </div>
    <!-- replacement faces (source/build_pp_faces.py): only eyes, mouth and cheeks change between them -->
    <div id="primer-plano-camara" data-layout-allow-overflow>
{caras}
    </div>"""
    script = f"""    const camara = {json.dumps(cam, separators=(",", ":"))};
    for (const [t, x, y, s] of camara) tl.set("#primer-plano-camara", {{ x, y, scale: s, transformOrigin: "0 0" }}, t);
    const fondo = {json.dumps(fondo, separators=(",", ":"))};
    for (const [t, x, y, s] of fondo) tl.set("#primer-plano-fondo-capa", {{ x, y, scale: s, transformOrigin: "0 0" }}, t);
    const luz = {json.dumps(luz, separators=(",", ":"))};
    for (const [t, v] of luz) tl.set("#primer-plano-fondo, .primer-plano-cara", {{ "--hf-color-grading-exposure": v }}, t);"""
    (ROOT / "compositions" / f"{scene}.html").write_text(scene_doc(scene, css, body, script))


def lettering_svg(scene):
    L = LETRAS
    x, paths, order = 0.0, [], 0
    for g in L["texto"]:
        gl = L["glifos"][g]
        for d in gl["trazos"]:
            paths.append(f'          <path class="{scene}-trazo" data-orden="{order}" data-glifo="{g}" '
                         f'transform="translate({x:g} 0)" d="{d}" />')
            order += 1
        x += gl["avance"]
    width = x
    t = C["alejamiento"]["texto"]
    sc = t["escala"]
    gx, gy = W / 2 - width * sc / 2, t["linea_base"]
    sw = t["grosor"]
    f = t["material"]
    return width, f"""    <!-- "te amo cerdita": a plasticine coil laid letter by letter (paths = the pen's route) -->
    <svg id="{scene}-texto" width="{W}" height="{H}" viewBox="0 0 {W} {H}" aria-hidden="true">
      <defs>
        <filter id="{scene}-plastilina" x="-10%" y="-40%" width="120%" height="180%">
          <feTurbulence id="{scene}-ruido-forma" type="fractalNoise" baseFrequency="0.03" numOctaves="2" seed="1" result="ondula" />
          <feDisplacementMap in="SourceGraphic" in2="ondula" scale="{sw * f['ondulacion']:.2f}" xChannelSelector="R" yChannelSelector="G" result="churro" />
          <feGaussianBlur in="churro" stdDeviation="{sw * 0.3:.2f}" result="altura0" />
          <feTurbulence id="{scene}-ruido-huellas" type="fractalNoise" baseFrequency="{f['frecuencia_huellas']}" numOctaves="2" seed="1" result="huellas" />
          <feComposite in="huellas" in2="altura0" operator="arithmetic" k2="{f['huellas']}" k3="1" result="altura" />
          <feDiffuseLighting in="altura" surfaceScale="{sw * 0.4:.2f}" diffuseConstant="1.2" lighting-color="#fff2e2" result="difusa">
            <feDistantLight azimuth="-50" elevation="45" />
          </feDiffuseLighting>
          <feSpecularLighting in="altura" surfaceScale="{sw * 0.4:.2f}" specularConstant="{f['brillo']}" specularExponent="9" lighting-color="#fff6ee" result="brillo">
            <feDistantLight azimuth="-50" elevation="55" />
          </feSpecularLighting>
          <feComposite in="difusa" in2="churro" operator="arithmetic" k1="1" result="iluminado" />
          <feComposite in="brillo" in2="churro" operator="in" result="brillo2" />
          <feComposite in="iluminado" in2="brillo2" operator="arithmetic" k2="1" k3="1" result="arcilla" />
          <feComposite in="arcilla" in2="churro" operator="in" result="arcilla2" />
          <feDropShadow in="arcilla2" dx="-5" dy="8" stdDeviation="5" flood-color="#3a1a10" flood-opacity="0.5" />
        </filter>
      </defs>
      <g transform="translate({gx:.1f} {gy}) scale({sc})" fill="none" stroke="{t['color']}" stroke-width="{sw}"
        stroke-linecap="round" stroke-linejoin="round" filter="url(#{scene}-plastilina)">
{chr(10).join(paths)}
      </g>
    </svg>"""


def write_alejamiento(boxes, anchors, grading_media, grading_cels, seed):
    c = C["alejamiento"]
    scene, frames = "alejamiento", c["frames"]
    k = c["k_puerta"]                                   # wide px per aerial px around the door
    dw, da = c["puerta_plano"], c["puerta_aereo"]       # door centre: wide shot / aerial (display px)
    zs, ze = c["zoom_inicial"], 1 / k
    fx, fy = face_point(c["cara_ancla"], anchors)
    FA = ((zs * fx - W / 2) / (zs - 1), (zs * fy - H / 2) / (zs - 1))      # zoom-out from the face
    FB = ((da[0] - ze * dw[0]) / (1 - ze), (da[1] - ze * dw[1]) / (1 - ze))  # lands on the aerial framing
    feet = anchors[c["pies_ancla"]]["feet"]
    d0, d1 = c["disolver_zoom"]
    shrink = c["encoger_nico"]
    pull = c["frames_alejamiento"]
    steps = camera_steps(frames)
    aereo, plano, nico, opac, luz_t = [], [], [], [], []
    for i, f in enumerate(steps):
        u = min(f / (pull - 2), 1.0)
        u = ease(u, "inout")
        z = math.exp(math.log(zs) + u * (math.log(ze) - math.log(zs)))
        F = FA if z >= 1 else FB
        A = (F[0] * (1 - z), F[1] * (1 - z))            # wide shot: screen = A + z * p
        t = t_local(f)
        # how far into the wide -> aerial dissolve we are (0 before, 1 after), in log-zoom
        w = min(max((math.log(d0) - math.log(z)) / (math.log(d0) - math.log(d1)), 0), 1)
        fs = 1 + (shrink - 1) * w                       # Nico gets slightly smaller as the view turns aerial
        plano.append([t, round(A[0], 2), round(A[1], 2), round(z, 5)])
        aereo.append([t, round(A[0] + z * dw[0] - z * k * da[0], 2), round(A[1] + z * dw[1] - z * k * da[1], 2),
                      round(z * k, 5)])
        nico.append([t, round(A[0] + z * feet[0] * (1 - fs), 2), round(A[1] + z * feet[1] * (1 - fs), 2),
                     round(z * fs, 5)])
        opac.append([t, round(1 - w, 3)])
        luz_t.append(t)
    luz = [[t, v] for t, v in zip(luz_t, flicker_values(len(luz_t), seed))]
    items = []
    for n, kf, note in c["cels"]:
        items.append((f"assets/cels/{n}.png", kf, note))
    cels = exposures_html(scene, items, "alejamiento-cel", boxes, grading_cels, frames, z=3)
    width, svg = lettering_svg(scene)
    tx = c["texto"]
    css = f"""    #alejamiento-aereo-capa,
    #alejamiento-plato-capa,
    #alejamiento-nico-capa {{
      position: absolute;
      left: 0;
      top: 0;
      width: {W}px;
      height: {H}px;
    }}
    #alejamiento-aereo,
    #alejamiento-plato,
    .alejamiento-cel {{
      position: absolute;
    }}
    #alejamiento-texto {{
      position: absolute;
      left: 0;
      top: 0;
      z-index: 5;
    }}"""
    body = f"""    <!-- one virtual camera for three nested sets: the aerial village, the wide set (melting into it,
         matched on the green door) and Nico, who keeps waving goodbye -->
    <div id="alejamiento-aereo-capa" data-layout-allow-overflow>
      <img id="alejamiento-aereo" class="clip" src="assets/pueblo/aereo.jpg" alt="El pueblo de plastilina desde el aire"
        data-start="0" data-duration="{frames / FPS:g}" data-track-index="0"
        {grading_media}
        style="left: 0; top: 0; width: {W}px; height: {H}px; z-index: 1; --hf-color-grading-exposure: 0" />
    </div>
    <div id="alejamiento-plato-capa" data-layout-allow-overflow>
      <img id="alejamiento-plato" class="clip" src="assets/pueblo/plato_fundido.png" alt="Plató"
        data-start="0" data-duration="{frames / FPS:g}" data-track-index="2"
        {grading_media}
        style="left: 0; top: 0; width: {W}px; height: {H}px; z-index: 2; --hf-color-grading-exposure: 0" />
    </div>
    <div id="alejamiento-nico-capa" data-layout-allow-overflow>
{cels}
    </div>
{svg}"""
    script = f"""    // virtual camera, one photographed step every 2 frames: [time, x, y, scale] per layer
    const aereo = {json.dumps(aereo, separators=(",", ":"))};
    const plano = {json.dumps(plano, separators=(",", ":"))};
    const nico = {json.dumps(nico, separators=(",", ":"))};
    const fundido = {json.dumps(opac, separators=(",", ":"))};
    for (const [t, x, y, s] of aereo) tl.set("#alejamiento-aereo-capa", {{ x, y, scale: s, transformOrigin: "0 0" }}, t);
    for (const [t, x, y, s] of plano) tl.set("#alejamiento-plato-capa", {{ x, y, scale: s, transformOrigin: "0 0" }}, t);
    for (const [t, x, y, s] of nico) tl.set("#alejamiento-nico-capa", {{ x, y, scale: s, transformOrigin: "0 0" }}, t);
    for (const [t, o] of fundido) tl.set("#alejamiento-plato-capa", {{ opacity: o }}, t);
    const luz = {json.dumps(luz, separators=(",", ":"))};
    for (const [t, v] of luz) tl.set("#alejamiento-aereo, #alejamiento-plato, .alejamiento-cel", {{ "--hf-color-grading-exposure": v }}, t);
    // lettering: the coil grows on every step at a constant pen speed, letter after letter
    const trazos = Array.from(document.querySelectorAll(".alejamiento-trazo"));
    const largos = trazos.map((p) => p.getTotalLength());
    const pausa = {tx['pausa_palabra']};                       // pen lift between words (path units)
    const inicio = [];
    let acumulado = 0;
    trazos.forEach((p, i) => {{
      if (i > 0 && p.dataset.glifo !== trazos[i - 1].dataset.glifo && trazos[i - 1].dataset.palabraFin) acumulado += pausa;
      inicio.push(acumulado);
      acumulado += largos[i];
    }});
    trazos.forEach((p, i) => tl.set(p, {{ strokeDasharray: largos[i] + " " + (largos[i] + 200), strokeDashoffset: largos[i] + 100 }}, 0));
    const pasos = {tx['pasos']}, desde = {tx['desde_frame']};
    for (let k = 1; k <= pasos; k++) {{
      const t = (desde + 2 * (k - 1)) / {FPS} - {EPS};
      const pluma = (acumulado * k) / pasos;
      trazos.forEach((p, i) => {{
        const visto = Math.min(Math.max(pluma - inicio[i], 0), largos[i]);
        const antes = Math.min(Math.max((acumulado * (k - 1)) / pasos - inicio[i], 0), largos[i]);
        if (visto !== antes) tl.set(p, {{ strokeDashoffset: visto > 0 ? largos[i] - visto : largos[i] + 100 }}, t);
      }});
    }}
    // the clay "boils": a new noise seed on every photographed step once the coil appears
    for (let f = desde; f < {frames}; f += 2) {{
      const t = f / {FPS} - {EPS}, semilla = 1 + ((f - desde) / 2) % 9;
      tl.set("#alejamiento-ruido-forma, #alejamiento-ruido-huellas", {{ attr: {{ seed: semilla }} }}, t);
    }}"""
    html = scene_doc(scene, css, body, script)
    # mark the last stroke of every word so the pen pauses before the next one
    for g in LETRAS["fin_de_palabra"]:
        html = html.replace(f'data-glifo="{g}" ', f'data-glifo="{g}" data-palabra-fin="1" ', 1)
    (ROOT / "compositions" / f"{scene}.html").write_text(html)
    return FA, FB, width


if __name__ == "__main__":
    boxes, anchors = wide_positions()
    make_assets(anchors)
    gm = bx.grading_attr(bx.X["grading"].get("plate"))
    gc = bx.grading_attr(bx.X["grading"].get("cels"))
    F = write_acercamiento(boxes, anchors, gm, gc, seed=23)
    write_primer_plano(gm, gc, seed=37)
    FA, FB, width = write_alejamiento(boxes, anchors, gm, gc, seed=51)
    print("acercamiento: zoom about", tuple(round(v, 1) for v in F))
    print("alejamiento: zoom about", tuple(round(v, 1) for v in FA), "then", tuple(round(v, 1) for v in FB),
          "| lettering width", width)
