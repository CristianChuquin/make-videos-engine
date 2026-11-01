#!/usr/bin/env python3
"""prep.py — trae un SVG del banco (Bioicons/Servier) al lenguaje Harper's Bazaar.

  harper(path, prefijo, ancho_px, grupos=None) -> str  (SVG listo para incrustar)

· Quita <text>, <title> y metadatos (las etiquetas son nuestras, en inglés).
· Prefija los id para que dos SVG convivan en la misma slide.
· Cada relleno pasa por su luminancia: oscuro → negro · medio → halftone denso ·
  claro → halftone ralo · muy claro → blanco. Los trazos oscuros quedan negros.
· Añade contorno negro a cada pieza rellena (salvo los brillos blancos): ese contorno
  es el que se TRAZA en la animación antes de que la pieza se rellene.
· Las tramas se definen dentro del propio SVG, escaladas a su viewBox, para que el
  punto de halftone mida lo mismo en pantalla sea cual sea el tamaño del dibujo.
· grupos = {"clase": función(hex_original) -> bool}: etiqueta piezas por su color
  original (p. ej. actina vs miosina) para moverlas por separado.
"""
import re
import xml.etree.ElementTree as ET

SVG = "http://www.w3.org/2000/svg"
ET.register_namespace("", SVG)
ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
SHAPES = {"path", "circle", "ellipse", "rect", "polygon", "polyline", "line"}
CREDIT = "Servier Medical Art (CC BY 3.0), via Bioicons"


def _hex(c):
    if not c:
        return None
    c = c.strip().lower()
    named = {"black": "#000000", "white": "#ffffff", "red": "#ff0000", "none": None}
    if c in named:
        return named[c]
    if re.fullmatch(r"#[0-9a-f]{3}", c):
        c = "#" + "".join(ch * 2 for ch in c[1:])
    return c if re.fullmatch(r"#[0-9a-f]{6}", c) else None


def lum(h):
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def _get(el, k):
    v = el.get(k)
    m = re.search(rf"(?:^|;)\s*{k}\s*:\s*([^;]+)", el.get("style", ""))
    return (m.group(1).strip() if m else v)


def _set(el, k, v):
    st = re.sub(rf"(?:^|;)\s*{k}\s*:[^;]*", "", el.get("style", "")).strip(";")
    if st:
        el.set("style", st)
    elif "style" in el.attrib:
        del el.attrib["style"]
    el.set(k, v)


def harper(path, pre, width_px, grupos=None, outline=1.15):
    raw = open(path, encoding="utf8", errors="ignore").read()
    raw = re.sub(r"<\?xml[^>]*\?>", "", raw)
    raw = re.sub(r"<(/?)ns\d+:", r"<\1", raw)
    root = ET.fromstring(raw)
    vb = [float(x) for x in re.split(r"[ ,]+", root.get("viewBox").strip())]
    k = vb[2] / width_px                            # unidades del SVG por px de pantalla
    for el in list(root.iter()):                    # fuera textos y metadatos
        for ch in list(el):
            if ch.tag.split("}")[-1] in ("text", "title", "metadata", "desc"):
                el.remove(ch)
    for el in root.iter():                          # prefijo de ids
        if el.get("id"):
            el.set("id", f"{pre}-{el.get('id')}")
        for a in list(el.attrib):
            v = el.attrib[a]
            if "url(#" in v:
                el.attrib[a] = re.sub(r"url\(#([^)]+)\)", rf"url(#{pre}-\1)", v)
            if a.endswith("href") and v.startswith("#"):
                el.attrib[a] = f"#{pre}-{v[1:]}"
    defs = root.find(f"{{{SVG}}}defs")
    if defs is None:
        defs = ET.SubElement(root, f"{{{SVG}}}defs")
        root.remove(defs); root.insert(0, defs)
    for pid, sp, r in ((f"{pre}-hd", 4.6, 1.6), (f"{pre}-hl", 5.6, 1.05)):
        p = ET.SubElement(defs, f"{{{SVG}}}pattern", id=pid, width=f"{sp * k:.3f}", height=f"{sp * k:.3f}",
                          patternUnits="userSpaceOnUse", patternTransform="rotate(30)")
        ET.SubElement(p, f"{{{SVG}}}circle", cx=f"{sp * k / 2:.3f}", cy=f"{sp * k / 2:.3f}", r=f"{r * k:.3f}", fill="#000")
    inside_defs = {id(e) for d in root.iter() if d.tag.split("}")[-1] in ("defs", "clipPath", "mask", "pattern") for e in d.iter()}
    n = 0
    for el in root.iter():
        if el.tag.split("}")[-1] not in SHAPES or id(el) in inside_defs:
            continue
        f, s = _hex(_get(el, "fill")), _hex(_get(el, "stroke"))
        fill_raw = (_get(el, "fill") or "").strip().lower()
        if fill_raw == "" and el.tag.split("}")[-1] not in ("line", "polyline"):
            f = "#000000"                            # relleno por defecto de SVG
        cls = []
        if f:
            L = lum(f)
            nf = "#000" if L < 0.40 else (f"url(#{pre}-hd)" if L < 0.62 else (f"url(#{pre}-hl)" if L < 0.84 else "#fff"))
            _set(el, "fill", nf)
            _set(el, "fill-opacity", "1")
            if nf != "#fff" and not s:
                _set(el, "stroke", "#000")
                _set(el, "stroke-width", f"{outline * k:.3f}")
                _set(el, "stroke-linejoin", "round")
            cls.append("pf")
            if grupos:
                for g, test in grupos.items():
                    if test(f):
                        cls.append(g)
        if s:
            _set(el, "stroke", "#000" if lum(s) < 0.75 else "#fff")
            cls.append("ps")
            if grupos and not f:
                for g, test in grupos.items():
                    if test(s):
                        cls.append(g)
        if (_get(el, "stroke") or "none") != "none":
            cls.append("pt")                           # tiene trazo: se dibuja
        if cls:
            el.set("class", " ".join(dict.fromkeys(cls)))
            n += 1
    root.set("data-pieces", str(n))
    for a in ("width", "height"):
        root.attrib.pop(a, None)
    return ET.tostring(root, encoding="unicode")


if __name__ == "__main__":
    import sys
    s = harper(sys.argv[1], "x", float(sys.argv[2]))
    print(len(s), s[:300])
