// mito.js — mitocondria en monolínea por código (viewBox 0 0 680 430).
// Mito.build(svg) crea los grupos #<p>ext, #<p>int, #<p>cr, #<p>st, #<p>gr, #<p>adn
// en el orden en que los trazaría la mano. No anima nada: eso lo decide la slide.
window.Mito = {
  build(svg, p = "m-") {
    const NS = "http://www.w3.org/2000/svg";
    const g = (id) => { const e = document.createElementNS(NS, "g"); e.id = p + id; svg.appendChild(e); return e; };
    const add = (G, tag, at) => { const e = document.createElementNS(NS, tag); for (const k in at) e.setAttribute(k, at[k]); G.appendChild(e); return e; };
    const ext = g("ext"), int = g("int"), cr = g("cr"), st = g("st"), gr = g("gr"), adn = g("adn");
    // membrana externa (bicapa = dos líneas) y membrana interna
    add(ext, "path", { class: "line", d: "M215 30 H465 A185 185 0 0 1 465 400 H215 A185 185 0 0 1 215 30 Z" });
    add(ext, "path", { class: "line thin", d: "M215 42 H465 A173 173 0 0 1 465 388 H215 A173 173 0 0 1 215 42 Z" });
    add(int, "path", { class: "line", d: "M215 66 H465 A149 149 0 0 1 465 364 H215 A149 149 0 0 1 215 66 Z" });
    // crestas: pliegues de la membrana interna, alternando arriba/abajo, con su lumen
    [[158, 1, 196], [218, -1, 236], [278, 1, 206], [338, -1, 226], [398, 1, 206], [458, -1, 236], [518, 1, 196]].forEach(([x, d, tip]) => {
      const y0 = d > 0 ? 66 : 364, q = d > 0 ? tip + 26 : tip - 26;
      add(cr, "path", { class: "line", d: `M${x} ${y0} V${tip} Q${x + 12} ${q} ${x + 24} ${tip} V${y0}` });
      add(cr, "path", { class: "line thin", d: `M${x + 6} ${y0} V${tip} Q${x + 12} ${q - d * 12} ${x + 18} ${tip} V${y0}` });
      for (let y = y0 + d * 26; d > 0 ? y < tip - 6 : y > tip + 6; y += d * 30) {   // ATP sintasas hacia la matriz
        add(st, "path", { class: "line thin", d: `M${x + 24} ${y} h7` });
        add(st, "circle", { class: "line thin", cx: x + 34, cy: y, r: 3.2 });
      }
    });
    // matriz: gránulos y ribosomas
    [[120, 250, 7], [250, 150, 5], [320, 300, 6], [440, 140, 5], [560, 270, 7], [500, 322, 4], [200, 300, 4], [380, 118, 4], [612, 210, 3], [86, 214, 3]]
      .forEach(([cx, cy, r]) => add(gr, "circle", { class: "line thin", cx, cy, r }));
    // ADN mitocondrial (circular)
    add(adn, "path", { class: "line thin", d: "M100 170 c-14 -18 22 -34 30 -12 c8 22 -20 32 -30 12 Z" });
    add(adn, "path", { class: "line thin", d: "M585 180 c-14 -18 22 -34 30 -12 c8 22 -20 32 -30 12 Z" });
    return { ext, int, cr, st, gr, adn };
  },

  // Traza la mitocondria completa a partir de t; devuelve cuándo termina.
  draw(S, p, t, k = 1) {
    S.draw(`#${p}ext path`, t, { dur: 1.4 * k, stagger: 0.35 * k });
    S.draw(`#${p}int path`, t + 0.9 * k, { dur: 1.2 * k });
    S.draw(`#${p}cr path`, t + 1.6 * k, { dur: 0.6 * k, stagger: 0.06 * k });
    S.draw(`#${p}st path, #${p}st circle`, t + 2.6 * k, { dur: 0.3 * k, stagger: 0.01 * k });
    S.pop(`#${p}gr circle`, t + 3.1 * k, { stagger: 0.05 * k });
    return S.draw(`#${p}adn path`, t + 3.3 * k, { dur: 0.7 * k, stagger: 0.2 * k });
  },
};
