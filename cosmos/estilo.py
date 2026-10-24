# estilo.py — make-videos · Tipo 1 (académico) · estilo «Cosmos» v2.5 (v2.3 + counter con convención inglesa)
# Fondo casi negro con estrellas que parpadean · tipografía cinética tipo After Effects ·
# LaTeX nítido · iconos que actúan · ilustraciones SVG detalladas (planetas que rotan, anatomía).
from manim import *
import numpy as np, os, hashlib
from PIL import Image

# ---------- 0. Formato ----------
FORMATO = os.environ.get("MV_FORMATO", "16:9")          # "16:9" (default) o "9:16"
if FORMATO == "9:16":
    config.pixel_width, config.pixel_height = 1080, 1920
    config.frame_height = 14.222; config.frame_width = 8.0
else:
    config.pixel_width, config.pixel_height = 1920, 1080
config.frame_rate = int(os.environ.get("MV_FPS", "30"))
if os.environ.get("MV_PREVIEW"):                         # borrador rápido: mitad de resolución, 30 fps
    config.pixel_width //= 2; config.pixel_height //= 2; config.frame_rate = 30
config.background_color = "#0B0F17"
FW, FH = config.frame_width, config.frame_height
CACHE = os.path.expanduser("~/.mv_cache"); os.makedirs(CACHE, exist_ok=True)

# ---------- 1. Paleta semántica ----------
BG, BG2 = "#0B0F17", "#121826"
INK, MUTED, FAINT, LINE = "#EEF1F6", "#8C96A8", "#3A4356", "#1E2636"
RED, BLUE, MINT, GOLD, VIOLET, CYAN = "#FF5A6E", "#5B8CFF", "#2EE6A8", "#FFC53D", "#A78BFA", "#4FD8F0"
# RED/BLUE: las dos clases que se comparan · MINT: resultado/correcto · GOLD: señalar/acotar/incógnita
# VIOLET: lo desconocido/idea · CYAN: datos · INK/MUTED: texto · FAINT/LINE: estructura

# ---------- 2. Tipografías ----------
GROT, MONO, DISP = "Space Grotesk", "JetBrains Mono", "Unbounded"

def T(s, size=48, color=INK, font=GROT, weight=BOLD, **kw):
    """Titulares, palabras clave y números grandes (Space Grotesk)."""
    return Text(s, font=font, font_size=size, color=color, weight=weight, **kw)

def MONO_T(s, size=26, color=MUTED, weight=NORMAL, **kw):
    """Rótulos, chips, unidades, notas (JetBrains Mono)."""
    return Text(s, font=MONO, font_size=size, color=color, weight=weight, **kw)

def DISPLAY(s, size=96, color=INK, **kw):
    """Golpes de título (Unbounded Black). Máx. 1-3 palabras."""
    return Text(s, font=DISP, font_size=size, color=color, weight=ULTRABOLD, **kw)

TEX_PRE = TexTemplate(); TEX_PRE.add_to_preamble(r"\usepackage{amsmath,amssymb,bm}")
def EQ(*parts, size=56, color=INK, tint=None, **kw):
    """Ecuación LaTeX real (MathTex). tint={r"g_M": CYAN} colorea términos. Partes separadas = submobjects
    manipulables (eq[1] es el segundo trozo) para enfocarlos o transformarlos."""
    m = MathTex(*parts, font_size=size, color=color, tex_template=TEX_PRE, **kw)
    for k, c in (tint or {}).items(): m.set_color_by_tex(k, c)
    return m

# ---------- 3. Curvas de easing (el «feel» After Effects) ----------
def ease_out_expo(t): return 1 - 2 ** (-10 * t) if t < 1 else 1
def ease_in_expo(t): return 0 if t == 0 else 2 ** (10 * t - 10)
def ease_out_back(t, s=1.70158): t = t - 1; return t * t * ((s + 1) * t + s) + 1
def ease_out_back_soft(t): return ease_out_back(t, 1.1)
def ease_in_out_cubic(t): return 4 * t ** 3 if t < .5 else 1 - (-2 * t + 2) ** 3 / 2
def ease_out_elastic(t):
    if t in (0, 1): return t
    return 2 ** (-10 * t) * np.sin((t * 10 - .75) * 2 * np.pi / 3) + 1

# ---------- 4. Sprites de luz (glow real, viñeta, grano) ----------
def _png(name, arr):
    p = os.path.join(CACHE, name)
    if not os.path.exists(p):                              # escritura atómica: las escenas se renderizan en paralelo
        tmp = f"{p}.{os.getpid()}.png"; Image.fromarray(arr).save(tmp); os.replace(tmp, p)
    return p

def _glow_png(color, soft=2.2):
    c = color_to_int_rgb(ManimColor(color)); n = 256
    y, x = np.mgrid[-1:1:n * 1j, -1:1:n * 1j]; r = np.sqrt(x * x + y * y)
    a = np.clip(np.exp(-(r * soft) ** 2) - np.exp(-soft ** 2), 0, 1) / (1 - np.exp(-soft ** 2))
    arr = np.zeros((n, n, 4), np.uint8); arr[..., :3] = c; arr[..., 3] = (a * 255).astype(np.uint8)
    return _png(f"glow_{hashlib.md5((str(color)+str(soft)).encode()).hexdigest()[:8]}.png", arr)

def glow(mob_or_point, color=GOLD, size=None, opacity=0.55):
    """Halo suave (imagen radial) detrás de un objeto o en un punto. Se añade ANTES que el objeto."""
    im = ImageMobject(_glow_png(color)).set_opacity(opacity)
    if isinstance(mob_or_point, Mobject):
        s = size or max(mob_or_point.width, mob_or_point.height) * 2.2
        im.set_height(s).move_to(mob_or_point)
    else:
        im.set_height(size or 2).move_to(mob_or_point)
    return im

def vignette():
    n = 512; y, x = np.mgrid[-1:1:n * 1j, -1:1:n * 1j]; r = np.sqrt((x * FW / FH) ** 2 / 3 + y * y / 1.2)
    a = np.clip((r - 0.45) / 0.95, 0, 1) ** 2.0 * 0.6
    arr = np.zeros((n, n, 4), np.uint8); arr[..., 3] = (a * 255).astype(np.uint8)
    im = ImageMobject(_png(f"vig_{FORMATO.replace(':','x')}.png", arr)); im.stretch_to_fit_width(FW); im.stretch_to_fit_height(FH)
    return im

# ---------- 5. Fondo «Cosmos»: estrellas que parpadean + constelación tenue ----------
class Cosmos(VGroup):
    """Campo de estrellas con parpadeo individual (fase y frecuencia propias) y líneas de constelación
    casi invisibles. Semilla fija → idéntico en todas las escenas (los cortes no saltan)."""
    def __init__(self, n=None, seed=11, lines=True):
        super().__init__()
        rng = np.random.default_rng(seed); n = n or int(230 * FW * FH / (14.22 * 8))
        pos = np.c_[rng.uniform(-FW / 2, FW / 2, n), rng.uniform(-FH / 2, FH / 2, n), np.zeros(n)]
        self.stars = VGroup()
        self.base = rng.uniform(0.15, 0.75, n) ** 1.6
        self.w = rng.uniform(0.6, 2.4, n); self.ph = rng.uniform(0, 2 * np.pi, n)
        for p, b in zip(pos, self.base):
            r = 0.006 + 0.02 * b
            col = rng.choice([WHITE, "#BFD3FF", "#FFE7C2", "#9FB7FF"], p=[.55, .25, .1, .1])
            self.stars.add(Dot(p, radius=r, color=col, fill_opacity=b))
        if lines:
            L = VGroup(); idx = rng.choice(n, 26, replace=False)
            for i in idx:
                d = np.linalg.norm(pos - pos[i], axis=1); d[i] = 9e9; j = int(np.argmin(d))
                if d[j] < 2.2: L.add(Line(pos[i], pos[j], stroke_width=1, color="#7C8AB0", stroke_opacity=0.10))
            self.add(L)
        self.add(self.stars); self.t = 0.0
        # 4 estrellas «destello» con cruz de luz que late
        self.flares = VGroup()
        for k in rng.choice(n, 4, replace=False):
            p = pos[k]; f = VGroup(Line(p + LEFT * .12, p + RIGHT * .12, stroke_width=1.2),
                                   Line(p + UP * .12, p + DOWN * .12, stroke_width=1.2)).set_color("#DCE6FF")
            f.k = k; self.flares.add(f)
        self.add(self.flares)
        self.add_updater(Cosmos._tick)

    @staticmethod
    def _tick(m, dt):
        m.t += dt
        a = m.base * (0.55 + 0.45 * np.sin(m.w * m.t * 2.2 + m.ph))
        for s, o in zip(m.stars, a): s.set_fill(opacity=float(o))
        for f in m.flares:
            v = max(0.0, np.sin(0.9 * m.t + f.k)) ** 6
            f.set_stroke(opacity=0.8 * v); f.set(width=0.24 * (0.4 + 0.6 * v) + 1e-3)

def fondo(scene, vig=True):
    """Primera línea de TODA escena 2D: fondo + estrellas + viñeta."""
    scene.camera.background_color = BG
    c = Cosmos(); scene.add(c)
    if vig: scene.add(vignette())
    return c

# ---------- 6. Tipografía cinética ----------
def _chars(txt):
    return [c for c in txt.submobjects if len(c.points) or len(c.submobjects)] if isinstance(txt, Text) else list(txt)

def rise(txt, rt=0.9, lag=0.06, dist=0.45, scale=0.85):
    """Cada letra sube desde abajo con sobrepaso (ease_out_back), escalonada. La entrada estándar."""
    return LaggedStart(*[FadeIn(c, shift=UP * dist, scale=scale, rate_func=ease_out_back_soft) for c in _chars(txt)],
                       lag_ratio=lag, run_time=rt)

def drop(txt, rt=0.9, lag=0.07, dist=0.8):
    """Letras que caen desde arriba y rebotan (para texto vertical y golpes)."""
    return LaggedStart(*[FadeIn(c, shift=DOWN * dist, rate_func=ease_out_back) for c in _chars(txt)],
                       lag_ratio=lag, run_time=rt)

def tracking_in(scene, txt, rt=1.1, spread=0.9):
    """Tracking de After Effects: letras abiertas y transparentes que se cierran a su sitio."""
    cs = _chars(txt); cx = txt.get_center()[0]; tg = [c.get_center().copy() for c in cs]
    for c in cs: c.shift(RIGHT * (c.get_center()[0] - cx) * spread); c.set_opacity(0)
    scene.add(txt)
    scene.play(*[c.animate(rate_func=ease_out_expo).move_to(p).set_opacity(1) for c, p in zip(cs, tg)], run_time=rt)

def vertical(s, size=64, color=INK, font=GROT, mode="stack", buff=0.02):
    """Texto VERTICAL. mode='stack': letras apiladas una bajo otra (cartel); mode='spine': texto girado 90°
    que se lee de abajo arriba (lomo de libro). Entra con drop() o rise()."""
    if mode == "spine":
        return T(s, size, color, font).rotate(PI / 2)
    g = VGroup(*[T(ch, size, color, font) for ch in s if ch != " "])
    return g.arrange(DOWN, buff=buff)

def wipe_in(scene, mob, color=GOLD, rt=0.8, pad=0.12):
    """Barrido de color: una barra cubre el texto de izquierda a derecha, el texto aparece debajo y la barra
    se retira hacia la derecha. La transición tipográfica más After Effects que hay."""
    w, h = mob.width + 2 * pad, mob.height + 2 * pad; L = mob.get_left()[0] - pad
    bar = Rectangle(width=0.001, height=h, fill_color=color, fill_opacity=1, stroke_width=0).move_to(mob)
    bar.align_to([L, 0, 0], LEFT)
    scene.add(bar)
    scene.play(bar.animate(rate_func=ease_in_out_cubic).stretch_to_fit_width(w).align_to([L, 0, 0], LEFT), run_time=rt * .45)
    scene.add(mob); scene.bring_to_front(bar)
    scene.play(bar.animate(rate_func=ease_in_out_cubic).stretch_to_fit_width(0.001).align_to([L + w, 0, 0], RIGHT), run_time=rt * .55)
    scene.remove(bar)

def roll_swap(scene, old, new, rt=0.6, dist=0.5):
    """Cambio de palabra tipo rodillo: la vieja sube y se va, la nueva sube desde abajo a su sitio."""
    new.move_to(old)
    scene.play(FadeOut(old, shift=UP * dist, rate_func=ease_in_expo), FadeIn(new, shift=UP * dist, rate_func=ease_out_back_soft), run_time=rt)

def stamp(scene, mob, rt=0.55, s0=1.7):
    """Golpe: entra grande y transparente, cae a su tamaño con sobrepaso y un temblor corto."""
    mob.scale(s0).set_opacity(0); scene.add(mob)
    scene.play(mob.animate(rate_func=ease_out_back).scale(1 / s0).set_opacity(1), run_time=rt)
    scene.play(Wiggle(mob, scale_value=1.04, rotation_angle=0.03 * TAU, n_wiggles=3), run_time=0.35)

def underline(scene, mob, color=GOLD, rt=0.6, buff=0.12, glow_on=True):
    """Subrayado que se dibuja desde la izquierda, con halo. Para «como mucho, aquí»."""
    ln = Line(mob.get_corner(DL) + DOWN * buff, mob.get_corner(DR) + DOWN * buff, color=color, stroke_width=5)
    if glow_on: scene.add(glow(ln.get_center(), color, size=mob.width * 0.9, opacity=0.25))
    scene.play(Create(ln, rate_func=ease_out_expo), run_time=rt); return ln

def marker(scene, mob, color=GOLD, rt=0.5, pad=0.1, opacity=0.22):
    """Resaltador: un bloque translúcido crece detrás de la palabra, de izquierda a derecha."""
    r = RoundedRectangle(corner_radius=0.08, width=mob.width + 2 * pad, height=mob.height + 2 * pad,
                         fill_color=color, fill_opacity=opacity, stroke_width=0).move_to(mob)
    r.set_z_index(mob.z_index - 1); L = r.get_left()
    r.stretch_to_fit_width(0.01).move_to(L, aligned_edge=LEFT)
    scene.add(r); scene.play(r.animate(rate_func=ease_out_expo).stretch_to_fit_width(mob.width + 2 * pad).move_to(mob), run_time=rt)
    return r

def chip(text, color=MUTED, size=24):
    """Etiqueta de borde fino (monoespaciada), como «Ronald Graham» en la referencia."""
    t = MONO_T(text, size, INK if color == MUTED else color)
    box = RoundedRectangle(corner_radius=0.08, width=t.width + 0.45, height=t.height + 0.3, stroke_color=color,
                           stroke_width=1.6, stroke_opacity=0.8, fill_color=BG2, fill_opacity=0.85)
    g = VGroup(box, t.move_to(box)); g.box, g.text = box, t; return g

def chip_in(scene, ch, rt=0.7):
    """El borde se dibuja, el relleno aparece, el texto se teclea. (v2.3) Dura de verdad `rt`: AddTextLetterByLetter de
    Manim impone ≥ 0,06 s por letra (24 letras = 1,4 s aunque se pida menos), así que el tecleo es un LaggedStart propio."""
    scene.play(Create(ch.box, rate_func=ease_out_expo), run_time=rt * .45)
    cs = _chars(ch.text)
    scene.play(LaggedStart(*[FadeIn(c, rate_func=rate_functions.rush_from) for c in cs], lag_ratio=1.0), run_time=rt * .55)

def typewriter(scene, txt, cps=28, cursor_color=GOLD):
    """Mono tecleado con cursor de bloque que parpadea al final."""
    scene.play(AddTextLetterByLetter(txt, time_per_char=1 / cps))
    cur = Rectangle(width=0.08, height=txt.height * 1.05, fill_color=cursor_color, fill_opacity=1, stroke_width=0)
    cur.next_to(txt, RIGHT, buff=0.06)
    cur.add_updater(lambda m, dt: m.set_fill(opacity=1.0 if (getattr(m, "_t", 0) % 1) < .5 else 0) or setattr(m, "_t", getattr(m, "_t", 0) + dt))
    scene.add(cur); return cur

def counter(value_tracker, fmt="{:,.0f}", size=72, color=MINT, font=GROT, anchor=ORIGIN, edge=None):
    """Número que cuenta en vivo, con convención inglesa (v2.5): miles con coma, decimales con punto (1,234.5).
    Queda anclado por el borde `edge` para que no baile al cambiar de ancho."""
    def make():
        s = fmt.format(value_tracker.get_value())
        m = T(s, size, color, font)
        return m.move_to(anchor, aligned_edge=edge) if edge is not None else m.move_to(anchor)
    return always_redraw(make)

def eq_in(scene, eq, rt=1.2, lag=0.05):
    """Ecuación LaTeX que entra glifo a glifo subiendo, escalonada (no el Write genérico)."""
    glyphs = [g for part in eq for g in part]
    scene.play(LaggedStart(*[FadeIn(g, shift=UP * 0.25, rate_func=ease_out_back_soft) for g in glyphs], lag_ratio=lag), run_time=rt)

def eq_focus(scene, eq, idx, color=GOLD, dim=0.25, rt=0.5):
    """Atenúa toda la ecuación salvo eq[idx] y le pone un marcador. Devuelve el marcador (quitarlo con
    eq_unfocus)."""
    others = [p for i, p in enumerate(eq) if i != idx]
    box = SurroundingRectangle(eq[idx], color=color, buff=0.1, corner_radius=0.08, stroke_width=2.5)
    scene.play(*[p.animate.set_opacity(dim) for p in others], eq[idx].animate.set_color(color), Create(box), run_time=rt)
    return box

def eq_unfocus(scene, eq, box, color=INK, rt=0.4):
    scene.play(*[p.animate.set_opacity(1) for p in eq], FadeOut(box), run_time=rt)

def zona_segura(mob, margen=0.45):
    """Mete `mob` dentro del cuadro con margen (se llama antes de animarlo si su posición es calculada)."""
    dx = max(0, -FW / 2 + margen - mob.get_left()[0]) - max(0, mob.get_right()[0] - FW / 2 + margen)
    dy = max(0, -FH / 2 + margen - mob.get_bottom()[1]) - max(0, mob.get_top()[1] - FH / 2 + margen)
    return mob.shift([dx, dy, 0])

def exit_all(scene, *mobs, rt=0.5, dist=0.4):
    """Salida estándar: todo sube un poco y se desvanece, escalonado (nunca un corte seco)."""
    mobs = mobs or [m for m in scene.mobjects if not isinstance(m, (Cosmos, ImageMobject))]
    scene.play(LaggedStart(*[FadeOut(m, shift=UP * dist, rate_func=ease_in_expo) for m in mobs], lag_ratio=0.05), run_time=rt)

def float_idle(mob, amp=0.04, w=0.9):
    """Vida en reposo: flotación vertical sutil mientras la voz habla."""
    mob._t0 = 0.0; base = mob.get_center().copy()
    def u(m, dt):
        m._t0 += dt; m.move_to(base + UP * amp * np.sin(w * m._t0 * 2 * np.pi / 2))
    mob.add_updater(u); return mob

# ---------- 7. Iconos que actúan (dibujados en código, trazo redondeado) ----------
def _ic(*m, color=INK, sw=5):
    g = VGroup(*m); g.set_stroke(color, sw); g.set_fill(opacity=0)
    for x in g.family_members_with_points(): x.joint_type = LineJointType.ROUND; x.cap_style = CapStyleType.ROUND
    return g

def icon(name, color=INK, size=0.8):
    """check · cross · bulb · alert · clock · target · eye · ruler · question · sparkle · arrow · scale"""
    if name == "check": g = _ic(VMobject().set_points_as_corners([[-.5, 0, 0], [-.15, -.35, 0], [.5, .4, 0]]), color=color)
    elif name == "cross": g = _ic(Line([-.4, -.4, 0], [.4, .4, 0]), Line([-.4, .4, 0], [.4, -.4, 0]), color=color)
    elif name == "bulb":
        g = _ic(Arc(radius=.38, start_angle=-PI / 4.5, angle=PI + 2 * PI / 4.5).shift(UP * .15),
                Line([-.26, -.12, 0], [-.18, -.38, 0]), Line([.26, -.12, 0], [.18, -.38, 0]),
                Line([-.18, -.45, 0], [.18, -.45, 0]), Line([-.12, -.55, 0], [.12, -.55, 0]), color=color)
    elif name == "alert":
        g = _ic(Polygon([0, .5, 0], [.5, -.4, 0], [-.5, -.4, 0]), Line([0, .2, 0], [0, -.1, 0]), Dot([0, -.25, 0], radius=.02), color=color)
    elif name == "clock":
        g = _ic(Circle(radius=.45), Line(ORIGIN, [0, .3, 0]), Line(ORIGIN, [.2, 0, 0]), color=color)
    elif name == "target":
        g = _ic(Circle(radius=.45), Circle(radius=.28), Circle(radius=.1), color=color)
    elif name == "eye":
        g = _ic(ArcBetweenPoints([-.5, 0, 0], [.5, 0, 0], angle=-PI / 2), ArcBetweenPoints([-.5, 0, 0], [.5, 0, 0], angle=PI / 2), Circle(radius=.14), color=color)
    elif name == "ruler":
        g = _ic(Rectangle(width=1.0, height=.3), *[Line([x, .15, 0], [x, .15 - (.14 if i % 2 else .08), 0]) for i, x in enumerate(np.linspace(-.4, .4, 9))], color=color)
    elif name == "question":
        g = _ic(Arc(radius=.25, start_angle=PI, angle=-1.35 * PI).shift(UP * .2), Line([0, -.05, 0], [0, -.2, 0]), Dot([0, -.38, 0], radius=.02), color=color)
    elif name == "sparkle":
        s = VMobject().set_points_smoothly([[0, .5, 0], [.1, .1, 0], [.5, 0, 0], [.1, -.1, 0], [0, -.5, 0], [-.1, -.1, 0], [-.5, 0, 0], [-.1, .1, 0], [0, .5, 0]])
        g = _ic(s, color=color)
    elif name == "arrow": g = _ic(Line([-.45, 0, 0], [.45, 0, 0]), Line([.45, 0, 0], [.2, .22, 0]), Line([.45, 0, 0], [.2, -.22, 0]), color=color)
    elif name == "scale":
        g = _ic(Line([0, -.45, 0], [0, .4, 0]), Line([-.45, .3, 0], [.45, .3, 0]), Arc(radius=.18, start_angle=PI, angle=PI).shift([-.4, 0, 0]),
                Arc(radius=.18, start_angle=PI, angle=PI).shift([.4, 0, 0]), Line([-.25, -.45, 0], [.25, -.45, 0]), color=color)
    else: raise ValueError(name)
    return g.scale_to_fit_height(size)

def icon_pop(scene, ic, rt=0.6, halo=True):
    """El icono se DIBUJA (trazo) y rebota; con halo de su color. Luego queda vivo con icon_idle."""
    if halo: scene.add(glow(ic, ic.get_stroke_color(), opacity=0.35))
    ic.save_state(); ic.scale(0.4)
    scene.play(Create(ic, rate_func=ease_out_expo), ic.animate(rate_func=ease_out_back).restore(), run_time=rt)

def icon_idle(ic, kind="bob"):
    """bob (sube-baja) · spin (gira lento) · pulse (late) · tick (oscila como aguja)."""
    ic._t = 0.0; c = ic.get_center().copy()
    def u(m, dt):
        m._t += dt
        if kind == "spin": m.rotate(dt * 0.6)
        elif kind == "pulse": m.scale((1 + 0.05 * np.sin(4 * m._t)) / (1 + 0.05 * np.sin(4 * (m._t - dt))))
        elif kind == "tick": m.rotate(0.02 * np.cos(3 * m._t))
        else: m.move_to(c + UP * 0.05 * np.sin(3 * m._t))
    ic.add_updater(u); return ic

# ---------- 8. Planetas: esfera de mosaico que ROTA (vector, proyección ortográfica real) ----------
def _noise(p, seed, octaves=5, f0=1.1):
    v = np.zeros(len(p)); a = 1.0; f = f0; rng = np.random.default_rng(seed); tot = 0
    for _ in range(octaves):
        for _ in range(3):
            d = rng.normal(size=3); d /= np.linalg.norm(d)
            v += a * np.sin(f * 3.0 * (p @ d) + rng.uniform(0, 6.28)); tot += a
        a *= 0.5; f *= 2.0
    return v / tot * 2

PLANETAS = {
    # radio relativo a la Tierra (datos reales), inclinación axial (°), color de atmósfera, nubes
    "tierra": dict(r=1.0, tilt=23.4, atm="#6FB6FF", clouds=True),
    "marte":  dict(r=0.532, tilt=25.2, atm="#FFB38A", clouds=False),
    "luna":   dict(r=0.273, tilt=6.7, atm=None, clouds=False),
}

def _sph(lat, lon):
    return np.c_[np.cos(lat) * np.cos(lon), np.sin(lat), np.cos(lat) * np.sin(lon)]

def _cell_colors(kind, lat, lon, seed):
    p = _sph(lat, lon); n = _noise(p, seed); w = _noise(p * 2.3, seed + 7, 3); aL = np.abs(np.degrees(lat))
    q = lambda x: np.quantile(n, x)
    cols = []
    for v, ww, a in zip(n, w, aL):
        k = int(abs(ww * 37 + v * 11)) % 4
        if kind == "tierra":
            if a > 74 + 5 * ww: c = ["#F4F8FF", "#E3ECF7", "#D5E2F1", "#F8FBFF"][k]                 # hielo
            elif v > q(0.66):                                                                      # tierra firme (34 %)
                if a < 30 and ww > 0.45: c = ["#D9B26F", "#C79A55", "#E3C07F", "#CFA462"][k]       # desierto
                elif v > q(0.93): c = ["#7A6B55", "#8C7B62", "#6B5D4A", "#9A8A70"][k]             # montaña
                elif a > 55: c = ["#5F7D55", "#6E8B5A", "#7F9563", "#56724D"][k]                  # tundra/taiga
                else: c = ["#3E9A4E", "#2F7F3F", "#4FA852", "#5DB35A"][k]                         # bosque/pradera
            elif v > q(0.60): c = ["#2B9BD8", "#34A6DE", "#2690CF", "#3AAEE3"][k]                # plataforma costera
            else: c = ["#1D5FAE", "#17509A", "#2468BD", "#12447F"][k]                            # océano
        elif kind == "marte":
            if a > 80 + 4 * ww: c = ["#F3EEE8", "#E6DDD2", "#F7F3EE", "#DDD2C4"][k]               # casquete polar
            elif v > q(0.80): c = ["#5E2A17", "#6E3219", "#4F2314", "#7A3A1E"][k]                # regiones oscuras
            elif v > q(0.45): c = ["#B4502A", "#C25E30", "#A34725", "#BA5A2C"][k]                # óxido rojo
            else: c = ["#D9793F", "#C98A4B", "#E09A55", "#B8763E"][k]                            # ocre/café
        else:
            c = ["#9A9CA3", "#8A8C93", "#B2B4BA", "#77797F"][k]
        cols.append(c)
    return cols

class Planet(Group):
    """Planeta de MOSAICO que rota de verdad: ~1600 teselas lat-lon proyectadas cada fotograma (entran por un
    borde y salen por el otro), nubes suaves que giran más rápido (Tierra), terminador degradado (lado noche),
    oscurecimiento de limbo, atmósfera con halo, brillo especular y casquetes polares. `radius` = radio de la
    TIERRA de referencia en unidades Manim; los demás se escalan con su tamaño real (Marte 0,532)."""
    def __init__(self, kind="tierra", radius=1.6, speed=0.16, nlat=28, nlon=56, pitch=16, seed=None, mosaic=True):
        super().__init__()
        cfg = PLANETAS[kind]; self.R = radius * cfg["r"]; self.speed = speed; self.phi = 0.0
        self.pitch = np.radians(pitch); self.tilt = np.radians(cfg["tilt"])
        seed = seed if seed is not None else {"tierra": 5, "marte": 21, "luna": 3}[kind]
        la = np.linspace(-PI / 2, PI / 2, nlat + 1); lo = np.linspace(0, TAU, nlon + 1)
        C = np.array([(la[i], la[i + 1], lo[j], lo[j + 1]) for i in range(nlat) for j in range(nlon)])
        cols = _cell_colors(kind, (C[:, 0] + C[:, 1]) / 2, (C[:, 2] + C[:, 3]) / 2, seed)
        t = np.linspace(0, 1, 4)[:-1]; A, B, Cc, D = C[:, [0]], C[:, [1]], C[:, [2]], C[:, [3]]
        self.lat_s = np.concatenate([A + 0 * t, A + (B - A) * t, B + 0 * t, B - (B - A) * t], 1)
        self.lon_s = np.concatenate([Cc + (D - Cc) * t, D + 0 * t, D - (D - Cc) * t, Cc + 0 * t], 1)
        sw = 0.45 if mosaic else 0
        so = 0.35 * np.cos((C[:, 0] + C[:, 1]) / 2) ** 2               # juntas del mosaico: se desvanecen hacia los polos
        self.tiles = VGroup(*[VMobject(fill_color=c, fill_opacity=1, stroke_color="#0A0F1A", stroke_width=sw, stroke_opacity=o) for c, o in zip(cols, so)])
        # nubes: «bocanadas» elípticas suaves que se aplastan hacia el limbo (no teselas)
        self.puffs = None
        if cfg["clouds"]:
            rng = np.random.default_rng(seed + 99); nc = 34; sub = 5; n = nc * sub      # 34 nubes × 5 bocanadas
            cl = np.clip(rng.normal(0, 0.6, nc), -1.25, 1.25); co = rng.uniform(0, TAU, nc)
            self.p_lat = np.repeat(cl, sub) + rng.normal(0, 0.05, n)
            self.p_lon = np.repeat(co, sub) + rng.normal(0, 0.11, n)
            self.p_r = rng.uniform(0.035, 0.075, n) * self.R; self.p_e = rng.uniform(1.0, 1.8, n)
            circ = Circle(radius=1, num_components=16).points
            self._circ = circ
            self.puffs = VGroup(*[VMobject(fill_color=WHITE, fill_opacity=0.0, stroke_width=0) for _ in range(n)])
            for m in self.puffs: m.set_points(circ.copy())
        if cfg["atm"]: self.add(glow(ORIGIN, cfg["atm"], size=self.R * 3.0, opacity=0.38))
        self.core = Circle(radius=self.R, fill_color="#05070C", fill_opacity=1, stroke_width=0); self.add(self.core)
        self.add(self.tiles)
        if self.puffs is not None: self.add(self.puffs)
        # terminador degradado: el Sol viene de arriba-izquierda; 7 medialunas superpuestas = sombra suave
        for k in range(7):
            s = 0.30 + k * 0.07
            try:
                cres = Difference(Circle(radius=self.R * 1.001), Circle(radius=self.R * 1.18).shift([-self.R * s, self.R * s * 0.6, 0]),
                                  fill_color="#02040A", fill_opacity=0.15, stroke_width=0)
                self.add(cres)
            except Exception: pass
        self.add(VGroup(*[Circle(radius=self.R * (1 - k * 0.015), stroke_color="#02040A", stroke_width=5, stroke_opacity=0.09 * (6 - k)) for k in range(6)]))
        self.add(Circle(radius=self.R, stroke_color=cfg["atm"] or "#CCCCCC", stroke_width=2.4, stroke_opacity=0.6))
        self.add(glow([-self.R * 0.35, self.R * 0.35, 0], WHITE, size=self.R * 1.0, opacity=0.10))
        self._project(); self.add_updater(Planet._tick)

    def _proj(self, lat, lon, R=None):
        k = (self.core.width / 2) / self.R if self.core.width > 0 else 1.0     # sigue cualquier .scale() del planeta
        R = (R or self.R) * k
        x = np.cos(lat) * np.sin(lon); y = np.sin(lat); z = np.cos(lat) * np.cos(lon)
        b = self.pitch; y2 = y * np.cos(b) - z * np.sin(b); z2 = y * np.sin(b) + z * np.cos(b)
        ct, st = np.cos(self.tilt), np.sin(self.tilt)
        P = np.stack([x * ct - y2 * st, x * st + y2 * ct], -1) * R
        vis = z2 > 0; r = np.linalg.norm(P, axis=-1, keepdims=True) + 1e-9
        return np.where(vis[..., None], P, P / r * R), vis, z2

    def _project(self):
        c = self.core.get_center()
        P, vis, _ = self._proj(self.lat_s, self.lon_s + self.phi); anyv = vis.any(1)
        z3 = np.zeros((12, 1)); dead = np.array([c, c])
        for k, m in enumerate(self.tiles):
            if anyv[k]:
                pts = np.hstack([P[k], z3]) + c; m.set_points_as_corners(np.vstack([pts, pts[:1]]))
            else: m.set_points_as_corners(dead)
        if self.puffs is not None:
            Q, v2, z = self._proj(self.p_lat, self.p_lon + self.phi * 1.4 + 0.7, self.R * 1.01)
            for k, m in enumerate(self.puffs):
                if not v2[k] or z[k] < 0.05: m.set_fill(opacity=0); continue
                ang = np.arctan2(Q[k, 1], Q[k, 0]); zz = max(z[k], 0.05)
                cs, sn = np.cos(ang), np.sin(ang); a, b = self.p_r[k] * self.p_e[k] ** 0.5, self.p_r[k] / self.p_e[k] ** 0.5
                base = self._circ[:, :2] * np.array([b * zz + 0.25 * b, a])       # aplastada en la dirección radial
                rot = np.c_[base[:, 0] * cs - base[:, 1] * sn, base[:, 0] * sn + base[:, 1] * cs]
                m.set_points(np.c_[rot + Q[k], np.zeros(len(rot))] + c)
                m.set_fill(opacity=0.30 * min(1, zz * 2.5))

    @staticmethod
    def _tick(m, dt):
        m.phi -= m.speed * dt; m._project()

# ---------- 9. 3D (sólidos de revolución, superficies, áreas) ----------
def ejes3d(x=(-1, 5, 1), y=(-3, 3, 1), z=(-3, 3, 1), length=(7, 5, 5)):
    return ThreeDAxes(x_range=x, y_range=y, z_range=z, x_length=length[0], y_length=length[1], z_length=length[2],
                      axis_config=dict(color=MUTED, stroke_width=2, include_tip=False))

def solido_revolucion(ax, f, a, b, theta, color_a=BLUE, color_b=RED, res=(24, 40)):
    """Superficie de revolución de y=f(x) sobre [a,b] alrededor del eje x, barrida hasta el ángulo theta
    (ValueTracker). Relleno en damero translúcido + alambre brillante: el look de la referencia."""
    def build():
        th = max(theta.get_value(), 1e-3)
        s = Surface(lambda u, v: ax.c2p(u, f(u) * np.cos(v), f(u) * np.sin(v)), u_range=[a, b], v_range=[0, th],
                    resolution=(res[0], max(2, int(res[1] * th / TAU))), checkerboard_colors=[color_a, color_b],
                    fill_opacity=0.28, stroke_color=INK, stroke_width=0.6, stroke_opacity=0.5)
        return s
    return always_redraw(build)

def disco(ax, f, x0, dx, color=GOLD):
    """Un disco del método de discos en x0 con grosor dx (cilindro)."""
    r = f(x0); ux = ax.x_length / (ax.x_range[1] - ax.x_range[0]); uy = ax.y_length / (ax.y_range[1] - ax.y_range[0])
    c = Cylinder(radius=uy * r, height=ux * dx,
                 direction=RIGHT, fill_color=color, fill_opacity=0.55, stroke_color=color, stroke_width=0.8, resolution=(2, 32))
    return c.move_to(ax.c2p(x0, 0, 0))

def riemann(scene, ax, graph, a, b, ns=(4, 8, 16, 48), color_a=BLUE, color_b=MINT, rt=0.9):
    """Rectángulos de Riemann que se refinan (n = 4 → 48) y convergen al área. Devuelve los últimos."""
    rects = ax.get_riemann_rectangles(graph, x_range=[a, b], dx=(b - a) / ns[0], fill_opacity=0.55,
                                      color=(color_a, color_b), stroke_width=1, stroke_color=BG)
    scene.play(LaggedStart(*[GrowFromEdge(r, DOWN) for r in rects], lag_ratio=0.08), run_time=rt)
    for n in ns[1:]:
        nr = ax.get_riemann_rectangles(graph, x_range=[a, b], dx=(b - a) / n, fill_opacity=0.55,
                                       color=(color_a, color_b), stroke_width=0.6 if n < 40 else 0, stroke_color=BG)
        scene.play(Transform(rects, nr, rate_func=ease_in_out_cubic), run_time=rt)
    return rects

# ---------- 10. Ilustración anatómica: CODO (vista lateral, brazo derecho, anterior = derecha) ----------
# Huesos marfil con brillo y borde, cartílago articular azul, cápsula; bíceps (se ACORTA y ENGROSA al flexionar,
# volumen conservado), braquial, braquiorradial y tríceps (se estira y adelgaza), con fibras y tendones.
BONE, BONE_D, BONE_L, CART = "#EDE3CF", "#B9A884", "#FFF9EC", "#8FCBFF"
MUSC, MUSC_D, MUSC_L, TEND = "#E0566A", "#9E3044", "#F2899A", "#F4EADB"

def _smooth(pts, fill, stroke, sw=2.2, fo=1.0):
    m = VMobject(fill_color=fill, fill_opacity=fo, stroke_color=stroke, stroke_width=sw)
    P = [np.array([p[0], p[1], 0.0]) for p in pts]; m.set_points_smoothly(P + [P[0]]); return m

def _muscle(A, B, w, side=1, flat=0.35, fibers=5, fill=MUSC, dark=MUSC_D, light=MUSC_L, t0=0.08, t1=0.92):
    """Vientre muscular fusiforme de A a B, ancho máximo w, abombado hacia `side` (+1 izq. de A→B)."""
    A, B = np.array(A[:2]), np.array(B[:2]); L = np.linalg.norm(B - A); u = (B - A) / L; n = np.array([-u[1], u[0]]) * side
    fs = np.linspace(t0, t1, 8); prof = np.sin(np.pi * (fs - t0) / (t1 - t0)) ** 0.75
    s1 = [A + u * L * f + n * w * p for f, p in zip(fs, prof)]
    s2 = [A + u * L * f - n * w * flat * p for f, p in reversed(list(zip(fs, prof)))]
    body = _smooth([A + u * L * t0 * 0.6] + s1 + [A + u * L * min(1, t1 + 0.04)] + s2, fill, dark, 2.4, 0.95)
    g = VGroup(body)
    for k in range(1, fibers + 1):
        a = -flat + (1 + flat) * k / (fibers + 1)
        pts = [np.r_[A + u * L * f + n * w * p * a, 0] for f, p in zip(fs[1:-1], prof[1:-1])]
        g.add(VMobject(stroke_color=light, stroke_width=1.3, stroke_opacity=0.55).set_points_smoothly(pts))
    g.add(_smooth([A + u * L * f + n * w * p * 0.72 for f, p in zip(fs[2:-2], prof[2:-2])] +
                  [A + u * L * f + n * w * p * 0.9 for f, p in reversed(list(zip(fs[2:-2], prof[2:-2])))], light, light, 0, 0.35))
    g.tip = A + u * L * t1
    return g

class Codo(VGroup):
    """Codo en vista lateral (brazo derecho, la parte anterior mira a la DERECHA). Pivote = centro de la tróclea.
    angle = flexión en grados (0 extendido, 90 antebrazo horizontal hacia la derecha, ~145 máx. fisiológico).
    Uso: v = ValueTracker(20); codo.add_updater(lambda m: m.set_angle(v.get_value())).
    Tamaño SOLO con height= (no usar .scale después); mover con move_to/shift/to_edge.
    Partes: .humero, .antebrazo, .biceps, .braquial, .braquiorradial, .triceps. Puntos: .puntos()."""
    def __init__(self, height=6.0, angle=90, fibras=True):
        super().__init__()
        k = height / 6.2; self.k = k; S = lambda pts: [(x * k, y * k) for x, y in pts]
        # ----- húmero (vertical, hacia arriba desde el pivote) -----
        shaft = _smooth(S([(-0.17, 3.3), (-0.16, 2.2), (-0.15, 1.2), (-0.2, 0.6), (-0.38, 0.28), (-0.33, 0.05), (-0.12, -0.25),
                           (0.12, -0.3), (0.3, -0.2), (0.4, 0.05), (0.36, 0.4), (0.2, 0.75), (0.16, 1.3), (0.17, 2.2), (0.19, 3.3)]),
                        BONE, BONE_D, 2.4)
        capit = Circle(radius=0.27 * k, fill_color=BONE, fill_opacity=1, stroke_color=BONE_D, stroke_width=2.2).move_to([0.05 * k, -0.02 * k, 0])
        fossa = _smooth(S([(-0.2, 0.55), (-0.12, 0.62), (-0.05, 0.5), (-0.1, 0.35), (-0.19, 0.38)]), BONE_D, BONE_D, 0, 0.45)
        hl = _smooth(S([(0.02, 3.3), (0.05, 2.0), (0.05, 1.0), (0.09, 1.0), (0.1, 2.0), (0.08, 3.3)]), BONE_L, BONE_L, 0, 0.7)
        ridge = VMobject(stroke_color=BONE_D, stroke_width=1.6, stroke_opacity=0.8).set_points_smoothly([np.r_[p, 0] for p in S([(0.18, 1.2), (0.26, 0.7), (0.36, 0.35)])])
        cart_h = Arc(radius=0.29 * k, start_angle=np.radians(200), angle=np.radians(200), arc_center=[0.05 * k, -0.02 * k, 0],
                     stroke_color=CART, stroke_width=6)
        self.piv = Dot([0.05 * k, -0.02 * k, 0], radius=1e-4, fill_opacity=0)
        self.humero = VGroup(shaft, capit, fossa, hl, ridge, cart_h, self.piv)
        # ----- antebrazo en pose de referencia (extendido, hacia ABAJO) -----
        ulna_b = _smooth(S([(-0.3, 0.32), (-0.46, 0.2), (-0.44, -0.1), (-0.3, -0.42), (-0.22, -0.8), (-0.18, -2.0), (-0.12, -3.1),
                            (-0.02, -3.2), (0.02, -3.1), (-0.01, -2.0), (0.02, -0.9), (0.14, -0.5), (0.3, -0.36), (0.22, -0.3),
                            (0.05, -0.36), (-0.14, -0.28), (-0.26, -0.08), (-0.26, 0.2)]), BONE, BONE_D, 2.4)
        rad_b = _smooth(S([(0.12, -0.36), (0.42, -0.36), (0.4, -0.5), (0.3, -0.56), (0.3, -0.8), (0.4, -0.95), (0.33, -1.1),
                           (0.31, -2.0), (0.36, -2.8), (0.42, -3.15), (0.12, -3.2), (0.1, -2.8), (0.14, -2.0), (0.15, -1.1),
                           (0.15, -0.8), (0.16, -0.56), (0.08, -0.5)]), "#E7DCC4", BONE_D, 2.4)
        cart_u = Arc(radius=0.33 * k, start_angle=np.radians(215), angle=np.radians(120), arc_center=[0.05 * k, -0.02 * k, 0],
                     stroke_color=CART, stroke_width=4, stroke_opacity=0.9)
        hl2 = _smooth(S([(-0.1, -0.9), (-0.08, -2.0), (-0.06, -3.0), (-0.03, -3.0), (-0.04, -2.0), (-0.06, -0.9)]), BONE_L, BONE_L, 0, 0.6)
        tub = Dot([0.36 * k, -0.95 * k, 0], radius=0.035 * k, color=BONE_D)
        self._fore_home = VGroup(ulna_b, hl2, cart_u, rad_b, tub)
        # puntos de inserción en pose de referencia (se rotan con el antebrazo)
        self._home = dict(tub=np.array([0.36, -0.95]) * k, uln=np.array([0.2, -0.45]) * k, olec=np.array([-0.4, 0.22]) * k,
                          br=np.array([0.36, -2.75]) * k, mano=np.array([0.15, -3.2]) * k, piv=np.array([0.05, -0.02]) * k)
        self._org = dict(bic=np.array([0.3, 3.3]) * k, bra=np.array([0.18, 1.5]) * k, brr=np.array([0.28, 1.05]) * k,
                         tri=np.array([-0.3, 3.3]) * k)
        self.fibras = fibras; self.theta = 0.0
        self.antebrazo = VGroup(); self.biceps = VGroup(); self.braquial = VGroup(); self.braquiorradial = VGroup(); self.triceps = VGroup()
        self.tendones = VGroup()
        self.add(self.triceps, self.braquiorradial, self.humero, self.antebrazo, self.braquial, self.biceps, self.tendones)
        self.L0 = {}; self.set_angle(0); self.L0 = self._lengths(); self.set_angle(angle)
        self.move_to(ORIGIN)

    def _off(self): return self.piv.get_center()[:2] - self._home["piv"]
    def _R(self, p):
        c, s = np.cos(self.theta), np.sin(self.theta); pv = self.piv.get_center()[:2]; d = p + self._off() - pv
        return pv + np.array([d[0] * c - d[1] * s, d[0] * s + d[1] * c])
    def _lengths(self):
        o = self._off()
        return dict(bic=np.linalg.norm(self._R(self._home["tub"]) - (self._org["bic"] + o)),
                    bra=np.linalg.norm(self._R(self._home["uln"]) - (self._org["bra"] + o)),
                    brr=np.linalg.norm(self._R(self._home["br"]) - (self._org["brr"] + o)),
                    tri=np.linalg.norm(self._R(self._home["olec"]) - (self._org["tri"] + o)))

    def set_angle(self, deg):
        self.theta = np.radians(deg)                       # antihorario: el antebrazo sube hacia la derecha (anterior)
        o = self._off(); pv = self.piv.get_center()
        self.antebrazo.become(self._fore_home.copy().shift(np.r_[o, 0]).rotate(self.theta, about_point=pv))
        k = self.k; Ls = self._lengths(); L0 = self.L0 or Ls
        g = lambda key: (L0[key] / Ls[key]) ** 1.3        # engrosa al acortarse, adelgaza al estirarse
        tub, uln, olec, br = (self._R(self._home[x]) for x in ("tub", "uln", "olec", "br"))
        bi = _muscle(self._org["bic"] + o, tub, 0.34 * k * g("bic"), side=-1, fibers=6 if self.fibras else 0, t1=0.78)
        ba = _muscle(self._org["bra"] + o, uln, 0.2 * k * g("bra"), side=-1, fibers=4 if self.fibras else 0, fill="#C94A5C", t1=0.85)
        brr = _muscle(self._org["brr"] + o, br, 0.13 * k * g("brr"), side=-1, fibers=3 if self.fibras else 0, fill="#D0606F", t1=0.9)
        tr = _muscle(self._org["tri"] + o, olec, 0.3 * k * g("tri"), side=1, fibers=5 if self.fibras else 0, fill=MUSC_D, dark="#6E1F2E", t1=0.8)
        self.biceps.become(bi); self.braquial.become(ba); self.braquiorradial.become(brr); self.triceps.become(tr)
        self.tendones.become(VGroup(Line(np.r_[bi.tip, 0], np.r_[tub, 0], stroke_color=TEND, stroke_width=7),
                                    Line(np.r_[ba.tip, 0], np.r_[uln, 0], stroke_color=TEND, stroke_width=5),
                                    Line(np.r_[tr.tip, 0], np.r_[olec, 0], stroke_color=TEND, stroke_width=6)))
        return self

    def puntos(self):
        """eje (fulcro), insercion (bíceps en la tuberosidad radial), mano (extremo del antebrazo), olecranon."""
        return dict(eje=self.piv.get_center(), insercion=np.r_[self._R(self._home["tub"]), 0],
                    mano=np.r_[self._R(self._home["mano"]), 0], olecranon=np.r_[self._R(self._home["olec"]), 0])

    def anclar(self, punto):
        """Coloca el PIVOTE (centro de la tróclea) en `punto`. Úsese en vez de move_to cuando importa dónde cae la
        articulación (diagramas de torque)."""
        self.shift(np.array(punto) - self.piv.get_center()); return self

# ---------- 11. Fondo para escenas 3D ----------
def fondo3d(scene, phi=70, theta=-50, zoom=1.0):
    """Primera línea de TODA ThreeDScene: cámara + estrellas fijas al cuadro (quedan DETRÁS de lo 3D)."""
    scene.camera.background_color = BG
    scene.set_camera_orientation(phi=phi * DEGREES, theta=theta * DEGREES, zoom=zoom)
    c = Cosmos(); scene.add_fixed_in_frame_mobjects(c); c.set_z_index(-100)
    return c

def rotulo(scene, punto, texto, hacia=UR, largo=1.1, color=MUTED, size=22, rt=0.6):
    """Rótulo con línea guía: un punto que late, una línea quebrada que se dibuja y el texto que se teclea.
    Para señalar partes de una ilustración («tuberosidad del radio», «fulcro»)."""
    p = np.array(punto); q = p + normalize(hacia) * largo * 0.6; r = q + (RIGHT if hacia[0] >= 0 else LEFT) * largo * 0.5
    dot = Dot(p, radius=0.05, color=GOLD); ln = VMobject(stroke_color=color, stroke_width=1.8).set_points_as_corners([p, q, r])
    t = MONO_T(texto, size, INK).next_to(r, RIGHT if hacia[0] >= 0 else LEFT, buff=0.12)
    if t.get_right()[0] > FW / 2 - 0.3 or t.get_left()[0] < -FW / 2 + 0.3:      # no cabe: se voltea al otro lado
        hacia = np.array([-hacia[0], hacia[1], 0]); q = p + normalize(hacia) * largo * 0.6
        r = q + (RIGHT if hacia[0] >= 0 else LEFT) * largo * 0.5
        ln = VMobject(stroke_color=color, stroke_width=1.8).set_points_as_corners([p, q, r])
        t.next_to(r, RIGHT if hacia[0] >= 0 else LEFT, buff=0.12)
    scene.play(GrowFromCenter(dot, rate_func=ease_out_back), Create(ln, rate_func=ease_out_expo), run_time=rt * 0.6)
    scene.play(AddTextLetterByLetter(t, time_per_char=0.025))
    dot.add_updater(lambda m, dt: m.set(width=0.1 * (1 + 0.25 * np.sin(6 * getattr(scene, "time", 0)))))
    return VGroup(dot, ln, t)

# ---------- 12. Simulaciones de referencia (v2.3): pseudo-3D propio, Rubik, relojes de ciclo, grafo, péndulos, muestreo ----------
import itertools
# Todo es Scene 2D con proyección ortográfica PROPIA (Proyector): mucho más barato que ThreeDScene (~0,1 s/fotograma) y
# con control total del orden de dibujo. Las simulaciones son la ecuación real: el cubo es una permutación de 54 pegatinas,
# los péndulos siguen θ_k = θ0·cos(2π N_k t / 60) con su largo real L_k = g/ω_k², el muestreo es cos(2π τ x) en x enteros.
class Proyector:
    """Cámara ortográfica para pseudo-3D. Mundo: x derecha, y arriba, z hacia el espectador.
    yaw < 0 deja ver la cara derecha (+x); pitch > 0 deja ver la cara de arriba (+y). escala = unidades Manim por unidad."""
    def __init__(self, yaw=-35, pitch=24, escala=1.0, centro=ORIGIN):
        self.yaw, self.pitch, self.escala, self.centro = yaw, pitch, escala, np.array(centro, dtype=float)
    def M(self):
        y, p = np.radians(self.yaw), np.radians(self.pitch)
        Ry = np.array([[np.cos(y), 0, np.sin(y)], [0, 1, 0], [-np.sin(y), 0, np.cos(y)]])
        Rx = np.array([[1, 0, 0], [0, np.cos(p), -np.sin(p)], [0, np.sin(p), np.cos(p)]])
        return Rx @ Ry
    def __call__(self, P, M=None):
        """P (n,3) → puntos de pantalla (n,3) con z=0, y profundidad (n,) (mayor = más cerca)."""
        Q = np.atleast_2d(P) @ (M if M is not None else self.M()).T
        S = np.c_[Q[:, 0] * self.escala, Q[:, 1] * self.escala, np.zeros(len(Q))] + self.centro
        return S, Q[:, 2]

def _rot(ax, ang):
    c, s = np.cos(ang), np.sin(ang)
    if ax == 0: return np.array([[1, 0, 0], [0, c, -s], [0, s, c]])
    if ax == 1: return np.array([[c, 0, s], [0, 1, 0], [-s, 0, c]])
    return np.array([[c, -s, 0], [s, c, 0], [0, 0, 1]])

# ---- Cubo de Rubik ----
RUBIK_COLORES = {(0, 1, 0): "#F1F3F7", (0, -1, 0): "#FFC53D", (0, 0, 1): "#1DB97E",
                 (0, 0, -1): "#3D7BFF", (1, 0, 0): "#E8336D", (-1, 0, 0): "#FF8A3D"}   # U blanco · D amarillo · F verde · B azul · R rojo · L naranja
RUBIK_MOV = {"R": (0, 1, -1), "L": (0, -1, 1), "U": (1, 1, -1), "D": (1, -1, 1), "F": (2, 1, -1), "B": (2, -1, 1)}   # eje, capa, sentido

def _pegatina(n=4, h=0.41, r=0.09):
    """Cuadrado redondeado en coordenadas locales (u, v)."""
    P = []
    for cx, cy, a0 in [(h - r, h - r, 0), (-h + r, h - r, 90), (-h + r, -h + r, 180), (h - r, -h + r, 270)]:
        for i in range(n + 1):
            a = np.radians(a0 + 90 * i / n); P.append((cx + r * np.cos(a), cy + r * np.sin(a)))
    return np.array(P)
_PEG = _pegatina()
_CARAS = [np.array(v) for v in [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]]

class Rubik(VGroup):
    """Cubo de Rubik 3×3 que GIRA DE VERDAD: 26 piezas con posición y orientación enteras; cada giro es una rotación
    de 90° de una capa (animada con un ángulo continuo y luego fijada en enteros, sin deriva). Se dibuja con el Proyector
    propio y orden del pintor por pieza. Cuerpos negros, pegatinas redondeadas, caras internas visibles al girar.
    Uso: cubo = Rubik(lado=3.2).move_to(...); cubo.girar(self, "R U", rt=0.35); cubo.aplicar("R U" * 100) (instantáneo).
    Resaltar: cubo.foco(ids, color, ruta=True) atenúa el resto y une las piezas del ciclo con una línea (ids = posiciones
    de origen, ver Rubik.ciclos). cubo.foco(None) lo quita. vivo=True: el cubo se balancea despacio (nunca está quieto)."""
    def __init__(self, lado=3.0, yaw=-34, pitch=26, vivo=True):
        super().__init__()
        self.cam = Proyector(yaw, pitch, lado / 3.0); self.yaw0 = yaw; self.vivo = vivo; self._t = 0.0
        self.piezas = []
        for p in itertools.product([-1, 0, 1], repeat=3):
            if p == (0, 0, 0): continue
            home = np.array(p); peg = [np.array(d) for d in RUBIK_COLORES if np.dot(d, home) == 1]
            self.piezas.append(dict(home=home, pos=home.copy(), O=np.eye(3, dtype=int), peg=peg))
        self.slots = VGroup(*[VMobject(fill_opacity=1, stroke_width=0) for _ in range(26 * 3 + 54 + 12)])   # caras visibles máx.
        self.add(self.slots)
        self.capa = None            # (eje, capa, ángulo) del giro en curso
        self._foco, self._fcol = None, GOLD
        self.ruta = VMobject(stroke_color=GOLD, stroke_width=3, stroke_opacity=0.0)
        self.ruta_pts = VGroup(*[Dot(radius=0.05, color=GOLD, fill_opacity=0) for _ in range(8)])
        self.add(self.ruta, self.ruta_pts)
        self._centro = ORIGIN.copy(); self._dibujar()
        self.add_updater(Rubik._tick)

    # ----- estado -----
    @staticmethod
    def _parse(seq):
        out = []
        for m in seq.split():
            k = 3 if m.endswith("'") else 2 if m.endswith("2") else 1
            out.append((m[0], k))
        return out
    def _commit(self, ax, layer, sg, k=1):
        R = np.rint(_rot(ax, sg * k * PI / 2)).astype(int)
        for q in self.piezas:
            if q["pos"][ax] == layer: q["pos"] = R @ q["pos"]; q["O"] = R @ q["O"]
    def aplicar(self, seq):
        """Aplica una secuencia SIN animar (avance rápido)."""
        for m, k in self._parse(seq):
            ax, layer, sg = RUBIK_MOV[m]; self._commit(ax, layer, sg, k)
        self._dibujar(); return self
    def resuelto(self):
        return all((q["pos"] == q["home"]).all() and (abs(q["home"]).sum() == 1 or (q["O"] == np.eye(3)).all()) for q in self.piezas)   # los centros giran sin que se note
    def girar(self, scene, seq, rt=0.35, rate=None, con=()):
        """Anima cada giro de la secuencia (rt por cuarto de vuelta), con easing de motion graphic.
        con = animaciones que se reproducen JUNTO al último giro (p. ej. el contador que sube)."""
        movs = self._parse(seq)
        for i, (m, k) in enumerate(movs):
            ax, layer, sg = RUBIK_MOV[m]; a = ValueTracker(0)
            target = sg * (PI / 2) * (-1 if k == 3 else k)
            self.capa = [ax, layer, 0.0]
            def u(mob, a=a): mob.capa[2] = a.get_value()
            self.add_updater(u)
            extra = list(con) if i == len(movs) - 1 else []
            scene.play(a.animate(rate_func=rate or ease_in_out_cubic).set_value(target), *extra, run_time=rt * (1.5 if k == 2 else 1))
            self.remove_updater(u); self.capa = None
            self._commit(ax, layer, sg, 1 if k == 1 else k if k == 2 else 3)
            self._dibujar()

    @staticmethod
    def ciclos(seq):
        """Ciclos de piezas de una secuencia: lista de dict(tipo 'arista'|'esquina', ids=[home…] en orden, orden=k)."""
        c = Rubik.__new__(Rubik); c.piezas = [dict(home=np.array(p), pos=np.array(p), O=np.eye(3, dtype=int))
                                              for p in itertools.product([-1, 0, 1], repeat=3) if p != (0, 0, 0)]
        for m, k in Rubik._parse(seq):
            ax, layer, sg = RUBIK_MOV[m]; R = np.rint(_rot(ax, sg * k * PI / 2)).astype(int)
            for q in c.piezas:
                if q["pos"][ax] == layer: q["pos"] = R @ q["pos"]; q["O"] = R @ q["O"]
        mp = {tuple(q["home"]): (tuple(q["pos"]), q["O"]) for q in c.piezas}; vis, res = set(), []
        for h in mp:
            if h in vis or sum(map(abs, h)) < 2: continue
            cyc = [h]; vis.add(h); x = mp[h][0]
            while x != h: cyc.append(x); vis.add(x); x = mp[x][0]
            O = np.eye(3, dtype=int); x = h                     # orientación acumulada tras recorrer el ciclo
            for _ in cyc: O = mp[x][1] @ O; x = mp[x][0]
            kO = 1; P = O.copy()
            while not (P == np.eye(3)).all(): P = O @ P; kO += 1
            if len(cyc) > 1 or kO > 1:
                res.append(dict(tipo="arista" if sum(map(abs, h)) == 2 else "esquina", ids=cyc, orden=len(cyc) * kO))
        return res

    def foco(self, ids=None, color=GOLD, ruta=True):
        self._foco = None if ids is None else {tuple(i) for i in ids}; self._fcol = color
        self._ruta_ids = list(ids) if (ids is not None and ruta and len(ids) > 1) else []
        self._dibujar(); return self

    # ----- dibujo -----
    def _dibujar(self):
        # IMPORTANTE (v2.3): durante un self.play Manim CONGELA el orden de dibujo de los mobjects que se mueven
        # (aplana la familia al empezar la animación). Reordenar submobjects a mitad de animación no sirve: el orden
        # del pintor se aplica rellenando un juego FIJO de polígonos (self.slots) en el orden calculado.
        cam = self.cam; cam.centro = self._centro; M = cam.M(); orden = []
        # Orden del pintor en DOS niveles: durante un giro, la capa que gira y el resto están separados por un plano;
        # se dibuja primero el grupo del lado lejano a la cámara y, dentro de cada grupo, por profundidad de la pieza.
        cerca = None
        if self.capa is not None:
            e = np.zeros(3); e[self.capa[0]] = np.sign(self.capa[1]); cerca = (M @ e)[2] > 0     # ¿la capa que gira mira a la cámara?
        for q in self.piezas:
            p = q["pos"].astype(float); Rl = np.eye(3); g0 = 0
            if self.capa is not None:
                gira = q["pos"][self.capa[0]] == self.capa[1]
                if gira: Rl = _rot(self.capa[0], self.capa[2])
                g0 = int(gira == cerca)
            orden.append((g0, (M @ (Rl @ p))[2], q, Rl))
        orden.sort(key=lambda o: (o[0], o[1]))
        dim = self._foco is not None; polys = []          # (puntos, relleno, trazo, grosor)
        for _, _, q, Rl in orden:
            p = q["pos"].astype(float); on = (not dim) or tuple(q["home"]) in self._foco
            for e in _CARAS:
                n = Rl @ e
                if (M @ n)[2] <= 1e-3: continue
                u = Rl @ np.roll(e, 1); v = Rl @ np.roll(e, 2); cc = Rl @ p + 0.5 * n
                S, _ = cam(np.array([cc + 0.5 * u + 0.5 * v, cc - 0.5 * u + 0.5 * v, cc - 0.5 * u - 0.5 * v, cc + 0.5 * u - 0.5 * v]), M)
                polys.append((S, "#151A24" if on else "#0F131B", "#2A3245", 1.2))
            for d in q["peg"]:
                n = Rl @ (q["O"] @ d)
                if (M @ n)[2] <= 1e-3: continue
                u = Rl @ (q["O"] @ np.roll(d, 1)); v = Rl @ (q["O"] @ np.roll(d, 2)); cc = Rl @ p + 0.502 * n
                S, _ = cam(cc + _PEG[:, :1] * u + _PEG[:, 1:] * v, M)
                col = RUBIK_COLORES[tuple(d)]
                if on: polys.append((S, col, self._fcol if dim else col, 3.5 if dim else 0))
                else: polys.append((S, interpolate_color(ManimColor(col), ManimColor(BG), 0.82), col, 0))
        for k, sl in enumerate(self.slots):
            if k < len(polys):
                S, f, c, w = polys[k]
                sl.set_points_as_corners(np.vstack([S, S[:1]])); sl.set_fill(f, opacity=1); sl.set_stroke(c, width=w, opacity=1)
            else:
                sl.set_points_as_corners([self._centro, self._centro]); sl.set_fill(opacity=0); sl.set_stroke(width=0)
        # ruta del ciclo: posiciones (fijas en el cubo) unidas en orden, con un punto en cada una
        ids = getattr(self, "_ruta_ids", [])
        if ids:
            P = np.array([np.array(h, float) * 1.08 for h in ids]); S, _ = cam(P, M)
            self.ruta.set_points_as_corners(np.vstack([S, S[:1]])); self.ruta.set_stroke(self._fcol, opacity=0.9)
            for k, dt in enumerate(self.ruta_pts):
                if k < len(S): dt.move_to(S[k]).set_fill(self._fcol, opacity=1)
                else: dt.set_fill(opacity=0)
        else:
            self.ruta.set_stroke(opacity=0); [dt.set_fill(opacity=0) for dt in self.ruta_pts]

    def move_to(self, point, **kw):
        self._centro = np.array(point, dtype=float); self._dibujar(); return self
    def shift(self, *v):
        self._centro = self._centro + sum(np.array(x, dtype=float) for x in v); self._dibujar(); return self
    def set_lado(self, lado):
        self.cam.escala = lado / 3.0; self._dibujar(); return self

    @staticmethod
    def _tick(m, dt):
        m._t += dt
        if m.vivo: m.cam.yaw = m.yaw0 + 5 * np.sin(0.45 * m._t); m.cam.pitch = 26 + 2.5 * np.sin(0.31 * m._t + 1)
        m._dibujar()

# ---- Reloj de ciclo ----
class RelojCiclo(Group):
    """Reloj que cuenta un ciclo de n pasos: aguja que avanza 1/n de vuelta por paso, marcas, número del ciclo y nombre.
    Se ENCIENDE (anillo grueso + relleno de su color + halo) cada vez que completa la vuelta. set_paso(k) admite k
    continuo (la aguja gira suave). Ideal para órdenes de permutaciones, periodos, mcm."""
    def __init__(self, n, nombre, color=GOLD, r=0.62):
        super().__init__()
        self.n, self.r, self.col = n, r, color
        self.halo = glow(ORIGIN, color, size=r * 4.2, opacity=0.0)
        self.disco = Circle(radius=r, fill_color=BG2, fill_opacity=0.9, stroke_color=color, stroke_width=2.2, stroke_opacity=0.55)
        self.marcas = VGroup(*[Dot(r * 0.84 * np.array([np.sin(TAU * i / n), np.cos(TAU * i / n), 0]), radius=0.022 if i else 0.04,
                                   color=color if i == 0 else MUTED) for i in range(n)])
        self.num = T(str(n), int(34 * r / 0.62), color).move_to(DOWN * r * 0.42)
        self.aguja = Line(ORIGIN, UP * r * 0.72, stroke_color=INK, stroke_width=4.5)
        self.eje = Dot(radius=0.045, color=INK)
        self.nombre = MONO_T(nombre, 20, MUTED).next_to(self.disco, DOWN, buff=0.16)
        self.add(self.halo, self.disco, self.marcas, self.num, self.aguja, self.eje, self.nombre)
        self.k = 0.0
    def set_paso(self, k):
        self.k = k; c = self.disco.get_center(); a = TAU * (k % self.n) / self.n
        self.aguja.put_start_and_end_on(c, c + self.r * 0.72 * np.array([np.sin(a), np.cos(a), 0]))
        d = abs(k - self.n * round(k / self.n)); lit = max(0.0, 1 - d / 0.6) if k > 0.5 else 0.0
        self.disco.set_stroke(width=2.2 + 4 * lit, opacity=0.55 + 0.45 * lit)
        self.disco.set_fill(interpolate_color(ManimColor(BG2), ManimColor(self.col), 0.28 * lit), opacity=0.9)
        self.halo.set_opacity(0.45 * lit).move_to(c); return self

# ---- Grafo de estados ----
def nube_estados(n=150, ancho=10, alto=5, seed=5, centro=ORIGIN, r=0.022):
    """Nube de puntos tenues: el espacio de estados (posiciones, configuraciones)."""
    rng = np.random.default_rng(seed)
    return VGroup(*[Dot(np.array(centro) + [rng.uniform(-ancho / 2, ancho / 2), rng.uniform(-alto / 2, alto / 2), 0], radius=r,
                        color=MUTED, fill_opacity=rng.uniform(0.35, 0.8)) for _ in range(n)])

def flecha_curva(a, b, color=INK, angle=-0.55, sw=2.4, buff=0.14):
    """Flecha curva entre dos mobjects (o puntos) que se recalcula si se mueven (usar dentro de always_redraw)."""
    pa = a.get_center() if isinstance(a, Mobject) else np.array(a); pb = b.get_center() if isinstance(b, Mobject) else np.array(b)
    d = pb - pa; L = np.linalg.norm(d) + 1e-9; pa2, pb2 = pa + d / L * buff, pb - d / L * buff
    return CurvedArrow(pa2, pb2, angle=angle, color=color, stroke_width=sw, tip_length=0.16)

# ---- Banco de péndulos (pendulum wave) ----
G_TIERRA = 9.81
class Pendulos(Group):
    """Banco de péndulos con su física real: el péndulo k hace N_k idas y vueltas por minuto, ω_k = 2π N_k / 60,
    largo real L_k = g / ω_k² (dibujado a escala relativa) y ángulo θ_k(t) = θ0·cos(ω_k t) (péndulo de ángulo pequeño).
    Oscilan en el plano z (profundidad); la cámara propia (Proyector) puede moverse: oblicua → casi cenital deja ver la onda.
    tiempo = ValueTracker en SEGUNDOS simulados. Colores en degradado MINT → CYAN → BLUE → VIOLET → RED.
    Uso: tt = ValueTracker(0); P = Pendulos(tt); self.play(tt.animate(rate_func=linear).set_value(4), run_time=4)."""
    def __init__(self, tiempo, ns=range(51, 66), ancho=8.0, alto=3.4, theta0=0.32, cam=None, centro=ORIGIN, glow_on=True):
        super().__init__()
        self.tt, self.ns = tiempo, list(ns); self.theta0 = theta0
        self.cam = cam or Proyector(-38, 18, 1.0, centro)
        w = 2 * np.pi * np.array(self.ns) / 60.0; self.w = w
        Lr = G_TIERRA / w ** 2; self.L = alto * Lr / Lr.max()            # largo real, a escala
        self.xs = np.linspace(-ancho / 2, ancho / 2, len(self.ns)); self.y0 = alto / 2 + 0.3; self.ancho = ancho
        self.cols = [ManimColor(c) for c in color_gradient([MINT, CYAN, BLUE, VIOLET, RED], len(self.ns))]
        self.suelo = VMobject(fill_color="#1A2233", fill_opacity=0.55, stroke_color=FAINT, stroke_width=1.2)
        self.marco = VGroup(*[Line(ORIGIN, RIGHT, stroke_color="#C9D2E3", stroke_width=w_) for w_ in (4, 2.2, 2.2)])
        self.hilos = VGroup(*[Line(ORIGIN, RIGHT, stroke_color="#C9D2E3", stroke_width=1.1, stroke_opacity=0.55) for _ in self.ns])
        self.halos = Group(*[glow(ORIGIN, c, size=0.75, opacity=0.5) for c in self.cols]) if glow_on else Group()
        self.bolas = VGroup(*[Dot(radius=0.12, color=c).set_sheen(-0.35, DR) for c in self.cols])
        self.brillo = VGroup(*[Dot(radius=0.035, color=WHITE, fill_opacity=0.85) for _ in self.ns])
        self.alfa = 1.0
        self.add(self.suelo, self.marco, self.hilos, self.halos, self.bolas, self.brillo)
        self._dibujar(); self.add_updater(lambda m: m._dibujar())
    def posiciones(self, t=None):
        t = self.tt.get_value() if t is None else t; th = self.theta0 * np.cos(self.w * t)
        return np.c_[self.xs, self.y0 - self.L * np.cos(th), self.L * np.sin(th)]
    def _dibujar(self):
        cam = self.cam; M = cam.M(); B = self.posiciones(); a = self.alfa
        top = np.c_[self.xs, np.full(len(self.xs), self.y0), np.zeros(len(self.xs))]
        hw, yb, zd = self.ancho / 2 + 0.5, -self.y0 + 0.2, 1.6
        S, _ = cam(np.array([[-hw, yb, -zd], [hw, yb, -zd], [hw, yb, zd], [-hw, yb, zd]]), M)
        self.suelo.set_points_as_corners(np.vstack([S, S[:1]])); self.suelo.set_fill(opacity=0.55 * a); self.suelo.set_stroke(opacity=a)
        E, _ = cam(np.array([[-hw, self.y0, 0], [hw, self.y0, 0], [-hw, yb, 0], [hw, yb, 0]]), M)
        self.marco[0].put_start_and_end_on(E[0], E[1]); self.marco[1].put_start_and_end_on(E[0], E[2]); self.marco[2].put_start_and_end_on(E[1], E[3])
        for m_ in self.marco: m_.set_stroke(opacity=0.9 * a)
        St, _ = cam(top, M); Sb, zb = cam(B, M)
        for k in range(len(self.ns)):
            self.hilos[k].put_start_and_end_on(St[k], Sb[k]); self.hilos[k].set_stroke(opacity=0.5 * a)
            s = 1 + 0.18 * np.tanh(zb[k])                                # más cerca = un poco más grande
            self.bolas[k].set(width=0.24 * s).move_to(Sb[k]).set_fill(opacity=a)
            self.brillo[k].move_to(Sb[k] + np.array([-0.04, 0.045, 0]) * s).set_fill(opacity=0.85 * a)
            if len(self.halos): self.halos[k].move_to(Sb[k]).set_opacity(0.5 * a)

# ---- Muestreo y aliasing ----
def onda_muestreada(ax, tau, n=15, colores=None, real=True, alias=True):
    """Muestras y_k = cos(2π τ k), k = 0…n-1 (p. ej., la posición de cada péndulo en la fracción de minuto τ).
    real: la onda continua cos(2π τ x) (dorada, rápida) que pasa por las muestras · alias: la onda MÁS LENTA que pasa por
    las mismas muestras, cos(2π (τ − round τ) x) (blanca). Cuando τ se acerca a un entero, la rápida y la lenta coinciden
    en las muestras: eso es el aliasing. Devuelve un VGroup (usar en always_redraw con un ValueTracker de τ)."""
    colores = colores or [interpolate_color(ManimColor(MINT), ManimColor(RED), i / (n - 1)) for i in range(n)]
    g = VGroup(); x0, x1 = -0.4, n - 0.6
    if real:
        op = float(np.clip((tau - 0.55) / 0.2, 0, 1))
        if op > 0: g.add(ax.plot(lambda x: np.cos(TAU * tau * x), x_range=[x0, x1, 0.01], color=GOLD, stroke_width=2.6, stroke_opacity=0.85 * op))
    if alias:
        ta = tau - round(tau)
        g.add(ax.plot(lambda x: np.cos(TAU * ta * x), x_range=[0, n - 1, 0.02], color=INK, stroke_width=2.2, stroke_opacity=0.75))
    for k in range(n):
        y = np.cos(TAU * tau * k); p = ax.c2p(k, y)
        g.add(Line(ax.c2p(k, 0), p, stroke_color=colores[k], stroke_width=1.6, stroke_opacity=0.5))
        g.add(Dot(p, radius=0.17, color=colores[k], fill_opacity=0.22)); g.add(Dot(p, radius=0.085, color=colores[k]))
    return g

def fasores(centro, r, tau, n=15, colores=None):
    """n agujas de un mismo reloj con fases 2π τ k: en τ = 1/4 caen en 4 direcciones (cuadrado), en 2/5 forman una estrella
    de 5, en 1/2 se reparten en 2 y en τ entero se alinean. Mismo dato que onda_muestreada, visto como reloj."""
    colores = colores or [interpolate_color(ManimColor(MINT), ManimColor(RED), i / (n - 1)) for i in range(n)]
    c = np.array(centro); g = VGroup()
    for k in range(n - 1, -1, -1):
        a = TAU * tau * k; p = c + r * np.array([np.sin(a), np.cos(a), 0])
        g.add(Line(c, p, stroke_color=colores[k], stroke_width=2, stroke_opacity=0.7))
        g.add(Dot(p, radius=0.08, color=colores[k]))
    return g
