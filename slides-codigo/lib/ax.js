// actina.js — piezas Harper's Bazaar por código para el deck de actina.
// Esferas negras con halftone + brillo (como perlas), hélice de F-actina,
// destellos de 4 puntas, red ramificada (Arp2/3) y generador determinista.
window.AX = (() => {
  const NS = "http://www.w3.org/2000/svg";
  const el = (p, tag, at = {}) => { const e = document.createElementNS(NS, tag); for (const k in at) e.setAttribute(k, at[k]); p.appendChild(e); return e; };

  // RNG determinista: el mismo deck sale idéntico en cada render
  const rng = (seed) => () => { seed = (seed * 16807) % 2147483647; return (seed - 1) / 2147483646; };

  // defs compartidos: trama halftone + máscara radial (luz arriba-izquierda)
  function defs() {
    const s = el(document.getElementById("stage"), "svg", { class: "abs frame-a", width: 0, height: 0, style: "left:0;top:0" });
    const d = el(s, "defs");
    const p = el(d, "pattern", { id: "ht", width: 4.2, height: 4.2, patternUnits: "userSpaceOnUse", patternTransform: "rotate(30)" });
    el(p, "circle", { cx: 2.1, cy: 2.1, r: 1.25, fill: "#fff" });
    const pk = el(d, "pattern", { id: "htk", width: 6, height: 6, patternUnits: "userSpaceOnUse", patternTransform: "rotate(30)" });
    el(pk, "circle", { cx: 3, cy: 3, r: 1.7, fill: "#000" });
    const g = el(d, "radialGradient", { id: "hg", cx: "0.34", cy: "0.3", r: "0.75" });
    el(g, "stop", { offset: "0", "stop-color": "#fff" });
    el(g, "stop", { offset: "0.5", "stop-color": "#888" });
    el(g, "stop", { offset: "1", "stop-color": "#000" });
    const m = el(d, "mask", { id: "hm", maskContentUnits: "objectBoundingBox" });
    el(m, "rect", { x: 0, y: 0, width: 1, height: 1, fill: "url(#hg)" });
    // degradado halftone lineal (para siluetas grandes): denso abajo, ralo arriba
    const lg = el(d, "linearGradient", { id: "lg", x1: 0, y1: 1, x2: 0, y2: 0 });
    el(lg, "stop", { offset: "0", "stop-color": "#fff" }); el(lg, "stop", { offset: "1", "stop-color": "#000" });
    const lm = el(d, "mask", { id: "lm", maskContentUnits: "objectBoundingBox" });
    el(lm, "rect", { x: 0, y: 0, width: 1, height: 1, fill: "url(#lg)" });
  }

  // esfera = negro + halftone blanco enmascarado + brillo especular. Devuelve el <g>.
  function sphere(p, cx, cy, r, cls = "sph") {
    const g = el(p, "g", { class: cls });
    el(g, "circle", { cx, cy, r, fill: "#000" });
    el(g, "circle", { cx, cy, r: r * 0.96, fill: "url(#ht)", mask: "url(#hm)" });
    el(g, "ellipse", { cx: cx - r * 0.36, cy: cy - r * 0.42, rx: r * 0.24, ry: r * 0.15, fill: "#fff", transform: `rotate(-30 ${cx - r * 0.36} ${cy - r * 0.42})` });
    return g;
  }

  // F-actina: dos protofilamentos enrollados. Pinta por profundidad, devuelve el orden de ENSAMBLE (por x).
  function helix(p, { x0, y0, len, r = 18, step, amp, period, angle = 0, cls = "sph" }) {
    step = step || r * 1.55; amp = amp || r * 0.85; period = period || step * 14;
    const g = el(p, "g", { transform: `rotate(${angle} ${x0} ${y0})` });
    const items = [];
    for (let s = 0; s < 2; s++) {
      for (let x = s * step / 2; x <= len; x += step) {
        const ph = 2 * Math.PI * x / period + s * Math.PI;
        items.push({ x, y: amp * Math.sin(ph), z: Math.cos(ph) });
      }
    }
    items.sort((a, b) => a.z - b.z).forEach((it) => { it.g = sphere(g, x0 + it.x, y0 + it.y, r * (0.86 + 0.14 * (it.z + 1) / 2), cls); });
    return { g, order: items.slice().sort((a, b) => a.x - b.x).map((it) => it.g), items };
  }

  // destello de 4 puntas (cóncavo) + rayos finos
  function sparkle(p, cx, cy, s, fill = "#fff", stroke = "#000", cls = "spk") {
    const g = el(p, "g", { class: cls });
    const k = s * 0.12;
    el(g, "path", { d: `M${cx} ${cy - s}Q${cx + k} ${cy - k} ${cx + s} ${cy}Q${cx + k} ${cy + k} ${cx} ${cy + s}Q${cx - k} ${cy + k} ${cx - s} ${cy}Q${cx - k} ${cy - k} ${cx} ${cy - s}Z`, fill, stroke, "stroke-width": 1.2 });
    el(g, "path", { d: `M${cx - s * 1.35} ${cy}H${cx + s * 1.35}M${cx} ${cy - s * 1.35}V${cy + s * 1.35}`, stroke: "#000", "stroke-width": 1, opacity: 0.9 });
    return g;
  }

  // red ramificada tipo lamelipodio: madres hacia la membrana, hijas a 70°
  function branched(p, { x0, x1, yBase, yTop, n = 7, seed = 3, w = 3 }) {
    const R = rng(seed), mothers = [], kids = [];
    for (let i = 0; i < n; i++) {
      const bx = x0 + (x1 - x0) * (i + 0.5) / n + (R() - 0.5) * 20;
      const a = ((i % 2 ? 1 : -1) * (14 + R() * 10)) * Math.PI / 180;  // respecto a la vertical
      const L = (yBase - yTop) / Math.cos(a);
      const ex = Math.min(x1 + 10, Math.max(x0 - 10, bx + Math.sin(a) * L)), ey = yTop;
      mothers.push(el(p, "path", { class: "fil", d: `M${bx} ${yBase}L${ex} ${ey}`, stroke: "#000", "stroke-width": w, "stroke-linecap": "round", fill: "none" }));
      for (let b = 0; b < 2; b++) {
        const t = 0.3 + R() * 0.45, px = bx + (ex - bx) * t, py = yBase + (ey - yBase) * t;
        const ba = a + (R() > 0.5 ? 1 : -1) * 70 * Math.PI / 180, bl = 45 + R() * 40;
        let qx = px + Math.sin(ba) * bl, qy = py - Math.cos(ba) * bl;
        qy = Math.max(qy, yTop + 4); qx = Math.min(x1 + 16, Math.max(x0 - 16, qx));
        kids.push(el(p, "path", { class: "fil", d: `M${px} ${py}L${qx} ${qy}`, stroke: "#000", "stroke-width": w * 0.8, "stroke-linecap": "round", fill: "none" }));
      }
    }
    return { mothers, kids };
  }

  // ── SVG del banco (Servier vía Bioicons), ya pasado a Harper por prep.py ──
  // mount: lo coloca en (x, y) con ancho w; devuelve sus piezas ordenadas de mayor a menor
  // (se construye de lo grande a lo pequeño, como `dibujar` de Cosmos).
  function bank(tplId, { x, y, w, rot = 0, frameA = false, id }) {
    const host = document.createElement("div");
    host.className = "abs" + (frameA ? " frame-a" : "");
    if (id) host.id = id;
    host.style.cssText += `left:${x}px;top:${y}px;width:${w}px;` + (rot ? `transform:rotate(${rot}deg);transform-origin:50% 50%;` : "");
    host.innerHTML = document.getElementById(tplId).innerHTML;
    document.getElementById("stage").appendChild(host);
    const svg = host.querySelector("svg");
    svg.style.width = "100%"; svg.style.height = "auto"; svg.style.display = "block"; svg.style.overflow = "visible";
    const pieces = [...svg.querySelectorAll(".pf, .ps")].filter((e) => !e.closest("defs, clipPath, mask, pattern"));
    const area = (e) => { try { const b = e.getBBox(); return b.width * b.height; } catch (_) { return 0; } };
    pieces.forEach((e) => (e.__a = area(e)));
    pieces.sort((a, b) => b.__a - a.__a);
    return { host, svg, pieces };
  }

  // build: cada pieza traza su contorno y luego se rellena, de lo grande a lo pequeño, en `dur` s.
  // Los trazos sueltos (sin relleno) se dibujan. Devuelve el instante en que termina.
  function build(S, pieces, t, dur, { piece = 0.55 } = {}) {
    const n = pieces.length, st = n > 1 ? Math.max(0, (dur - piece) / (n - 1)) : 0;
    pieces.forEach((e, i) => {
      e.__sc = true;
      const ti = t + i * st;
      if (e.classList.contains("pt")) S.tl.fromTo(e, { drawSVG: "0%" }, { drawSVG: "100%", duration: piece, ease: "power2.inOut" }, ti);
      if (e.classList.contains("pf")) S.tl.fromTo(e, { fillOpacity: 0 }, { fillOpacity: 1, duration: piece * 0.6, ease: "power1.out" }, ti + piece * 0.55);
    });
    return t + dur;
  }

  return { el, rng, defs, sphere, helix, sparkle, branched, bank, build };
})();
