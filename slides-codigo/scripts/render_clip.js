#!/usr/bin/env node
// render_clip.js — renderiza UNA slide (HTML) a un MP4 mudo de 2560×1440,
// cuadro a cuadro: salta a cada instante de la línea de tiempo y fotografía.
//
//   node render_clip.js slide_01.html <salida_dir> [--fps 30] [--name 01] [--force]
//
// Escribe: <salida>/<name>.mp4 · <name>_first.png (frame inicial) · <name>_last.png (frame final)
// y <name>.json (duración de la animación, verbo de apertura, lint).
// Aborta si el HTML tiene errores o si el lint de «nada solo aparece» no está limpio
// (salvo --force, que se declara en el reporte).
const fs = require("fs");
const path = require("path");
const { spawn } = require("child_process");
const { chromium } = require("playwright");

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const html = path.resolve(args[0]);
const outDir = path.resolve(args[1] || ".");
const fps = +opt("--fps", 30);
const name = opt("--name", path.basename(html, ".html").replace(/^slide_?/, ""));
const force = args.includes("--force");
const CHROME = ["/usr/bin/google-chrome", "/usr/bin/chromium", "/usr/bin/chromium-browser"].find((p) => fs.existsSync(p));

(async () => {
  fs.mkdirSync(outDir, { recursive: true });
  const browser = await chromium.launch({ executablePath: CHROME, args: ["--font-render-hinting=none", "--allow-file-access-from-files"] });
  const ctx = await browser.newContext({ viewport: { width: 1280, height: 720 }, deviceScaleFactor: 2 });
  const page = await ctx.newPage();
  const logs = [];
  page.on("console", (m) => logs.push(`${m.type()}: ${m.text()}`));
  page.on("pageerror", (e) => logs.push(`pageerror: ${e.message}`));
  await page.goto("file://" + html);
  await page.waitForFunction(() => window.SC_READY === true, null, { timeout: 60000 });
  const info = await page.evaluate(() => ({ err: window.SC_ERROR || null, lint: window.SC_LINT || [], open: window.SC_OPEN, anim: SC.tl.duration(), DUR: SC.DUR }));
  const errs = logs.filter((l) => /error/i.test(l));
  if (info.err || errs.length) { console.error("ERROR en el HTML:\n" + (info.err || "") + "\n" + errs.join("\n")); await browser.close(); process.exit(1); }
  if (info.lint.length && !force) { console.error("LINT (corrige o usa --force):\n- " + info.lint.join("\n- ")); await browser.close(); process.exit(2); }

  const N = Math.round(info.DUR * fps);
  const mp4 = path.join(outDir, `${name}.mp4`);
  const ff = spawn("ffmpeg", ["-v", "error", "-y", "-f", "image2pipe", "-framerate", String(fps), "-c:v", "png", "-i", "-",
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "16", "-pix_fmt", "yuv420p", "-profile:v", "high",
    "-an", "-movflags", "+faststart", mp4], { stdio: ["pipe", "inherit", "inherit"] });
  const write = (buf) => new Promise((res) => (ff.stdin.write(buf) ? res() : ff.stdin.once("drain", res)));
  const t0 = Date.now();
  for (let f = 0; f < N; f++) {
    await page.evaluate((t) => SC.seek(t), f / fps);
    const png = await page.screenshot({ type: "png" });
    if (f === 0) fs.writeFileSync(path.join(outDir, `${name}_first.png`), png);
    if (f === N - 1) fs.writeFileSync(path.join(outDir, `${name}_last.png`), png);
    await write(png);
  }
  ff.stdin.end();
  await new Promise((res, rej) => ff.on("close", (c) => (c === 0 ? res() : rej(new Error("ffmpeg " + c)))));
  await browser.close();
  const rep = { name, mp4, frames: N, fps, duration: info.DUR, animation_ends: +info.anim.toFixed(2), open_verb: info.open, lint: info.lint, forced: force && info.lint.length > 0, render_s: Math.round((Date.now() - t0) / 1000) };
  fs.writeFileSync(path.join(outDir, `${name}.json`), JSON.stringify(rep, null, 2));
  console.log(`OK ${name}: ${N} cuadros · animación termina en ${rep.animation_ends}s · abre con ${rep.open_verb} · ${rep.render_s}s de render`);
})().catch((e) => { console.error(e); process.exit(1); });
