/* runtime.js — motor de animación de slides-codigo (HTML + GSAP, render cuadro a cuadro).
 *
 * Cada slide es un HTML que carga gsap + DrawSVG + SplitText (+ MathJax si hay
 * ecuaciones) y este runtime, y escribe su animación dentro de
 * SC.build(() => { ... }). Todo cuelga de UNA línea de tiempo pausada (SC.tl):
 * el render salta a cada instante con SC.seek(t) y fotografía el cuadro, así
 * que el clip es exacto y reproducible cuadro a cuadro.
 *
 * GRAMÁTICA (heredada de make-videos-cosmos §3.4 y del catálogo de design):
 *  Texto ─ rise · drop · tracking · type · stamp · wipeIn · roll · vertical
 *  Énfasis ─ marker · underline · halo
 *  Datos ─ grow · ride · count · ring
 *  Dibujo ─ draw (trim path real) · pop · arrive · wipe · flood · spin
 *  Compuestos ─ chip · rotulo · eq (LaTeX glifo a glifo)
 * Lo que vive dentro de .frame-a es el Frame A: ya está y NO se anima.
 */
(function () {
  gsap.registerPlugin(DrawSVGPlugin, SplitText);
  if (window.MorphSVGPlugin) gsap.registerPlugin(MorphSVGPlugin);

  const DUR = 12;   // segundos por clip
  const HOLD = 1;   // último segundo quieto: el clip aterriza y se congela en la slide
  const counters = [];
  const tl = gsap.timeline({ paused: true, defaults: { ease: "power3.out" } });
  const els = (q) => gsap.utils.toArray(q);
  const mark = (q) => { const l = els(q); l.forEach((e) => (e.__sc = true)); return l; };
  const opens = [];  // primer verbo de texto de la slide (regla de variedad de Cosmos)
  const split = (el, type = "words,chars") => new SplitText(el, { type, wordsClass: "w" });
  const textVerb = (v, t) => { opens.push({ v, t }); };

  const SC = {
    DUR, HOLD, tl,

    /* ───────────── TEXTO ───────────── */

    // Letras que SUBEN escalonadas con sobrepaso (rise de Cosmos).
    rise(q, t, { stagger = 0.035, dur = 0.75 } = {}) {
      textVerb("rise", t); let end = t;
      mark(q).forEach((el) => {
        const s = split(el);
        tl.fromTo(s.chars, { yPercent: 70, autoAlpha: 0 }, { yPercent: 0, autoAlpha: 1, duration: dur, stagger, ease: "back.out(1.7)" }, end);
        end += dur + stagger * (s.chars.length - 1) * 0.5;
      });
      return end;
    },

    // Letras que CAEN desde arriba (drop): titulares verticales y golpes cortos.
    drop(q, t, { stagger = 0.04, dur = 0.7 } = {}) {
      textVerb("drop", t); let end = t;
      mark(q).forEach((el) => {
        const s = split(el);
        tl.fromTo(s.chars, { yPercent: -90, autoAlpha: 0 }, { yPercent: 0, autoAlpha: 1, duration: dur, stagger, ease: "bounce.out" }, end);
        end += dur + stagger * (s.chars.length - 1);
      });
      return end;
    },

    // Letras abiertas que se CIERRAN (tracking_in).
    tracking(q, t, { dur = 1.0, from = "0.45em" } = {}) {
      textVerb("tracking", t);
      mark(q).forEach((el) => {
        const final = getComputedStyle(el).letterSpacing;      // se lee ANTES de abrir las letras
        const to = final === "normal" ? "0px" : final;
        tl.fromTo(el, { letterSpacing: from, autoAlpha: 0 }, { letterSpacing: to, autoAlpha: 1, duration: dur, ease: "expo.out" }, t);
      });
      return t + dur;
    },

    // Máquina de escribir: letra por letra, sin fundido. cursor:true añade un caret que se va al terminar.
    type(q, t, { letter = 0.035, cursor = false } = {}) {
      textVerb("type", t); let end = t;
      mark(q).forEach((el) => {
        const s = split(el);
        gsap.set(s.chars, { visibility: "hidden" });
        s.chars.forEach((c, i) => tl.set(c, { visibility: "visible" }, end + i * letter));
        if (cursor) {
          const k = document.createElement("span"); k.className = "sc-caret"; k.textContent = "▍"; k.__sc = true;
          k.style.cssText = "display:inline-block;margin-left:.05em;color:var(--accent)"; el.appendChild(k);
          tl.set(k, { autoAlpha: 1 }, t); tl.set(k, { autoAlpha: 0 }, end + s.chars.length * letter + 0.25);
          gsap.set(k, { autoAlpha: 0 });
        }
        end += s.chars.length * letter;
      });
      return end;
    },

    // Entra grande y CAE con temblor (stamp): una palabra que debe golpear.
    stamp(q, t, { dur = 0.55 } = {}) {
      textVerb("stamp", t);
      const l = mark(q);
      tl.fromTo(l, { scale: 1.9, autoAlpha: 0, transformOrigin: "50% 60%" }, { scale: 1, autoAlpha: 1, duration: dur, ease: "power4.in" }, t);
      tl.to(l, { keyframes: { x: [0, -6, 5, -3, 2, 0] }, duration: 0.32, ease: "none" }, t + dur);
      return t + dur + 0.32;
    },

    // Barra de color que CUBRE y se RETIRA dejando el texto (wipe_in: el recurso más After Effects).
    wipeIn(q, t, { color = "var(--accent)", dur = 0.9 } = {}) {
      textVerb("wipeIn", t);
      mark(q).forEach((el) => {
        el.style.position = el.style.position || "relative";
        const bar = document.createElement("span"); bar.__sc = true;
        bar.style.cssText = `position:absolute;left:-4px;right:-4px;top:4%;bottom:4%;background:${color};transform-origin:0 50%;transform:scaleX(0)`;
        el.appendChild(bar);
        const kids = [...el.childNodes].filter((n) => n !== bar);
        const wrap = document.createElement("span"); kids.forEach((k) => wrap.appendChild(k)); el.insertBefore(wrap, bar);
        gsap.set(wrap, { autoAlpha: 0 });
        tl.to(bar, { scaleX: 1, duration: dur * 0.45, ease: "power3.in" }, t);
        tl.set(wrap, { autoAlpha: 1 }, t + dur * 0.45);
        tl.set(bar, { transformOrigin: "100% 50%" }, t + dur * 0.45);
        tl.to(bar, { scaleX: 0, duration: dur * 0.55, ease: "power3.out" }, t + dur * 0.45);
      });
      return t + dur;
    },

    // Rodillo: la palabra vieja sube y sale, la nueva entra desde abajo (roll_swap).
    roll(oldQ, newQ, t, { dur = 0.6 } = {}) {
      mark(oldQ); mark(newQ);
      tl.to(oldQ, { yPercent: -110, autoAlpha: 0, duration: dur, ease: "power3.in" }, t);
      tl.fromTo(newQ, { yPercent: 110, autoAlpha: 0 }, { yPercent: 0, autoAlpha: 1, duration: dur, ease: "power3.out" }, t + dur * 0.4);
      return t + dur * 1.4;
    },

    /* ───────────── ÉNFASIS ───────────── */

    // Bloque translúcido que CRECE detrás del texto (marker).
    marker(q, t, { color = "var(--accent)", opacity = 0.28, dur = 0.6 } = {}) {
      mark(q).forEach((el) => {
        el.style.position = el.style.position || "relative";
        el.style.isolation = "isolate";   // el bloque va detrás del texto, nunca detrás del fondo
        const m = document.createElement("span"); m.__sc = true;
        m.style.cssText = `position:absolute;left:-.12em;right:-.12em;top:52%;bottom:2%;background:${color};opacity:${opacity};z-index:-1;transform-origin:0 50%`;
        el.appendChild(m);
        tl.fromTo(m, { scaleX: 0 }, { scaleX: 1, duration: dur, ease: "power2.out" }, t);
      });
      return t + dur;
    },

    // Subrayado que se traza bajo el texto.
    underline(q, t, { color = "var(--accent)", dur = 0.5, h = 4 } = {}) {
      mark(q).forEach((el) => {
        el.style.position = el.style.position || "relative";
        const u = document.createElement("span"); u.__sc = true;
        u.style.cssText = `position:absolute;left:0;right:0;bottom:-${h + 4}px;height:${h}px;background:${color};transform-origin:0 50%`;
        el.appendChild(u);
        tl.fromTo(u, { scaleX: 0 }, { scaleX: 1, duration: dur, ease: "power3.out" }, t);
      });
      return t + dur;
    },

    // Halo que se expande y se apaga (golpe de un icono o una cifra). Termina invisible.
    halo(q, t, { color = "var(--accent)", size = 1.8, dur = 0.8 } = {}) {
      mark(q).forEach((el) => {
        const r = el.getBoundingClientRect(), st = document.getElementById("stage").getBoundingClientRect();
        const d = Math.max(r.width, r.height);
        const h = document.createElement("div"); h.__sc = true; h.className = "abs";
        h.style.cssText += `left:${r.left - st.left + r.width / 2 - d / 2}px;top:${r.top - st.top + r.height / 2 - d / 2}px;width:${d}px;height:${d}px;border-radius:50%;border:2px solid ${color};pointer-events:none`;
        document.getElementById("stage").appendChild(h);
        tl.fromTo(h, { scale: 0.6, autoAlpha: 0.9 }, { scale: size, autoAlpha: 0, duration: dur, ease: "power2.out" }, t);
      });
      return t + dur;
    },

    /* ───────────── DATOS ───────────── */

    // Barras que CRECEN ancladas a su base (en SVG o HTML).
    grow(q, t, { dur = 0.8, stagger = 0.12, axis = "y" } = {}) {
      const l = mark(q);
      const o = axis === "y" ? "50% 100%" : "0% 50%";
      tl.fromTo(l, { [axis === "y" ? "scaleY" : "scaleX"]: 0, transformOrigin: o }, { [axis === "y" ? "scaleY" : "scaleX"]: 1, duration: dur, stagger, ease: "power3.out" }, t);
      return t + dur + stagger * (l.length - 1);
    },

    // La cifra VIAJA con el borde superior de su barra (2-ter): misma t, dur y stagger que grow.
    ride(q, dy, t, { dur = 0.8, stagger = 0.12, axis = "y" } = {}) {
      const l = mark(q);
      l.forEach((el, i) => {
        const d = Array.isArray(dy) ? dy[i] : dy;
        tl.fromTo(el, { [axis]: d, autoAlpha: 0 }, { [axis]: 0, autoAlpha: 1, duration: dur, ease: "power3.out" }, t + i * stagger);
      });
      return t + dur + stagger * (l.length - 1);
    },

    // Cifra que MIDE y cuenta desde cero, con golpe final (counter + stamp de Cosmos). Las nominales tipean.
    count(q, to, t, { dur = 1.4, from = 0, decimals = 0, prefix = "", suffix = "", locale = "es-EC", punch = true } = {}) {
      const el = mark(q)[0];
      const proxy = { v: from };
      const fmt = (v) => prefix + v.toLocaleString(locale, { minimumFractionDigits: decimals, maximumFractionDigits: decimals }) + suffix;
      tl.fromTo(el, { autoAlpha: 0 }, { autoAlpha: 1, duration: 0.15 }, t);
      tl.fromTo(proxy, { v: from }, { v: to, duration: dur, ease: "expo.out" }, t);
      counters.push(() => (el.textContent = fmt(proxy.v)));
      if (punch) tl.fromTo(el, { scale: 1 }, { keyframes: { scale: [1, 1.12, 1] }, duration: 0.35, ease: "power2.out", transformOrigin: "50% 60%" }, t + dur * 0.8);
      return t + dur;
    },

    // Dona que GIRA REVELANDO: el grupo rota y los sectores nacen del giro (2-sexies).
    // groupQ: <g data-cx data-cy> · segQ: <circle> por sector · segs: [[ini%, fin%], ...]
    ring(groupQ, segQ, segs, t, { dur = 1.8, turn = 300 } = {}) {
      const g = mark(groupQ)[0];
      const l = mark(segQ);
      const origin = `${g.dataset.cx} ${g.dataset.cy}`;
      tl.fromTo(g, { rotation: -turn, svgOrigin: origin }, { rotation: 0, svgOrigin: origin, duration: dur, ease: "power3.out" }, t);
      l.forEach((c, i) => {
        const [a, b] = segs[i];
        tl.fromTo(c, { drawSVG: `${a}% ${a}%` }, { drawSVG: `${a}% ${b}%`, duration: dur * 0.7, ease: "power2.out" }, t + (dur * 0.3 * i) / Math.max(1, l.length - 1));
      });
      return t + dur;
    },

    /* ───────────── DIBUJO ───────────── */

    // Line work que se TRAZA, trazo por trazo en el orden del DOM (= el orden de la mano).
    draw(q, t, { dur = 0.9, stagger = 0.08, ease = "power2.inOut" } = {}) {
      const l = mark(q);
      tl.fromTo(l, { drawSVG: "0%" }, { drawSVG: "100%", duration: dur, stagger, ease }, t);
      return t + dur + stagger * (l.length - 1);
    },

    // Nodo, punto, icono que escala desde cero con rebote.
    pop(q, t, { dur = 0.5, stagger = 0.08 } = {}) {
      const l = mark(q);
      tl.fromTo(l, { scale: 0, transformOrigin: "50% 50%" }, { scale: 1, duration: dur, stagger, ease: "back.out(2)" }, t);
      return t + dur + stagger * (l.length - 1);
    },

    // Objeto o figura que LLEGA moviéndose desde un borde (nada solo aparece).
    arrive(q, t, { from = "left", dist = 300, dur = 1.0, stagger = 0.1 } = {}) {
      const l = mark(q);
      const v = { left: { x: -dist }, right: { x: dist }, top: { y: -dist }, bottom: { y: dist } }[from];
      tl.fromTo(l, { ...v, autoAlpha: 0 }, { x: 0, y: 0, autoAlpha: 1, duration: dur, stagger, ease: "power3.out" }, t);
      return t + dur + stagger * (l.length - 1);
    },

    // Bloque o relleno que se revela desde su borde de anclaje (clip-path).
    wipe(q, t, { dir = "right", dur = 0.8, stagger = 0.1 } = {}) {
      const l = mark(q);
      const start = { right: "inset(0% 100% 0% 0%)", left: "inset(0% 0% 0% 100%)", up: "inset(100% 0% 0% 0%)", down: "inset(0% 0% 100% 0%)" }[dir];
      tl.fromTo(l, { clipPath: start }, { clipPath: "inset(0% 0% 0% 0%)", duration: dur, stagger, ease: "power2.inOut" }, t);
      return t + dur + stagger * (l.length - 1);
    },

    // Relleno sólido de una forma SVG que inunda tras su trazo.
    flood(q, t, { dur = 0.5, to = 1 } = {}) {
      const l = mark(q);
      tl.fromTo(l, { fillOpacity: 0 }, { fillOpacity: to, duration: dur, ease: "power2.out" }, t);
      return t + dur;
    },

    // Mecanismo YA trazado que se pone en marcha y asienta en registro (no cuenta como entrada).
    spin(q, t, { deg = 360, dur = 1.6, origin = "50% 50%" } = {}) {
      tl.fromTo(els(q), { rotation: -deg, transformOrigin: origin }, { rotation: 0, duration: dur, ease: "power2.inOut" }, t);
      return t + dur;
    },

    /* ───────────── COMPUESTOS ───────────── */

    // Chip: el borde se dibuja y el texto se teclea (chip_in de Cosmos). el = .chip con texto.
    chip(q, t, { dur = 0.5, letter = 0.03 } = {}) {
      let end = t;
      mark(q).forEach((el) => {
        tl.fromTo(el, { clipPath: "inset(0% 100% 0% 0%)" }, { clipPath: "inset(0% 0% 0% 0%)", duration: dur, ease: "power2.inOut" }, end);
        const inner = el.querySelector(".chip-t") || el;
        const s = split(inner, "chars");
        gsap.set(s.chars, { visibility: "hidden" });
        s.chars.forEach((c, i) => tl.set(c, { visibility: "visible" }, end + dur * 0.6 + i * letter));
        end = end + dur * 0.6 + s.chars.length * letter;
      });
      return end;
    },

    // Rótulo: punto que late + guía que se traza + texto que se teclea (rotulo de Cosmos).
    rotulo(dotQ, leadQ, textQ, t, { letter = 0.03 } = {}) {
      const d = mark(dotQ);
      tl.fromTo(d, { scale: 0, transformOrigin: "50% 50%" }, { scale: 1, duration: 0.35, ease: "back.out(2.5)" }, t);
      tl.to(d, { keyframes: { scale: [1, 1.5, 1] }, duration: 0.5, ease: "sine.inOut" }, t + 0.35);
      SC.draw(leadQ, t + 0.25, { dur: 0.5, stagger: 0 });
      const e = SC.type(textQ, t + 0.65, { letter });
      opens.pop();  // un rótulo no cuenta como verbo de apertura
      return e;
    },

    // Ecuación LaTeX (MathJax SVG) que entra glifo a glifo, subiendo (eq_in de Cosmos).
    eq(q, t, { stagger = 0.04, dur = 0.6 } = {}) {
      let end = t;
      mark(q).forEach((el) => {
        const glyphs = el.querySelectorAll("svg use, svg path, svg rect");
        tl.fromTo(glyphs, { y: 18, autoAlpha: 0 }, { y: 0, autoAlpha: 1, duration: dur, stagger, ease: "back.out(1.6)" }, end);
        end += dur + stagger * (glyphs.length - 1);
      });
      return end;
    },

    /* ───────────── CICLO ───────────── */

    build(fn) {
      const go = () => {
        try { fn(SC); } catch (e) { window.SC_ERROR = String((e && e.stack) || e); }
        tl.seek(0, true);
        window.SC_LINT = SC.lint();
        window.SC_OPEN = opens.length ? opens.slice().sort((a, b) => a.t - b.t)[0].v : null;
        window.SC_READY = true;
      };
      const tex = window.MathJax && MathJax.startup && MathJax.startup.promise;
      document.fonts.ready.then(() => (tex ? MathJax.startup.promise.then(go) : go()));
    },

    seek(t) {
      tl.seek(t, true);
      counters.forEach((f) => f());
    },

    // «Nada solo aparece» + presupuesto de tiempo, verificados sobre el DOM real.
    lint() {
      const out = [];
      const stage = document.getElementById("stage");
      const covered = (el) => { for (let n = el; n && n !== stage; n = n.parentNode) { if (n.__sc) return true; if (n.classList && n.classList.contains("frame-a")) return true; } return false; };
      const name = (el) => el.id ? `#${el.id}` : `${el.tagName.toLowerCase()}.${(el.getAttribute("class") || "").split(" ")[0]}`;
      stage.querySelectorAll("path,line,circle,ellipse,rect,polyline,polygon,img,image").forEach((el) => {
        if (el.closest("mjx-container, defs, clipPath, mask")) return;
        if (!covered(el)) out.push(`aparece sin verbo: ${name(el)}`);
      });
      stage.querySelectorAll("div,span,p,h1,h2,h3,li,td,th").forEach((el) => {
        const own = [...el.childNodes].some((n) => n.nodeType === 3 && n.textContent.trim());
        if (own && !covered(el)) out.push(`texto sin verbo: ${name(el)} «${el.textContent.trim().slice(0, 30)}»`);
      });
      stage.querySelectorAll("mjx-container").forEach((el) => { if (!covered(el)) out.push("ecuación sin verbo"); });
      if (tl.duration() > DUR - HOLD + 1e-6) out.push(`la animación termina en ${tl.duration().toFixed(2)} s: debe terminar ≤ ${DUR - HOLD} s (hold final)`);
      return out;
    },
  };
  window.SC = SC;
})();
