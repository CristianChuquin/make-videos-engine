#!/usr/bin/env python3
"""gen.py — escribe slide_01..12.html del deck de actina (estilo Harper's Bazaar)."""
import os, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "lib"))   # slides-codigo/lib
from prep import harper
OUT = Path(os.environ.get("OUT", "."))               # carpeta de build (con enlaces engine/ y ax.js)
BANKS = {k: os.path.expanduser(v) for k, v in (l.split("|")[:2] for l in (HERE / "banks.txt").read_text().split("\n") if l)}
BANKW = {}  # slide -> [(nombre, ancho_px)]

HEAD = """<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<link rel="stylesheet" href="engine/styles/base.css">
<link rel="stylesheet" href="engine/styles/harper_bazaar.css">
<link rel="stylesheet" href="deck.css">
<script src="engine/vendor/gsap.min.js"></script>
<script src="engine/vendor/DrawSVGPlugin.min.js"></script>
<script src="engine/vendor/SplitText.min.js"></script>
<script src="engine/runtime.js"></script>
<script src="ax.js"></script>
</head><body>
<div id="stage"><div class="bg-tex frame-a" style="background-image:url(bg_NN.png)"></div>
"""
TAIL = """</div>
<script>
AX.defs();
const $ = (id) => document.getElementById(id);
SCRIPT
</script>
</body></html>
"""

S = {}

# ───────────────────────── 01 · PORTADA (amarillo)
S[1] = ("""
<svg id="sp" class="abs" style="left:0;top:0" width="1280" height="720"></svg>
<div id="t1" class="abs d" style="left:58px;top:44px;font-size:212px">Actin</div>
<div id="t2" class="abs d" style="left:66px;top:248px;font-size:86px">Filaments</div>
<div id="sub" class="abs lab" style="left:70px;top:356px;width:560px">Assembly, protrusion and contraction</div>
<div id="by" class="abs cap" style="left:760px;top:52px;width:420px;text-align:right">Cristian Chuquin · Cell Biology<br>Yachay Tech · November 2026</div>
<div id="spine" class="abs k" style="left:1226px;top:72px;writing-mode:vertical-rl">Rottner 2017 · Svitkina 2018</div>
""", r"""
const a = AX.bank("tpl-actin", { x: 30, y: 420, w: 1180, rot: -7 });       // F-actina de Servier, en Harper
// destellos sobre el filamento (eje inclinado -7° por el centro del dibujo)
const cx = 620, cy = 420 + 1180 * 69.052 / 460.12 / 2;
[[230, 46], [470, 34], [760, 46], [1010, 34]].forEach(([x, s]) => AX.sparkle($("sp"), x, cy - (x - cx) * Math.tan(7 * Math.PI / 180) - 8, s));
SC.build((S) => {
  AX.build(S, a.pieces, 0.0, 3.0);                             // se construye pieza a pieza, de lo grande a lo pequeño
  S.pop(".spk", 3.1, { stagger: 0.18, dur: 0.5 });
  S.rise("#t1", 3.6, { stagger: 0.08 });
  S.tracking("#t2", 4.6, { dur: 1.0 });
  S.type("#sub", 5.7, { letter: 0.03 });
  S.type("#by", 7.0, { letter: 0.022 });
  S.drop("#spine", 8.4, { stagger: 0.022, dur: 0.6 });
});
""")
BANKW[1] = [("actin", 1180)]

# ───────────────────────── 02 · LAMELLIPODIA vs FILOPODIA (split vertical)
S[2] = ("""
<svg id="net" class="abs" style="left:0;top:0" width="1280" height="720">
  <path id="mem1" d="M86 176 Q330 140 584 176" fill="none" stroke="#000" stroke-width="7" stroke-linecap="round"/>
  <g id="lam"></g>
  <path id="base" d="M690 452 H800 M1006 452 H1030" fill="none" stroke="#000" stroke-width="7" stroke-linecap="round"/>
  <path id="fing" d="M800 452 C830 330 870 222 885 178 A18 18 0 0 1 921 178 C936 222 976 330 1006 452" fill="none" stroke="#000" stroke-width="7" stroke-linejoin="round"/>
  <g id="bund"></g><g id="fas"></g>
  <g id="tip"><circle cx="896" cy="186" r="5" fill="#000"/><circle cx="910" cy="186" r="5" fill="#000"/><circle cx="903" cy="176" r="5" fill="#000"/></g>
</svg>
<div id="tl" class="abs d" style="left:64px;top:40px;font-size:64px">Lamellipodia</div>
<div id="tr" class="abs d" style="left:704px;top:40px;font-size:64px">Filopodia</div>
<div id="n1" class="abs d nu" style="left:1046px;top:170px;font-size:58px">≤10</div>
<div id="n1u" class="abs" style="left:1158px;top:186px;font:500 34px Inter,sans-serif">µm</div>
<div id="n1c" class="abs k" style="left:1050px;top:236px">length</div>
<div id="n2" class="abs d" style="left:1046px;top:300px;font-size:40px;width:220px">A few dozen</div>
<div id="n2c" class="abs cap" style="left:1050px;top:388px;width:210px">parallel filaments</div>
<div id="l1" class="abs k" style="left:64px;top:488px">Branched network</div>
<div id="l2" class="abs lab" style="left:64px;top:528px">Arp2/3 complex</div>
<div id="l3" class="abs lab" style="left:64px;top:570px">Activated by Rac</div>
<div id="r1" class="abs k" style="left:704px;top:488px">Parallel bundle</div>
<div id="r2" class="abs lab" style="left:704px;top:528px">Formins · Ena/VASP · fascin</div>
<div id="r3" class="abs lab" style="left:704px;top:570px">Activated by Cdc42</div>
<div id="foot" class="abs cap" style="left:1010px;top:670px">Rottner et al., 2017</div>
""", r"""
const net = AX.branched($("lam"), { x0: 130, x1: 540, yBase: 440, yTop: 178, n: 7, seed: 5, w: 3.2 });
// haz paralelo: 9 filamentos del ancho de la base al de la punta
for (let i = 0; i < 9; i++) {
  const f = i / 8, xb = 846 + f * 114, xt = 893 + f * 20;
  AX.el($("bund"), "path", { d: `M${xb} 440 L${xt} 196`, stroke: "#000", "stroke-width": 2.6, fill: "none" });
}
[262, 322, 384].forEach((y) => {               // entrecruzamientos de fascina
  const t = (440 - y) / 244, xl = 846 + (893 - 846) * t - 4, xr = 960 + (913 - 960) * t + 4;
  AX.el($("fas"), "path", { d: `M${xl} ${y} H${xr}`, stroke: "#000", "stroke-width": 5, fill: "none" });
});
SC.build((S) => {
  S.draw("#mem1", 0.0, { dur: 0.8 });
  S.draw(net.mothers, 0.4, { dur: 0.7, stagger: 0.12 });
  S.draw(net.kids, 1.4, { dur: 0.35, stagger: 0.06 });
  S.draw("#base, #fing", 0.3, { dur: 1.2, stagger: 0.1 });
  S.draw("#bund path", 1.3, { dur: 0.8, stagger: 0.06 });
  S.draw("#fas path", 2.3, { dur: 0.3, stagger: 0.12 });
  S.pop("#tip circle", 2.7, { stagger: 0.08 });
  S.tracking("#tl", 3.0, { dur: 0.9 });
  S.tracking("#tr", 3.3, { dur: 0.9 });
  S.count("#n1", 10, 3.6, { prefix: "≤", dur: 1.0 });
  S.type("#n1u", 4.2, { letter: 0.08 });
  S.type("#n1c", 4.4, { letter: 0.04 });
  S.type("#n2", 4.8, { letter: 0.04 });
  S.type("#n2c", 5.4, { letter: 0.03 });
  ["l1", "l2", "l3"].forEach((id, i) => S.type("#" + id, 6.0 + i * 0.6, { letter: 0.025 }));
  ["r1", "r2", "r3"].forEach((id, i) => S.type("#" + id, 6.3 + i * 0.6, { letter: 0.025 }));
  S.type("#foot", 8.6, { letter: 0.025 });
});
""")

# ───────────────────────── 03 · PROFILIN (blanco)
S[3] = ("""
<svg id="dg" class="abs" style="left:0;top:0" width="1280" height="720">
  <g id="mono"></g><g id="prof"></g>
  <g id="formin"><rect x="1026" y="440" width="24" height="22" rx="4" fill="#000"/><rect x="1026" y="478" width="24" height="22" rx="4" fill="#000"/></g>
  <g id="inc"></g>
  <path id="arr" d="M1196 330 Q1100 318 1062 430 M1062 430 l-2 -16 M1062 430 l13 -9" fill="none" stroke="#000" stroke-width="2.6" stroke-linecap="round"/>
</svg>
<div id="t" class="abs d" style="left:62px;top:40px;font-size:148px">Profilin</div>
<div id="sub" class="abs lab" style="left:70px;top:196px">One monomer-binding protein, two roles</div>
<div id="h1" class="abs d" style="left:64px;top:300px;font-size:44px">01 Barrier</div>
<div id="h2" class="abs d" style="left:680px;top:300px;font-size:44px">02 Delivery</div>
<div id="c1" class="abs cap" style="left:64px;top:580px;width:520px">Holds G-actin, so filaments never start at random</div>
<div id="c2" class="abs cap" style="left:680px;top:580px;width:520px">Formins and Ena/VASP hand it to the barbed end</div>
<div id="lb" class="abs k" style="left:960px;top:514px">barbed end (+)</div>
<div id="foot" class="abs cap" style="left:1010px;top:670px">Rottner et al., 2017</div>
""", r"""
// 01: monómeros con su profilina (arco negro grueso que los abraza)
const arc = (cx, cy, r) => { const a0 = -60 * Math.PI / 180, a1 = 60 * Math.PI / 180;
  return `M${cx + r * Math.cos(a0)} ${cy + r * Math.sin(a0)} A${r} ${r} 0 0 1 ${cx + r * Math.cos(a1)} ${cy + r * Math.sin(a1)}`; };
[[120, 470], [235, 440], [350, 478], [465, 448]].forEach(([x, y]) => {
  AX.sphere($("mono"), x, y, 22, "mono");
  AX.el($("prof"), "path", { d: arc(x, y, 30), stroke: "#000", "stroke-width": 9, fill: "none", "stroke-linecap": "round" });
});
// 02: filamento que crece hacia la formina + 3 complejos profilina-actina que llegan
const fb = AX.bank("tpl-actine-filament", { x: 690, y: 449, w: 330 });   // actina F de Servier
[[1110, 372], [1170, 352], [1226, 384]].forEach(([x, y]) => {
  const g = AX.sphere($("inc"), x, y, 15, "inc");
  AX.el(g, "path", { d: arc(x, y, 21), stroke: "#000", "stroke-width": 6, fill: "none", "stroke-linecap": "round" });
});
SC.build((S) => {
  S.arrive(".mono", 0.2, { from: "top", dist: 90, dur: 0.9, stagger: 0.15 });
  S.draw("#prof path", 1.2, { dur: 0.5, stagger: 0.12 });
  AX.build(S, fb.pieces, 0.4, 1.6);
  S.pop("#formin rect", 1.9, { stagger: 0.12 });
  S.arrive(".inc", 2.2, { from: "right", dist: 160, dur: 0.9, stagger: 0.15 });
  S.draw("#arr", 2.9, { dur: 0.7 });
  S.stamp("#t", 3.6);
  S.type("#sub", 4.6, { letter: 0.028 });
  S.rise("#h1", 5.8);
  S.rise("#h2", 6.2);
  S.type("#c1", 6.9, { letter: 0.02 });
  S.type("#c2", 7.9, { letter: 0.02 });
  S.type("#lb", 8.9, { letter: 0.03 });
  S.type("#foot", 9.5, { letter: 0.025 });
});
""")

BANKW[3] = [("actine-filament", 330)]

# ───────────────────────── 04 · ARP2/3 (amarillo)
S[4] = ("""
<svg id="dg" class="abs" style="left:0;top:0" width="1280" height="720">
  <g id="mother"></g><g id="daughter"></g><g id="arp"></g>
  <path id="ang" d="M890 478 A78 78 0 0 0 838.7 404.7" fill="none" stroke="#000" stroke-width="2.4" stroke-dasharray="1 0"/>
  <circle id="d1" class="dot" cx="1110" cy="520" r="5"/><path id="g1" class="lead" d="M1110 520 V588"/>
  <circle id="d2" class="dot" cx="905" cy="245" r="5"/><path id="g2" class="lead" d="M905 245 H1000"/>
  <circle id="d3" class="dot" cx="812" cy="486" r="5"/><path id="g3" class="lead" d="M812 486 V598"/>
</svg>
<div id="t" class="abs d" style="left:62px;top:40px;font-size:150px">Arp2/3</div>
<div id="t2" class="abs d" style="left:68px;top:196px;font-size:58px">Complex</div>
<div id="n7" class="abs d" style="left:64px;top:320px;font-size:170px">7</div>
<div id="n7c" class="abs k" style="left:184px;top:360px">subunits</div>
<div id="n7l" class="abs cap" style="left:184px;top:398px;width:300px">Arp2 · Arp3 · ArpC1–ArpC5</div>
<div id="deg" class="abs d nu" style="left:896px;top:384px;font-size:46px">70°</div>
<div id="x1" class="abs cap" style="left:1030px;top:594px">Mother filament</div>
<div id="x2" class="abs cap" style="left:1010px;top:229px">Daughter filament</div>
<div id="x3" class="abs cap" style="left:700px;top:604px">Branch point</div>
<div id="nb" class="abs lab" style="left:64px;top:560px;width:460px">Nucleates new filaments on the side of old ones</div>
<div id="foot" class="abs cap" style="left:64px;top:670px">Svitkina, 2018</div>
<div id="spine" class="abs k" style="left:1228px;top:60px;writing-mode:vertical-rl">Branched networks</div>
""", r"""
const m = AX.helix($("mother"), { x0: 560, y0: 520, len: 640, r: 16 });
const d = AX.helix($("daughter"), { x0: 812, y0: 478, len: 290, r: 14, angle: -70 });
const arp = [[812, 490]]; for (let i = 0; i < 6; i++) { const a = i * Math.PI / 3; arp.push([812 + 17 * Math.cos(a), 490 + 17 * Math.sin(a)]); }
const arpEls = arp.map(([x, y]) => AX.sphere($("arp"), x, y, 9, "arpS"));
if (arpEls.length !== 7) throw new Error("Arp2/3 debe tener 7 subunidades");
SC.build((S) => {
  S.pop(m.order, 0.0, { dur: 0.3, stagger: 0.026 });       // filamento madre
  S.pop(arpEls, 1.5, { dur: 0.35, stagger: 0.07 });          // el complejo se une al costado
  S.pop(d.order, 2.1, { dur: 0.3, stagger: 0.04 });          // la hija nace y crece en ángulo
  S.draw("#ang", 3.3, { dur: 0.6 });
  S.count("#deg", 70, 3.3, { suffix: "°", dur: 0.9 });
  S.drop("#t", 4.1, { stagger: 0.05 });
  S.rise("#t2", 4.9);
  S.count("#n7", 7, 5.4, { dur: 0.8 });
  S.type("#n7c", 5.8, { letter: 0.04 });
  S.type("#n7l", 6.2, { letter: 0.025 });
  S.rotulo("#d3", "#g3", "#x3", 6.8);
  S.rotulo("#d1", "#g1", "#x1", 7.3);
  S.rotulo("#d2", "#g2", "#x2", 7.8);
  S.type("#nb", 8.5, { letter: 0.018 });
  S.type("#foot", 9.5, { letter: 0.03 });
  S.drop("#spine", 9.6, { stagger: 0.025, dur: 0.6 });
});
""")

# ───────────────────────── 05 · NPFs (blanco)
ROWS = [("WAVE", "Lamellipodia"), ("WASP · N-WASP", "Podosome and invadopodium core"),
        ("N-WASP + WIP", "Endocytosis · comet tails"), ("WASH", "Endosome recycling"), ("WHAMM · JMY", "Autophagosomes · ER")]
rows_html = ""
for i, (a, b) in enumerate(ROWS):
    y = 196 + i * 92
    rows_html += f'<div id="c{i}" class="chip" style="left:430px;top:{y}px"><span class="chip-t">{a}</span></div>\n'
    rows_html += f'<div id="e{i}" class="abs lab" style="left:796px;top:{y + 4}px">{b}</div>\n'
seps = "".join(f'<path class="sep" d="M430 {196 + i * 92 + 70} H1216" stroke="#000" stroke-width="1" fill="none"/>' for i in range(4))
arrs = "".join(f'<path class="ar" d="M700 {196 + i * 92 + 24} H770 M770 {196 + i * 92 + 24} l-10 -7 M770 {196 + i * 92 + 24} l-10 7" stroke="#000" stroke-width="2.4" fill="none"/>' for i in range(5))
S[5] = (f"""
<svg class="abs" style="left:0;top:0" width="1280" height="720">{seps}{arrs}</svg>
<div id="t" class="abs d" style="left:64px;top:44px;font-size:62px">Who switches Arp2/3 on</div>
<div id="n5" class="abs d" style="left:64px;top:188px;font-size:180px">5</div>
<div id="n5c" class="abs k" style="left:70px;top:372px">NPF families</div>
<div id="n5l" class="abs cap" style="left:70px;top:410px;width:300px">Each one sends Arp2/3 to a different place</div>
<div id="lis" class="abs cap" style="left:70px;top:540px;width:300px">Listeria hijacks it with ActA</div>
{rows_html}
<div id="foot" class="abs cap" style="left:1010px;top:670px">Rottner et al., 2017</div>
""", r"""
SC.build((S) => {
  S.wipeIn("#t", 0.0, { color: "#000", dur: 0.9 });
  S.count("#n5", 5, 0.6, { dur: 0.8 });
  S.draw(".sep", 0.9, { dur: 0.6, stagger: 0.1 });
  for (let i = 0; i < 5; i++) {
    const t = 1.4 + i * 0.75;
    S.chip("#c" + i, t, { letter: 0.03 });
    S.draw(document.querySelectorAll(".ar")[i], t + 0.45, { dur: 0.35 });
    S.type("#e" + i, t + 0.65, { letter: 0.02 });
  }
  S.type("#n5c", 6.4, { letter: 0.04 });
  S.type("#n5l", 6.9, { letter: 0.02 });
  S.type("#lis", 8.0, { letter: 0.025 });
  S.marker("#lis", 8.9, { color: "#CCCC00", opacity: 0.9 });
  S.type("#foot", 9.4, { letter: 0.025 });
});
""")

# ───────────────────────── 06 · DESCANSO (amarillo) — Frame A completo + idle que vuelve al origen
S[6] = ("""
<svg id="sp" class="abs frame-a" style="left:0;top:0" width="1280" height="720"></svg>
""", r"""
const fb = AX.bank("tpl-fibroblast-3", { x: 70, y: 128, w: 1140, frameA: true, id: "fib" });   // célula migrando, Servier
[[150, 170, 40], [330, 560, 30], [960, 150, 46], [1130, 420, 32]].forEach(([x, y, s], i) => AX.sparkle($("sp"), x, y, s, i % 2 ? "#000" : "#fff", "#000", "spk"));
$("stage").appendChild($("sp"));
SC.build((S) => {
  // idle: la célula respira y los destellos laten; a los 11 s todo está donde empezó
  S.tl.to("#fib", { scale: 1.018, y: -4, transformOrigin: "50% 50%", duration: 2.75, yoyo: true, repeat: 3, ease: "sine.inOut" }, 0);
  S.tl.to(".spk", { scale: 1.3, transformOrigin: "50% 50%", duration: 1.375, yoyo: true, repeat: 7, ease: "sine.inOut" }, 0);
});
""")
BANKW[6] = [("fibroblast-3", 1140)]

# ───────────────────────── 07 · PODOSOMES vs INVADOPODIA (mosaico)
S[7] = ("""
<svg id="dg" class="abs" style="left:0;top:0" width="1280" height="720">
  <g id="ring"></g><g id="core"></g>
  <path id="imem" d="M704 166 H918 C930 226 936 288 950 318 A14 14 0 0 0 978 318 C992 288 998 226 1010 166 H1030" fill="none" stroke="#000" stroke-width="6" stroke-linejoin="round"/>
  <g id="icore"></g><g id="mmp"></g>
</svg>
<div id="tl" class="abs d" style="left:64px;top:38px;font-size:60px">Podosomes</div>
<div id="tr" class="abs d" style="left:704px;top:38px;font-size:60px">Invadopodia</div>
<div id="a1" class="abs k" style="left:64px;top:392px">Cells</div><div id="a2" class="abs lab" style="left:64px;top:420px">Macrophages · osteoclasts</div>
<div id="a3" class="abs k" style="left:64px;top:482px">Role</div><div id="a4" class="abs lab" style="left:64px;top:510px">Adhesion · mechanosensing</div>
<div id="a5" class="abs k" style="left:64px;top:572px">Lifetime</div><div id="a6" class="abs d" style="left:64px;top:604px;font-size:50px">Minutes</div>
<div id="b1" class="abs k" style="left:704px;top:392px">Cells</div><div id="b2" class="abs lab" style="left:704px;top:420px">Carcinoma · melanoma</div>
<div id="b3" class="abs k" style="left:704px;top:482px">Role</div><div id="b4" class="abs lab" style="left:704px;top:510px">Matrix degradation · invasion</div>
<div id="b5" class="abs k" style="left:704px;top:572px">Lifetime</div><div id="b6" class="abs d nu" style="left:704px;top:604px;font-size:50px">&gt; 60 min</div>
<div id="foot" class="abs cap" style="left:1010px;top:670px">Rottner et al., 2017</div>
""", r"""
// podosoma: núcleo de actina ramificada (esfera) + anillo de adhesión
AX.sphere($("core"), 230, 236, 40, "pcore");
for (let i = 0; i < 12; i++) { const a = i * Math.PI / 6; AX.sphere($("ring"), 230 + 80 * Math.cos(a), 236 + 80 * Math.sin(a), 10, "pring"); }
// bancos: macrófago (célula con podosomas), célula tumoral (invadopodios), fibras de colágeno (matriz)
const mac = AX.bank("tpl-macrophage", { x: 400, y: 118, w: 196 });
const can = AX.bank("tpl-cancerous-cell-3", { x: 1052, y: 122, w: 168 });
const c1 = AX.bank("tpl-collagen-3", { x: 708, y: 206, w: 300 });
const c2 = AX.bank("tpl-collagen-3", { x: 708, y: 280, w: 300 });
$("stage").appendChild($("dg"));                                 // la protrusión va por delante de la matriz
[[964, 196], [964, 236], [964, 276]].forEach(([x, y]) => AX.sphere($("icore"), x, y, 11, "ic"));
[[946, 344], [964, 352], [982, 344], [956, 360], [974, 360]].forEach(([x, y]) => AX.el($("mmp"), "circle", { cx: x, cy: y, r: 3.6, fill: "#000" }));
SC.build((S) => {
  S.pop("#core .pcore", 0.2, { dur: 0.6 });
  S.pop(".pring", 0.6, { dur: 0.35, stagger: 0.06 });
  S.draw("#imem", 0.2, { dur: 1.2 });
  AX.build(S, mac.pieces, 0.3, 1.6);
  AX.build(S, can.pieces, 0.5, 1.6);
  AX.build(S, c1.pieces.concat(c2.pieces), 0.7, 1.4);
  S.pop(".ic", 1.6, { stagger: 0.12 });
  S.pop("#mmp circle", 2.2, { stagger: 0.07 });
  S.rise("#tl", 3.0);
  S.rise("#tr", 3.4);
  ["a1", "a2", "a3", "a4", "a5"].forEach((id, i) => S.type("#" + id, 4.2 + i * 0.45, { letter: 0.022 }));
  ["b1", "b2", "b3", "b4", "b5"].forEach((id, i) => S.type("#" + id, 4.4 + i * 0.45, { letter: 0.022 }));
  S.type("#a6", 6.7, { letter: 0.05 });
  S.count("#b6", 60, 6.9, { prefix: "> ", suffix: " min", dur: 1.2 });
  S.halo("#b6", 8.2, { color: "#000", size: 1.5 });
  S.type("#foot", 9.0, { letter: 0.025 });
});
""")

BANKW[7] = [("macrophage", 196), ("cancerous-cell-3", 168), ("collagen-3", 300)]

# ───────────────────────── 08 · CORTEX (blanco)
S[8] = ("""
<svg id="dg" class="abs" style="left:0;top:0" width="1280" height="720">
  <g id="erm"></g><g id="mesh"></g><g id="myo"></g>
  <path id="pl" d="M540 300 H600 M600 300 l-10 -7 M600 300 l-10 7" fill="none" stroke="#000" stroke-width="3"/>
  <path id="pr" d="M1240 300 H1180 M1180 300 l10 -7 M1180 300 l10 7" fill="none" stroke="#000" stroke-width="3"/>
  <path id="brk" d="M1252 120 V384 M1244 120 H1260 M1244 384 H1260" fill="none" stroke="#000" stroke-width="2"/>
</svg>
<div id="t" class="abs d" style="left:62px;top:40px;font-size:74px">The cortex</div>
<div id="lm" class="abs cap" style="left:900px;top:84px">Plasma membrane</div>
<div id="le" class="abs cap" style="left:850px;top:400px">ERM proteins</div>
<div id="nn" class="abs d nu" style="left:1046px;top:400px;font-size:46px">~100 nm</div>
<div id="nnc" class="abs k" style="left:1050px;top:456px">thickness</div>
<div id="lx" class="abs lab" style="left:64px;top:222px;width:440px">Myosin II pulls on the actin mesh</div>
<div id="lk" class="abs k" style="left:64px;top:334px">Cortical tension for</div>
<div id="i1" class="abs lab" style="left:64px;top:372px">Cell division</div>
<div id="i2" class="abs lab" style="left:64px;top:412px">Migration</div>
<div id="i3" class="abs lab" style="left:64px;top:452px">Shape change</div>
<div id="lmy" class="abs cap" style="left:576px;top:400px">Myosin II minifilaments</div>
<div id="foot" class="abs cap" style="left:64px;top:670px">Rottner et al., 2017</div>
""", r"""
const R = AX.rng(11);
const m1 = AX.bank("tpl-membrane-2d-redlight", { x: 570, y: 120, w: 320 }), m2 = AX.bank("tpl-membrane-2d-redlight", { x: 890, y: 120, w: 320 });
for (let i = 0; i < 8; i++) { const x = 600 + i * 84; AX.el($("erm"), "path", { d: `M${x} 214 V238`, stroke: "#000", "stroke-width": 5, fill: "none" }); }
for (let i = 0; i < 26; i++) {
  const cx = 590 + R() * 600, cy = 244 + R() * 128, a = (R() - 0.5) * Math.PI * 0.9, L = 70 + R() * 90;
  const x0 = Math.max(578, cx - Math.cos(a) * L / 2), x1 = Math.min(1202, cx + Math.cos(a) * L / 2);
  const y0 = Math.min(380, Math.max(240, cy - Math.sin(a) * L / 2)), y1 = Math.min(380, Math.max(240, cy + Math.sin(a) * L / 2));
  AX.el($("mesh"), "path", { d: `M${x0} ${y0} L${x1} ${y1}`, stroke: "#000", "stroke-width": 2.2, fill: "none" });
}
[[700, 330], [900, 300], [1090, 346]].forEach(([x, y]) => {           // minifilamento bipolar de miosina II
  const g = AX.el($("myo"), "g", { class: "my" });
  AX.el(g, "path", { d: `M${x - 34} ${y} H${x + 34}`, stroke: "#000", "stroke-width": 7, fill: "none" });
  [-1, 1].forEach((s) => [-9, 0, 9].forEach((o) => AX.el(g, "circle", { cx: x + s * 42, cy: y + o, r: 5, fill: "#000" })));
});
SC.build((S) => {
  AX.build(S, m1.pieces.concat(m2.pieces), 0.0, 1.4);
  S.draw("#erm path", 1.2, { dur: 0.25, stagger: 0.06 });
  S.draw("#mesh path", 1.4, { dur: 0.45, stagger: 0.03 });
  S.arrive(".my", 2.2, { from: "bottom", dist: 110, dur: 0.8, stagger: 0.15 });
  S.tl.to("#mesh", { scaleX: 0.95, transformOrigin: "50% 50%", duration: 0.45, yoyo: true, repeat: 1, ease: "sine.inOut" }, 3.4);
  S.draw("#pl, #pr", 3.3, { dur: 0.5 });
  S.draw("#brk", 3.0, { dur: 0.5 });
  S.count("#nn", 100, 3.2, { prefix: "~", suffix: " nm", dur: 1.0 });
  S.tracking("#t", 4.3, { dur: 1.0 });
  S.type("#le", 5.3, { letter: 0.03 });
  S.type("#lm", 5.7, { letter: 0.03 });
  S.type("#lmy", 6.2, { letter: 0.025 });
  S.type("#nnc", 6.6, { letter: 0.04 });
  S.type("#lx", 7.0, { letter: 0.02 });
  S.type("#lk", 7.8, { letter: 0.025 });
  ["i1", "i2", "i3"].forEach((id, i) => S.type("#" + id, 8.4 + i * 0.4, { letter: 0.025 }));
  S.type("#foot", 9.8, { letter: 0.025 });
});
""")

BANKW[8] = [("membrane-2d-redlight", 320)]

# ───────────────────────── 09 · PROTRUSION FORCE (amarillo)
S[9] = ("""
<svg id="dg" class="abs" style="left:0;top:0" width="1280" height="720">
  <path id="mem" d="M1000 112 C1036 260 1036 460 1000 610" fill="none" stroke="#000" stroke-width="8" stroke-linecap="round"/>
  <path id="push" d="M1062 360 H1196 M1196 360 l-16 -11 M1196 360 l-16 11" fill="none" stroke="#000" stroke-width="7" stroke-linecap="round"/>
  <circle id="dp" class="dot" cx="986" cy="201" r="5"/><path id="gp" class="lead" d="M986 201 L1070 150"/>
  <circle id="dm" class="dot" cx="612" cy="500" r="5"/><path id="gm" class="lead" d="M612 500 V610"/>
</svg>
<div id="t" class="abs d" style="left:62px;top:40px;font-size:112px">The force</div>
<div id="t2" class="abs d" style="left:68px;top:158px;font-size:58px">to protrude</div>
<div id="x1" class="abs lab" style="left:64px;top:290px;width:420px">Actin polymerization pushes the membrane</div>
<div id="x2" class="abs k" style="left:64px;top:400px">Force per filament</div>
<div id="x3" class="abs d nu" style="left:64px;top:432px;font-size:72px">pN</div>
<div id="x4" class="abs k" style="left:64px;top:536px">Model</div>
<div id="x5" class="abs lab" style="left:64px;top:566px">Elastic Brownian ratchet</div>
<div id="xp" class="abs cap" style="left:1076px;top:118px">Barbed end (+)</div>
<div id="xm" class="abs cap" style="left:570px;top:616px">Pointed end (−)</div>
<div id="foot" class="abs cap" style="left:1060px;top:670px">Svitkina, 2018</div>
""", r"""
const net = AX.bank("tpl-actin-filament", { x: 600, y: 190, w: 392 });   // red de actina ramificada de Servier
$("stage").appendChild($("dg"));
SC.build((S) => {
  S.draw("#mem", 0.0, { dur: 0.9 });
  AX.build(S, net.pieces, 0.4, 2.0);                          // la red se construye y llega a la membrana
  S.tl.to("#mem", { x: 16, duration: 0.45, yoyo: true, repeat: 1, ease: "power2.out" }, 2.6);
  S.draw("#push", 2.6, { dur: 0.7 });
  S.drop("#t", 3.4, { stagger: 0.05 });
  S.rise("#t2", 4.3);
  S.rotulo("#dp", "#gp", "#xp", 5.0);
  S.rotulo("#dm", "#gm", "#xm", 5.6);
  S.type("#x1", 6.3, { letter: 0.02 });
  S.type("#x2", 7.3, { letter: 0.03 });
  S.stamp("#x3", 7.9);
  S.type("#x4", 8.7, { letter: 0.04 });
  S.type("#x5", 9.0, { letter: 0.025 });
  S.type("#foot", 9.9, { letter: 0.025 });
});
""")

BANKW[9] = [("actin-filament", 392)]

# ───────────────────────── 10 · CONTRACTION (split horizontal)
COLS = [("01", "RLC phosphorylation at Ser19"), ("02", "Bipolar myosin II filaments"), ("03", "Tropomyosin and α-actinin bundle actin"),
        ("04", "Anchoring turns sliding into work"), ("05", "IIA contracts fast, IIB holds tension")]
cols_html = "".join(f'<div id="cn{i}" class="abs d" style="left:{64 + i * 234}px;top:412px;font-size:52px">{n}</div>'
                    f'<div id="cc{i}" class="abs cap" style="left:{64 + i * 234}px;top:476px;width:206px">{c}</div>\n' for i, (n, c) in enumerate(COLS))
S[10] = (f"""
<svg id="dg" class="abs" style="left:0;top:0" width="1280" height="720">
  <rect id="za" x="548" y="168" width="12" height="62" fill="#000"/>
  <rect id="zb" x="1212" y="232" width="12" height="62" fill="#000"/>
  <g id="actL"></g><g id="actR"></g>
  <path id="bar" d="M772 230 H1000" fill="none" stroke="#000" stroke-width="12" stroke-linecap="round"/>
  <g id="heads"></g>
  <path id="sc" d="M772 300 H1000 M772 292 V308 M1000 292 V308" fill="none" stroke="#000" stroke-width="2"/>
</svg>
<div id="t" class="abs d" style="left:62px;top:40px;font-size:96px">Contraction</div>
<div id="sub" class="abs lab" style="left:66px;top:150px;width:440px">Myosin II slides actin filaments, powered by ATP</div>
<div id="nm" class="abs d nu" style="left:830px;top:310px;font-size:34px">300 nm</div>
<div id="k5" class="abs k" style="left:64px;top:380px">Five processes</div>
{cols_html}
<div id="foot" class="abs cap" style="left:64px;top:670px">Svitkina, 2018</div>
<div id="spine" class="abs k" style="left:1236px;top:388px;writing-mode:vertical-rl">ATP-driven sliding</div>
""", r"""
const L = AX.helix($("actL"), { x0: 560, y0: 200, len: 300, r: 10 });
const Rr = AX.helix($("actR"), { x0: 912, y0: 262, len: 300, r: 10 });
[-1, 1].forEach((s) => [-14, -5, 5, 14].forEach((o) =>                 // cabezas motoras en ambos extremos
  AX.sphere($("heads"), s < 0 ? 760 : 1012, 230 + o * 1.6, 7, "hd")));
SC.build((S) => {
  S.pop("#za, #zb", 0.0, { dur: 0.4 });
  S.pop(L.order, 0.2, { dur: 0.25, stagger: 0.022 });
  S.pop(Rr.order, 0.3, { dur: 0.25, stagger: 0.022 });
  S.draw("#bar", 1.2, { dur: 0.8 });
  S.pop(".hd", 1.8, { dur: 0.3, stagger: 0.05 });
  S.draw("#sc", 2.3, { dur: 0.5 });
  S.count("#nm", 300, 2.4, { suffix: " nm", dur: 0.9 });
  // el mecanismo, ya trazado, se mueve: los filamentos y sus anclas deslizan hacia el centro
  S.tl.to(["#actL", "#za"], { x: 34, duration: 1.1, ease: "power2.inOut" }, 3.0);
  S.tl.to(["#actR", "#zb"], { x: -34, duration: 1.1, ease: "power2.inOut" }, 3.0);
  S.rise("#t", 4.0);
  S.type("#sub", 5.0, { letter: 0.018 });
  S.type("#k5", 5.6, { letter: 0.03 });
  for (let i = 0; i < 5; i++) { S.type("#cn" + i, 6.0 + i * 0.55, { letter: 0.06 }); S.type("#cc" + i, 6.2 + i * 0.55, { letter: 0.016 }); }
  S.type("#foot", 9.4, { letter: 0.025 });
  S.drop("#spine", 9.2, { stagger: 0.025, dur: 0.6 });
});
""")

# ───────────────────────── 11 · CIERRE (blanco)
S[11] = ("""
<svg class="abs" style="left:0;top:0" width="1280" height="720"><g id="sp"></g></svg>
<div id="l1" class="abs d" style="left:64px;top:118px;font-size:124px">Same actin.</div>
<div class="abs d" style="left:64px;top:318px;font-size:76px"><span id="a1">Polymerization</span> <span id="a2" style="display:inline-block">pushes.</span></div>
<div class="abs d" style="left:64px;top:418px;font-size:76px"><span id="b1">Myosin II</span> <span id="b2" style="display:inline-block">pulls.</span></div>
<div id="foot" class="abs cap" style="left:64px;top:670px">Svitkina, 2018</div>
""", r"""
[[1130, 150, 40], [1190, 250, 24], [1060, 560, 30]].forEach(([x, y, s]) => AX.sparkle($("sp"), x, y, s, "#000", "#000", "spk"));
SC.build((S) => {
  S.tracking("#l1", 0.3, { dur: 1.2 });
  const e1 = S.type("#a1", 1.8, { letter: 0.05 });
  S.stamp("#a2", e1 + 0.15);
  const e2 = S.type("#b1", 3.8, { letter: 0.05 });
  S.stamp("#b2", e2 + 0.15);
  S.marker("#a2", 5.8, { color: "#CCCC00", opacity: 0.95 });
  S.marker("#b2", 6.3, { color: "#CCCC00", opacity: 0.95 });
  S.pop(".spk", 7.0, { stagger: 0.18, dur: 0.5 });
  S.type("#foot", 8.0, { letter: 0.03 });
});
""")

# ───────────────────────── 12 · REFERENCIAS (blanco)
S[12] = ("""
<svg class="abs" style="left:0;top:0" width="1280" height="720"><path id="rule" d="M64 134 H1216" stroke="#000" stroke-width="1.6" fill="none"/></svg>
<div id="t" class="abs d" style="left:64px;top:56px;font-size:56px">References</div>
<div id="r1" class="abs ref" style="left:64px;top:186px">Rottner, K., Faix, J., Bogdan, S., Linder, S., &amp; Kerkhoff, E. (2017). Actin assembly mechanisms at a glance. <i>Journal of Cell Science, 130</i>, 3427–3435. https://doi.org/10.1242/jcs.206433</div>
<div id="r2" class="abs ref" style="left:64px;top:330px">Svitkina, T. (2018). The actin cytoskeleton and actin-based motility. <i>Cold Spring Harbor Perspectives in Biology, 10</i>, a018267. https://doi.org/10.1101/cshperspect.a018267</div>
<div id="cr" class="abs cap" style="left:64px;top:490px;width:1100px">Illustrations adapted from Servier Medical Art (CC BY 3.0), via Bioicons.</div>
<div id="ft" class="abs k" style="left:64px;top:640px">Homework 9 · Cell Biology · Yachay Tech · 2026</div>
""", r"""
SC.build((S) => {
  S.type("#t", 0.2, { letter: 0.06 });
  S.draw("#rule", 0.9, { dur: 0.9 });
  S.type("#r1", 1.6, { letter: 0.013 });
  S.type("#r2", 4.6, { letter: 0.013 });
  S.type("#cr", 7.0, { letter: 0.015 });
  S.type("#ft", 8.4, { letter: 0.03 });
});
""")

for n, (body, script) in S.items():
    nn = f"{n:02d}"
    tpls = "".join(f'<template id="tpl-{name}">{harper(BANKS[name], f"s{nn}{name[:4]}{i}", w)}</template>\n'
                   for i, (name, w) in enumerate(BANKW.get(n, [])))
    html = HEAD.replace("bg_NN", f"bg_{nn}") + body + TAIL.replace("SCRIPT", script.strip()).replace("</div>\n<script>", "</div>\n" + tpls + "<script>", 1)
    (OUT / f"slide_{nn}.html").write_text(html, encoding="utf-8")
print("OK", len(S), "slides")
