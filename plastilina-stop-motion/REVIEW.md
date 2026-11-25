# REVIEW — Nico saluda (14,25 s, 24 fps)

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

---

# Continuación (fotogramas 73–342): acercamiento, primer plano y alejamiento aéreo

## Decisiones creativas

- **Acercamiento:** cuando termina el saludo, Nico baja la mano y mira a cámara mientras la cámara se le
  acerca, acelerando. Se corta en el punto más rápido a un primer plano en el mismo eje. Es la técnica de
  rodaje real: los planos cercanos se ruedan con una marioneta de "cabeza grande", no ampliando el plano
  general, que a más de ~2,3× pierde nitidez.
- **Primer plano:** la actuación sigue la regla de "leer, luego actuar". Mira a cámara (0,75 s), parpadea,
  se ilumina con la sonrisa abierta y termina con los ojos felices y rubor (1 s). Así el mensaje del final
  llega con causa.
- **Alejamiento:** corte en movimiento al plano general mientras Nico se despide. La cámara se aleja sin
  cortes hasta el pueblo entero, empalmando el plató con la toma aérea en la puerta verde. El texto
  empieza a dibujarse justo cuando la cámara aterriza.
- **Texto:** un churro de plastilina rosa (rosa por "cerdita") sobre el cielo, como letras de arcilla sobre
  un cristal delante de la lente, técnica clásica de títulos en stop motion. Se descartaron dos opciones:
  generarlo con IA, porque no se podría dibujar trazo a trazo, y una fuente tipográfica, porque no se
  "escribe" como un lápiz.
- **Descartados:** un fundido entre la cara del primer plano y la del plano general, porque dejaría doble
  imagen de dos dibujos distintos (se cortó en su lugar), y la viñeta aplicada al plató, porque se
  ampliaría con la cámara.

## Qué se midió y qué solo se miró

Medido sobre el MP4 decodificado (342 fotogramas):

- **Paso en dos en toda la película.** En los fotogramas impares la imagen solo cambia por grano: diferencia
  máxima 0,21–0,30 en las cinco escenas. Cámara, caras, Nico y texto avanzan solo en fotogramas pares.
- **Cortes y disolución:** los mayores cambios son los dos cortes previstos (fotogramas 102 y 166) y la
  disolución hacia la aérea (202–210).
- **Corte acercamiento → primer plano:** los ojos quedan en el mismo eje, ≈(955, 540), al final del
  acercamiento, en el primer plano y al empezar el alejamiento.
- **Caras de reemplazo:** el pase de expresión está desplazado (−2, −2) px respecto a la base, el mismo
  valor estimado en el gorro y en el abrigo.
- `hyperframes check`: 0 errores. Las notas de desbordamiento de las capas de cámara se marcaron con
  `data-layout-allow-overflow` porque son intencionadas.
- Construcción determinista: `npm run build` reproduce byte a byte las composiciones renderizadas.

Solo mirado:

- Hojas de `snapshot --review`: momentos clave, las cuatro costuras y la vista de móvil (el texto se lee
  a 360 px).
- Hoja de contacto del render final y recortes al 100 %: cara, texto y Nico en la toma aérea.

Nadie lo ha comprobado:

- La reproducción en dispositivos reales.
- El sonido: no hay pista de audio, y con 14,25 s HyperFrames no la exige.

## Notas

- **P1** · t=8,0–8,6 s · disolución plató → aérea · durante 3–4 fotos se ven los bordes fundidos del plató
  sobre la toma aérea ampliada y algo blanda → con más tiempo, una toma aérea intermedia más cercana a
  la casita (otra generación) daría nitidez en ese tramo · el empalme en la puerta funciona.
- **P2** · t=9,3–14,25 s · Nico en la toma aérea es el dibujo a ras de suelo reducido; a ~120 px no se nota
  que no está visto desde arriba, pero una pose cenital sería más exacta.
- **P2** · texto · el trazado de las letras es propio. La "o" de "amo" es la más irregular; se puede
  retocar en `source/letras.json` sin tocar nada más.
- **P2** · sonido · un tintineo al aparecer cada letra y música suave reforzarían el final.

## Avisos mantenidos a propósito

- `timeline_track_too_dense` en las escenas nuevas (4, 6 y 36 elementos): cada exposición es un clip, igual
  que en la hoja de exposición de la primera parte.

## Notas técnicas para quien continúe

- Cada escena nueva lleva su propio plató gradado. La media gradada en la raíz ocultaba elementos no
  gradados de las sub-escenas; dentro de la misma escena, el SVG del texto sí se ve sobre media gradada
  (verificado).
- La cámara se mueve sobre envoltorios sin tiempo (`*-camara`, `*-capa`) que contienen los clips; nunca
  se transforma un clip directamente.
- HyperFrames 0.9.92 ya está publicado. El proyecto sigue fijado a 0.9.86, la versión con la que se
  verificó; actualizarlo es decisión de quien lo mantenga
  (`hyperframes --cli-version latest upgrade --project .`).
