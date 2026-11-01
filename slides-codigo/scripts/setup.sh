#!/usr/bin/env bash
# setup.sh — preflight F0. Verifica el entorno; instala solo lo que falte.
set -u
ok=1
for b in ffmpeg ffprobe google-chrome; do command -v $b >/dev/null || { echo "FALTA $b"; ok=0; }; done
export NODE_PATH="$(npm root -g)"
node -e "require('playwright')" 2>/dev/null || { echo "FALTA playwright (npm i -g playwright; NO correr 'playwright install')"; ok=0; }
node -e "require('pptxgenjs')" 2>/dev/null || npm i -g pptxgenjs >/dev/null 2>&1 || { echo "FALTA pptxgenjs"; ok=0; }
node -e "require('sharp')" 2>/dev/null || npm i -g sharp >/dev/null 2>&1 || { echo "FALTA sharp"; ok=0; }
python3 -c "import lxml, PIL, numpy" 2>/dev/null || pip install --break-system-packages -q lxml pillow numpy
D="$(cd "$(dirname "$0")/../engine/vendor" && pwd)"
# MathJax (2 MB) no viaja dentro de la skill: se baja solo si el deck tiene ecuaciones (--tex)
if [ "${1:-}" = "--tex" ] && [ ! -f "$D/tex-svg.js" ]; then
  T=$(mktemp -d) && (cd "$T" && npm init -y >/dev/null && npm i mathjax@3 >/dev/null 2>&1) && cp "$T/node_modules/mathjax/es5/tex-svg.js" "$D/" && echo "MathJax instalado"
fi
[ $ok = 1 ] && echo "F0 OK" || { echo "F0 con faltantes"; exit 1; }
