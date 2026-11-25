# Registro de generaciones de imagen

Generador: herramienta de imagen de **vidIQ** (`vidiq_image_generate`), modelo elegido por el servicio
(todas las imágenes salieron de **GPT Image 2.6**). Sin modelo forzado. Coste total: **148 créditos**
(4 imágenes × 22 + 5 × 12) de los 190 disponibles; quedan 42.

Regla seguida: cada pose nueva se genera con **la imagen maestra + el fotograma (o la hoja) anterior como
referencias**, pidiendo un cambio localizado. Para ahorrar créditos y ganar consistencia, las poses se
piden como **hojas de 4 poses** en una sola generación (misma luz, misma escala, mismo material).

| # | Archivo (raw) | Referencias | Formato | Créditos | Uso |
|---|---|---|---|---|---|
| 1 | `01_master_raw.png` | — | 9:16, fondo transparente | 22 | Imagen maestra; también es la pose de parada (`nico_master`) |
| 2 | `02_plate_raw.jpg` | — | 16:9 | 22 | Plató vacío (`assets/plate/plato.jpg`) |
| 3 | `03_walk_sheet_A_raw.png` | maestra | 16:9, transparente | 22 | Paso con la pierna cercana: `walk_n1..n4` |
| 4 | `05_wave_sheet_raw.png` | maestra (= fotograma anterior: la parada) | 16:9, transparente | 22 | Anticipación, mano fuera, mano dentro, parpadeo: `wave_1..4` |
| 5 | `04_walk_sheet_B_raw.png` | maestra + hoja A | 16:9, transparente | 12 | Pedida como paso opuesto; **repitió el paso de A** → se reutiliza como variantes de reemplazo `walk_n*_alt` |
| 6 | `06_walk_sheet_C_raw.png` | maestra + hoja A | 16:9, transparente | 12 | Paso opuesto (brazos invertidos): `walk_f1..f4` |
| 7 | `07_pp_base_raw.png` | maestra + hoja de saludo | 9:16, transparente | 12 | Primer plano base (sonrisa cerrada, mira a cámara) |
| 8 | `08_aerial_raw.jpg` | plató | 16:9 | 12 | Toma aérea del pueblo con la misma casita (`assets/pueblo/aereo.jpg`) |
| 9 | `09_pp_expression_raw.png` | PP base + maestra | 9:16, transparente | 12 | Pase de expresión del PP: solo se injertan ojos, boca y mejillas (`build_pp_faces.py`) |

Las URLs originales de cada resultado están en el historial de la sesión; los archivos descargados aquí
son la fuente de verdad. `source/prep_assets.py` los convierte en los recortes de `assets/nico/`.

## Prompts exactos

### 1 · Imagen maestra (`01_master_raw.png`)

> Original stop-motion claymation character reference, the master model sheet image. 'Nico', a small cheerful boy sculpted entirely from modelling clay (plasticine). Child proportions, about 3.5 heads tall: big round head, round rosy cheeks, small rounded button nose, large round glossy black bead eyes set in clay eyelids, thick soft clay eyebrows, small warm closed-mouth smile, warm peach skin. He wears a chunky orange knitted beanie with a small pom-pom on top, a knee-length mustard-yellow raincoat with a small collar and three large dark-brown wooden toggle buttons down the front, dark teal rubber boots with rounded toes. Simple chunky clay hands with four fingers. Full body, standing in a relaxed neutral pose, arms hanging at his sides, feet close together flat on the ground. The whole body and head are turned three-quarters toward the right of the image (facing right and slightly toward the camera), eyes looking toward the camera, friendly. Handcrafted plasticine surface with subtle fingerprints, sculpting tool marks and small imperfections, matte clay with a soft natural sheen, like a real hand-made puppet. Cinematic miniature photography lighting: warm key light from the upper right, soft cool fill light from the left, gentle rim light on the edges, physically real puppet shot with a macro lens, crisp focus over the whole figure. Centered, the entire figure visible from the top of the pom-pom to the soles of the boots with margin around it. Isolated character only, no floor, no shadow, no text.

### 2 · Plató (`02_plate_raw.jpg`)

> Empty miniature stop-motion film set, a film still from a handcrafted claymation short, with no characters, no people, no animals and no figures anywhere. A quiet village sidewalk of chunky clay cobblestones runs horizontally from the left edge to the right edge across the lower third of the frame, flat and clear so a puppet can walk along it. Behind the sidewalk stands a warm red-brick cottage wall built from hand-pressed clay bricks, with a small round-topped dark green wooden door slightly left of center, a cottage window to the right with a wooden flower box of clay geraniums, a little ivy climbing the bricks, and a low stone kerb at the front edge of the sidewalk. Everything is hand-sculpted plasticine, painted wood and felt, with visible fingerprints and tool marks. Camera at a low eye level about a child puppet's chest height, gentle 35mm lens perspective, shallow depth of field: the cobblestone sidewalk in the middle ground is in sharp focus, the brick wall a little soft, the far background softly blurred. Lighting: warm late-afternoon key light from the upper right casting soft shadows toward the left, soft cool bluish fill from the left, a cozy cinematic mood with a faint atmospheric haze and gentle vignetting. Photographed real miniature, rich warm colours, no text, no signage.

### 3 · Hoja de caminata A (`03_walk_sheet_A_raw.png`) — referencia: maestra

> Stop-motion animation pose sheet: one row of exactly four full-body poses of the clay boy Nico from the reference image, evenly spaced on a transparent canvas, not overlapping. Keep him identical to the reference in every pose: same plasticine puppet, proportions and head size, orange knitted beanie with pom-pom, brown clay hair, rosy cheeks, glossy black bead eyes, small smile, mustard-yellow duffle raincoat with three dark-brown wooden toggles, dark trousers, dark teal rubber boots, same fingerprints, clay texture and lighting (warm key light from upper right, soft fill from left). All four figures the same height and scale, same three-quarter view facing right, grounded boots on one shared invisible ground line.
> The poses are consecutive frames of ONE walking step to the right; only legs, arms, coat hem and body height change:
> 1 (left) CONTACT: near leg (closest to viewer) reaches forward, heel touching, toes up; far leg stretched behind on its toes; widest stride; near arm swings back, far arm forward.
> 2 DOWN: weight drops onto the forward near leg, foot flat, knee bent; body lower and slightly squashed; back heel lifts; arms at widest swing.
> 3 PASSING: near leg straight under the body carrying the weight; far leg lifted, knee bent, boot passing beside it; arms close to the body.
> 4 (right) UP: body at its highest, rising onto the toes of the near foot; far leg swinging forward, knee raised, about to step; arms starting to swap.
> Real handcrafted stop-motion puppet photographed in a miniature studio, crisp focus. Transparent background, no floor, no shadows, no text, no labels, no numbers.

### 4 · Hoja de saludo (`05_wave_sheet_raw.png`) — referencia: maestra (el fotograma anterior es la parada)

> Stop-motion animation pose sheet: one row of exactly four full-body poses of the clay boy Nico from the reference image, evenly spaced on a transparent canvas, not overlapping. The reference is the previous frame: he has just stopped walking, feet together. Keep him identical to the reference in every pose: same plasticine puppet, proportions and head size, orange knitted beanie with pom-pom, brown clay hair, rosy cheeks, glossy black bead eyes, mustard-yellow duffle raincoat with three dark-brown wooden toggles, dark trousers, dark teal rubber boots, same fingerprints, clay texture and lighting (warm key light from upper right, soft fill from left). All four the same height and scale as the reference, same three-quarter view facing right, boots flat on one shared invisible ground line.
> Localized change only, like an animator moving just the puppet's arm: boots, legs, coat and body stay exactly as in the reference; only the near arm (on the left side of the image, closest to the viewer), a slight head turn toward the camera and the expression change:
> 1 (left) ANTICIPATION: knees slightly bent, near arm lifting from the elbow, hand at chest height, head starting to turn to camera, closed smile.
> 2 WAVE OUT: near arm raised high beside the head, open palm facing camera, hand tilted outward away from the head, big happy open-mouth smile, eyes on camera.
> 3 WAVE IN: same as 2 but the raised hand tilted inward toward the head.
> 4 (right) BLINK: same as 2 but eyes closed in a happy blink.
> Real handcrafted stop-motion puppet photographed in a miniature studio, crisp focus. Transparent background, no floor, no shadows, no text, no labels, no numbers.

### 5 · Hoja de caminata B (`04_walk_sheet_B_raw.png`) — referencias: maestra + hoja A

> Stop-motion animation pose sheet: one row of exactly four full-body poses of the clay boy Nico, evenly spaced on a transparent canvas, not overlapping. The first reference is his master model; the second reference shows the previous four frames of his walk: continue from its last pose and match those figures exactly in size, proportions, head size and three-quarter view facing right. Keep him identical in every pose: same plasticine puppet, orange knitted beanie with pom-pom, brown clay hair, rosy cheeks, glossy black bead eyes, small smile, mustard-yellow duffle raincoat with three dark-brown wooden toggles, dark trousers, dark teal rubber boots, same fingerprints, clay texture and lighting (warm key light from upper right, soft fill from left). Boots that touch the ground rest on one shared invisible ground line.
> These are the next frames: the SECOND walking step to the right, now led by the far leg; only legs, arms, coat hem and body height change:
> 1 (left) CONTACT: far leg reaches forward, heel touching, toes up; near leg (closest to viewer) stretched behind on its toes; widest stride; near arm swings forward, far arm back.
> 2 DOWN: weight drops onto the forward far leg, foot flat, knee bent; body lower and slightly squashed; back heel lifts; arms at widest swing.
> 3 PASSING: far leg straight under the body carrying the weight; near leg lifted, knee bent, its boot passing in front of the far leg; arms close to the body.
> 4 (right) UP: body at its highest, rising onto the toes of the far foot; near leg swinging forward, knee raised, about to step; arms starting to swap.
> Real handcrafted stop-motion puppet photographed in a miniature studio, crisp focus. Transparent background, no floor, no shadows, no text, no labels, no numbers.

Resultado: el modelo copió la configuración de la hoja A (misma pierna y mismos brazos adelante).
No se descartó: sus cuatro dibujos son variantes de reemplazo del mismo paso (`walk_n*_alt`), así los
ciclos no se repiten idénticos, como al reposar una marioneta real.

### 6 · Hoja de caminata C (`06_walk_sheet_C_raw.png`) — referencias: maestra + hoja A

> Stop-motion animation pose sheet of the clay boy Nico: one row of exactly four full-body poses on a transparent canvas, evenly spaced, not overlapping. Same character as the first reference, and the same size, proportions, three-quarter view facing right, lighting and plasticine texture as the figures in the second reference image (the previous walking step).
> IMPORTANT: this is the OPPOSITE step, not a copy. In the second reference the near leg (closest to the viewer) leads and the near arm swings back. Here the FAR leg leads, the NEAR ARM swings FORWARD across the front of the coat and the far arm swings back behind the body. Swap legs and arms in every pose:
> 1 (left) CONTACT: far leg forward, heel down, its boot slightly higher and partly behind; near leg stretched behind on its toes, its boot nearer and lower; near hand swinging forward in front of the coat.
> 2 DOWN: weight on the forward far leg, knee bent, body lower; near leg behind with heel lifting; near hand at its most forward, in front of the coat.
> 3 PASSING: far leg straight under the body; near leg lifted with knee bent, its boot passing IN FRONT of the standing leg and hiding part of it; arms close to the body.
> 4 (right) UP: body at its highest on the toes of the far foot; near leg swinging forward with knee raised, in front; near hand starting to swing back.
> Same orange knitted beanie with pom-pom, brown clay hair, rosy cheeks, glossy black bead eyes, small smile, mustard-yellow duffle raincoat with three dark-brown wooden toggles, dark trousers, dark teal rubber boots, warm key light from upper right, soft fill from left, fingerprints in the clay. Real handcrafted stop-motion puppet photographed in a miniature studio, crisp focus. Transparent background, no floor, no shadows, no text, no labels, no numbers.

Resultado: invierte claramente los brazos (la mano cercana cruza por delante del abrigo); las piernas
quedan parecidas a A. En plano 3/4 y a 1/3 s por paso, la alternancia de brazos es la que lee el ojo.

## Continuación (acercamiento, primer plano y toma aérea)

### 7 · Primer plano base (`07_pp_base_raw.png`) — referencias: maestra + hoja de saludo

> Close-up portrait (head and shoulders) of the clay boy Nico from the reference images, the same handcrafted plasticine stop-motion puppet: chunky orange knitted beanie with pom-pom, brown clay hair, round rosy cheeks, small rounded nose, glossy black bead eyes set in clay eyelids, soft thick clay eyebrows, gentle closed-mouth smile, warm peach skin, mustard-yellow duffle coat collar with one dark-brown wooden toggle visible at the bottom. Face turned slightly toward the right of the image but looking straight into the camera lens, sweet and friendly. Show every handcrafted detail in sharp macro focus: fingerprints and tiny tool marks in the clay skin, the soft sheen of the plasticine, tiny warm catchlight reflections in the bead eyes, the wool texture of the knitted beanie, individually sculpted hair strands. Same lighting as the references: warm golden key light from the upper right, soft cool fill from the left, gentle warm rim light on the edges. Real stop-motion puppet photographed with a macro lens. The figure is cut at mid-chest by the bottom edge of the image; head, beanie and pom-pom fully visible with a small margin above. Transparent background, no floor, no shadow, no text.

### 8 · Toma aérea (`08_aerial_raw.jpg`) — referencia: plató

> Aerial high-angle panoramic view, looking down at about 40 degrees from high above and in front, of a whole tiny handcrafted clay miniature village at golden hour, the same world and materials as the reference set: chunky clay cobblestone streets winding between cottages of hand-pressed red clay bricks with clay-tile and thatched roofs, chimneys, little gardens, picket fences, round clay trees and bushes, a small stone bridge over a blue clay stream, a village green, soft green rolling hills around. At the lower center of the image, facing the camera on a cobbled street, stands the same cottage as in the reference: red brick wall, small round-topped dark green wooden door, a window with a wooden flower box of red geraniums and ivy, seen from the front and above. Warm low sun from the right casting long soft shadows to the left, gentle haze. The upper third of the image is a soft warm peach-and-pale-blue sky with a few puffy clay clouds and plenty of clear empty space for a title. Everything sculpted from plasticine, felt and painted wood, with visible fingerprints and tool marks. Tilt-shift miniature photography: sharp village center, gently blurred edges. No people, no animals, no text, no signage, no letters.

### 9 · Pase de expresión del primer plano (`09_pp_expression_raw.png`) — referencias: PP base + maestra

> Edit of the first reference image, the close-up of the clay boy Nico: keep absolutely everything identical to it: the same framing, size and position in the image, the same head angle, the same knitted orange beanie and pom-pom, brown clay hair, ears, nose, coat collar and wooden toggle, the same lighting, clay texture, fingerprints and transparent background. Change only the facial expression, like a stop-motion animator swapping replacement pieces on the puppet's face: both eyes closed in a happy squint (gently curved closed clay eyelids with a soft crease), a big happy open-mouth smile with a little pink tongue, and the rosy cheek blush a little stronger and pinker. The face must stay exactly where it is, with the same proportions. Real stop-motion puppet photographed with a macro lens, crisp focus. Transparent background, no text.

Resultado: mismo encuadre con un desplazamiento de solo (−2, −2) px. Las 4 caras del primer plano
(`assets/pp/pp_s0..s3.png`) se construyen injertando únicamente ojos y cejas, boca y mejillas de este pase
sobre la base.

El texto *"te amo cerdita"* no se generó: es un trazado de cursiva de una línea dibujado a mano
(`source/letras.json`) y renderizado como plastilina con un filtro SVG.
