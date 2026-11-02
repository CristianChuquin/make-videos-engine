"""SVG de banco público → monolínea del estilo (sin relleno, trazo uniforme, sin texto ni logos).
Devuelve un <svg> anidado listo para incrustar dentro del <svg> de la slide."""
import re
from lxml import etree

ROOT = "/home/claude/bancos/bioicons/static/icons/"
DROP_TAGS = {"text", "tspan", "style", "title", "desc", "metadata", "clipPath", "mask", "image", "use",
             "linearGradient", "radialGradient", "defs", "pattern", "filter", "symbol", "switch", "foreignObject"}
SHAPES = {"path", "rect", "circle", "ellipse", "line", "polyline", "polygon"}
KEEP = {"d", "x", "y", "width", "height", "cx", "cy", "r", "rx", "ry", "x1", "y1", "x2", "y2", "points", "transform"}

def local(tag):
    return tag.split("}")[-1] if isinstance(tag, str) else ""

def bank(rel, pid, x, y, w, h, color="#fff", sw=1.5, drop=r"logo|copyright|sib_", drop_clipped=False):
    tree = etree.parse(ROOT + rel, etree.XMLParser(huge_tree=True, remove_comments=True))
    root = tree.getroot()
    vb = root.get("viewBox")
    if not vb:
        vb = f"0 0 {float(re.sub('[a-z]', '', root.get('width')))} {float(re.sub('[a-z]', '', root.get('height')))}"
    vx, vy, vw, vh = map(float, vb.replace(",", " ").split())
    scale = min(w / vw, h / vh)
    usw = sw / scale                      # grosor en unidades del viewBox → trazo uniforme en pantalla
    for el in list(root.iter()):
        if el is root or el.getparent() is None:
            continue
        t = local(el.tag)
        clipped = drop_clipped and el.get("clip-path")          # degradados simulados por recortes
        if t in DROP_TAGS or not t or clipped or (el.get("id") and re.search(drop, el.get("id"), re.I)):
            el.getparent().remove(el)
    n = 0
    for el in root.iter():
        t = local(el.tag)
        for a in list(el.attrib):
            if local(a) not in KEEP:
                del el.attrib[a]
        if t in SHAPES:
            el.set("fill", "none"); el.set("stroke", color); el.set("stroke-width", f"{usw:.3f}")
            el.set("stroke-linecap", "round"); el.set("stroke-linejoin", "round")
            el.set("class", f"bk {pid}-p"); n += 1
    inner = "".join(etree.tostring(c, encoding="unicode") for c in root)
    inner = re.sub(r'\sxmlns(:\w+)?="[^"]*"', "", inner)
    inner = re.sub(r"<(/?)\w+:", r"<\1", inner)
    return (f'<svg id="{pid}" x="{x}" y="{y}" width="{w}" height="{h}" viewBox="{vb}" '
            f'preserveAspectRatio="xMidYMid meet" overflow="visible">{inner}</svg>'), n
