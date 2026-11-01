#!/usr/bin/env node
// build_pptx.js — monta un clip por diapositiva, a pantalla completa, para que el
// video NO parezca video: el fondo de la slide y la portada del video son el
// primer frame del clip (sin salto al entrar), y el clip se congela en su último
// frame (la slide terminada) hasta que Cris avanza.
//
//   node build_pptx.js <clips_dir> <salida.pptx> [--title "Título del deck"]
//
// Toma <clips_dir>/NN.mp4 + NN_first.png en orden numérico. Después hay que
// correr inject_media.py, que añade la reproducción automática (pptxgenjs no la escribe).
const fs = require("fs");
const path = require("path");
const pptxgen = require("pptxgenjs");
const sharp = require("sharp");

const [dir, out] = process.argv.slice(2);
const ti = process.argv.indexOf("--title");
const title = ti > 0 ? process.argv[ti + 1] : "Deck";
if (!dir || !out) { console.error("uso: node build_pptx.js <clips_dir> <salida.pptx> [--title T]"); process.exit(1); }

const clips = fs.readdirSync(dir).filter((f) => /^\d{2}\.mp4$/.test(f)).sort();
if (!clips.length) { console.error("no hay NN.mp4 en " + dir); process.exit(1); }

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";          // 13.333" × 7.5" = 16:9, igual que los clips de 2560×1440
pres.title = title;
(async () => {
for (const c of clips) {
  const n = c.slice(0, 2);
  const png = path.join(dir, `${n}_first.png`);
  if (!fs.existsSync(png)) { console.error(`falta ${n}_first.png`); process.exit(1); }
  // JPG q92: un PNG de 2560×1440 con grano pesa ~4 MB; el JPG ~0,5 MB y no se distingue. Una sola imagen para fondo y portada.
  const first = path.join(dir, `${n}_first.jpg`);
  await sharp(png).jpeg({ quality: 92, chromaSubsampling: "4:4:4" }).toFile(first);
  const s = pres.addSlide();
  s.background = { path: first };     // la slide ya «es» el primer frame antes de que el video cargue
  s.addMedia({
    type: "video", path: path.join(dir, c), x: 0, y: 0, w: 13.333, h: 7.5,
    cover: "data:image/jpeg;base64," + fs.readFileSync(first).toString("base64"),
    objectName: `clip_${n}`,
  });
}
await pres.writeFile({ fileName: out });
console.log(`OK → ${out} (${clips.length} slides)`);
})();
