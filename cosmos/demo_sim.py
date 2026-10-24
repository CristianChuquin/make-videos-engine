# demo_sim.py — reel v2.3 del tipo 1: R U = 105 · grafo de estados · pendulum wave · aliasing
from estilo import *
import math
WF = 1.0
if os.environ.get("MV_FAST"): config.pixel_width, config.pixel_height, config.frame_rate = 640, 360, 10

CIC = {c["tipo"] + str(len(c["ids"])): c for c in Rubik.ciclos("R U")}   # arista7 (orden 7) · esquina5 (orden 15) · esquina1 (orden 3)
assert math.lcm(*[c["orden"] for c in CIC.values()]) == 105


class E01Cubo(Scene):
    """Gancho + ciclos: R U repetido, tres relojes (7, 15, 3) y el mcm = 105."""
    def construct(self):
        fondo(self)
        cubo = Rubik(lado=3.5).move_to(LEFT * 3.4 + DOWN * 0.15)
        tam = ValueTracker(0.05); up = lambda m: m.set_lado(tam.get_value())
        cubo.add_updater(up); self.add(cubo)
        self.play(tam.animate(rate_func=ease_out_back).set_value(3.5), run_time=0.9)
        cubo.remove_updater(up)
        lomo = vertical("CYCLES", 26, FAINT, mode="spine").move_to(LEFT * 6.75)
        # cabecera: secuencia + contador
        seq = MONO_T("R   U", 34, INK).move_to(RIGHT * 3.2 + UP * 3.05)
        k = ValueTracker(0)
        por = MONO_T("×", 40, MUTED).move_to(RIGHT * 2.35 + UP * 2.05)
        num = counter(k, size=84, color=MINT, anchor=RIGHT * 2.7 + UP * 2.05, edge=LEFT)
        self.play(AddTextLetterByLetter(seq, time_per_char=0.05), drop(lomo, rt=0.5))
        self.play(FadeIn(por, shift=UP * 0.2), FadeIn(num, shift=UP * 0.3, rate_func=ease_out_back_soft), run_time=0.45)

        q = T("How many times?", 58).move_to(RIGHT * 3.2 + DOWN * 0.6)
        stamp(self, q)
        for n in (1, 2):
            cubo.girar(self, "R U", rt=0.3, con=[k.animate.set_value(n)])
        q2 = T("until it comes back", 44, MUTED)
        roll_swap(self, q, q2)
        self.wait(0.3 * WF)

        # tres relojes: el orden de cada ciclo
        relojes = [RelojCiclo(7, "Edges", GOLD, r=0.66), RelojCiclo(15, "Corners", BLUE, r=0.66), RelojCiclo(3, "Twisting one", VIOLET, r=0.66)]
        for r_, x in zip(relojes, (1.3, 3.3, 5.3)):
            r_.move_to(RIGHT * x + DOWN * 0.45); r_.set_paso(2)
        sig = lambda m: [r_.set_paso(k.get_value()) for r_ in relojes]
        self.play(FadeOut(q2, shift=UP * 0.4, rate_func=ease_in_expo), run_time=0.35)
        self.play(LaggedStart(*[FadeIn(r_, shift=UP * 0.4, scale=0.7, rate_func=ease_out_back_soft) for r_ in relojes], lag_ratio=0.15), run_time=0.8)
        ancla = Mobject(); ancla.add_updater(sig); self.add(ancla)

        notas = [("arista7", GOLD, 0, "7 edges go around"), ("esquina5", BLUE, 1, "5 corners × 3 twists = 15"),
                 ("esquina1", VIOLET, 2, "1 corner only twists: 3")]
        prev = None
        for key, col, i, txt in notas:
            cubo.foco(CIC[key]["ids"], col)
            c = chip(txt, col, 24).move_to(RIGHT * 3.25 + DOWN * 2.35)
            if prev is not None: self.play(FadeOut(prev, shift=UP * 0.3), run_time=0.25)
            self.play(Indicate(relojes[i].disco, color=col, scale_factor=1.15), run_time=0.3)
            chip_in(self, c, rt=0.5); prev = c
            self.wait(0.6 * WF)
        cubo.foco(None)
        self.play(FadeOut(prev, shift=UP * 0.3), run_time=0.3)

        # avance rápido: el estado del cubo se actualiza paso a paso (permutación real)
        hechos = [2]
        def ff(m):
            while hechos[0] < int(k.get_value() + 1e-6):
                m.aplicar("R U"); hechos[0] += 1
        cubo.add_updater(ff)
        self.play(k.animate(rate_func=ease_in_out_cubic).set_value(102), run_time=2.8)
        cubo.remove_updater(ff)
        for n in range(103, 106):
            cubo.girar(self, "R U", rt=0.2 + 0.03 * (n - 102), con=[k.animate.set_value(n)])
        assert cubo.resuelto()
        self.wait(0.2)
        eq = EQ(r"\mathrm{lcm}(7,\,15,\,3)", r"=", r"105", size=62, tint={r"105": MINT}).move_to(RIGHT * 3.25 + DOWN * 2.4)
        eq_in(self, eq, rt=0.9)
        underline(self, eq[2], MINT)
        self.wait(0.6 * WF)
        self.remove(ancla)
        exit_all(self)


class E02Grafo(Scene):
    """Por qué siempre vuelve: el grafo de estados de un giro fijo es un ciclo (cada giro tiene reversa)."""
    def construct(self):
        fondo(self)
        v = ValueTracker(0)
        num = counter(v, size=64, color=GOLD, anchor=UP * 0.45)
        lbl = MONO_T("possible cube positions", 24, MUTED).move_to(DOWN * 0.35)
        self.add(num)
        self.play(v.animate(rate_func=ease_out_expo).set_value(43252003274489856000), FadeIn(lbl, shift=UP * 0.2), run_time=1.0)
        nube = nube_estados(170, 12.6, 5.6, centro=DOWN * 0.35, r=0.034)
        num.clear_updaters()
        self.play(num.animate.scale(0.55).move_to(UP * 3.35), lbl.animate.scale(0.85).move_to(UP * 2.85),
                  LaggedStart(*[FadeIn(d, scale=0.3) for d in nube], lag_ratio=0.004), run_time=0.8)

        P = [(-4.6, -2.5), (-3.7, -1.5), (-4.1, 0.0), (-2.7, 1.1), (-0.9, 0.8), (0.6, 1.5), (1.7, 0.3), (1.0, -1.2), (-0.6, -1.15)]
        nodos = VGroup(*[Dot([x, y, 0], radius=0.11 if i == 0 else 0.075, color=MINT if i == 0 else INK) for i, (x, y) in enumerate(P)])
        res = MONO_T("Solved", 22, MINT).next_to(nodos[0], DOWN, buff=0.15)
        g0 = glow(nodos[0], MINT, size=0.9, opacity=0.5); g0.add_updater(lambda m: m.move_to(nodos[0])); self.add(g0)
        self.play(GrowFromCenter(nodos[0], rate_func=ease_out_back), AddTextLetterByLetter(res, time_per_char=0.03), run_time=0.5)
        fl = []
        for i in range(1, len(P)):
            a = flecha_curva(nodos[i - 1], nodos[i], INK, angle=-0.45)
            self.play(Create(a, rate_func=ease_out_expo), GrowFromCenter(nodos[i], rate_func=ease_out_back), run_time=0.15)
            fl.append(a)

        # ¿y si dos flechas entraran al mismo nodo?
        roja = flecha_curva(nodos[-1], nodos[4], RED, angle=0.5)
        preg = MONO_T("Where does it come from?", 24, RED).move_to(nodos[4].get_center() + UP * 0.55 + LEFT * 1.0)
        self.play(Create(roja, rate_func=ease_out_expo), nodos[4].animate.set_color(RED).scale(1.4), run_time=0.5)
        self.play(AddTextLetterByLetter(preg, time_per_char=0.03))
        x_ = icon("cross", RED, 0.45).move_to(roja.point_from_proportion(0.5))
        icon_pop(self, x_, halo=False)
        nota = T("every turn can be undone", 34, INK).move_to(RIGHT * 3.6 + DOWN * 3.05)
        self.play(rise(nota, rt=0.7))
        self.wait(0.4 * WF)
        self.play(FadeOut(VGroup(roja, preg, x_), shift=UP * 0.2), nodos[4].animate.set_color(INK).scale(1 / 1.4), run_time=0.4)

        # entonces la cadena tiene que cerrarse: un ciclo
        col = [INK]
        vivas = [always_redraw(lambda i=i: flecha_curva(nodos[i - 1], nodos[i], col[0], angle=-0.45)) for i in range(1, len(P))]
        self.remove(*fl); self.add(*vivas)
        c0, R = np.array([-0.6, -0.15, 0]), 2.25
        dest = [c0 + R * np.array([np.cos(np.radians(-90 - 40 * i)), np.sin(np.radians(-90 - 40 * i)), 0]) for i in range(len(P))]
        res.add_updater(lambda m: m.next_to(nodos[0], DOWN, buff=0.15))
        self.play(*[n.animate(rate_func=ease_in_out_cubic).move_to(d) for n, d in zip(nodos, dest)],
                  FadeOut(nota, shift=UP * 0.3), run_time=0.9)
        cierre = flecha_curva(nodos[-1], nodos[0], MINT, angle=-0.45)
        col[0] = MINT
        self.play(Create(cierre, rate_func=ease_out_expo), Flash(nodos[0], color=MINT, line_length=0.25), run_time=0.5)
        txt = VGroup(T("it always closes", 40, MINT), T("into a cycle", 40, MINT)).arrange(DOWN, aligned_edge=LEFT, buff=0.2)
        txt.move_to(RIGHT * 2.25 + DOWN * 0.15, aligned_edge=LEFT)
        self.play(rise(txt[0], rt=0.6)); self.play(rise(txt[1], rt=0.5))
        self.wait(0.5 * WF)
        res.clear_updaters()
        self.play(FadeOut(g0), run_time=0.15)
        exit_all(self)


class E03Pendulos(Scene):
    """Banco de péndulos: N_k = 51…65 idas y vueltas por minuto, largo real g/ω², se realinean al minuto."""
    def construct(self):
        fondo(self)
        tt, al, es = ValueTracker(0), ValueTracker(0), ValueTracker(0.45)
        cam = Proyector(-42, 22, 0.45, DOWN * 0.55)
        P = Pendulos(tt, ancho=8.6, alto=3.3, cam=cam, theta0=0.45)
        def vida(m):
            m.alfa = al.get_value(); m.cam.escala = es.get_value(); m._dibujar()
        P.add_updater(vida); self.add(P)
        tit = T("15 pendulums", 52).move_to(LEFT * 3.4 + UP * 3.25)
        sub = MONO_T("51, 52 … 65 swings per minute", 22, MUTED).next_to(tit, DOWN, buff=0.18).align_to(tit, LEFT)
        reloj = always_redraw(lambda: T(f"{int(tt.get_value() // 60)}:{int(tt.get_value() % 60):02d}", 60, INK, font=MONO).move_to(RIGHT * 5.3 + UP * 3.2))
        self.play(al.animate.set_value(1), es.animate(rate_func=ease_out_back).set_value(0.92), rise(tit), run_time=1.1)
        self.play(AddTextLetterByLetter(sub, time_per_char=0.02), FadeIn(reloj, shift=DOWN * 0.2), run_time=0.6)

        eq1 = EQ(r"\theta_k(t)", r"=", r"\theta_0", r"\cos\!\left(2\pi\,\tfrac{N_k\,t}{60\,\mathrm{s}}\right)", size=42).move_to(LEFT * 3.5 + DOWN * 3.3)
        eq2 = EQ(r"L_k", r"=", r"\dfrac{g}{\omega_k^{2}}", size=42).move_to(RIGHT * 3.6 + DOWN * 3.3)
        g1 = [g for p in eq1 for g in p]; g2 = [g for p in eq2 for g in p]
        self.play(tt.animate(rate_func=linear).set_value(1.2),
                  LaggedStart(*[FadeIn(g, shift=UP * 0.25, rate_func=ease_out_back_soft) for g in g1], lag_ratio=0.05), run_time=1.2)
        self.play(tt.animate(rate_func=linear).set_value(2.4),
                  LaggedStart(*[FadeIn(g, shift=UP * 0.25, rate_func=ease_out_back_soft) for g in g2], lag_ratio=0.08), run_time=1.2)
        # salto en el tiempo + la cámara sube para ver la onda
        self.play(tt.animate(rate_func=ease_in_out_cubic).set_value(28.5), al.animate(rate_func=there_and_back).set_value(0.2),
                  UpdateFromAlphaFunc(Mobject(), lambda m, a: (setattr(cam, "pitch", 22 + 30 * ease_in_out_cubic(a)), setattr(cam, "yaw", -42 + 28 * ease_in_out_cubic(a)))),
                  run_time=0.9)
        c1 = chip("half a minute: two rows", GOLD, 24).move_to(RIGHT * 4.6 + UP * 2.2)
        self.play(tt.animate(rate_func=linear).set_value(30), run_time=1.4)
        self.add(c1); chip_in(self, c1, rt=0.5)
        self.play(tt.animate(rate_func=linear).set_value(30.9), run_time=0.6)
        self.play(tt.animate(rate_func=ease_in_out_cubic).set_value(58.0), al.animate(rate_func=there_and_back).set_value(0.2),
                  FadeOut(c1, shift=UP * 0.3), run_time=0.8)
        self.play(tt.animate(rate_func=linear).set_value(60), run_time=2.0)
        c2 = T("1:00 · all together", 40, MINT).move_to(RIGHT * 4.2 + UP * 2.2)
        self.play(tt.animate(rate_func=linear).set_value(60.7), rise(c2, rt=0.7), run_time=0.7)
        self.wait(0.6 * WF)
        exit_all(self)


class E04Aliasing(Scene):
    """Lo mismo visto como muestras: cada péndulo es una muestra de cos(2π τ x). Cerca del minuto aparece el aliasing."""
    def construct(self):
        fondo(self)
        tau = ValueTracker(0.0)
        tit = T("Each pendulum is a sample", 48).move_to(UP * 3.15)
        tracking_in(self, tit)
        cc = LEFT * 4.5 + UP * 0.2
        circ = Circle(radius=1.6, stroke_color=FAINT, stroke_width=2).move_to(cc)
        mins = VGroup(*[Line(cc + 1.6 * np.array([np.sin(a), np.cos(a), 0]) * 0.94, cc + 1.6 * np.array([np.sin(a), np.cos(a), 0]),
                             stroke_color=FAINT, stroke_width=2 if i % 5 else 3.5) for i, a in enumerate(np.linspace(0, TAU, 60, endpoint=False))])
        ax = Axes(x_range=[-0.6, 14.6, 1], y_range=[-1.35, 1.35, 1], x_length=8.0, y_length=3.3,
                  axis_config=dict(color=FAINT, stroke_width=1.5, include_tip=False, include_ticks=False)).move_to(RIGHT * 2.55 + UP * 0.2)
        ax.y_axis.set_opacity(0)
        lomo = vertical("ALIASING", 24, FAINT, mode="spine").move_to(RIGHT * 6.78)
        self.play(Create(circ, rate_func=ease_out_expo), LaggedStart(*[FadeIn(m) for m in mins], lag_ratio=0.01), Create(ax.x_axis), drop(lomo), run_time=0.8)
        fas = always_redraw(lambda: fasores(cc, 1.42, tau.get_value()))
        onda = always_redraw(lambda: onda_muestreada(ax, tau.get_value()))
        self.play(FadeIn(fas), FadeIn(onda), run_time=0.4)
        lab = T("0 s", 38, GOLD).move_to(cc + DOWN * 2.3)
        self.play(rise(lab, rt=0.5))

        def paso(valor, texto, rt, espera):
            nuevo = T(texto, 38, GOLD).move_to(lab)
            self.play(tau.animate(rate_func=ease_in_out_cubic).set_value(valor), run_time=rt)
            roll_swap(self, self._lab, nuevo, rt=0.4); self._lab = nuevo
            if espera > 0: self.wait(espera * WF)
        self._lab = lab
        paso(0.25, "1/4 minute", 1.0, 0.5)
        paso(0.4, "2/5 minute", 0.8, 0.4)
        paso(0.5, "1/2 minute", 0.5, 0.3)
        paso(0.95, "57 s", 1.1, 0.0)
        a1 = T("Aliasing", 56, INK).move_to(RIGHT * 2.55 + DOWN * 2.45)
        wipe_in(self, a1, GOLD)
        a2 = MONO_T("fast looks slow", 24, MUTED).next_to(a1, DOWN, buff=0.18)
        self.play(AddTextLetterByLetter(a2, time_per_char=0.02))
        self.wait(0.6 * WF)
        paso(1.0, "1 minute", 0.8, 0.5)
        exit_all(self)


class E05Cierre(Scene):
    def construct(self):
        fondo(self)
        cubo = Rubik(lado=2.5).move_to(LEFT * 3.9 + UP * 0.6)
        tt = ValueTracker(59.6)
        P = Pendulos(tt, ancho=4.6, alto=2.0, cam=Proyector(-34, 30, 0.85, RIGHT * 3.4 + UP * 0.55))
        tam = ValueTracker(0.05); up = lambda m: m.set_lado(tam.get_value()); cubo.add_updater(up)
        self.add(cubo, P)
        P.alfa = 0; al = ValueTracker(0); P.add_updater(lambda m: (setattr(m, "alfa", al.get_value()), m._dibujar()))
        self.play(tam.animate(rate_func=ease_out_back).set_value(2.5), al.animate.set_value(1), tt.animate(rate_func=linear).set_value(60.4), run_time=0.8)
        cubo.remove_updater(up)
        l1 = T("Everything that repeats", 54).move_to(DOWN * 2.15)
        self.play(rise(l1), tt.animate(rate_func=linear).set_value(61.2), run_time=0.8)
        l2 = DISPLAY("returns.", 92, MINT).move_to(DOWN * 3.2)
        stamp(self, l2)
        self.play(tt.animate(rate_func=linear).set_value(62.8), run_time=1.6)
        exit_all(self)
