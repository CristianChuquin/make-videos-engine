#!/usr/bin/env python3
"""PDF de la presentación: una página por slide = su frame final, en 16:9 (13,333 × 7,5 in,
igual que el PPTX), SIEMPRE < 4 MB. Ajusta calidad JPEG y, si hace falta, resolución.
uso: python3 make_pdf.py <carpeta clips> <salida.pdf> [--max-mb 3.9]"""
import glob, io, os, sys
import img2pdf
from PIL import Image

clips, out = sys.argv[1], sys.argv[2]
max_mb = float(sys.argv[sys.argv.index("--max-mb") + 1]) if "--max-mb" in sys.argv else 3.9
frames = sorted(glob.glob(os.path.join(clips, "[0-9][0-9]_last.jpg")))
assert len(frames) >= 1, "no hay NN_last.jpg"
src = [Image.open(f).convert("RGB") for f in frames]
layout = img2pdf.get_layout_fun((img2pdf.in_to_pt(13.333), img2pdf.in_to_pt(7.5)))

for width in (2560, 1920, 1600, 1280):
    for q in (90, 85, 80, 75, 70, 65, 60):
        jpgs = []
        for im in src:
            if im.width != width:
                im = im.resize((width, round(width * im.height / im.width)), Image.LANCZOS)
            b = io.BytesIO(); im.save(b, "JPEG", quality=q, optimize=True, progressive=True, subsampling=0 if q >= 80 else 2)
            jpgs.append(b.getvalue())
        pdf = img2pdf.convert(jpgs, layout_fun=layout)
        mb = len(pdf) / 1e6
        if mb < max_mb:
            open(out, "wb").write(pdf)
            print(f"PDF {out}: {len(frames)} páginas, {width}px, q{q}, {mb:.2f} MB")
            sys.exit(0)
sys.exit("no se pudo bajar de %.1f MB" % max_mb)
