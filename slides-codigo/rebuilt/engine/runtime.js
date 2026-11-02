/* slides-codigo · motor mínimo escrito desde cero (GSAP 3.13 + DrawSVG + SplitText)
   Cada verbo devuelve el instante en que termina. Todo es determinista: SC.seek(t). */
(function () {
  gsap.registerPlugin(DrawSVGPlugin, SplitText);
  const tl = gsap.timeline({ paused: true });
  const customs = [];              // efectos evaluados a mano en seek (contadores)
  const stage = () => document.getElementById("stage");
  const $ = (q) => (typeof q === "string" ? Array.from(document.querySelectorAll(q))
                   : Array.isArray(q) ? q.flatMap($) : q instanceof Element ? [q] : Array.from(q));
  const mark = (els) => els.forEach((e) => (e.__sc = true));
  const SHAPES = "path,line,circle,rect,polyline,polygon,ellipse";
  const shapesOf = (els) => els.flatMap((e) => (e.matches(SHAPES) ? [e] : Array.from(e.querySelectorAll(SHAPES))));
  const opens = [];
  const note = (v, t) => opens.push([t, v]);
  function split(els, type, extra) {
    return els.map((e) => new SplitText(e, Object.assign({ type: type || "words,chars", wordsClass: "w", charsClass: "ch", linesClass: "ln" }, extra || {})));
  }
  function rectOf(el) {
    const s = stage().getBoundingClientRect(), r = el.getBoundingClientRect();
    return { x: r.left - s.left, y: r.top - s.top, w: r.width, h: r.height };
  }
  function addDiv(css) {
    const d = document.createElement("div");
    d.className = "abs";
    Object.assign(d.style, css);
    d.__sc = true;
    stage().appendChild(d);
    return d;
  }

  function typewriter(el, chars, s0, L, o) {
    const st = stage().getBoundingClientRect();
    const R = chars.map((c) => { const r = c.getBoundingClientRect(); return { x: r.left - st.left, y: r.top - st.top, w: r.width, h: r.height }; });
    const vertical = getComputedStyle(el).writingMode.startsWith("vertical");
    const n = chars.length, end = s0 + n * L;
    gsap.set(chars, { transformOrigin: "50% 80%" });
    tl.fromTo(chars, { autoAlpha: 0, scale: o.strike ?? 1.45, yPercent: -10 },
      { autoAlpha: 1, scale: 1, yPercent: 0, duration: 0.14, stagger: L, ease: "power3.out" }, s0);
    flash(chars, s0, L);
    const cw = o.caret ?? 2.5;
    const caret = document.createElement("div");
    caret.className = "abs"; caret.__sc = true;
    Object.assign(caret.style, { background: "var(--accent)", visibility: "hidden", zIndex: 6, borderRadius: "1px" });
    stage().appendChild(caret);
    customs.push((T) => {
      if (T < s0 - 0.3 || T > end + 0.55) { caret.style.visibility = "hidden"; return; }
      const idx = Math.min(n - 1, Math.floor((T - s0) / L));
      const r = R[Math.max(0, idx)];
      let x, y, w, h;
      if (vertical) { w = r.w * 0.9; h = cw; x = r.x + r.w * 0.05; y = idx < 0 ? r.y + r.h + 2 : r.y - cw - 2; }
      else { w = cw; h = r.h * 0.82; y = r.y + r.h * 0.12; x = idx < 0 ? r.x - cw - 1 : r.x + r.w + 1; }
      Object.assign(caret.style, { left: x + "px", top: y + "px", width: w + "px", height: h + "px" });
      const typing = T >= s0 && T < end;
      const blink = Math.floor((T - (typing ? s0 : end)) / 0.18) % 2 === 0;
      caret.style.visibility = typing || blink ? "visible" : "hidden";
    });
  }
  function flash(chars, t, L) {
    const acc = getComputedStyle(document.documentElement).getPropertyValue("--accent").trim() || "#FF5B35";
    chars.forEach((c, i) => {
      if (!c.closest(".acc")) return;
      const s0 = t + i * L + 0.15;
      tl.fromTo(c, { color: "#ffffff", textShadow: `0 0 22px ${acc}` }, { color: acc, textShadow: "0 0 0px rgba(0,0,0,0)", duration: 0.6, ease: "power2.out" }, s0);
    });
  }

  const S = {
    tl,
    /* trazo real: paths/círculos/líneas en orden del DOM */
    draw(q, t, o = {}) {
      const els = shapesOf($(q)); if (!els.length) throw new Error("draw: vacío " + q);
      const dur = o.dur ?? 0.9, st = o.stagger ?? 0.08;
      mark($(q)); mark(els);
      tl.fromTo(els, { drawSVG: o.from ?? "0%" }, { drawSVG: o.to ?? "100%", duration: dur, stagger: st, ease: o.ease ?? "power1.inOut" }, t);
      return t + dur + st * (els.length - 1);
    },
    /* máquina de escribir: letra por letra, sin fundido */
    /* MÁQUINA DE ESCRIBIR: cada letra se escribe una por una con golpe de tecla y un cursor
       que avanza delante del texto y parpadea al terminar. Varios bloques encadenados forman una
       cascada de máquinas (la siguiente arranca poco después), cada una con su propio cursor. */
    type(q, t, o = {}) {
      const els = $(q); mark(els); note(o.verb || "type", t);
      const L = Math.max(o.letter ?? 0.045, o.minLetter ?? 0.038);
      let start = t, last = t;
      els.forEach((el, k) => {
        const chars = split([el], "words,chars")[0].chars;
        if (!chars.length) return;
        const s0 = o.parallel ? t + k * (o.gap ?? 0.12) : start;
        typewriter(el, chars, s0, L, o);
        last = Math.max(last, s0 + chars.length * L);
        if (!o.parallel) start = s0 + Math.min(chars.length * L, o.overlap ?? 0.35);
      });
      return o.parallel ? t + 0.4 : start;
    },
    /* títulos: la misma máquina, más lenta y con cursor grueso */
    rise(q, t, o = {}) { return S.type(q, t, { letter: 0.05, caret: 4, strike: 1.7, verb: "rise", overlap: 0.6, ...o }); },
    drop(q, t, o = {}) { return S.type(q, t, { letter: 0.05, caret: 4, strike: 1.7, verb: "drop", overlap: 0.6, ...o }); },
    tracking(q, t, o = {}) { return S.type(q, t, { letter: 0.05, caret: 4, strike: 1.7, verb: "tracking", overlap: 0.6, ...o }); },
    stamp(q, t, o = {}) { return S.type(q, t, { letter: 0.05, caret: 4, strike: 1.7, verb: "stamp", overlap: 0.6, ...o }); },
    /* barra que cubre y se retira dejando el texto */
    wipeIn(q, t, o = {}) { return S.type(q, t, { letter: 0.05, caret: 4, strike: 1.7, verb: "wipeIn", overlap: 0.6, ...o }); },
    marker(q, t, o = {}) {
      const els = $(q); let end = t;
      els.forEach((e) => {
        const r = rectOf(e);
        const m = addDiv({ left: r.x - 8 + "px", top: r.y + r.h * 0.12 + "px", width: r.w + 16 + "px", height: r.h * 0.82 + "px", background: o.color || "var(--accent)", zIndex: -1, transformOrigin: "0% 50%" });
        tl.fromTo(m, { scaleX: 0 }, { scaleX: 1, duration: 0.45, ease: "power2.out" }, t);
        end = t + 0.45;
      });
      return end;
    },
    underline(q, t, o = {}) {
      const els = $(q); let end = t;
      els.forEach((e) => {
        const r = rectOf(e);
        const m = addDiv({ left: r.x + "px", top: r.y + r.h + 2 + "px", width: r.w + "px", height: (o.h || 3) + "px", background: o.color || "var(--accent)", transformOrigin: "0% 50%" });
        tl.fromTo(m, { scaleX: 0 }, { scaleX: 1, duration: 0.5, ease: "power2.inOut" }, t);
        end = t + 0.5;
      });
      return end;
    },
    /* halo que se abre y se apaga */
    halo(q, t, o = {}) {
      const e = $(q)[0], r = rectOf(e), D = Math.max(r.w, r.h) * 1.15;
      const h = addDiv({ left: r.x + r.w / 2 - D / 2 + "px", top: r.y + r.h / 2 - D / 2 + "px", width: D + "px", height: D + "px", borderRadius: "50%", border: "3px solid " + (o.color || "var(--accent)") });
      tl.fromTo(h, { scale: 0.5, autoAlpha: 0 }, { keyframes: [{ scale: 1, autoAlpha: 1, duration: 0.3 }, { scale: 1.5, autoAlpha: 0, duration: 0.6 }], ease: "power2.out" }, t);
      return t + 0.9;
    },
    grow(q, t, o = {}) {
      const els = $(q); mark(els);
      const d = o.dur ?? 0.9, st = o.stagger ?? 0.12;
      const y = (o.axis || "y") === "y";
      gsap.set(els, { transformOrigin: y ? "50% 100%" : "0% 50%" });
      tl.fromTo(els, y ? { scaleY: 0 } : { scaleX: 0 }, { ...(y ? { scaleY: 1 } : { scaleX: 1 }), duration: d, stagger: st, ease: o.ease ?? "power3.out" }, t);
      return t + d + st * (els.length - 1);
    },
    /* la cifra viaja con el borde de su elemento */
    ride(q, dys, t, o = {}) {
      const els = $(q); mark(els);
      const d = o.dur ?? 0.9, st = o.stagger ?? 0.12;
      els.forEach((e, i) => tl.fromTo(e, { y: dys[i] ?? dys, x: (o.dxs || [])[i] ?? 0 }, { y: 0, x: 0, duration: d, ease: o.ease ?? "power3.out" }, t + i * st));
      return t + d + st * (els.length - 1);
    },
    /* cuenta desde 0 con golpe final (evaluado a mano: determinista en seek) */
    count(q, val, t, o = {}) {
      const els = $(q); mark(els);
      const d = o.dur ?? 1.4, dec = o.decimals ?? 0, ease = gsap.parseEase(o.ease || "power2.out");
      const fmt = (v) => (o.prefix || "") + v.toFixed(dec).replace(/\B(?=(\d{3})+(?!\d))/g, o.sep ?? " ") + (o.suffix || "");
      els.forEach((e) => {
        e.style.display = getComputedStyle(e).display === "inline" ? "inline-block" : e.style.display;
        customs.push((T) => {
          if (T < t) { e.style.visibility = "hidden"; return; }
          e.style.visibility = "visible";
          const p = Math.min(1, (T - t) / d);
          e.textContent = fmt(val * ease(p));
        });
        tl.fromTo(e, { scale: 1 }, { keyframes: [{ scale: 1.18, duration: 0.12 }, { scale: 1, duration: 0.25 }], ease: "power2.out", transformOrigin: o.origin || "50% 50%" }, t + d);
      });
      note("count", t);
      return t + d + 0.37;
    },
    /* la dona gira y los sectores nacen del giro. Cada sector: <circle data-a data-b> en % */
    ring(g, t, o = {}) {
      const G = $(g)[0]; mark([G]);
      const segs = Array.from(G.querySelectorAll("[data-a]")); mark(segs);
      const d = o.dur ?? 2.0, st = o.stagger ?? 0.15;
      segs.forEach((s, i) => {
        const a = +s.dataset.a, b = +s.dataset.b;
        tl.fromTo(s, { drawSVG: `${a}% ${a}%` }, { drawSVG: `${a}% ${b}%`, duration: d - st * i, ease: "power2.out" }, t + st * i);
      });
      if (o.origin) gsap.set(G, { svgOrigin: o.origin }); else gsap.set(G, { transformOrigin: "50% 50%" });
      tl.fromTo(G, { rotation: o.deg ?? -150 }, { rotation: 0, duration: d + 0.3, ease: "power3.out" }, t);
      return t + d + 0.3;
    },
    pop(q, t, o = {}) {
      const els = $(q); mark(els);
      const d = o.dur ?? 0.5, st = o.stagger ?? 0.08;
      gsap.set(els, { transformOrigin: "50% 50%" });
      tl.fromTo(els, { scale: 0, autoAlpha: 0 }, { scale: 1, autoAlpha: 1, duration: d, stagger: st, ease: "back.out(2.2)" }, t);
      return t + d + st * (els.length - 1);
    },
    arrive(q, t, o = {}) {
      const els = $(q); mark(els);
      const d = o.dur ?? 0.9, st = o.stagger ?? 0.1, D = o.dist ?? 260;
      const from = { left: { x: -D }, right: { x: D }, top: { y: -D }, bottom: { y: D } }[o.from || "left"];
      tl.fromTo(els, { ...from, autoAlpha: 0 }, { x: 0, y: 0, autoAlpha: 1, duration: d, stagger: st, ease: "power3.out" }, t);
      return t + d + st * (els.length - 1);
    },
    /* bloque/relleno que se descubre desde su borde (HTML) */
    wipe(q, t, o = {}) {
      const els = $(q); mark(els);
      const d = o.dur ?? 0.7, st = o.stagger ?? 0.1;
      const start = { up: "inset(100% 0 0 0)", down: "inset(0 0 100% 0)", right: "inset(0 100% 0 0)", left: "inset(0 0 0 100%)" }[o.dir || "right"];
      tl.fromTo(els, { clipPath: start }, { clipPath: "inset(0% 0% 0% 0%)", duration: d, stagger: st, ease: "power2.inOut" }, t);
      return t + d + st * (els.length - 1);
    },
    spin(q, t, o = {}) {
      const els = $(q); mark(els);
      const d = o.dur ?? 1.6;
      gsap.set(els, o.origin ? { svgOrigin: o.origin } : { transformOrigin: "50% 50%" });
      tl.fromTo(els, { rotation: o.deg ?? -360 }, { rotation: 0, duration: d, ease: o.ease ?? "power2.out" }, t);
      return t + d;
    },
    /* punto que late + guía trazada + texto tecleado */
    rotulo(dot, lead, text, t, o = {}) {
      let e = S.pop(dot, t, { dur: 0.35 });
      e = S.draw(lead, e - 0.1, { dur: 0.45 });
      return S.type(text, e, o);
    },
    /* SVG de banco: pieza por pieza, de lo grande a lo pequeño (contorno trazado) */
    build(q, t, o = {}) {
      const root = $(q)[0]; mark([root]);
      const els = shapesOf([root]).map((e) => { let a = 0; try { const b = e.getBBox(); a = b.width * b.height + (b.width + b.height); } catch (_) {} return [a, e]; })
        .sort((p, q2) => q2[0] - p[0]).map((p) => p[1]);
      mark(els);
      const span = o.span ?? 1.8, d = o.dur ?? 0.7, st = els.length > 1 ? span / (els.length - 1) : 0;
      tl.fromTo(els, { drawSVG: "0%" }, { drawSVG: "100%", duration: d, stagger: st, ease: "power1.inOut" }, t);
      return t + d + span;
    },
    /* movimiento cíclico (descanso): de 0 a 12 s exactos, vuelve al origen */
    idle(q, vars) {
      const els = $(q); mark(els);
      const { svgOrigin, ...from } = vars.from; if (svgOrigin) gsap.set(els, { svgOrigin });
      const { svgOrigin: _s, ...to } = vars.to;
      tl.fromTo(els, from, { ...to, duration: 12, ease: "none" }, 0);
    },
  };

  function lint() {
    const bad = [];
    const leaves = Array.from(stage().querySelectorAll("*")).filter((e) => {
      if (e.closest(".frame-a") || e.closest("defs") || e.tagName === "svg" || e.tagName === "g") return false;
      if (e.matches(SHAPES)) return true;
      const own = Array.from(e.childNodes).some((n) => n.nodeType === 3 && n.textContent.trim());
      const cs = getComputedStyle(e);
      const painted = (cs.backgroundColor !== "rgba(0, 0, 0, 0)" && e !== stage()) || parseFloat(cs.borderTopWidth) > 0;
      return own || painted;
    });
    leaves.forEach((e) => {
      let n = e, ok = false;
      while (n && n !== stage()) { if (n.__sc) { ok = true; break; } n = n.parentNode; }
      if (!ok) bad.push((e.id ? "#" + e.id : e.tagName.toLowerCase() + "." + (e.getAttribute("class") || "")) + " «" + (e.textContent || "").trim().slice(0, 30) + "»");
    });
    return bad;
  }

  window.SC = {
    S,
    async build(fn) {
      await document.fonts.ready;
      fn(S);
      const ends = tl.duration();
      tl.set({}, {}, 12);            // la línea dura 12 s
      opens.sort((a, b) => a[0] - b[0]);
      window.SC_INFO = { animation_ends: +ends.toFixed(2), open_verb: opens.length ? opens[0][1] : "-", lint: lint() };
      SC.seek(0);
      window.SC_READY = true;
    },
    seek(T) { tl.seek(T, false); customs.forEach((f) => f(T)); },
  };
})();
