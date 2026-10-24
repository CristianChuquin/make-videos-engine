# make-videos-engine

Motores y librerías para hacer **videos explicativos con código**: animación en Manim (estilo «Cosmos»), voz narrada y una sincronía donde **la voz manda y el video se adapta**.

Lo creó Cristian Chuquín para su pipeline de videos académicos (matemática, física y biología). Es público para que cualquiera pueda usarlo y adaptarlo.

## Qué hay

| Carpeta | Qué es |
|---|---|
| `cosmos/estilo.py` | Estilo «Cosmos» para Manim CE: fondo estelar vivo, paleta semántica, tipografía cinética tipo After Effects (`rise`, `stamp`, `wipe_in`, `typewriter`, `counter`…), ecuaciones LaTeX enfocables, planetas que rotan, codo anatómico, sólidos de revolución, Riemann y simulaciones de referencia (`Proyector` pseudo-3D, `Rubik` como permutación real, `Pendulos`, `onda_muestreada`, `fasores`). |
| `cosmos/svgbank.py` | Busca ilustraciones como **código** (SVG/TikZ) en bancos libres (tikz.net, Iconify, Openverse/Wikimedia, bancos de biología) para animarlas por piezas. Lleva los créditos y filtra licencias (nunca NC ni ND). |
| `cosmos/demo_sim.py` | Reel de prueba de ~1 min: cubo de Rubik (R U = 105), grafo de estados, banco de péndulos y aliasing. Sirve de plantilla. |
| `shared/master.py` | Une las pistas de voz, recorta pausas largas y normaliza a −16 LUFS. Se detiene si queda algún silencio de más de 1 s. |
| `shared/transcribe.py` | Transcripción con marcas por palabra (faster-whisper). |
| `shared/sync.py` | Re-cronometra cada tramo del video mudo entre anclas para que dure exactamente lo que su tramo de voz (cámara lenta ≤ ×3, aceleración ≤ ×2). |

Los comentarios del código están en español.

## Requisitos

```bash
apt-get install -y dvisvgm libpango1.0-dev libcairo2-dev pkg-config texlive-latex-extra ffmpeg
pip install manim soundfile numpy faster-whisper cairosvg
```

Fuentes (Google Fonts): **Unbounded**, **Space Grotesk** y **JetBrains Mono**.

## Uso rápido

```bash
git clone https://github.com/CristianChuquin/make-videos-engine.git
cd make-videos-engine/cosmos
MV_FAST=1 manim -ql demo_sim.py E01Cubo      # borrador rápido
manim -qh demo_sim.py E01Cubo                # 1080p30
```

En tu propio `video.py`:

```python
from estilo import *
from svgbank import *

class E01(Scene):
    def construct(self):
        fondo(self)                    # siempre primero
        t = T("Hello", 72); self.play(rise(t))
        self.wait(1)
        exit_all(self)                 # siempre al final
```

Flujo de voz y sincronía (desde la carpeta de trabajo, con `A.wav`, `B.wav`… a 48 kHz):

```bash
python3 ../shared/master.py A B C          # → master.wav
python3 ../shared/transcribe.py master     # → words_master.json
python3 ../shared/sync.py cfg.json         # → video final sincronizado
```

`cfg.json` lleva el video mudo, su duración, el audio, las palabras y la lista de anclas `[frase, segundo del video mudo]`.

## Licencia

Código bajo licencia MIT (ver `LICENSE`). Las ilustraciones que baja `svgbank.py` conservan la licencia de su banco de origen y se acreditan en cada video.
