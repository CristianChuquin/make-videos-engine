// sheet.js — hoja de candidatos numerada (SVG del banco tal cual) para elegir mirando
const fs = require("fs"), { chromium } = require("playwright");
const files = process.argv.slice(3), out = process.argv[2];
(async () => {
  const cells = files.map((f, i) => `<div class=c><div class=n>${i} · ${f.split("/").pop().slice(0, -4)}</div><img src="file://${f}"></div>`).join("");
  const html = `<html><body style="margin:0;background:#fff;font:13px Arial;display:grid;grid-template-columns:repeat(5,250px);gap:6px;padding:6px">
  <style>.c{border:1px solid #ccc;height:210px;display:flex;flex-direction:column}.n{padding:2px 4px;background:#eee}img{flex:1;min-height:0;object-fit:contain;padding:6px}</style>${cells}</body></html>`;
  const tmp = require("os").tmpdir() + "/sheet.html"; fs.writeFileSync(tmp, html);
  const b = await chromium.launch({ executablePath: "/usr/bin/google-chrome", args: ["--allow-file-access-from-files"] });
  const p = await (await b.newContext({ viewport: { width: 1286, height: 300 } })).newPage();
  await p.goto("file://" + tmp); await p.waitForTimeout(800);
  await p.screenshot({ path: out, fullPage: true }); await b.close(); console.log(out);
})();
