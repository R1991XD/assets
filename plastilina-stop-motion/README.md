# Nico saluda — cortometraje de stop motion digital en plastilina (HyperFrames)

Animación stop motion digital con aspecto de plastilina artesanal. **Nico**, un niño de plastilina
original con chubasquero mostaza, gorro naranja y botas verde azulado, camina por la acera empedrada de
su casita al atardecer y saluda. La cámara se acerca hasta un primer plano de su carita, donde parpadea,
sonríe y se sonroja. Después se aleja hasta ver el pueblo entero desde el aire, mientras
*"te amo cerdita"* se dibuja letra a letra con un churro de plastilina rosa.

- **Render:** [`renders/nico-saluda_24fps.mp4`](renders/nico-saluda_24fps.mp4): 14,25 s, 1920×1080, H.264,
  **24 fps, 342 fotogramas**. Hoja de contacto de la continuación:
  [`renders/nico-saluda_contactos.jpg`](renders/nico-saluda_contactos.jpg).
- **Proyecto editable:** composición HyperFrames (`index.html` + 5 escenas en `compositions/`), la hoja de
  exposición y la configuración de los planos de cámara (`source/*.json`), y los scripts que reconstruyen
  todo a partir de las imágenes generadas.

| Escena | Fotogramas | Qué pasa |
|---|---|---|
| `camina` | 1–38 | Camina en dos, con el pie apoyado bloqueado |
| `saluda` | 39–72 | Se para, anticipación y saludo |
| `acercamiento` | 73–102 | La cámara se acerca a su cara: motion control fotografiado en dos, acelerando hasta el corte |
| `primer-plano` | 103–166 | Primer plano con caras de reemplazo: mira a cámara, parpadea, se ilumina y sonríe feliz con rubor |
| `alejamiento` | 167–342 | Corte en movimiento a plano general; la cámara se aleja hasta el pueblo entero empalmando en la puerta verde; Nico se despide y *"te amo cerdita"* se dibuja letra a letra |

## Cómo verlo, editarlo y renderizarlo

Requisitos: Node 22+, FFmpeg y Chrome/Chromium. El CLI está fijado a `hyperframes@0.9.86`.

```bash
npx --yes hyperframes@0.9.86 preview          # Studio en el navegador (timeline editable)
npx --yes hyperframes@0.9.86 check            # lint + runtime + layout + movimiento + contraste
npm run build                                  # reconstruye las escenas desde source/*.json
npm run render:final                           # MP4 de entrega a 24 fps
```

Para desactivar la telemetría de HyperFrames: `HYPERFRAMES_NO_TELEMETRY=1`.

## Estructura

```
index.html                       raíz: 5 escenas, plató de la 1.ª parte, viñeta fija al cuadro, 24 fps
compositions/camina.html          caminata (19 exposiciones)
compositions/saluda.html          parada + anticipación + saludo (9 exposiciones)
compositions/acercamiento.html    acercamiento (cámara escalonada en dos)
compositions/primer-plano.html    primer plano (fondo con paralaje + 5 exposiciones de caras)
compositions/alejamiento.html     alejamiento a la toma aérea + texto de plastilina (SVG)
assets/nico/*.png                 recortes de cada dibujo + medidas .json
assets/cels/*.png                 cels finales: dibujo + sombra de contacto + sombra proyectada
assets/pp/                        caras de reemplazo del primer plano (pp_s0..s3) y su fondo desenfocado
assets/pueblo/                    toma aérea y plató con bordes fundidos (para el empalme)
assets/plate/plato.jpg            plató; assets/fx/vineta.png = viñeta de lente
source/generations/               imágenes originales del generador + PROMPTS.md
source/xsheet.json                hoja de exposición de la 1.ª parte, gradación, sombras, escenas extra
source/continuacion.json          planos de cámara, caras del PP, empalme y texto
source/letras.json                recorrido del lápiz de cada letra de "te amo cerdita"
source/prep_assets.py             limpieza de alfa y separación de hojas de poses
source/build_xsheet.py            X-sheet → raíz + camina/saluda (registro, sombras, tiempos)
source/build_pp_faces.py          caras de reemplazo por regiones (ojos, boca, mejillas)
source/build_continuacion.py      acercamiento, primer plano, alejamiento y texto
REVIEW.md                         revisión: decisiones, mediciones, puntos débiles
```

## Pipeline

1. **Generación** (vidIQ → GPT Image 2.6). Se generaron una maestra, un plató, hojas de 4 poses y, para
   la continuación, un primer plano, su pase de expresión y la toma aérea. Siempre se usó la maestra y la
   imagen anterior como referencias, pidiendo cambios localizados. Detalle en
   `source/generations/PROMPTS.md`.
2. **Recorte** (`prep_assets.py`). Se normaliza el alfa, porque el generador deja un halo tenue, y se
   separan las figuras por componentes conexas.
3. **Construcción** (`npm run build`). Se ejecutan en orden `build_xsheet.py`, `build_pp_faces.py` y
   `build_continuacion.py`.
4. **HyperFrames:** `check`, `snapshot --review`, `render --quality delivery --fps 24`.

## Decisiones técnicas

- **Todo en dos, nada interpolado.** Los dibujos son exposiciones retenidas, un clip `<img>` por exposición.
  La cámara se mueve como un motion control fotografiado en dos: salta a una nueva posición cada 2
  fotogramas con `tl.set` siguiendo una curva suave, pero nunca se desliza entre fotogramas. El texto
  crece y la luz parpadea también una vez por foto.
  - Verificado en el MP4: en los fotogramas impares nada cambia salvo el grano (diferencia máx. 0,30).
- **Registro como en un set real** (1.ª parte):
  - Escala por hoja como media entre la altura y el tamaño del ojo respecto a la maestra.
  - Pie apoyado bloqueado entre dibujos.
  - Línea de suelo sobre la acera iluminada.
  - Sombras horneadas en cada cel: contacto más la silueta de la pose proyectada.
- **Caras de reemplazo** (`build_pp_faces.py`). Las dos generaciones del primer plano se alinean por
  correlación de fase (−2, −2 px). Cada estado es la base con solo ojos, boca o mejillas injertados, así que
  gorro, pelo y abrigo son idénticos píxel a píxel entre caras, como las piezas de reemplazo del stop motion.
- **Fondo del primer plano.** Es el propio plató detrás de su cabeza, ampliado 3,7× y desenfocado, con
  paralaje respecto a la cara.
- **Alejamiento continuo.** Una sola cámara virtual mueve tres capas: la toma aérea, el plató con bordes
  fundidos y Nico. Las capas empalman en la puerta verde (k≈3,30) y cada fase es un zoom puro alrededor de
  un punto fijo, así que al alejarse la casita "recibe" su tejado de la toma aérea. Nico encoge un 20 %
  extra mientras la vista se vuelve cenital.
- **Texto dibujado.** Es cursiva de una sola línea diseñada a mano: el recorrido real del lápiz. Se dibuja
  con `stroke-dashoffset` a velocidad de pluma constante, con pausa entre palabras. Lleva un filtro SVG de
  plastilina: relieve iluminado desde la derecha, textura de huellas y sombra. La textura cambia de semilla
  en cada foto (*boil*).
- **Look** con `hyperframes media-treatment`: calidez y grano en cels y caras, y grano en los platós. La
  viñeta es una capa fija al cuadro, porque si fuera en el plató se ampliaría con la cámara.

## Para regenerar imágenes

Hace falta un generador que acepte **imágenes de referencia** y entregue **PNG con fondo transparente**.
Aquí se usó la herramienta de imagen del conector **vidIQ** (`vidiq_image_generate`, 12–22 créditos por
imagen). El proyecto completo costó **148 créditos**, en 9 generaciones. Sin ese acceso se necesita una de
estas dos opciones:

- el conector vidIQ con generación de imágenes y créditos;
- una clave de API de un generador equivalente, por ejemplo GPT Image con `background: transparent`.
