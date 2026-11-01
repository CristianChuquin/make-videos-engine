#!/usr/bin/env python3
"""
textures.py — fondos texturizados POR CÓDIGO (0 créditos, deterministas por semilla).
Son el «Frame A» de cada slide: van como fondo y JAMÁS se animan.

  python3 textures.py harper  --variant yellow|white|split-h|split-v|quad --seed 3 -o bg.png
  python3 textures.py davinci --seed 7 [--folds 2] [--splatters 7] -o bg.png

minimalista_linea no usa textura: su fondo es un relleno plano en el pptx.
Salida: 2667×1500 px (13.333" × 7.5" a 200 dpi).
"""
import argparse

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

W, H = 2667, 1500


def hex2rgb(h):
    h = h.lstrip("#")
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)], dtype=np.float32)


def grain(rng, amp):
    g = rng.normal(0, amp, (H, W)).astype(np.float32)
    # suavizado 2×2 en numpy (PIL no difumina imágenes float): grano fino, no ruido digital
    g = (g + np.roll(g, 1, 0) + np.roll(g, 1, 1) + np.roll(g, 1, (0, 1))) / 2.0
    return g[..., None]


def harper(variant, seed):
    rng = np.random.default_rng(seed)
    Y, Wt = hex2rgb("CCCC00"), hex2rgb("FFFFFF")
    img = np.zeros((H, W, 3), np.float32)
    if variant == "yellow":
        img[:] = Y
    elif variant == "white":
        img[:] = Wt
    elif variant == "split-h":
        img[: H // 2], img[H // 2:] = Y, Wt
    elif variant == "split-v":
        img[:, : W // 2], img[:, W // 2:] = Y, Wt
    elif variant == "quad":
        img[:] = Wt
        img[: H // 2, : W // 2] = Y
        img[H // 2:, W // 2:] = Y
    else:
        raise SystemExit(f"variante desconocida: {variant}")
    # Moiré / pulso sutil solo sobre campos blancos
    white = (img.sum(axis=2) > 700)[..., None]
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    cx, cy = W * rng.uniform(0.55, 0.8), H * rng.uniform(0.3, 0.7)
    r = np.sqrt((xx - cx) ** 2 + (yy - cy) ** 2)
    moire = (np.sin(r / 9.0) * np.sin(r / 9.6)) * 5.0
    img = np.where(white, img - np.abs(moire)[..., None], img)
    img += grain(rng, 7.0)  # grano de película
    return Image.fromarray(np.clip(img, 0, 255).astype(np.uint8))


def davinci(seed, folds, splatters):
    rng = np.random.default_rng(seed)
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    # pergamino: claro al centro, amarillento hacia los bordes
    d = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H / 2) / (H / 2)) ** 2) / 1.41
    c0, c1 = hex2rgb("E8D9B5"), hex2rgb("CDB88E")
    img = c0 + (c1 - c0) * (d[..., None] ** 1.8)
    # manchas grandes de envejecimiento
    blot = rng.normal(0, 1, (H // 160 + 2, W // 160 + 2)).astype(np.float32)
    blot = np.array(Image.fromarray(blot).resize((W, H), Image.BICUBIC), dtype=np.float32)
    img -= (blot * 3.0)[..., None]
    img += grain(rng, 5.0)
    pil = Image.fromarray(np.clip(img, 0, 255).astype(np.uint8)).convert("RGBA")

    over = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    dr = ImageDraw.Draw(over)
    # pliegues: línea de sombra + línea de luz, fuera de centro
    for i in range(folds):
        if i % 2 == 0:
            x = int(W * rng.uniform(0.28, 0.72))
            dr.line([(x, 0), (x + int(rng.uniform(-25, 25)), H)], fill=(90, 70, 40, 46), width=5)
            dr.line([(x + 6, 0), (x + 6 + int(rng.uniform(-25, 25)), H)], fill=(255, 250, 235, 60), width=3)
        else:
            y = int(H * rng.uniform(0.3, 0.7))
            dr.line([(0, y), (W, y + int(rng.uniform(-20, 20)))], fill=(90, 70, 40, 40), width=5)
            dr.line([(0, y + 6), (W, y + 6 + int(rng.uniform(-20, 20)))], fill=(255, 250, 235, 55), width=3)
    # salpicaduras de tinta, en bordes y esquinas
    inks = [(28, 61, 122), (92, 58, 30)]
    for _ in range(splatters):
        edge = rng.integers(4)
        cx = rng.uniform(0.02, 0.18) * W if edge == 0 else (rng.uniform(0.82, 0.98) * W if edge == 1 else rng.uniform(0.05, 0.95) * W)
        cy = rng.uniform(0.04, 0.2) * H if edge == 2 else (rng.uniform(0.8, 0.96) * H if edge == 3 else rng.uniform(0.05, 0.95) * H)
        col = inks[rng.integers(2)]
        r0 = rng.uniform(5, 16)
        dr.ellipse([cx - r0, cy - r0, cx + r0, cy + r0], fill=col + (int(rng.uniform(120, 190)),))
        for _ in range(int(rng.integers(8, 22))):
            ang, dist = rng.uniform(0, 2 * np.pi), rng.uniform(r0, r0 * 6)
            rr = rng.uniform(1.2, 4.5)
            px, py = cx + np.cos(ang) * dist, cy + np.sin(ang) * dist
            dr.ellipse([px - rr, py - rr, px + rr, py + rr], fill=col + (int(rng.uniform(90, 170)),))
    # una huella dactilar tenue: anillos concéntricos semitransparentes
    fx, fy = W * rng.uniform(0.75, 0.93), H * rng.uniform(0.62, 0.88)
    for k in range(14):
        a, b = 34 + k * 5.2, 46 + k * 6.4
        dr.ellipse([fx - a, fy - b, fx + a, fy + b], outline=(110, 95, 80, 22), width=2)
    over = over.filter(ImageFilter.GaussianBlur(0.8))
    return Image.alpha_composite(pil, over).convert("RGB")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("style", choices=["harper", "davinci"])
    ap.add_argument("--variant", default="yellow")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--folds", type=int, default=2)
    ap.add_argument("--splatters", type=int, default=7)
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    img = harper(a.variant, a.seed) if a.style == "harper" else davinci(a.seed, a.folds, a.splatters)
    img.save(a.out, quality=95) if a.out.lower().endswith(".jpg") else img.save(a.out)
    print(f"OK → {a.out}")


if __name__ == "__main__":
    main()
