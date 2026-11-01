## ESTILOS — los 3, completos (extraídos de `cowork-notebooklm-slides` v3.9 el 1-nov-2026)

Esta sección es la **fuente única** de los estilos. La skill `cowork-notebooklm-slides` se retiró, así que nada de aquí remite a ella. Cada estilo tiene dos partes:

- **Especificación original:** el template que Cris validó en producción, copiado **literal** (en inglés, como se escribió). Es la referencia de cómo tiene que verse el estilo y no se reescribe.
- **En código:** cómo se cumple cada regla con el motor (`engine/`, `lib/`, `scripts/textures.py`). Donde el motor todavía no puede, dice **«por implementar»**.

### Elegir el estilo

| Si el mensaje de Cris contiene… | `STYLE_SLUG` |
|---|---|
| "harper", "bazaar", "editorial", **o no menciona estilo** | `harper_bazaar` (default) |
| "cuaderno", "davinci", "da vinci", "anatómico", "manuscrito", "tinta" | `cuaderno_davinci` |
| "minimalista", "minimal", "línea azul", "linea azul", "blueprint", "memphis", "flat" | `minimalista_linea` |

- **Dos estilos contradictorios** en el mismo mensaje ("harper pero minimalista"): STOP y preguntar cuál de los 3. **Nunca se mezclan.**
- Los 3 se numeran así cuando Cris habla de «estilo 1/2/3»: **1 = Harper's Bazaar, 2 = Da Vinci, 3 = Minimalista**.

| Slug | Nombre | Atmósfera dominante | Cuándo usarlo |
|---|---|---|---|
| `harper_bazaar` | Harper's Bazaar Científico | Editorial luxury: amarillo/blanco/negro, Didone, halftones, destellos | Default; papers densos en datos cuantitativos (biomateriales, ingeniería de procesos, química analítica) |
| `cuaderno_davinci` | Cuaderno Anatómico Da Vinci | Manuscrito histórico: tinta azul de Prusia y sepia sobre papel envejecido, TODO bocetado a mano | Anatomía, fisiología, medicina, biología estructural; donde la estética manuscrita-naturalista sume narrativa |
| `minimalista_linea` | Minimalista Línea Azul | Fondos planos off-white/cobalto (sin degradados), estructuras en monolínea azul sin relleno, gráficos densos | Validado por Cris en producción (sep 2026) |

### Contaminación cruzada = falla crítica

Nunca se mezcla vocabulario ni elementos entre estilos:

- En `cuaderno_davinci` **no existen** Didone, destellos, halftones, degradados ni cobalto.
- En `minimalista_linea` **no existen** pluma, sepia, huellas, Didone, halftones, destellos **ni fondos con degradado** (el degradado solo vive dentro de los gráficos).
- En `harper_bazaar` **no existen** degradados, manuscrito, salpicaduras de tinta ni cobalto.

En la revisión de F4, un destello en Da Vinci o en minimalista, un degradado saturado en Harper o Da Vinci, o tinta y papel en Harper o minimalista, marca la slide como ❌ y se corrige.

### Contrato de contenido por slide (F1)

Cada slide se planifica con estos seis campos. **Si falta uno, la slide sale genérica.**

| Campo | Qué contiene |
|---|---|
| `TÍTULO` | Título científicamente exacto, sin adornos ni metáforas |
| `DATO` | Valores reales ya estructurados: filas y columnas, o serie con etiquetas y unidades. **Mínimo 4 puntos.** Nunca un párrafo |
| `GRÁFICO` | Qué forma toma ese dato: dona, pastel, tabla, barras, gráficos pequeños comparados, diagrama etiquetado |
| `ILUSTRACIÓN` | Qué estructura se dibuja |
| `HALLAZGO` | La lectura clave en 6 palabras, para la anotación con flecha |
| `FUENTE` | `n` y la cita, como irá en el pie de figura |

**Prohibida la prosa corrida.** Un concepto sin números se entrega igual de estructurado: los conceptos nombrados y sus relaciones, listos para volverse nodos o filas. Las slides de break, N-1 y N solo llevan su rol.

**Estructura de todo deck:** slide 1 portada · **un solo** descanso visual en `BREAKS = [round(N/2)]` (N=12 → 6, N=15 → 8; nunca múltiplos de 5: tres descansos fragmentan el argumento, decidido por Cris en producción) · N-1 declaración de cierre · N referencias APA. Con N ≤ 4 no hay break. Si el punto medio cae en N-1 o N, el break se corre una slide atrás.

---

### Estilo 1 · `harper_bazaar` — Harper's Bazaar Científico

#### Especificación original (literal, tal como estaba en `cowork-notebooklm-slides` v3.9; `[N]`, `[BREAK]`, `[N-1]`, `[AUTORES]`, `[FECHA]` y las referencias a «PDF Section DIAPOSITIVA N» son marcadores de ese pipeline: aquí equivalen a N, `BREAKS`, la slide de cierre, los datos del paper y el contrato de F1)

```
1. MASTER VISUAL SYSTEM

Atmosphere: Editorial luxury with dense texture. Elevated Flat Design layered with photographic film grain — NEVER look digitally cheap, clean, or "corporate tech."

Palette: Solid Yellow (#CCCC00) alternating with Pure White (#FFFFFF). Text and graphic elements ALWAYS in Deep Black (#000000). Background patterns rotate across the deck:
- Full yellow slides
- Full white slides with subtle Moiré/Pulse Effect
- Half-split slides (horizontal or vertical yellow/white split)
- Quartered mosaic slides (2x2 yellow/white checkered)
Never three consecutive identical backgrounds.

Typography: Didone Display / Modern Serif (HTF Didot or Bodoni Poster). Extreme contrast thick/hairline. ALL CAPS GIANT at POSTER SCALE — titles occupy 25–40% of canvas. Kerning -20. Some titles horizontal, some vertical (rotated 90° left edge), some stacked. Body: clean neutral sans-serif (Inter, Neue Haas Grotesk), small scale, extreme hierarchy.

2. SCIENTIFIC ILLUSTRATION SYSTEM

Every illustration MUST combine:
A) SOLID BLACK SILHOUETTES (Malika Favre): bold flat black silhouettes, dramatic negative space.
B) DENSE HALFTONE GRADIENTS (Tavis Coburn): halftone dots graduated dense→sparse inside/around silhouettes.
C) FINE INK-SKETCH DETAIL LINES (Patrick Nagel): delicate hand-drawn ink lines, slightly imperfect.
D) METALLIC SPARKLE BURSTS (NON-NEGOTIABLE): 4-line sparkle bursts and dot-glitter clusters. 3–7 per illustration.
E) EDITORIAL COLLAGE COMPOSITION: multiple scientific elements with deliberate asymmetry.
F) GOLD/YELLOW HIGHLIGHT ACCENTS: strategic #CCCC00 on white-background slides only.

Reference artists: Malika Favre, Patrick Nagel, Tavis Coburn, Tom Whalen, Brian Stauffer, Olly Moss.

3. DATA VISUALIZATION

Scatter Plots — "CONSTELLATIONS": data points as ✦ star-marks, trend lines as elegant hand-drawn curves with sparkles on key points.
Bar Charts — "MONOLITHS": solid deep black blocks or diagonal hatching, no borders/shadows/gradients.
Pie Charts — "BAUHAUS JEWELS": solid black + halftone-filled segments, Didot labels outside with leader lines.
Concept Maps: nodes as black circles/icons, ink-stroke connections with arrows, sparkles at key nodes.
Tables: thin horizontal rules only, no verticals or boxes.

4. COMPOSITION RULES

- 30–50% negative space per slide.
- Title and illustration may overlap for editorial drama.
- Body text left-aligned, max 60 chars/line, placed in corners or edges.
- NEVER center everything — deliberate asymmetry.

5. DECK STRUCTURE — [N] SLIDES

[INSERTAR mapping slide-por-slide referenciando secciones exactas del PDF]

SLIDE 1 — COVER: "[título científico exacto]"
Visual: Large editorial illustration — black silhouette figure + scientific iconography + halftones + sparkles. Solid yellow background.
Title: Giant Didot, ONE word vertical left edge, ONE word horizontal bottom. ALL CAPS.
Subtitle: [AUTORES] | [FECHA] small sans-serif.
Content source: PDF Section "DIAPOSITIVA 1"

SLIDE [BREAK] — THE ONLY VISUAL BREAK (no text)
Full-bleed dramatic scientific metaphor. Solid yellow. Black silhouettes + dense halftones + heavy sparkles. NO title, NO caption.

SLIDE [N-1] — CLOSING IMPACT
Full white + subtle Moiré. Giant Didot declarative sentence from PDF Section "DIAPOSITIVA [N-1]". Fills 60–70% canvas. NO illustration.

SLIDE [N] — REFERENCES
Full white. "REFERENCIAS" small Didot caps. Full APA list in clean sans-serif. No decoration.
```

**Fondo (sustrato que la slide conserva debajo del contenido):** campos planos amarillo `#CCCC00` y blanco `#FFFFFF` en su posición exacta (incluidas las divisiones horizontal/vertical y el mosaico 2×2), el moiré/pulso sutil sobre los campos blancos y el grano de película. Los destellos ornamentales en zonas vacías pueden quedar en el fondo. El amarillo es exactamente `#CCCC00` y el blanco exactamente `#FFFFFF`, sin corrimiento de tono.

> Bloque PRESERVE original (literal): *"PRESERVE ONLY: the flat background fields and their exact positions — Solid Yellow #CCCC00 and Pure White #FFFFFF, including any horizontal/vertical half-split or 2x2 quartered mosaic arrangement exactly where it sits; the subtle Moiré/pulse pattern on white fields; the photographic film grain. Purely ornamental sparkle bursts in otherwise empty areas MAY remain. Do NOT shift hue or saturation: the yellow must stay exactly #CCCC00, the white exactly #FFFFFF."*

#### En código

| Regla | Cómo se cumple |
|---|---|
| Fondos que rotan, nunca 3 iguales seguidos; grano de película; moiré en blanco | `scripts/textures.py harper` con las variantes amarillo · blanco con moiré · split-v · split-h · mosaico 2×2; el grano va horneado en la textura. Se planifica la secuencia de fondos en F2 |
| Didone gigante en mayúsculas, 25–40 % del lienzo, kerning -20 | Bodoni Moda 700 (`.t-title` / `.t-hero`, `letter-spacing: -.02em`). El título ocupa ese porcentaje de verdad; se mide en el frame final |
| Títulos horizontales, verticales (90° en el borde izquierdo) o apilados | Vertical con `writing-mode: vertical-rl` + `drop`; apilado por líneas con `rise`. Repartir los tres tipos en el deck |
| Cuerpo sans neutra, pequeño, jerarquía extrema | Inter (`--font-body`) sobre los pisos de `base.css` (27/21 px); jerarquía por tamaño, nunca por color |
| A · siluetas negras planas | Relleno `#000` en los SVG; los del banco pasan por `harper()` (`lib/prep.py`), que manda los tonos oscuros a negro |
| B · halftone graduado denso→ralo | Patrones `ht`/`htk` y máscaras `hm`/`lm` de `AX.defs()`; `AX.sphere()` para volúmenes; `harper()` asigna halftone denso o ralo según luminancia |
| C · líneas finas de tinta, levemente imperfectas | Trazos `.line` de 1–1,4 px que se dibujan con `draw` |
| **D · destellos de 4 puntas: 3–7 por ilustración (no negociable)** | `AX.sparkle()`; entran con `pop` en la Etapa 2. Se cuentan en la revisión de F4 |
| E · collage editorial asimétrico | Varios elementos científicos por slide, nunca uno centrado solo |
| F · acento amarillo solo en slides de fondo blanco | `--accent` `#CCCC00` (marker, chip) solo cuando el fondo es blanco |
| Dispersión = «constelaciones» | Puntos como destellos pequeños (`pop`), tendencia como curva a mano trazada con `draw`, destellos en los puntos clave |
| Barras = «monolitos» | Bloques negros o con achurado diagonal, sin borde, sombra ni degradado; crecen con `grow` y la cifra viaja con `ride` |
| Pastel = «joyas Bauhaus» | Segmentos negros + con halftone (`ring`), rótulos Didone afuera con líneas guía (`rotulo`) |
| Mapas conceptuales | Nodos círculos negros (`pop`), conexiones de tinta con flecha (`draw`), destellos en nodos clave |
| Tablas | Solo reglas horizontales finas; nada de verticales ni cajas |
| 30–50 % de espacio negativo; nunca todo centrado | Se mide en el frame final; texto alineado a la izquierda, ≤ 60 caracteres por línea, en esquinas o bordes; título e ilustración pueden solaparse |
| Portada | Fondo amarillo; ilustración grande (silueta + iconografía + halftone + destellos); una palabra vertical en el borde izquierdo y otra horizontal abajo; autores y fecha en sans pequeña |
| Break | Amarillo a sangre, siluetas + halftone denso + muchos destellos, **sin texto**; clip **idle** (algo que respira o gira y vuelve al origen) |
| N-1 | Blanco con moiré; una frase declarativa en Didone gigante que llena 60–70 % del lienzo; sin ilustración |
| N | Blanco; "REFERENCES" en Didone pequeña; APA completa en sans; sin decoración |
| Unidades en Didone | `uppercase` rompe `pN`/`nm`/`µm`: cifras con unidad con `text-transform: none`, el `µ` en Inter aparte |

**Revisión del frame final:** títulos Didone, datos legibles, siluetas + halftone + destellos sin daño; paleta exacta `#CCCC00` / `#FFFFFF` / `#000000`.

---

### Estilo 2 · `cuaderno_davinci` — Cuaderno Anatómico Da Vinci

**Regla absoluta:** NUNCA tipografía digital limpia, NUNCA bordes vectoriales perfectos, NUNCA fondos de color saturado. Toda línea, número, letra y eje se ve como trazo de pluma humana sobre pergamino. TODO el contenido (dispersión, barras, tablas, mapas) se renderiza como boceto a mano alzada.

#### Especificación original (literal, tal como estaba en `cowork-notebooklm-slides` v3.9; `[N]`, `[BREAK]`, `[N-1]`, `[AUTORES]`, `[FECHA]` y las referencias a «PDF Section DIAPOSITIVA N» son marcadores de ese pipeline: aquí equivalen a N, `BREAKS`, la slide de cierre, los datos del paper y el contrato de F1)

```
1. MASTER VISUAL SYSTEM

Atmosphere: Historical scientific manuscript — every slide MUST look like a torn page from a 15th-19th century laboratory notebook by Leonardo da Vinci, Andreas Vesalius, or Ernst Haeckel. Hand-drawn ink on aged paper, with the tactile presence of folded creases, fingerprint smudges, ink splatters, marginal corrections, and underline emphasis. NEVER digital, NEVER clean vector lines, NEVER flat color fills.

Paper substrate (NON-NEGOTIABLE): all slides share a base canvas of aged parchment / cream cotton paper, color #E8D9B5 to #D4C29A range, with:
- Visible horizontal and vertical crease folds (one or two per slide, off-center)
- Random ink splatters and dot-spray in deep blue or sepia (4-10 spots per slide, edges and corners)
- Faint fingerprint smudges (1-2 per slide, semi-transparent, gray-brown)
- Subtle paper grain and slight yellowing toward edges
- Optional: a tiny coffee-ring stain or wax-seal mark on cover/closing slide only

Ink palette (only these inks exist):
- PRIMARY INK: Deep Prussian Blue (#1C3D7A) for all main strokes, titles, diagrams, axes, bar fills (via diagonal hatching), arrows.
- SECONDARY INK: Sepia Brown (#5C3A1E) for marginal annotations, secondary captions, fingerprint-style accents.
- HIGHLIGHT WASH: Translucent watercolor yellow (#E8C547 at 40% opacity) used ONLY to circle, underline, or emphasize the single most important data point or term per slide — manuscript-style highlight, irregular edge.
- NEVER use pure black, never use any other color. Text and graphics live exclusively in the blue/sepia/yellow-wash trio.

Typography (NO digital fonts visible):
- Titles: hand-lettered cursive script in Prussian Blue, with the natural irregularity of a quill pen — varying stroke weight, slight slant, occasional pen-pause dots. Reference: Da Vinci's mirror-script handwriting, Vesalius's De Humani Corporis Fabrica chapter headers.
- Body: smaller hand-lettered print, mixed cursive/print, sometimes underlined with a wavy hand-drawn line.
- Numbers/data labels: hand-written, with the proportional inconsistency of human writing (a "4" may differ slightly from another "4" on the same slide).
- Marginal notes: tiny sepia hand-lettering, sometimes upside-down or sideways, sometimes with a question mark "?" or arrow "→" pointing back to the main diagram. These add scientific-process realism.
- Crossed-out corrections: visible. A wrong number or word with a single hand-drawn strikethrough line, with the correction written above or beside it in smaller script. 1-2 corrections per slide max — gives authenticity.

2. SCIENTIFIC ILLUSTRATION SYSTEM

Every illustration MUST combine:
A) ANATOMICAL HAND-DRAWN LINEWORK (Da Vinci, Vesalius): organic figures and objects drawn with quill-pen ink strokes, varying line weight, visible hatching for shading. NEVER smooth vector contours.
B) CROSS-HATCHING SHADOW (Albrecht Dürer): all shading achieved through dense parallel or crossed ink lines, never solid fills, never gradients.
C) BOTANICAL/SCIENTIFIC STIPPLING (Ernst Haeckel, Maria Sibylla Merian): texture and depth via dot-stippling clusters, especially on biological forms.
D) MARGINAL DIAGRAMS AND ARROWS: every key element of the main illustration MUST have a hand-drawn arrow pointing to a sepia annotation in the margin — "vena cava", "stress concentration zone", "C/P ratio = 1.67", etc. 3-6 marginal labels per slide.
E) MEASUREMENT MARKS: little hand-drawn rulers, calipers, or dimension lines with hand-written values where dimensions matter.
F) SCIENTIFIC AUTHENTICITY MARKS (NON-NEGOTIABLE): every slide MUST contain at least one of — a fingerprint smudge near the diagram, a small ink blot, a corner page-curl, or a tiny sketched hand reaching into the frame. These break digital sterility.

Reference artists / sources: Leonardo da Vinci (Anatomical Notebooks, Codex Atlanticus), Andreas Vesalius (De Humani Corporis Fabrica 1543), Ernst Haeckel (Kunstformen der Natur), Maria Sibylla Merian, Albrecht Dürer, Eadweard Muybridge motion studies, Stephen Biesty cutaway illustrations.

3. DATA VISUALIZATION — ALL HAND-DRAWN AS INK SKETCHES

Scatter Plots — "INK CONSTELLATIONS": axes are hand-drawn wobbly lines with hand-lettered tick marks. Data points are small hand-drawn ink crosses "×" or filled circles "●" with slight size inconsistency. Trend lines are confident single quill strokes, not perfectly smooth — natural human curve. Key outliers circled with the yellow watercolor wash.
Bar Charts — "INK COLUMNS": each bar drawn as a rectangle outline in Prussian Blue with diagonal hatching fill INSIDE (parallel ink strokes at 45°, drawn by hand — visible irregularity in spacing). Value labels hand-written above each bar (e.g. "40 MPa"). Y-axis with hand-lettered numbers; dashed reference lines drawn as broken hand-strokes. The TOP value or the highest bar always gets a yellow-wash circle highlight. See reference: the bioactive-surface engineering slide with Plasma/HVOF/Cold Spray bars at 25/40/30 MPa.
Pie Charts — "QUILL SLICES": circle drawn as a single not-quite-perfect hand stroke. Slices separated by radial ink lines. Each slice filled with a DIFFERENT hand-drawn pattern (parallel hatching, crossed hatching, stippling dots, wavy lines) — never solid color. Labels outside with leader lines drawn as hand-pulled strokes ending in a small arrow.
Concept Maps — "ANATOMICAL DIAGRAMS": nodes as small hand-drawn circles or organic blob shapes with text inside in cursive. Connections as flowing ink lines with hand-drawn arrowheads. Treat the diagram like an anatomical labeling sheet — central object dominant, satellite labels around it.
Tables — "LEDGER GRIDS": ruled with hand-drawn horizontal and (optionally) vertical lines that wobble slightly. Headers in cursive blue, body in print blue, occasional sepia annotation in margin. NEVER spreadsheet-perfect.
Equations/formulas — hand-written across the slide in cursive, with one or two terms circled in yellow wash if they are the key.

4. COMPOSITION RULES

- Treat each slide as a notebook page: title at the top in flowing cursive, main diagram dominant in the center, marginal annotations and corrections scattered around the edges with hand-drawn arrows linking them back to the diagram.
- 25-40% negative space (more dense than Harper's Bazaar — this is a working notebook, not a poster).
- Asymmetry is organic, not designed: things end up where the scientist's hand wandered, not on a grid.
- Multiple ink elements may slightly overlap (a marginal note crossing a fold line, an arrow crossing the chart axis).
- NEVER center everything cleanly. NEVER align margins perfectly. The human hand is the rhythm.

5. DECK STRUCTURE — [N] SLIDES

[INSERTAR mapping slide-por-slide referenciando secciones exactas del PDF]

SLIDE 1 — COVER: "[título científico exacto]"
Visual: A large anatomical or scientific hand-drawn illustration centered on the page (relevant to paper subject — e.g. a heart, a molecule, a hand-drawn machine cross-section), surrounded by marginal sepia annotations in the scientist's hand. Aged paper, two visible fold creases, ink splatters, one fingerprint smudge in corner.
Title: Hand-lettered cursive in Prussian Blue, spanning the top third, slightly slanted as if written quickly. Sometimes flowing across an underlined hand-drawn banner.
Subtitle: [AUTORES] | [FECHA] in smaller sepia cursive, lower-right, possibly with a hand-drawn flourish or date format like "Anno MMXXVI".
Content source: PDF Section "DIAPOSITIVA 1"

SLIDE [BREAK] — THE ONLY VISUAL BREAK (no text)
Full-page hand-drawn anatomical or naturalistic illustration related to paper subject. Dense cross-hatching, stippling, marginal arrows WITHOUT labels (just the arrows — gives a "study sketch" feeling). NO title. The paper texture, fingerprints, and ink splatters carry the slide. Optionally a single small sepia notation in a corner like "fig. V" or "estudio nro 3".

SLIDE [N-1] — CLOSING IMPACT
The paper page now shows a single large declarative sentence in flowing hand-cursive Prussian Blue, with the single most important phrase or number circled by yellow watercolor wash. Optional: a marginal sepia note arrowing into the phrase. Heavy paper grain, two ink splatters. NO illustration — the handwriting IS the illustration.
Content source: PDF Section "DIAPOSITIVA [N-1]"

SLIDE [N] — REFERENCES
Hand-lettered "REFERENCIAS" in cursive at top. Full APA list rendered as a hand-written bibliography in smaller print-cursive, slightly inconsistent line spacing as if copied by hand from another source. Sepia ink. One yellow-wash highlight on the most-cited author or key paper if such exists.
```

**Fondo (sustrato, obligatorio, NO es contenido):** pergamino `#E8D9B5`–`#D4C29A` con su grano, amarillento hacia los bordes, pliegues visibles, salpicaduras y spray de tinta en azul de Prusia `#1C3D7A` y sepia `#5C3A1E`, huellas tenues y, solo en portada o cierre, una mancha de café o un sello de lacre. Nunca se reemplaza el pergamino por blanco, crema o un color plano, ni se "digitaliza" su textura.

> Bloque PRESERVE original (literal): *"PRESERVE ONLY: the aged parchment substrate with its exact color range #E8D9B5 to #D4C29A, the paper grain, the yellowing toward the edges, the visible fold creases, the ink splatters and dot-spray in Prussian Blue #1C3D7A and Sepia #5C3A1E, the faint fingerprint smudges, and any coffee-ring or wax-seal stain. These marks are the substrate and MUST survive — they are not content. Remove every hand-lettered word, every hand-drawn diagram, axis, bar, data point, arrow, marginal annotation and correction. Do NOT digitize, smooth or flatten the paper texture. Do NOT replace the parchment with white, cream or any flat color."*

#### En código

> ⚠️ **Da Vinci todavía no se ha probado con el motor.** Antes de la primera corrida real se hace un piloto de 2-3 slides y se mira el frame final contra esta especificación. Los puntos marcados **por implementar** se resuelven en ese piloto y se suben al repo.

| Regla | Cómo se cumple |
|---|---|
| Pergamino con 1-2 pliegues, 4-10 salpicaduras, 1-2 huellas, grano, bordes amarillentos | `scripts/textures.py davinci` (determinista por semilla, una semilla distinta por slide). Mancha de café o sello: solo portada y cierre |
| Tintas: solo `#1C3D7A`, `#5C3A1E` y lavado `#E8C547` al 40 %; **nunca negro** | Tokens de `cuaderno_davinci.css` (`--ink`, `--ink2`, `--accent`, `.wash`). Cualquier `#000` en una slide Da Vinci es un error |
| Lavado amarillo: UNO por slide, en el dato o término más importante, borde irregular | `.wash` como mancha de contorno irregular (no un rectángulo) que entra con `flood` o `marker` |
| Títulos en cursiva a pluma, cuerpo manuscrito | Homemade Apple (títulos) + Caveat (cuerpo, notas, cifras) |
| Cifras con la inconsistencia de la escritura humana | **Por implementar:** pequeña rotación y escala aleatoria por glifo (semilla fija) sobre `SplitText` |
| **Líneas de pluma, nunca vectores perfectos** | **Por implementar:** temblor de trazo (filtro SVG `feTurbulence` + `feDisplacementMap` suave, o desplazamiento de puntos del path con semilla) y grosor variable. Sin esto el estilo no se cumple |
| Notas al margen en sepia: 3-6 por slide, a veces de costado o al revés, con flecha al diagrama | `rotulo` con guía sepia (`.lead`) y texto `.note`; la flecha se traza con `draw` |
| Tachones: 1-2 por slide | Palabra o cifra equivocada → línea de tachado trazada con `draw` → corrección tecleada encima en letra más pequeña |
| Sombra solo por achurado cruzado (Dürer), textura por punteado (Haeckel) | **Por implementar:** patrones SVG de achurado a 45° y cruzado, y punteado, en tinta azul; nunca rellenos sólidos ni degradados |
| Marcas de medida: reglas, calibres, cotas con valores | Cotas trazadas con `draw` + valor manuscrito tecleado |
| Marca de autenticidad en CADA slide (huella cerca del diagrama, borrón, esquina doblada o mano esbozada entrando) | Huella o borrón desde la textura o como SVG encima del diagrama. **La mano esbozada no se usa** (regla de Cris: nunca figuras humanas) |
| Dispersión = «constelaciones de tinta» | Ejes temblorosos con ticks manuscritos; puntos `×` o `●` de tamaño irregular (`pop`); tendencia de un solo trazo (`draw`); atípicos rodeados con lavado |
| Barras = «columnas de tinta» | Contorno azul + achurado a 45° irregular adentro (crece con `grow`); valor manuscrito arriba ("40 MPa"); líneas de referencia punteadas a mano; **la barra más alta lleva círculo de lavado** |
| Pastel = «rebanadas a pluma» | Círculo de un trazo imperfecto (`draw`); radios de tinta; **cada sector con un patrón distinto** (achurado paralelo, cruzado, punteado, ondas); rótulos afuera con guía terminada en flecha |
| Mapas conceptuales = «láminas anatómicas» | Objeto central dominante; nodos círculos u óvalos a mano con cursiva; conexiones fluidas con punta de flecha |
| Tablas = «libro contable» | Reglas a mano levemente onduladas; encabezados en cursiva azul, cuerpo en letra de imprenta azul; nota sepia al margen |
| Ecuaciones | Manuscritas en cursiva; 1-2 términos clave con lavado |
| Composición de página de cuaderno; 25-40 % de espacio negativo | Título arriba, diagrama dominante al centro, notas y correcciones en los bordes; nada perfectamente alineado; los elementos pueden solaparse levemente (una nota cruzando un pliegue) |
| Portada | Ilustración anatómica o científica grande al centro con notas sepia alrededor; título cursivo azul en el tercio superior, un poco inclinado; autores y fecha en cursiva sepia abajo a la derecha (p. ej. "Anno MMXXVI"); dos pliegues, salpicaduras, una huella en la esquina |
| Break | Lámina completa a mano: achurado denso, punteado, flechas al margen **sin rótulos**; sin título; opcional "fig. V" en sepia en una esquina; clip **idle** |
| N-1 | Una frase declarativa grande en cursiva azul, la frase o cifra clave rodeada con lavado; opcional una nota sepia con flecha; sin ilustración: la letra es la ilustración |
| N | "REFERENCES" en cursiva arriba; APA completa como bibliografía copiada a mano, interlineado algo irregular, tinta sepia; un lavado sobre el autor o paper clave |

**Revisión del frame final:** cursiva a mano, diagramas a tinta, notas sepia, huellas/salpicaduras/pliegues presentes; paleta pergamino `#E8D9B5`–`#D4C29A` + `#1C3D7A` + `#5C3A1E` + lavado `#E8C547`; cero negro.

---

### Estilo 3 · `minimalista_linea` — Minimalista Línea Azul

Validado por Cris en producción (sep 2026). Sustituyó al viejo `minimalista_gradient`: **los degradados salieron del fondo y viven solo dentro de los gráficos.** Sus firmas son el dibujo monolínea azul sin relleno para toda estructura y los gráficos densos con cifras reales.

#### Especificación original (literal, tal como estaba en `cowork-notebooklm-slides` v3.9; `[N]`, `[BREAK]`, `[N-1]`, `[AUTORES]`, `[FECHA]` y las referencias a «PDF Section DIAPOSITIVA N» son marcadores de ese pipeline: aquí equivalen a N, `BREAKS`, la slide de cierre, los datos del paper y el contrato de F1)

```
1. MASTER VISUAL SYSTEM

Contemporary editorial minimalism. Calm, precise. 50-65% negative space, ONE focal point, 16:9.

Palette — ONLY TWO BACKGROUNDS, alternating, NEVER a gradient background:
- OFF-WHITE #F7F5F0: default ground, most slides.
- SOLID COBALT #2E5BFF: cover, break, accent slides.
- Text: Deep Indigo #1A2340 on off-white, White on cobalt.
- Inside charts only, fills may run cobalt #2E5BFF > violet #A93DF5, plus orange #FF5B35 for one key word or segment. The gradient lives in the data, never in the canvas.

Typography: geometric sans-serif, Light and Regular ONLY, sentence case, wide tracking. NEVER serif.

2. NO PLAIN TEXT — THE HARDEST RULE

PARAGRAPHS AND PROSE ARE FORBIDDEN: a block of sentences beside a picture is a FAILED slide. Turn each PDF section into a GRAPHIC — a table, bars, a donut, a pie, a labelled diagram or a flow of nodes. Words appear ONLY as labels, figures and captions of 8 words or fewer. Max 25 words per slide. With no numbers, turn the concepts into a labelled diagram.

3. DATA VISUALIZATION — DENSE, NEVER DECORATIVE

A graphic with two labels and no numbers is also a FAILED slide. Every graphic MUST carry its section's real values: at least 4 labelled data points, segments or rows, each with its figure and unit. Axes get ticks and units, and a second series when a comparison is possible. Show the data, never illustrate the idea of data.
DONUTS AND RINGS lead most data slides: 4 to 6 segments, each with its percentage, one key number giant in the centre.
PIE CHARTS: max 5 segments, values outside.
TABLES: minimum 4 columns and 4 rows of real values, no vertical rules, hairline horizontals, units in the header.
BARS when not circular: 5 to 8 slim bars, gradient-filled, values at the end, no grid lines.
LAYER EVERY GRAPHIC so it rewards a second look: a hero number with its breakdown beside it, a reference line labelled with its value, minor ticks, a legend, ONE arrow annotation reading the key finding in 6 words.
Comparing conditions, use SMALL MULTIPLES: 3 or 4 miniatures of the same chart side by side.
Close every graphic with a tiny footnote: n and source.
Density reference: Fragapane, Lupi, Scientific American graphics.

4. TWO ILLUSTRATION LANGUAGES ON THE SAME SLIDE

A) BLUE LINE DRAWING — for every structure, mechanism, building, cell, organ, molecule, board or device. THIS IS THE DECK'S SIGNATURE: an extremely detailed monoline sketch in cobalt #2E5BFF, uniform hairline weight, COMPLETELY UNFILLED so the ground shows through every shape. Build texture only by repeating lines — seats, membranes, grids, ribs, contours — never by shading with solid colour. Isometric or cross-section, exploded when it clarifies, every part labelled with a thin leader. It must read like a meticulous blue ballpoint pen study, patient and precise, not an icon. Add a scale bar and ONE magnified callout: a circle enlarging one region, joined by a thin line.
Line reference: Vincent Mahé, Jing Zhang, Peter Grundy, blueprints and patent drawings.

B) CORPORATE MEMPHIS FIGURES — humans are ALWAYS flat vector, filled with two or three flat tones, never line art. Geometric limbs, oversized hands, mid-action poses, with FACES: eyes, brows, a mouth. Two to four figures at generous scale, physically interacting with the line drawing or the chart: climbing, measuring, pointing, holding it.
Figure reference: Alegria by Buck, Slack and Duolingo, Owen Davey, Ana Hard, Magoz.

The structure is the protagonist, the figures give it scale. NEVER shrink it to fit the people, NEVER draw people as outlines.

REAL BRANDS: when a section names a real company or product — Nvidia, Apple, Google — its LOGO MUST APPEAR on that slide. Never omit it, never swap it for a generic icon. Redraw it in the deck's own language: the exact official shape and proportions, traced as an unfilled cobalt monoline like every other structure, at LARGE scale beside its data. Compared brands are drawn the same size, aligned in a row. Keep the shape faithful, never invent a mark.

5. STRUCTURE — [N] SLIDES

Take each slide's data, graphic and illustration from its "DIAPOSITIVA N" section.
SLIDE 1, COVER — THE MOST STRIKING IMAGE OF THE DECK: solid cobalt, ONE enormous illustration filling the canvas: a giant line object metaphorising the subject, with Memphis figures at large scale. Title upper-left, and below it: [AUTORES] | [FECHA].
SLIDE [BREAK] — THE ONLY VISUAL BREAK: solid cobalt, ONE giant line drawing of the deck's central object in white line. ZERO text, ZERO chart. No other break.
THE DECK MUST ALWAYS END WITH BOTH CLOSING SLIDES, never truncated, never merged:
SLIDE [N-1]: off-white, one declarative sentence in giant Light type, one key word in orange #FF5B35.
SLIDE [N]: off-white, "Referencias" small top-left, then the COMPLETE APA list of every source in 3 or 4 columns, set VERY SMALL, smaller than any other text in the deck, with authors, year, title, journal, volume and pages. All on this one slide.
```

**Fondo (sustrato):** un campo plano, off-white `#F7F5F0` o cobalto `#2E5BFF`, con su tono exacto; sin degradado, textura, viñeteo ni ornamento.

> Bloque PRESERVE original (literal): *"PRESERVE ONLY: the flat background field exactly as it is — either Off-white #F7F5F0 or Solid Cobalt #2E5BFF, whichever the input uses — with its exact hue and saturation. Remove EVERY foreground element: all typography, all cobalt monoline drawings and their labels, leaders, scale bars and callouts, all corporate Memphis figures, all charts, tables and their gradient fills, the orange accent and the footnote. The result is one clean, empty flat field. Do NOT introduce a gradient, a texture, a vignette or any ornament. Do NOT shift hue, do NOT desaturate."*

**Historia del estilo (errores ya pagados, no repetir):**

| Iteración | Qué falló | Corrección que quedó |
|---|---|---|
| v1 | Párrafos de 8 líneas junto al dibujo | Bloque 2 completo, con criterio de fallo |
| v2 | Gráficos con dos etiquetas y ningún número | Mínimos duros: 4 puntos, 4 filas, ejes con unidades |
| v3 | Gráficos correctos pero planos | Capas: línea de referencia, ticks menores, leyenda, flecha de hallazgo, gráficos pequeños comparados |
| v4 | Humanos donde tocaba la estructura | Jerarquía: la estructura es protagonista |
| v5 | Portada sosa | Portada = la imagen más impactante del deck |
| v6 | Marcas nombradas omitidas | Bloque REAL BRANDS |

#### En código

| Regla | Cómo se cumple |
|---|---|
| Solo dos fondos planos que alternan; nunca degradado de fondo | `#stage` (off-white) y `#stage.alt` (cobalto: portada, break, acentos). Sin textura |
| Texto índigo `#1A2340` sobre off-white, blanco sobre cobalto | Tokens `--ink` / `--ink-alt` |
| Degradado cobalto → violeta **solo dentro de los gráficos**; naranja `#FF5B35` para UNA palabra o segmento | `--c1..c4` en rellenos de barras y sectores; `--accent` una vez por slide |
| Sans geométrica Light/Regular, sentence case, tracking amplio; nunca serif | Jost 300/400 |
| **Sin prosa**: solo rótulos, cifras y pies de ≤ 8 palabras; máximo 25 palabras por slide | Contrato de F1 + conteo en la revisión de F4 |
| Cada gráfico con ≥ 4 datos rotulados con cifra y unidad; ejes con ticks y unidades; segunda serie si hay comparación | RC-6: las cifras salen de la fuente y se verifican en el código con `throw` |
| Donas y anillos lideran: 4-6 segmentos con %, un número gigante al centro | `ring` + `count` en el centro |
| Pastel ≤ 5 segmentos con valores afuera | `ring` + `rotulo` |
| Tablas ≥ 4 columnas × 4 filas, sin reglas verticales, horizontales finas, unidades en el encabezado | Filas que entran con `wipeIn` o `type` |
| Barras: 5-8 delgadas, con degradado, valor al final, sin cuadrícula | `grow` + `ride` |
| Capas: número héroe con su desglose, línea de referencia rotulada, ticks menores, leyenda, **UNA flecha con el hallazgo en 6 palabras** | El campo `HALLAZGO` del contrato es esa flecha (`draw` + `type`) |
| Comparar condiciones con 3-4 gráficos pequeños iguales lado a lado | Mismo módulo de gráfico instanciado 3-4 veces |
| Pie de figura diminuto con n y fuente | `.t-caption` (piso 21 px) |
| **Dibujo monolínea cobalto, trazo fino uniforme, TOTALMENTE sin relleno**; textura solo repitiendo líneas; isométrico o en corte, despiezado si aclara; cada parte con su guía | `.line` (`fill: none`, 1,6 px; `.thin` 1,1 px); se traza con `draw` en el orden de la mano; módulos como `mito.js` |
| Barra de escala + UNA lupa: círculo que amplía una región, unido por una línea fina | Siempre en las slides de estructura |
| Figuras corporate Memphis | **No se usan en slides-codigo**: choca con la regla de Cris «nunca figuras humanas en mis diapositivas». La estructura carga la escala sola (barra de escala, lupa). Solo si Cris las pide explícitamente para un deck |
| Marcas reales nombradas | Se muestran por su **nombre**, en la tipografía del deck y a buen tamaño junto a su dato, todas del mismo tamaño y alineadas. **No se redibujan logotipos** |
| 50-65 % de espacio negativo, UN punto focal | Se mide en el frame final |
| Portada | Cobalto; UN objeto en línea blanca enorme que llena el lienzo como metáfora del tema; título arriba a la izquierda y debajo autores y fecha |
| Break | Cobalto; UN dibujo gigante en línea blanca del objeto central del deck; cero texto, cero gráfico; clip **idle** |
| N-1 | Off-white; una frase declarativa en Light gigante; una palabra en naranja |
| N | Off-white; "References" pequeño arriba a la izquierda; APA completa (autores, año, título, revista, volumen, páginas) en 3-4 columnas, el texto más pequeño del deck pero **sin bajar del piso de 16 px** (`.t-refs`); todo en esa slide |

**Revisión del frame final:** títulos sans Light, fondo plano sin corrimiento, monolínea íntegra (no engrosada ni rellenada), gráficos legibles con sus cifras y pie; paleta `#F7F5F0` o `#2E5BFF` planos, degradado solo dentro de gráficos.

---

### Tokens de cada estilo (`engine/styles/*.css`)

Cada CSS fija `--bg`, `--bg-alt`, `--ink`, `--line`, `--accent`, `--c1..c5` y las fuentes. Resumen:

| | `harper_bazaar` | `cuaderno_davinci` | `minimalista_linea` |
|---|---|---|---|
| Fondo | Textura `harper` (amarillo `#CCCC00`, blanco con moiré, splits, mosaico, grano) | Textura `davinci` (pergamino, pliegues, salpicaduras, huellas) | Off-white `#F7F5F0` / cobalto `#2E5BFF`, planos, **nunca degradado** |
| Tipografía | Bodoni Moda Bold MAYÚSCULAS + Inter | Homemade Apple (títulos) + Caveat | Jost Light, sentence case |
| Tinta | Negro `#000` | Azul de Prusia `#1C3D7A` + sepia `#5C3A1E` + lavado `#E8C547` al 40 % | Cobalto `#2E5BFF`, índigo `#1A2340`, naranja `#FF5B35` |
| Ilustración | Silueta negra + halftone + destellos; SVG del banco pasado a negro/halftone | Tinta con achurado y punteado, notas sepia | Monolínea cobalto o blanca **sin relleno**, lupa + barra de escala |
| Datos | Monolitos negros o con trama; constelaciones; joyas Bauhaus | Columnas de tinta achuradas; constelaciones de tinta; rebanadas con patrones | Donas, barras con degradado cobalto→violeta solo dentro del gráfico |
| Espacio negativo | 30-50 %, asimétrico | 25-40 %, denso y orgánico | 50-65 %, un punto focal |
