#!/usr/bin/env python3
"""Genera slide_NN.html — The Heroes of CRISPR (Lander, 2016). Estilo 3 minimalista,
variante de esta corrida: TODAS las slides en cobalto plano con texto y línea blancos."""
import math, os, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "engine"))
from bank import bank
PHAGE = "cc-by-4.0/Viruses/DBCLS/phage.svg"

HEAD = """<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="engine/style.css">
<script src="engine/vendor/gsap.min.js"></script>
<script src="engine/vendor/DrawSVGPlugin.min.js"></script>
<script src="engine/vendor/SplitText.min.js"></script>
<script src="engine/runtime.js"></script></head>
<body data-break="{brk}"><div id="stage">
{body}
</div>
<script>SC.build((S) => {{
{script}
}});</script></body></html>"""

FOOT = "Lander, E. S. (2016). The heroes of CRISPR. Cell, 164, 18–28"

def T(id_, x, y, txt, cls="t-label", w=None, extra=""):
    ws = f"width:{w}px;" if w else ""
    return f'<div id="{id_}" class="abs {cls}" style="left:{x}px;top:{y}px;{ws}{extra}">{txt}</div>'

def foot(txt=FOOT, id_="foot"):
    return T(id_, 64, 672, txt, "t-caption")

def table(pfx, x, y, cols, header, rows, rowh=62, fs=24, hfs=20):
    """Tabla de divs: encabezado + reglas horizontales finas, sin verticales."""
    out, W = [], sum(cols)
    cx = [x + sum(cols[:i]) for i in range(len(cols))]
    for j, h in enumerate(header):
        out.append(f'<div class="abs {pfx}-h" style="left:{cx[j]}px;top:{y}px;width:{cols[j]-20}px;font-size:{hfs}px;font-weight:400;letter-spacing:.06em;color:var(--soft)">{h}</div>')
    out.append(f'<div class="rule h2 {pfx}-r" style="left:{x}px;top:{y+36}px;width:{W}px"></div>')
    for i, r in enumerate(rows):
        top = y + 50 + i * rowh
        for j, c in enumerate(r):
            out.append(f'<div class="abs {pfx}-c{i}" style="left:{cx[j]}px;top:{top}px;width:{cols[j]-22}px;font-size:{fs}px;line-height:1.2">{c}</div>')
        out.append(f'<div class="rule {pfx}-r" style="left:{x}px;top:{top+rowh-12}px;width:{W}px;opacity:.55"></div>')
    return "\n".join(out)

def table_anim(pfx, t, nrows, letter=0.022):
    return f"""  {{ let e = S.grow(".{pfx}-r", {t}, {{axis:"x", dur:.6, stagger:.08}});
    e = S.type(".{pfx}-h", {t}+.2, {{letter:.02}});
    for (let i = 0; i < {nrows}; i++) e = S.type(".{pfx}-c" + i, e + .08, {{letter:.033, minLetter:.032, overlap:.3}});
    window._tEnd = e; }}"""

def donut(gid, cx, cy, r, w, segs, gap=0.5):
    """segs: [(a%, b%, color)] — gira desde las 12 en sentido horario."""
    c = "".join(f'<circle data-a="{a+gap:.2f}" data-b="{b-gap:.2f}" cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{col}" stroke-width="{w}"/>' for a, b, col in segs)
    return f'<g transform="rotate(-90 {cx} {cy})"><g id="{gid}">{c}</g></g>'

def phage(id_, x, y, s=1.0):
    """Bacteriófago monolínea: cabeza hexagonal, cola, 4 patas. (x,y)=punta de la cola."""
    hx, hy, R = x, y - 92 * s, 24 * s
    pts = " ".join(f"{hx+R*math.cos(math.radians(a)):.1f},{hy+R*math.sin(math.radians(a)):.1f}" for a in range(-90, 270, 60))
    legs = "".join(f'<path class="line thin" d="M{x} {y-14*s} L{x+dx*s} {y+4*s}"/>' for dx in (-22, -9, 9, 22))
    return (f'<g id="{id_}"><polygon class="line" points="{pts}"/>'
            f'<path class="line thin" d="M{hx-R*.5:.1f} {hy:.1f} L{hx+R*.5:.1f} {hy:.1f}"/>'
            f'<path class="line" d="M{x} {hy+R:.1f} L{x} {y-14*s}"/>'
            f'<rect class="line thin" x="{x-6*s}" y="{hy+R+8*s:.1f}" width="{12*s}" height="{40*s:.1f}"/>{legs}</g>')

def array(pfx, x, y, h, pattern, rep_w=40, sp_w=110, leader=True, colors=None):
    """Arreglo CRISPR: líder + repeticiones (contorno con rayado) + espaciadores (relleno)."""
    out, fills, cx = [], [], x
    if leader:
        out.append(f'<rect class="line {pfx}-o" x="{cx}" y="{y}" width="70" height="{h}" rx="6"/>'); cx += 78
    k = 0
    for p in pattern:
        if p == "R":
            out.append(f'<rect class="line {pfx}-o" x="{cx}" y="{y}" width="{rep_w}" height="{h}"/>')
            for i in range(1, 5):
                xx = cx + i * rep_w / 5
                out.append(f'<path class="line thin {pfx}-hatch" d="M{xx:.1f} {y+6} L{xx:.1f} {y+h-6}"/>')
            cx += rep_w
        else:
            col = (colors or ["var(--c2)", "var(--c3)", "var(--c1)", "var(--c2)"])[k % 4]; k += 1
            out.append(f'<rect class="line {pfx}-o" x="{cx}" y="{y}" width="{sp_w}" height="{h}"/>')
            fills.append(f'<rect class="{pfx}-f" x="{cx+5}" y="{y+5}" width="{sp_w-10}" height="{h-10}" fill="{col}"/>')
            cx += sp_w
    return "\n".join(out + fills), cx

slides = {}

# ───────────── 01 · PORTADA ─────────────
cx, cy, R = 935, 360, 235
segs, dia = [], []
cols = ["var(--c1)", "var(--c2)", "var(--c3)", "var(--c2)", "var(--c1)", "var(--c3)"]
for i in range(18):
    a, b = i * 100 / 18 + 0.9, (i + 1) * 100 / 18 - 0.9
    segs.append((a, b, "var(--accent)" if i == 4 else cols[i % 6]))
    th = math.radians(i * 20)
    px, py = cx + R * math.sin(th), cy - R * math.cos(th)
    dia.append(f'<rect class="dia" x="{px-7:.1f}" y="{py-7:.1f}" width="14" height="14" fill="#fff" transform="rotate(45 {px:.1f} {py:.1f})"/>')
slides[1] = dict(body=f"""
<svg width="1280" height="720">
  <circle id="c1i" class="line thin" cx="{cx}" cy="{cy}" r="185" transform="rotate(-90 {cx} {cy})"/>
  <circle id="c1j" class="line thin" cx="{cx}" cy="{cy}" r="140" stroke-dasharray="2 9" transform="rotate(-90 {cx} {cy})"/>
  {donut("ring1", cx, cy, R, 30, segs, gap=0)}
  {"".join(dia)}
  {bank(PHAGE, "bk1", cx-62, cy-108, 124, 213, drop_clipped=True)[0]}
</svg>
{T("vt", 26, 64, "Perspective · Cell 2016", "vert")}
{T("title", 92, 196, 'The Heroes<br>of <span class="acc">CRISPR</span>', "t-hero", 680, "font-size:108px")}
{T("sub", 96, 452, "Eric S. Lander · Cell, 14 de enero de 2016", "t-label")}
{T("cap", 96, 500, "Análisis de artículo · Microbiología · Cristian Chuquín", "t-caption")}
""", script="""
  S.ring("#ring1", .2, {dur:2.4, stagger:.04, deg:-200, origin:"935 360"});
  S.draw("#c1i, #c1j", .6, {dur:1.6});
  S.pop(".dia", 2.3, {stagger:.035, dur:.4});
  S.build("#bk1", 1.0, {span:1.4, dur:.8});
  let e = S.tracking("#title", 3.2, {dur:1.4});
  e = S.type("#sub", e + .1);
  e = S.type("#cap", e + .1, {letter:.025});
  S.drop("#vt", e + .1);
""")

# ───────────── 02 · FICHA + MÉTODO ─────────────
vc = [(890, 330), (1040, 330), (965, 455)]
slides[2] = dict(body=f"""
{T("title", 64, 58, "Qué tipo de artículo es", "t-title")}
{table("tb", 64, 190, [210, 400], ["CAMPO", "DATO"], [
    ["Tipo", "Perspective (no experimental)"],
    ["Autor", "Eric S. Lander"],
    ["Revista", "Cell 164 · enero 2016"],
    ["Institución", "Broad Institute, MIT y Harvard"]], rowh=70, fs=25)}
<svg width="1280" height="720">
  <circle id="v1" class="line" cx="{vc[0][0]}" cy="{vc[0][1]}" r="130" transform="rotate(-90 {vc[0][0]} {vc[0][1]})"/>
  <circle id="v2" class="line" cx="{vc[1][0]}" cy="{vc[1][1]}" r="130" transform="rotate(-90 {vc[1][0]} {vc[1][1]})"/>
  <circle id="v3" class="line fat" style="stroke:var(--accent)" cx="{vc[2][0]}" cy="{vc[2][1]}" r="130" transform="rotate(-90 {vc[2][0]} {vc[2][1]})"/>
  <circle id="d2" cx="1086" cy="560" r="6" fill="#fff"/>
  <path id="l2" class="line thin" d="M1086 566 L1086 616 L1060 616"/>
</svg>
{T("vh", 760, 150, "MÉTODO · 3 FUENTES", "t-caption", None, "letter-spacing:.08em")}
{T("vl1", 752, 290, "Artículos<br>publicados", "t-label", 150, "text-align:center;font-size:24px")}
{T("vl2", 1018, 300, "Entrevistas", "t-label", 150, "text-align:center;font-size:24px")}
{T("vl3", 890, 500, "Cartas de<br>rechazo", "t-label", 150, "text-align:center;font-size:24px")}
{T("h2", 700, 600, "la fuente que nadie había usado", "t-label", 360, "text-align:right;font-size:24px")}
{foot("Lander, E. S. (2016). Cell, 164, 18–28 · doi:10.1016/j.cell.2015.12.041")}
""", script="""
  let e = S.rise("#title", .2, {stagger:.035});
  S.draw("#v1, #v2, #v3", 1.0, {dur:1.2, stagger:.3});
  S.type("#vh", 1.3, {letter:.02});
  """ + table_anim("tb", 2.6, 4, .025) + """
  e = S.type("#vl1, #vl2, #vl3", window._tEnd + .1, {letter:.03});
  e = S.rotulo("#d2", "#l2", "#h2", e + .15, {letter:.025});
  S.type("#foot", 2.0, {letter:.01});
""")

# ───────────── 03 · QUÉ ES CRISPR ─────────────
arr, xend = array("a3", 150, 380, 64, "RSRSRSRSR", rep_w=46, sp_w=130)
sp_x = [150 + 78 + 46 + i * 176 for i in range(4)]       # x de cada espaciador
slides[3] = dict(body=f"""
{T("title", 64, 58, "Qué es un locus CRISPR", "t-title")}
<svg width="1280" height="720">
  {arr}
  {bank(PHAGE, "ph1", sp_x[0] + 65 - 34, 330 - 116, 68, 116, drop_clipped=True)[0]}
  {bank(PHAGE, "ph2", sp_x[2] + 65 - 34, 330 - 116, 68, 116, drop_clipped=True)[0]}
  <path id="cot1" class="line thin" d="M{sp_x[0]-46} 470 L{sp_x[0]-46} 486 M{sp_x[0]-46} 478 L{sp_x[0]} 478 M{sp_x[0]} 470 L{sp_x[0]} 486"/>
  <path id="cot2" class="line thin" d="M{sp_x[1]} 470 L{sp_x[1]} 486 M{sp_x[1]} 478 L{sp_x[1]+130} 478 M{sp_x[1]+130} 470 L{sp_x[1]+130} 486"/>
  <circle id="d3" cx="{xend-23}" cy="452" r="6" fill="#fff"/>
  <path id="l3" class="line thin" d="M{xend-23} 458 L{xend-23} 300 L{xend+10} 300"/>
</svg>
<div class="abs" style="left:{sp_x[0]-80}px;top:494px;width:114px;text-align:center"><span id="n1" class="t-big">30</span><span class="t-caption" id="u1"> b</span></div>
<div class="abs" style="left:{sp_x[1]+8}px;top:494px;width:114px;text-align:center"><span id="n2" class="t-big">36</span><span class="t-caption" id="u2"> b</span></div>
{T("lr", sp_x[0]-110, 556, "repetición", "t-caption", 174, "text-align:center")}
{T("ls", sp_x[1], 556, "espaciador", "t-caption", 130, "text-align:center")}
{T("lp", sp_x[1]-30, 150, "fragmentos de virus", "t-caption", 240, "text-align:center")}
{T("h3", xend+20, 284, 'un archivo de<br><span class="acc">infecciones</span> pasadas', "t-big", 260)}
{foot("Mojica et al., 1993 · Haloferax mediterranei, salinas de Santa Pola (España)")}
""", script="""
  let e = S.type("#title", .2);
  e = S.draw(".a3-o", .6, {dur:.8, stagger:.08});
  S.draw(".a3-hatch", 1.4, {dur:.3, stagger:.02});
  e = S.grow(".a3-f", e, {axis:"x", dur:.6, stagger:.12});
  S.build("#ph1", 2.6, {span:.6, dur:.5}); e = S.build("#ph2", 2.8, {span:.6, dur:.5});
  S.type("#lp", e, {letter:.03});
  e = S.draw("#cot1, #cot2", e + .2, {dur:.5, stagger:.2});
  S.count("#n1", 30, e, {dur:1.0}); S.type("#u1", e, {});
  S.count("#n2", 36, e + .2, {dur:1.0}); S.type("#u2", e + .2, {});
  e = S.type("#lr, #ls", e + 1.4, {letter:.03});
  e = S.rotulo("#d3", "#l3", "#h3", e + .2, {letter:.035});
  S.type("#foot", e + .1, {letter:.012});
""")

# ───────────── 04 · LÍNEA DE TIEMPO CIRCULAR ─────────────
ccx, ccy, cr = 640, 405, 185
hitos = [("1993", "Repeticiones en una arquea de salina (Mojica)"),
         ("2005", "Los espaciadores vienen de virus"),
         ("2007", "Prueba en S. thermophilus (Danisco)"),
         ("2008", "El blanco es el ADN"),
         ("2012", "Corte in vitro y ARN guía"),
         ("2013", "Edición en células humanas")]
nodes, labels = [], []
for i, (yr, tx) in enumerate(hitos):
    ang = 30 + i * 60
    nx, ny = ccx + cr * math.sin(math.radians(ang)), ccy - cr * math.cos(math.radians(ang))
    col = "var(--accent)" if i == 5 else "#fff"
    nodes.append(f'<circle class="nd" id="nd{i}" cx="{nx:.1f}" cy="{ny:.1f}" r="11" fill="{col}"/>')
    off = 28 if ang in (90, 270) else 70
    if ang < 180:
        labels.append(T(f"yr{i}", nx + off, ny - 34, yr, "t-label b") + T(f"tx{i}", nx + off, ny + 2, tx, "t-caption", 330))
    else:
        labels.append(T(f"yr{i}", nx - off - 330, ny - 34, yr, "t-label b", 330, "text-align:right") +
                      T(f"tx{i}", nx - off - 330, ny + 2, tx, "t-caption", 330, "text-align:right"))
slides[4] = dict(body=f"""
{T("title", 64, 52, "Veinte años de historia", "t-title")}
<svg width="1280" height="720">
  <circle id="arc4" class="line" cx="{ccx}" cy="{ccy}" r="{cr}" transform="rotate(-90 {ccx} {ccy})"/>
  <circle id="arc4b" class="line thin" cx="{ccx}" cy="{ccy}" r="{cr-28}" stroke-dasharray="2 8" transform="rotate(-90 {ccx} {ccy})"/>
  {"".join(nodes)}
</svg>
{"".join(labels)}
<div class="abs" style="left:{ccx-150}px;top:{ccy-82}px;width:300px;text-align:center">
  <span id="n12" class="t-hero" style="font-size:88px">12</span> <span id="u12" class="t-label">ciudades</span><br>
  <span id="n9" class="t-hero acc" style="font-size:88px">9</span> <span id="u9" class="t-label">países</span></div>
{foot()}
""", script="""
  let e = S.stamp("#title", .2);
  S.draw("#arc4", .6, {dur:2.2, ease:"none"});
  S.draw("#arc4b", .9, {dur:2.2, ease:"none"});
  for (let i = 0; i < 6; i++) { const tn = .6 + 2.2 * (30 + i * 60) / 360; S.pop("#nd" + i, tn - .1, {dur:.4}); S.type("#yr" + i, tn, {}); }
  S.count("#n12", 12, 3.0, {dur:1.3}); S.type("#u12", 3.0, {});
  S.count("#n9", 9, 3.3, {dur:1.3}); S.type("#u9", 3.3, {});
  e = 4.9;
  for (let i = 0; i < 6; i++) e = S.type("#tx" + i, e + .08, {letter:.019});
  S.type("#foot", e + .1, {letter:.01});
""")

# ───────────── 05 · HALLAZGO 1 · MOJICA 2005 ─────────────
bx, by, br = 330, 405, 200
sr = br * math.sqrt(88 / 4500)
assert abs(sr - 27.97) < .1
slides[5] = dict(body=f"""
{T("vt", 26, 64, "Hallazgo 1 · 2005", "vert")}
{T("title", 92, 52, "Los espaciadores vienen de virus", "t-title")}
<svg width="1280" height="720">
  <circle id="big5" class="line" cx="{bx}" cy="{by}" r="{br}" transform="rotate(-90 {bx} {by})"/>
  <circle id="sm5" cx="{bx+90}" cy="{by+130}" r="{sr:.1f}" fill="#fff"/>
  <path id="l5" class="line thin" d="M{bx+90+sr+4:.0f} {by+130} L{bx+250} {by+130} L{bx+250} {by+190}"/>
  {donut("ring5", 900, 395, 150, 46, [(0, 66.67, "var(--accent)"), (66.67, 100, "var(--c2)")], gap=.6)}
  <rect id="sw1" x="790" y="586" width="22" height="22" fill="var(--accent)"/>
  <rect id="sw2" x="790" y="626" width="22" height="22" fill="var(--c2)"/>
</svg>
<div class="abs" style="left:{bx-150}px;top:{by-62}px;width:300px;text-align:center"><span id="n45" class="t-hero" style="font-size:84px">4 500</span></div>
{T("u45", bx-150, by+30, "espaciadores revisados", "t-label", 300, "text-align:center")}
{T("l88", bx+150, by+196, "88 con parecido conocido", "t-caption", 260)}
{T("frac", 820, 330, "⅔", "t-hero", 160, "text-align:center;font-size:96px")}
{T("lg1", 826, 580, "virus o plásmidos", "t-label", 360, "font-size:24px")}
{T("lg2", 826, 620, "otras secuencias", "t-label", 360, "font-size:24px")}
{T("dl", 830, 180, "DE LOS 88", "t-caption", 140, "text-align:center;letter-spacing:.08em")}
{foot("Mojica et al., 2005 · J. Mol. Evol., 60, 174–182")}
""", script="""
  S.drop("#vt", .2);
  let e = S.type("#title", .4);
  S.draw("#big5", .8, {dur:1.4});
  S.count("#n45", 4500, 1.2, {dur:1.6});
  S.type("#u45", 1.6, {});
  S.pop("#sm5", 2.6, {dur:.5});
  S.type("#dl", 2.8, {letter:.03});
  e = S.ring("#ring5", 3.0, {dur:2.0, origin:"900 395"});
  S.type("#frac", 4.4, {});
  e = S.rotulo("#sm5", "#l5", "#l88", 5.6, {letter:.03});
  S.pop("#sw1, #sw2", 6.4, {stagger:.3, dur:.35});
  e = S.type("#lg1", 6.6, {letter:.03});
  e = S.type("#lg2", e + .05, {letter:.03});
  S.type("#foot", e + .2, {letter:.012});
""")
# rotulo vuelve a hacer pop del círculo: lo sacamos del rotulo usando un punto propio
slides[5]["script"] = slides[5]["script"].replace('S.rotulo("#sm5", "#l5", "#l88", 5.6, {letter:.03});',
    'S.draw("#l5", 5.6, {dur:.5}); e = S.type("#l88", 6.1, {letter:.03});')

# ───────────── 06 · HALLAZGO 2 · DANISCO 2007 ─────────────
chain = "".join(f'<circle class="line cc" cx="{110+i*56}" cy="{330+(8 if i%2 else -8)}" r="26" transform="rotate(-90 {110+i*56} {330+(8 if i%2 else -8)})"/>' for i in range(6))
arr6, xe6 = array("a6", 640, 300, 56, "RSRSRSR", rep_w=36, sp_w=96,
                  colors=["var(--accent)", "var(--c2)", "var(--c3)", "var(--c1)"])
slides[6] = dict(body=f"""
{T("kick", 64, 30, "HALLAZGO 2 · BARRANGOU ET AL., 2007", "t-caption", None, "letter-spacing:.08em")}
{T("title", 64, 62, "La prueba salió de una fábrica de yogurt", "t-title")}
<svg width="1280" height="720">
  {chain}
  {bank(PHAGE, "ph1", 166 - 30, 300 - 104, 60, 104, drop_clipped=True)[0]}
  {bank(PHAGE, "ph2", 334 - 30, 300 - 104, 60, 104, drop_clipped=True)[0]}
  {bank("cc-by-3.0/General_items/Servier/yoghurt.svg", "yg", 488, 352, 62, 92)[0]}
  <path id="ar6" class="line" d="M460 330 L590 330 M576 318 L590 330 L576 342"/>
  {arr6}
  <circle id="d6" cx="{640+78+36+48}" cy="292" r="6" fill="#fff"/>
  <path id="l6" class="line thin" d="M{640+78+36+48} 286 L{640+78+36+48} 222 L{640+78+36+80} 222"/>
</svg>
{T("lch", 80, 384, "<i>S. thermophilus</i> atacada por fagos", "t-caption", 360)}
{T("h6", 640+78+36+90, 204, "espaciador nuevo = ADN del fago", "t-caption", 340)}
{table("tb", 64, 450, [150, 470, 520], ["GEN", "SI FALTA", "FUNCIÓN"], [
    ["cas7", "no se gana resistencia", "crea espaciadores nuevos"],
    ["cas9", "se pierde la resistencia", 'corta: es la <span class="acc">tijera</span>']], rowh=64, fs=25)}
{foot("Barrangou et al., 2007 · Science, 315, 1709–1712")}
""", script="""
  let e = S.rise("#title", .1, {stagger:.028});
  S.type("#kick", .4, {letter:.015});
  S.draw(".cc", .6, {dur:.6, stagger:.1});
  S.build("#ph1", 1.4, {span:.6, dur:.45}); S.build("#ph2", 1.6, {span:.6, dur:.45});
  S.build("#yg", 2.4, {span:.5, dur:.5});
  S.type("#lch", 2.3, {letter:.025});
  e = S.draw("#ar6", 3.0, {dur:.5});
  e = S.draw(".a6-o", 3.2, {dur:.6, stagger:.07});
  S.draw(".a6-hatch", 3.9, {dur:.25, stagger:.02});
  e = S.grow(".a6-f", e, {axis:"x", dur:.5, stagger:.12});
  """ + table_anim("tb", 5.4, 2, .022) + """
  e = S.rotulo("#d6", "#l6", "#h6", window._tEnd + .1, {letter:.025});
  S.type("#foot", 4.6, {letter:.01});
""")

# ───────────── 07 · HALLAZGO 3 · MARRAFFINI 2008 ─────────────
slides[7] = dict(body=f"""
{T("kick", 64, 30, "HALLAZGO 3 · MARRAFFINI Y SONTHEIMER, 2008", "t-caption", None, "letter-spacing:.08em")}
{T("title", 64, 62, "¿El blanco es ARN o ADN?", "t-title")}
<svg width="1280" height="720">
  <rect id="g1" class="line" x="120" y="212" width="250" height="44"/>
  <rect id="g2" class="line fat" style="stroke:var(--accent)" x="370" y="212" width="130" height="44"/>
  <rect id="g3" class="line" x="500" y="212" width="250" height="44"/>
  {"".join(f'<path class="line thin ih" style="stroke:var(--accent)" d="M{380+i*14} 250 L{392+i*14} 218"/>' for i in range(8))}
  {bank("cc-by-3.0/Nucleic_acids/Servier/plasmid.svg", "pl7", 795, 150, 112, 120)[0]}
  <circle id="d7" cx="435" cy="262" r="5" fill="#fff"/><path id="l7" class="line thin" d="M435 268 L435 300 L470 300"/>
</svg>
{T("lg", 925, 196, "gen <i>nes</i> del plásmido", "t-caption", 300)}
{T("li", 480, 286, "intrón autoprocesable insertado", "t-caption", 380)}
{table("tb", 64, 360, [230, 330, 360, 220], ["SI EL BLANCO ES", "EL INTRÓN", "PREDICCIÓN", "RESULTADO"], [
    ["ARN mensajero", "se elimina al procesarse", "la interferencia sigue", "no ocurre"],
    ["ADN", "rompe la coincidencia", "la interferencia cae", '<span class="acc b">observado</span>']], rowh=66, fs=25)}
{T("h7", 64, 584, "CRISPR es una enzima de restricción programable", "t-label")}
{foot("Marraffini y Sontheimer, 2008 · Science, 322, 1843–1845")}
""", script="""
  let e = S.wipeIn("#title", .1);
  S.type("#kick", .5, {letter:.015});
  e = S.draw("#g1, #g2, #g3", .9, {dur:.7, stagger:.25});
  S.draw(".ih", 1.9, {dur:.25, stagger:.03});
  S.build("#pl7", 1.6, {span:.8, dur:.6});
  S.type("#lg", 2.8, {letter:.03});
  e = S.rotulo("#d7", "#l7", "#li", 2.8, {letter:.025});
  """ + table_anim("tb", 4.4, 2, .02) + """
  e = S.halo("#tb-x", window._tEnd) ;
  e = S.type("#h7", e + .1, {letter:.022});
  S.type("#foot", 3.6, {letter:.01});
""")
slides[7]["body"] = slides[7]["body"].replace('<span class="acc b">observado</span>', '<span id="tb-x" class="acc b">observado</span>')

# ───────────── 08 · DESCANSO ─────────────
bcx, bcy = 640, 360
bseg = "".join(f'<path class="line fat" d="M{bcx+260*math.sin(math.radians(i*20+3)):.1f} {bcy-260*math.cos(math.radians(i*20+3)):.1f} A260 260 0 0 1 {bcx+260*math.sin(math.radians(i*20+17)):.1f} {bcy-260*math.cos(math.radians(i*20+17)):.1f}" style="stroke-width:{14 if i%3 else 26}px"/>' for i in range(18))
bdia = "".join(f'<rect x="{bcx+260*math.sin(math.radians(i*20))-6:.1f}" y="{bcy-260*math.cos(math.radians(i*20))-6:.1f}" width="12" height="12" fill="#fff" transform="rotate(45 {bcx+260*math.sin(math.radians(i*20)):.1f} {bcy-260*math.cos(math.radians(i*20)):.1f})"/>' for i in range(18))
inner = "".join(f'<path class="line" d="M{bcx+170*math.sin(math.radians(i*40+6)):.1f} {bcy-170*math.cos(math.radians(i*40+6)):.1f} A170 170 0 0 1 {bcx+170*math.sin(math.radians(i*40+34)):.1f} {bcy-170*math.cos(math.radians(i*40+34)):.1f}"/>' for i in range(9))
slides[8] = dict(brk=1, body=f"""
<svg width="1280" height="720">
  <g id="outer">{bseg}{bdia}</g>
  <g id="inner">{inner}</g>
  <g id="core"><circle class="line thin" cx="{bcx}" cy="{bcy}" r="96" stroke-dasharray="2 9"/>
  <circle cx="{bcx}" cy="{bcy}" r="10" fill="var(--accent)"/></g>
</svg>""", script=f"""
  S.idle("#outer", {{from:{{rotation:0, svgOrigin:"{bcx} {bcy}"}}, to:{{rotation:360, svgOrigin:"{bcx} {bcy}"}}}});
  S.idle("#inner", {{from:{{rotation:0, svgOrigin:"{bcx} {bcy}"}}, to:{{rotation:-360, svgOrigin:"{bcx} {bcy}"}}}});
  S.idle("#core", {{from:{{rotation:0, svgOrigin:"{bcx} {bcy}"}}, to:{{rotation:120, svgOrigin:"{bcx} {bcy}"}}}});
""")

# ───────────── 09 · MECANISMO ─────────────
mcx, mcy, mr = 230, 420, 140
pasos = ["Transcripción del arreglo y el tracrRNA", "Maduración del crRNA guía",
         "Búsqueda en el ADN invasor", "Reconocimiento del PAM", "Corte de las dos hebras"]
mn, ma = [], []
for i in range(5):
    ang = i * 72
    x, y = mcx + mr * math.sin(math.radians(ang)), mcy - mr * math.cos(math.radians(ang))
    mn.append(f'<circle class="mnode" id="mn{i}" cx="{x:.1f}" cy="{y:.1f}" r="30" fill="{"var(--accent)" if i==4 else "var(--bg)"}" stroke="#fff" stroke-width="2"/>')
    a0, a1 = math.radians(ang + 15), math.radians(ang + 57)
    ma.append(f'<path class="line marc" d="M{mcx+mr*math.sin(a0):.1f} {mcy-mr*math.cos(a0):.1f} A{mr} {mr} 0 0 1 {mcx+mr*math.sin(a1):.1f} {mcy-mr*math.cos(a1):.1f}"/>')
numdivs = "".join(T(f"mt{i}", mcx + mr * math.sin(math.radians(i*72)) - 30, mcy - mr * math.cos(math.radians(i*72)) - 18, str(i+1), "t-label b mnum", 60, "text-align:center") for i in range(5))
lista = "".join(T(f"ps{i}", 440, 210 + i * 78, f'<span class="b">{i+1}</span>  {p}', "t-label", 380, "font-size:24px") for i, p in enumerate(pasos))
# ADN detalle (x 860–1220)
ticks = "".join(f'<path class="line thin tk" d="M{872+i*14} 412 L{872+i*14} 468"/>' for i in range(25))
slides[9] = dict(body=f"""
{T("title", 64, 58, "Cómo corta Cas9", "t-title")}
<svg width="1280" height="720">
  {"".join(ma)}{"".join(mn)}
  {bank("cc-by-4.0/Nucleic_acids/DBCLS/CRISPR-CAS9-pink.svg", "cas", 880, 128, 320, 167)[0]}
  <path id="s1" class="line fat" d="M860 410 L1220 410"/>
  <path id="s2" class="line fat" d="M860 470 L1220 470"/>
  {ticks}
  <rect id="pam" class="line fat" style="stroke:var(--accent)" x="1110" y="460" width="70" height="20" rx="4"/>
  <path id="guide" class="line" style="stroke:var(--c2);stroke-dasharray:6 6" d="M880 382 L1080 382"/>
  <path id="cut1" class="line fat" style="stroke:var(--accent)" d="M1068 396 L1076 410 L1068 424"/>
  <path id="cut2" class="line fat" style="stroke:var(--accent)" d="M1068 456 L1076 470 L1068 484"/>
  <path id="cot9" class="line thin" d="M1072 510 L1072 526 M1072 518 L1110 518 M1110 510 L1110 526"/>
</svg>
{numdivs}{lista}
{T("lpam", 1112, 488, "PAM", "t-caption b", 80, "color:var(--accent)")}
{T("lgd", 900, 344, "ARN guía", "t-caption", 200)}
<div class="abs" style="left:1040px;top:530px;width:110px;text-align:center"><span id="n3" class="t-big">3</span><span id="u3" class="t-caption"> nt</span></div>
{T("lcut", 900, 600, "corte a 3 nt del PAM", "t-label", 330, "font-size:24px")}
{foot("Gasiunas et al., 2012 · Jinek et al., 2012")}
""", script="""
  let e = S.tracking("#title", .2, {dur:1.3});
  S.pop(".mnode", .6, {stagger:.28, dur:.4});
  S.pop(".mnum", .7, {stagger:.28, dur:.4});
  S.draw(".marc", .8, {dur:.4, stagger:.28});
  S.build("#cas", 1.6, {span:1.0, dur:.7});
  e = S.draw("#s1, #s2", 2.6, {dur:1.0, stagger:.15});
  S.draw(".tk", 3.0, {dur:.25, stagger:.02});
  S.draw("#pam", 3.5, {dur:.6});
  S.type("#lpam", 4.0, {});
  S.draw("#guide", 3.8, {dur:.8});
  S.type("#lgd", 4.4, {letter:.03});
  e = 5.0;
  for (let i = 0; i < 5; i++) e = S.type("#ps" + i, e + .08, {letter:.02});
  S.draw("#cut1, #cut2", e + .1, {dur:.35, stagger:.12});
  S.draw("#cot9", e + .5, {dur:.4});
  S.count("#n3", 3, e + .7, {dur:.6}); S.type("#u3", e + .7, {});
  S.type("#lcut", e + 1.0, {letter:.025});
  S.type("#foot", 4.6, {letter:.01});
""")

# ───────────── 10 · HALLAZGO 4 · 2012–2013 ─────────────
base = 560
bub = [("Zhang", "humano y ratón", 16, 190), ("Church", "humano", 7, 400), ("Kim", "humano", 2, 545)]
rmax = 118
bsvg, blab = [], []
for i, (who, cel, n, x) in enumerate(bub):
    r = rmax * math.sqrt(n / 16)
    bsvg.append(f'<circle class="line bb" cx="{x}" cy="{base-r:.1f}" r="{r:.1f}" transform="rotate(90 {x} {base-r:.1f})" style="{"stroke:var(--accent);stroke-width:3" if i==0 else ""}"/>')
    blab.append(f'<div class="abs" style="left:{x-60}px;top:{base-r-26:.0f}px;width:120px;text-align:center"><span id="bn{i}" class="t-big {"acc" if i==0 else ""}" style="font-size:{44 if i<2 else 30}px">{n}</span></div>')
    blab.append(T(f"bl{i}", x - 80, base + 14, f'<span class="b">{who}</span><br>{cel}', "t-caption", 160, "text-align:center;color:#fff"))
assert (16, 7, 2) == tuple(b[2] for b in bub)
slides[10] = dict(body=f"""
{T("kick", 64, 30, "HALLAZGO 4 · 2012–2013", "t-caption", None, "letter-spacing:.08em")}
{T("title", 64, 62, "Del tubo de ensayo a la célula humana", "t-title")}
<svg width="1280" height="720"><path id="base" class="line thin" d="M60 {base} L640 {base}"/>{"".join(bsvg)}</svg>
{"".join(blab)}
{T("bh", 64, 160, "SITIOS EDITADOS EN CÉLULAS", "t-caption", None, "letter-spacing:.08em")}
{table("tb", 680, 170, [140, 190, 236], ["FECHA", "GRUPO", "HITO"], [
    ["6 abr 2012", "Siksnys", "envía el corte in vitro; Cell lo rechaza"],
    ["28 jun 2012", "Charpentier y Doudna", "ARN guía único, Science"],
    ["4 sep 2012", "Siksnys", "sale en PNAS"],
    ["3 ene 2013", "Zhang · Church", "edición en células humanas"]], rowh=88, fs=21, hfs=19)}
{foot("Cong et al., 2013 · Mali et al., 2013 · Cho et al., 2013")}
""", script="""
  let e = S.type("#title", .1, {letter:.03});
  S.type("#kick", .4, {letter:.015});
  S.draw("#base", .8, {dur:.8});
  S.draw(".bb", 1.1, {dur:1.0, stagger:.3});
  S.type("#bh", 1.6, {letter:.02});
  S.count("#bn0", 16, 1.6, {dur:1.3}); S.count("#bn1", 7, 1.9, {dur:1.1}); S.count("#bn2", 2, 2.2, {dur:.9});
  S.type("#bl0, #bl1, #bl2", 3.5, {letter:.022});
  """ + table_anim("tb", 4.4, 4, .018) + """
  S.type("#foot", window._tEnd + .1, {letter:.01});
""")

# ───────────── 11 · QUÉ SIGNIFICA ─────────────
cxs = [250, 640, 1030]
net = "".join(f'<path class="line thin ic1" d="M{a[0]} {a[1]} L{b[0]} {b[1]}"/>' for a, b in [((200,350),(250,300)),((250,300),(305,345)),((200,350),(232,420)),((305,345),(290,425)),((232,420),(290,425)),((250,300),(262,372)),((262,372),(232,420)),((262,372),(290,425))])
netd = "".join(f'<circle class="ic1d" cx="{x}" cy="{y}" r="9" fill="#fff"/>' for x, y in [(200,350),(250,300),(305,345),(232,420),(290,425),(262,372)])
seq = "".join(f'<path class="line ic2" d="M{580} {300+i*22} L{580+w} {300+i*22}"/>' for i, w in enumerate([120, 80, 110, 60, 100, 90]))
seqh = '<path class="line fat ic2" style="stroke:var(--accent)" d="M600 366 L670 366"/>'
tgt = '<circle class="line ic3" cx="1060" cy="345" r="34"/><circle class="line ic3" cx="1060" cy="345" r="14"/><path class="line ic3" d="M965 420 C990 330, 1010 300, 1040 300 M1030 292 L1042 300 L1032 312"/>'
slides[11] = dict(body=f"""
{T("title", 64, 58, 'La edición genómica se <span class="acc">acumuló</span>', "t-title")}
<svg width="1280" height="720">
  {"".join(f'<circle class="line big3" cx="{x}" cy="360" r="150" transform="rotate(-90 {x} 360)"/>' for x in cxs)}
  {net}{netd}
  {bank("cc-by-4.0/Nucleic_acids/DBCLS/DNA_monochrome.svg", "dna11", 640-95, 360-95, 190, 190)[0]}
  {bank("cc-by-3.0/General_items/Servier/salt.svg", "salt", 965, 292, 60, 120)[0]}
  {bank("cc-by-3.0/General_items/Servier/yoghurt.svg", "yg11", 1040, 300, 76, 112)[0]}
</svg>
{T("k1", cxs[0]-160, 540, "Distribuida", "t-label b", 320, "text-align:center")}
{T("k2", cxs[1]-160, 540, "Bioinformática", "t-label b", 320, "text-align:center")}
{T("k3", cxs[2]-160, 540, "Orígenes ajenos", "t-label b", 320, "text-align:center")}
{T("q1", cxs[0]-170, 582, "ningún laboratorio hizo la ruta completa", "t-caption", 340, "text-align:center")}
{T("q2", cxs[1]-170, 582, "el motor fue el análisis de secuencias", "t-caption", 340, "text-align:center")}
{T("q3", cxs[2]-170, 582, "salinas, defensa y yogurt", "t-caption", 340, "text-align:center")}
{foot()}
""", script="""
  let e = S.rise("#title", .2, {stagger:.035});
  S.draw(".big3", .6, {dur:1.2, stagger:.3});
  S.draw(".ic1", 2.0, {dur:.35, stagger:.06}); S.pop(".ic1d", 2.3, {stagger:.06, dur:.3});
  S.build("#dna11", 2.5, {span:.9, dur:.6});
  S.build("#salt", 3.0, {span:.7, dur:.5}); S.build("#yg11", 3.3, {span:.6, dur:.5});
  e = 4.6;
  for (const k of ["1", "2", "3"]) { e = S.type("#k" + k, e + .05, {letter:.03}); e = S.type("#q" + k, e + .05, {letter:.022}); }
  S.type("#foot", e + .1, {letter:.01});
""")

# ───────────── 12 · RAMA DE MICROBIOLOGÍA ─────────────
vv = [(250, 340), (400, 340), (325, 465)]
slides[12] = dict(body=f"""
{T("title", 64, 58, "A qué microbiología pertenece", "t-title")}
<svg width="1280" height="720">
  {"".join(f'<circle class="line vv" cx="{x}" cy="{y}" r="135" transform="rotate(-90 {x} {y})"/>' for x, y in vv)}
  <circle id="vc" cx="325" cy="382" r="9" fill="var(--accent)"/>
</svg>
{T("w1", 128, 300, "Molecular", "t-label", 150, "font-size:24px")}
{T("w2", 405, 296, "Alimentaria<br>e industrial", "t-label", 150, "font-size:22px")}
{T("w3", 255, 540, "Básica", "t-label", 140, "text-align:center;font-size:24px")}
{table("tb", 640, 210, [250, 360], ["RAMA", "POR QUÉ"], [
    ["Molecular", "inmunidad adaptativa procariota"],
    ["Alimentaria e industrial", 'prueba en la bacteria del <span class="acc">yogurt</span> (Danisco)'],
    ["Básica", "el hallazgo no buscaba aplicación"]], rowh=92, fs=25)}
{foot()}
""", script="""
  let e = S.stamp("#title", .2);
  S.draw(".vv", .6, {dur:1.2, stagger:.3});
  S.type("#w1, #w2, #w3", 2.2, {letter:.03});
  S.pop("#vc", 3.3, {dur:.4});
  """ + table_anim("tb", 3.8, 3, .022) + """
  e = S.halo("#vc", window._tEnd + .1);
  S.type("#foot", 3.0, {letter:.01});
""")

# ───────────── 13 · ANÁLISIS CRÍTICO ─────────────
slides[13] = dict(body=f"""
{T("vt", 26, 64, "Análisis crítico", "vert")}
{T("title", 92, 58, "Lo demostrado y lo interpretado", "t-title")}
<svg width="1280" height="720">
  <circle id="cd" class="line" cx="215" cy="345" r="115" transform="rotate(-90 215 345)"/>
  <circle id="ci" class="line fat" style="stroke:var(--accent)" cx="465" cy="345" r="115" transform="rotate(-90 465 345)"/>
  <circle id="d13" cx="465" cy="468" r="6" fill="#fff"/><path id="l13" class="line thin" d="M465 474 L465 520 L430 520"/>
</svg>
{T("c1", 135, 300, '<span class="b">Demostrado</span><br><span class="t-caption" style="color:#fff">experimentos citados</span>', "t-label", 160, "text-align:center;font-size:24px")}
{T("c2", 385, 300, '<span class="b">Interpretado</span><br><span class="t-caption" style="color:#fff">orden y crédito</span>', "t-label", 160, "text-align:center;font-size:24px")}
{T("h13", 120, 504, "aquí cayó la disputa", "t-label", 300, "text-align:right;font-size:24px")}
{table("tb", 640, 170, [190, 410], ["", ""], [
    ["Fortaleza", "fuentes primarias inéditas; rescata laboratorios olvidados"],
    ["Límite", "el autor dirige el Broad, con patentes en disputa; conflicto no declarado"],
    ["Respuesta", "Doudna: la descripción de su laboratorio es incorrecta"]], rowh=110, fs=24)}
{foot()}
""", script="""
  S.drop("#vt", .2);
  let e = S.type("#title", .4, {letter:.03});
  S.draw("#cd, #ci", .9, {dur:1.2, stagger:.35});
  S.type("#c1", 2.4, {letter:.025}); S.type("#c2", 3.0, {letter:.025});
  """ + table_anim("tb", 3.8, 3, .017) + """
  e = S.rotulo("#d13", "#l13", "#h13", window._tEnd + .1, {letter:.03});
  S.type("#foot", 2.6, {letter:.01});
""")
slides[13]["body"] = slides[13]["body"].replace(
    '<div class="abs tb-h" style="left:640px;top:170px;width:170px;font-size:20px;font-weight:400;letter-spacing:.06em;color:var(--soft)"></div>', "")

# ───────────── 14 · CIERRE ─────────────
slides[14] = dict(body=f"""
<svg width="1280" height="720"><path id="r14" class="line" d="M96 150 L360 150"/></svg>
{T("cl", 96, 190, 'La herramienta que hoy edita genomas humanos salió de una arquea de salina, un laboratorio de defensa y una fábrica de <span class="acc">yogurt</span>.', "t-title", 1090, "font-size:60px;line-height:1.18")}
{foot()}
""", script="""
  S.draw("#r14", .3, {dur:.8});
  let e = S.rise("#cl", .6, {stagger:.028});
  S.type("#foot", e + .2, {letter:.012});
""")

# ───────────── 15 · REFERENCIAS ─────────────
refs = [
 "Barrangou, R., Fremaux, C., Deveau, H., Richards, M., Boyaval, P., Moineau, S., Romero, D. A., y Horvath, P. (2007). CRISPR provides acquired resistance against viruses in prokaryotes. <i>Science, 315</i>, 1709–1712.",
 "Cho, S. W., Kim, S., Kim, J. M., y Kim, J.-S. (2013). Targeted genome engineering in human cells with the Cas9 RNA-guided endonuclease. <i>Nature Biotechnology, 31</i>, 230–232.",
 "Cong, L., Ran, F. A., Cox, D., Lin, S., Barretto, R., Habib, N., Hsu, P. D., Wu, X., Jiang, W., Marraffini, L. A., y Zhang, F. (2013). Multiplex genome engineering using CRISPR/Cas systems. <i>Science, 339</i>, 819–823.",
 "Gasiunas, G., Barrangou, R., Horvath, P., y Siksnys, V. (2012). Cas9–crRNA ribonucleoprotein complex mediates specific DNA cleavage for adaptive immunity in bacteria. <i>PNAS, 109</i>, E2579–E2586.",
 "Jinek, M., Chylinski, K., Fonfara, I., Hauer, M., Doudna, J. A., y Charpentier, E. (2012). A programmable dual-RNA-guided DNA endonuclease in adaptive bacterial immunity. <i>Science, 337</i>, 816–821.",
 "Lander, E. S. (2016). The heroes of CRISPR. <i>Cell, 164</i>(1–2), 18–28. https://doi.org/10.1016/j.cell.2015.12.041",
 "Mali, P., Yang, L., Esvelt, K. M., Aach, J., Guell, M., DiCarlo, J. E., Norville, J. E., y Church, G. M. (2013). RNA-guided human genome engineering via Cas9. <i>Science, 339</i>, 823–826.",
 "Marraffini, L. A., y Sontheimer, E. J. (2008). CRISPR interference limits horizontal gene transfer in staphylococci by targeting DNA. <i>Science, 322</i>, 1843–1845.",
 "Mojica, F. J. M., Juez, G., y Rodríguez-Valera, F. (1993). Transcription at different salinities of <i>Haloferax mediterranei</i> sequences adjacent to partially modified PstI sites. <i>Molecular Microbiology, 9</i>, 613–621.",
 "Mojica, F. J. M., Díez-Villaseñor, C., García-Martínez, J., y Soria, E. (2005). Intervening sequences of regularly spaced prokaryotic repeats derive from foreign genetic elements. <i>Journal of Molecular Evolution, 60</i>, 174–182.",
]
colA = "".join(f'<p class="rA" style="margin-bottom:14px;padding-left:22px;text-indent:-22px">{r}</p>' for r in refs[:5])
colB = "".join(f'<p class="rB" style="margin-bottom:14px;padding-left:22px;text-indent:-22px">{r}</p>' for r in refs[5:])
slides[15] = dict(body=f"""
{T("title", 64, 48, "Referencias", "t-label")}
<svg width="1280" height="720"><path id="r15" class="line thin" d="M64 92 L1216 92"/></svg>
<div class="abs t-refs" style="left:64px;top:118px;width:560px;font-size:17px">{colA}</div>
<div class="abs t-refs" style="left:656px;top:118px;width:560px;font-size:17px">{colB}</div>
{T("cred", 64, 662, "Ilustraciones adaptadas de Bioicons: DBCLS (CC BY 4.0) y Servier Medical Art (CC BY 3.0).", "t-caption")}
""", script="""
  let e = S.type("#title", .2);
  S.draw("#r15", .4, {dur:.9});
  S.type(".rA", 1.0, {letter:.034, minLetter:.03, parallel:true, gap:.25});
  S.type(".rB", 1.1, {letter:.034, minLetter:.03, parallel:true, gap:.25});
  S.type("#cred", 6.6, {letter:.034, minLetter:.032});
""")

os.chdir(os.path.dirname(os.path.abspath(__file__)))
for n, s in slides.items():
    html = HEAD.format(brk=s.get("brk", 0), body=s["body"], script=s["script"])
    open(f"slide_{n:02d}.html", "w").write(html)
print("ok", len(slides), "slides")
