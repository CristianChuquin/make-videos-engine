// HTML → MP4 cuadro a cuadro (2560×1440, 30 fps, 12 s, mudo) + first/last + reporte
// uso: node render_clip.js slide_NN.html outdir [--force]
const { chromium } = require("playwright");
const { spawn } = require("child_process");
const fs = require("fs"), path = require("path");
const FPS = 30, DUR = 12, N = FPS * DUR;

(async () => {
  const [html, out = "clips"] = process.argv.slice(2);
  const force = process.argv.includes("--force");
  const id = path.basename(html).match(/(\d+)/)[1];
  fs.mkdirSync(out, { recursive: true });
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 2 });
  const errs = [];
  page.on("pageerror", (e) => errs.push(String(e)));
  await page.goto("file://" + path.resolve(html));
  try { await page.waitForFunction(() => window.SC_READY === true, null, { timeout: 20000 }); }
  catch (e) { console.error(id, "NO CARGA", errs.join(" | ")); process.exit(2); }
  const info = await page.evaluate(() => window.SC_INFO);
  info.errors = errs;
  const isBreak = await page.evaluate(() => document.body.dataset.break === "1");
  const problems = [];
  if (info.lint.length) problems.push("aparece sin verbo: " + info.lint.join("; "));
  if (!isBreak && info.animation_ends > 11) problems.push(`la animación termina en ${info.animation_ends} s`);
  if (errs.length) problems.push("errores JS: " + errs.join(" | "));
  if (problems.length && !force) { console.error(id, "BLOQUEADO →", problems.join(" || ")); await browser.close(); process.exit(3); }
  info.forced = problems.length ? problems : undefined;
  if (process.argv.includes("--peek")) {           // revisión rápida: 6 instantes + último
    for (const T of [1, 2.5, 4, 5.5, 7, 9, 11.99]) {
      await page.evaluate((T) => SC.seek(T), T);
      await page.screenshot({ path: path.join(out, `${id}_t${String(T).replace(".", "_")}.jpg`), type: "jpeg", quality: 80 });
    }
    console.log(id, "PEEK", JSON.stringify({ ends: info.animation_ends, open: info.open_verb, lint: info.lint.length, problems }));
    await browser.close(); return;
  }

  const mp4 = path.join(out, `${id}.mp4`);
  const ff = spawn("ffmpeg", ["-y", "-loglevel", "error", "-f", "image2pipe", "-framerate", String(FPS), "-c:v", "mjpeg", "-i", "-",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-profile:v", "high", "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an", mp4],
    { stdio: ["pipe", "inherit", "inherit"] });
  const t0 = Date.now();
  for (let f = 0; f < N; f++) {
    await page.evaluate((T) => SC.seek(T), f / FPS);
    const buf = await page.screenshot({ type: "jpeg", quality: 95 });
    if (f === 0) fs.writeFileSync(path.join(out, `${id}_first.jpg`), buf);
    if (f === N - 1) fs.writeFileSync(path.join(out, `${id}_last.jpg`), buf);
    if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once("drain", r));
  }
  ff.stdin.end();
  await new Promise((r) => ff.on("close", r));
  info.render_s = Math.round((Date.now() - t0) / 1000);
  fs.writeFileSync(path.join(out, `${id}.json`), JSON.stringify(info, null, 1));
  console.log(id, "OK", JSON.stringify({ ends: info.animation_ends, open: info.open_verb, s: info.render_s }));
  await browser.close();
})();
