# Nico saluda — prueba de stop motion digital en plastilina (HyperFrames)

Prueba funcional de animación stop motion digital con aspecto de plastilina artesanal: un personaje
original (**Nico**, un niño de plastilina con chubasquero mostaza, gorro naranja y botas verde azulado)
camina por la acera empedrada de una casita al atardecer, se detiene delante de la puerta y saluda.

- **Render:** [`renders/nico-saluda_24fps.mp4`](renders/nico-saluda_24fps.mp4) — 3 s, 1920×1080, H.264,
  **24 fps, 72 fotogramas**. Hoja de contacto: [`renders/nico-saluda_contactos.jpg`](renders/nico-saluda_contactos.jpg).
- **Proyecto editable:** composición HyperFrames (`index.html` + `compositions/`), hoja de exposición
  (`source/xsheet.json`) y scripts que reconstruyen todo a partir de las imágenes generadas.

## Cómo verlo, editarlo y renderizarlo

Requisitos: Node 22+, FFmpeg y Chrome/Chromium. El CLI está fijado a `hyperframes@0.9.86`.

```bash
npx --yes hyperframes@0.9.86 preview          # Studio en el navegador (timeline editable)
npx --yes hyperframes@0.9.86 check            # lint + runtime + layout + movimiento + contraste
npx --yes hyperframes@0.9.86 render --quality delivery --fps 24 -o renders/nico-saluda_24fps.mp4
```

Los scripts de `package.json` hacen lo mismo (`npm run dev`, `npm run check`, `npm run build`,
`npm run render:final`). Para desactivar la telemetría de HyperFrames: `HYPERFRAMES_NO_TELEMETRY=1`.

## Estructura

```
index.html                     raíz: plató (media) + 2 escenas, 24 fps, parpadeo de luz del plató
compositions/camina.html       escena 1: 19 exposiciones de la caminata (en dos)
compositions/saluda.html       escena 2: parada, anticipación y saludo (9 exposiciones)
assets/plate/plato.jpg         plató 1920×1080
assets/nico/*.png              recortes de cada dibujo (alfa limpio) + medidas .json
assets/cels/*.png              cels finales: dibujo + sombra de contacto + sombra proyectada
source/generations/            imágenes originales del generador + PROMPTS.md (prompts, referencias, coste)
source/prep_assets.py          limpieza de alfa y separación de hojas de poses en dibujos
source/xsheet.json             hoja de exposición: qué dibujo, cuántos fotogramas, colocación, sombras, gradación
source/build_xsheet.py         X-sheet → HTML HyperFrames (registro, sombras, tiempos exactos)
source/*.template.html         plantillas de la raíz y de las escenas
REVIEW.md                      revisión: decisiones, mediciones, puntos débiles
```

## Pipeline

1. **Generación (vidIQ → GPT Image 2.6).** Una imagen maestra del personaje (fondo transparente), un
   plató vacío con la misma luz descrita, y las poses en **hojas de 4 poses** generadas con la maestra y
   el fotograma/hoja anterior como referencias. El saludo es un **cambio localizado** sobre la pose de
   parada; la maestra se **reutiliza** como pose de parada. Detalle en `source/generations/PROMPTS.md`.
2. **Recorte** (`python3 source/prep_assets.py ...`): el alfa del generador trae un halo tenue (alfa 1–15)
   que se vería como resplandor; se normaliza el alfa y se separan las figuras por componentes conexas.
3. **Hoja de exposición** (`python3 source/build_xsheet.py`): coloca cada dibujo y escribe las escenas.
4. **HyperFrames**: `check`, `snapshot --review`, `render` a 24 fps.

## Decisiones técnicas

- **Poses discretas, sin interpolación.** Cada exposición es su propio clip `<img>` que muestra un
  dibujo sin cambios durante N fotogramas. Nada se interpola: lo único que sigue a los dibujos (el
  parpadeo de luz) salta con `tl.set` una vez por exposición. Verificado en el MP4: dentro de cada
  exposición la zona del personaje solo varía por grano y luz (dif. máx. 0,43); en las 27 transiciones
  cambia la pose (dif. mín. 3,11).
- **Exposición en dos** en toda la caminata (19 dibujos × 2 fotogramas). Retenciones más largas donde
  corresponde: parada 4 f, anticipación 4 f y saludo en cuatros (con solo dos posiciones de mano, en dos
  sería un aleteo de 6 Hz; en cuatros es un saludo de ~3 Hz).
- **Registro como en un set real.** Escala por hoja = media geométrica entre "misma altura de pie" y
  "mismo tamaño de ojo" que la maestra (las hojas generadas varían ~5–10 % de proporción); el pie
  apoyado se **bloquea** entre dibujos (talón → planta → punta), así que los pies no patinan; la línea de
  suelo está sobre la acera iluminada (y = 900), con la escala corregida por perspectiva.
- **Sombras horneadas en cada cel**: oclusión de contacto bajo las botas + la **silueta de la propia
  pose proyectada** hacia atrás-izquierda (sol bajo desde la derecha), difuminada y desvaneciéndose.
- **Look** con `hyperframes media-treatment` (no filtros CSS): viñeta y grano fílmico en el plató;
  calidez, contraste y el mismo grano en los cels. **Parpadeo de luz** de rodaje stop motion: un pequeño
  desvío de exposición por foto (≈2,7 % de rango), determinista.
- **Reutilización:** 6 generaciones → 17 dibujos → 28 exposiciones. Las hojas A/B/C se alternan para
  que los ciclos no se repitan idénticos.

## Hoja de exposición (resumen)

| Fotogramas | Dibujo | | Fotogramas | Dibujo |
|---|---|---|---|---|
| 1–8 | paso A: contacto, bajada, paso, subida (2 f c/u) | | 39–42 | parada (maestra) |
| 9–16 | paso C: contacto, bajada, paso, subida | | 43–46 | anticipación |
| 17–24 | paso A (variantes B) | | 47–70 | saludo fuera/dentro (4 f c/u), parpadeo en 59–62 |
| 25–32 | paso C | | 71–72 | saludo fuera |
| 33–38 | paso A hasta la parada | | | |

Para cambiar tiempos u orden: edita `source/xsheet.json` y ejecuta `python3 source/build_xsheet.py`
(sobrescribe `index.html` y `compositions/`). También se puede editar directamente en el Studio de
HyperFrames: cada exposición aparece como un clip en el timeline de su escena.

## Para regenerar imágenes

Hace falta un generador que acepte **imágenes de referencia** y entregue **PNG con fondo transparente**.
Aquí se usó la herramienta de imagen del conector **vidIQ** (`vidiq_image_generate`, 12–22 créditos por
imagen; el set completo costó 112). Sin ese acceso se necesita: el conector vidIQ con generación de
imágenes y créditos (≥ ~130 para repetir el set con margen), o una clave de API de un generador
equivalente (p. ej. GPT Image con `background: transparent`). No se recomienda recortar sobre fondo
liso con `hyperframes remove-background`: usa un modelo de segmentación de personas
(`u2net_human_seg`) poco fiable con figuras de plastilina.
