# REVIEW — Nico saluda (3 s, 24 fps)

## Decisiones creativas

- **Personaje original**, no derivado de ninguna franquicia: de Wallace & Gromit se toma solo la
  *técnica* (plastilina con huellas, maqueta física, luz cálida práctica, poca profundidad de campo,
  animación en dos).
- **Un plano fijo** (cámara en trípode, como en un set de stop motion) con dos acciones: camina → se para
  delante de la puerta verde (fondo oscuro que hace contraste con el gorro y la mano) → saluda a cámara.
- **Descartados:** caminar hacia cámara reutilizando dibujos espejados (la luz lateral se invertiría en
  cada paso); entrar desde fuera de cuadro (primer fotograma con el personaje cortado); un giro completo
  hacia cámara antes de saludar (más dibujos de los que permitía el presupuesto de créditos).

## Qué se midió y qué solo se miró

Medido:

- `ffprobe` del MP4: 1920×1080, H.264 High, yuv420p, **24/1 fps, 72 fotogramas, 3,000 s**.
- Fotograma a fotograma, sobre el MP4 decodificado:
  - cada fotograma muestra el dibujo que indica `source/xsheet.json`;
  - dentro de cada exposición la zona del personaje solo cambia por grano y luz (dif. máx. 0,43);
  - en las 27 transiciones cambia la pose (dif. mín. 3,11): no hay fotogramas intermedios ni interpolación.
- Parpadeo de luz: ≈2,7 % de rango de luminancia en el plató; los saltos ocurren solo al empezar una
  exposición (escalón medio 0,86 en los límites frente a 0,021 dentro).
- `hyperframes check`: 0 errores (lint, runtime, layout, movimiento, contraste, oficio).

Solo mirado:

- Tira de continuidad de las 28 exposiciones.
- Papel cebolla de exposiciones consecutivas: el pie apoyado no patina.
- Hojas de `snapshot --review`: momentos clave, costura entre escenas y vista de móvil.
- Recortes al 100 %.

Nadie lo ha comprobado:

- La reproducción en dispositivos reales y el color en un monitor calibrado.
- El sonido: no hay pista de audio.

## Notas

- **P1** · t=0,33–1,58 s · piernas en la caminata · los pasos A y C alternan los brazos, pero la oclusión
  de las piernas casi no cambia (en el paso, la bota levantada siempre queda detrás) → una hoja más con
  la pierna cercana pasando por delante, o un retoque localizado de esa oclusión · se mantienen el ritmo,
  el registro y las sombras.
- **P1** · t=1,54–1,92 s · proporciones entre hojas · la cabeza varía ≈5–7 % entre caminata, maestra y
  saludo (compensado con la escala mixta y coincidente con cambios de pose: erguirse al parar,
  aplastarse en la anticipación) → con más créditos, generar las poses de caminata con más peso de la
  maestra o una hoja de transición caminata→parada.
- **P2** · t=1,92–2,96 s · saludo · solo hay dos posiciones de mano, así que se expone en cuatros (≈3 Hz)
  → con 3–4 posiciones podría animarse en dos.
- **P2** · iluminación del personaje · es más frontal y suave que el sol lateral del plató; la calidez se
  igualó con gradación → un borde de luz cálida desde la derecha lo integraría más.
- **P2** · sonido · pasos sobre adoquín y ambiente de calle reforzarían el gesto (HyperFrames solo lo
  pide a partir de ~15 s).

## Plano más débil

La caminata, por la oclusión de piernas casi idéntica entre pasos (primera nota P1). Es lo primero que
cambiaría con más créditos: una sola generación de hoja de pasos con la pierna cercana por delante.

## Avisos mantenidos a propósito

- `timeline_track_too_dense` (19 y 9 elementos temporizados): es una hoja de exposición, con un clip
  por exposición. Partir más una acción continua haría más difícil retocar los tiempos en Studio.

## Notas técnicas para quien continúe

- **Elementos no gradados bajo el plató gradado.** Con el plató gradado (`data-color-grading`), los
  `<div>` sin gradación de las escenas (degradados CSS, fondos PNG) dejaron de verse en snapshot y render.
  Las `<img>` sí se ven. Por eso las sombras van horneadas dentro de cada cel.
- **El render `draft` parece omitir la gradación.** En `draft` el parpadeo medido fue ≈0,5 %, frente a
  ≈2,7 % en `delivery` con una amplitud casi igual. Hay que juzgar el look siempre con `delivery`.
- **Telemetría desactivada.** Durante el trabajo se usó `HYPERFRAMES_NO_TELEMETRY=1` y no se enviaron
  notas de uso ni `feedback`.
