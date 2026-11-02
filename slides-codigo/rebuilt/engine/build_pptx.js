// clips/NN.mp4 → un PPTX, una slide por clip. Fondo y portada = primer frame (JPG).
// uso: node build_pptx.js clips out.pptx "Título"
const pptxgen = require("pptxgenjs");
const fs = require("fs"), path = require("path");
const [dir, out, title] = process.argv.slice(2);
const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE";            // 13.333 × 7.5 in
pres.title = title || "Slides";
const ids = fs.readdirSync(dir).filter((f) => /^\d+\.mp4$/.test(f)).sort();
for (const f of ids) {
  const id = f.replace(".mp4", "");
  const coverPath = path.join(dir, `${id}_first.jpg`);
  const cover = "data:image/jpeg;base64," + fs.readFileSync(coverPath).toString("base64");
  const s = pres.addSlide();
  s.background = { path: coverPath };
  s.addMedia({ type: "video", path: path.join(dir, f), cover, x: 0, y: 0, w: 13.333, h: 7.5 });
}
pres.writeFile({ fileName: out }).then(() => console.log("pptx", out, ids.length, "slides"));
