#!/usr/bin/env bash
# render_all.sh — renderiza todas las slide_NN.html de una carpeta de construcción
# a clips (2 en paralelo: el contenedor tiene 2 núcleos) y arma el PPTX final.
#
#   bash render_all.sh <carpeta_build> <salida.pptx> "<Título del deck>"
#
# La carpeta de construcción tiene las slide_NN.html, los .js propios del deck
# y un enlace «engine» al motor de la skill (lo crea este script si falta).
set -euo pipefail
SKILL="$(cd "$(dirname "$0")/.." && pwd)"
B="$(cd "$1" && pwd)"; OUT="$2"; TITLE="${3:-Deck}"
export NODE_PATH="$(npm root -g)"
[ -e "$B/engine" ] || ln -s "$SKILL/engine" "$B/engine"
[ -e "$B/ax.js" ] || ln -s "$SKILL/lib/ax.js" "$B/ax.js"     # piezas Harper y SVG del banco (lib/ax.js)
mkdir -p "$B/clips"
cd "$B"
ls slide_*.html | sort | xargs -P 2 -I{} sh -c 'node "'"$SKILL"'/scripts/render_clip.js" "{}" clips || echo "FALLÓ {}" >> clips/_fallos.txt'
if [ -s clips/_fallos.txt ]; then cat clips/_fallos.txt; rm -f clips/_fallos.txt; exit 1; fi
node "$SKILL/scripts/build_pptx.js" clips "$B/_raw.pptx" --title "$TITLE"
python3 "$SKILL/scripts/inject_media.py" "$B/_raw.pptx" -o "$OUT"
rm -f "$B/_raw.pptx"
V=/mnt/skills/public/pptx/scripts/office/validate.py
[ -f "$V" ] && python3 "$V" "$OUT" || echo "(validate.py de la skill pptx no disponible: se omite)"
