# slides-codigo

Diapositivas vivas hechas con código. Cada slide es un clip de **12 s a 2560×1440**, sin audio, montado a pantalla completa en un PPTX. El clip arranca solo al entrar a la slide, se congela en su último frame (la slide terminada) y espera el clic para avanzar. Así no parece un video: parece la diapositiva animándose.

Motor de la skill `slides-codigo`. Animación en HTML/SVG con GSAP; renderizado frame a frame con Playwright y ffmpeg.

## Qué hay

| Carpeta | Qué es |
|---|---|
| `engine/runtime.js` | Motor `SC`: una línea de tiempo GSAP en pausa y los verbos de animación (`draw`, `type`, `rise`, `stamp`, `wipeIn`, `marker`, `count`, `grow`, `ride`, `pop`…). El lint («nada solo aparece») exige que todo entre con un verbo y que la animación termine en ≤ 11 s. |
| `engine/styles/` | `base.css` y los 3 estilos: `harper_bazaar.css` (1), `cuaderno_davinci.css` (2), `minimalista_linea.css` (3). |
| `engine/fonts/`, `engine/vendor/` | Fuentes (OFL) y GSAP 3 con DrawSVG, SplitText y MorphSVG. |
| `scripts/setup.sh` | Preflight: comprueba ffmpeg, Chrome y Playwright e instala pptxgenjs, sharp, lxml, pillow y numpy si faltan. |
| `scripts/render_clip.js` | Pasa de HTML a MP4 (h264, CRF 16, 30 fps, deviceScaleFactor 2) y escribe `NN_first.png`, `NN_last.png` y `NN.json`. |
| `scripts/render_all.sh` | Renderiza todas las slides de una carpeta. |
| `scripts/textures.py` | Fondos con textura (amarillo, blanco, divididos, grano) para el estilo Harper. |
| `scripts/build_pptx.js` | Arma el PPTX: un clip por slide; el fondo y la portada son el primer frame en JPG. |
| `scripts/inject_media.py` | Añade la reproducción automática y la congelación en el último frame (`p:timing`). |
| `lib/bank.py` | Busca ilustraciones en Bioicons (y Reactome). La primera vez clona Bioicons en `~/.mv_cache/bancos`. Solo licencias sin NC. |
| `lib/prep.py` | `harper()`: pasa un SVG del banco al lenguaje Harper (negro, tramas halftone y contorno que se traza al animar). |
| `lib/ax.js` | `AX`: esferas halftone, hélices, destellos, redes ramificadas, `bank()` para montar un SVG del banco y `build()` para animarlo pieza por pieza. |
| `lib/sheet.js` | Hoja de candidatos numerada para elegir SVG mirando. |
| `examples/` | `demo-mitocondria` (estilo 3, 5 slides) y `actin-filaments` (estilo 1, 12 slides, generador `gen.py`). |

## Uso

```bash
git clone --depth 1 https://github.com/CristianChuquin/make-videos-engine.git
E=make-videos-engine/slides-codigo
bash $E/scripts/setup.sh

mkdir build
# escribir build/slide_01.html … slide_NN.html (o generarlas, como examples/actin-filaments/gen.py)
bash $E/scripts/render_all.sh build "Deck.pptx" "Título del deck"
# → build/clips/NN.mp4 + NN_first.png y Deck.pptx (crea los enlaces engine/ y ax.js si faltan)
```

El renderizado de 12 clips a 2K tarda entre 20 y 40 minutos.

## Créditos

GSAP © GreenSock (licencia estándar sin costo). Ilustraciones de los ejemplos: Servier Medical Art (CC BY 3.0) vía Bioicons; el crédito va en la slide de referencias de cada deck.
