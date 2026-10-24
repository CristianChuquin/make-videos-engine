# svgbank.py — (v1.7) bancos de ilustraciones EN CÓDIGO para las tres skills Cosmos, cada una con SUS bancos.
# Lo principal es la simulación: se necesita el CÓDIGO de la imagen (SVG o TikZ) para editarla y animarla por piezas;
# un PNG/JPG no sirve para simular. Orden de recursos de Cris (23-oct-2026), siempre en este orden y PLANEADO antes:
#   1) banco SVG especializado del estilo  (buscar_svg(q, estilo))            → gratis, vector animable por piezas
#   2) banco libre de código general        (openverse_svg: Wikimedia; tikz)  → gratis, vector
#   3) gráfico diseñado por Claude con código (Manim, o propio() con <g id>)   → gratis
#   4) imagen generada con el MCP de Higgsfield                                → ÚLTIMA opción: gasta créditos
# Perfiles (BANCOS): "bio" = Bioicons (Servier, DBCLS), Reactome, NIH · "matematicas" = tikz.net + Iconify de línea
# (tabler, lucide, ph, carbon) · "general" = Iconify temático (healthicons, game-icons, tabler, fluent-emoji-flat, ph) + tikz.net.
# foto() (raster) queda solo para una foto real de contexto que la voz nombra, nunca para una simulación.
# Bancos: Bioicons (incluye ~1.375 SVG de Servier Medical Art y ~630 de DBCLS/TogoTV), Reactome Icon Library y
# NIH BioArt Source (por id). Nunca licencias NC (no comerciales): los videos pueden monetizarse.
# El SVG se usa como VECTOR: cada pieza (path o <g id>) es un objeto de Manim que se anima por separado.
from manim import *
import os, re, json, glob, subprocess, urllib.request, urllib.parse, urllib.error, time, xml.etree.ElementTree as ET
import numpy as np
from estilo import *

BANCO = os.path.expanduser("~/.mv_cache/bancos"); os.makedirs(BANCO, exist_ok=True)
BIOICONS = os.path.join(BANCO, "bioicons")
PROPIOS = os.path.join(BANCO, "propios"); os.makedirs(PROPIOS, exist_ok=True)
LIC_OK = {"cc-0", "cc0", "mit", "bsd", "cc-by-3.0", "cc-by-4.0", "cc-by-sa-3.0", "cc-by-sa-4.0", "public domain", "propio"}
LIC_OK |= {"cc-by-2.0", "cc-by-2.5", "cc-by-sa-2.0", "cc-by-sa-2.5", "cc0-1.0", "pdm", "apache-2.0", "isc", "ofl-1.1", "cc-by-4.0", "unlicense"}
LIC_TXT = {"cc-0": "CC0", "cc0-1.0": "CC0", "pdm": "Public Domain", "apache-2.0": "Apache 2.0", "isc": "ISC", "ofl-1.1": "OFL 1.1",
           "cc-by-2.0": "CC BY 2.0", "cc-by-2.5": "CC BY 2.5", "cc-by-sa-2.0": "CC BY-SA 2.0", "cc-by-sa-2.5": "CC BY-SA 2.5", "unlicense": "Unlicense",
           "mit": "MIT", "bsd": "BSD", "cc-by-3.0": "CC BY 3.0", "cc-by-4.0": "CC BY 4.0",
           "cc-by-sa-3.0": "CC BY-SA 3.0", "cc-by-sa-4.0": "CC BY-SA 4.0", "public domain": "Public Domain"}
CREDITOS = {}          # path -> (autor, fuente, licencia); se llena al usar cada SVG

# ---------------- 1. Bancos e índice ----------------
def preparar_bancos():
    """Clona Bioicons (solo static/icons, ~440 MB, una vez por sesión) y arma el índice."""
    if not os.path.isdir(os.path.join(BIOICONS, "static", "icons")):
        subprocess.run(f"git clone -q --depth 1 --filter=blob:none --sparse https://github.com/duerrsimon/bioicons.git {BIOICONS} "
                       f"&& cd {BIOICONS} && git sparse-checkout set static/icons", shell=True, check=True)
    return indice()


_IDX = None
def indice():
    global _IDX
    if _IDX is None:
        _IDX = []
        for p in glob.glob(os.path.join(BIOICONS, "static/icons/*/*/*/*.svg")):
            lic, cat, autor = p.split(os.sep)[-4:-1]
            _IDX.append(dict(path=p, name=os.path.basename(p)[:-4], cat=cat, autor=autor, lic=lic, fuente="Bioicons"))
        for p in glob.glob(os.path.join(PROPIOS, "*.svg")):
            _IDX.append(dict(path=p, name=os.path.basename(p)[:-4], cat="propio", autor="propio", lic="propio", fuente="propio"))
    return _IDX


ES_EN = {"mitocondria": "mitochondri", "nucleo": "nucleus", "núcleo": "nucleus", "celula": "cell", "célula": "cell",
         "membrana": "membrane", "ribosoma": "ribosom", "reticulo": "reticulum", "retículo": "reticulum", "golgi": "golgi",
         "virus": "virus", "bacteria": "bacteri", "anticuerpo": "antibod", "neurona": "neuron", "linfocito": "lymphocyte",
         "sangre": "blood", "eritrocito": "erythro", "globulo": "blood cell", "plaqueta": "platelet", "piel": "skin",
         "musculo": "muscle", "músculo": "muscle", "hueso": "bone", "corazon": "heart", "corazón": "heart", "higado": "liver",
         "riñon": "kidney", "riñón": "kidney", "pulmon": "lung", "pulmón": "lung", "cerebro": "brain", "ojo": "eye",
         "adn": "dna", "arn": "rna", "proteina": "protein", "proteína": "protein", "enzima": "enzyme", "receptor": "receptor",
         "canal": "channel", "vesicula": "vesicle", "vesícula": "vesicle", "lisosoma": "lysosom", "microtubulo": "microtubul",
         "microtúbulo": "microtubul", "actina": "actin", "miosina": "myosin", "filamento": "filament", "cromosoma": "chromosom",
         "raton": "mouse", "ratón": "mouse", "planta": "plant", "hoja": "leaf", "cloroplasto": "chloroplast", "tejido": "tissue",
         "epitelio": "epitheli", "macrofago": "macrophage", "macrófago": "macrophage", "tumor": "tumor", "cancer": "cancer"}

def buscar(q, n=12, lic=LIC_OK, fuentes=("Bioicons", "propio")):
    """Busca en el índice local (nombre, categoría, autor). Acepta términos en español o inglés."""
    toks = [ES_EN.get(t, t) for t in re.findall(r"[\wáéíóúñ]+", q.lower())]
    res = []
    for e in indice():
        if e["lic"] not in lic or e["fuente"] not in fuentes: continue
        txt = (e["name"] + " " + e["cat"]).lower().replace("_", " ").replace("-", " ")
        s = sum(2 if re.search(r"\b" + re.escape(t), txt) else (1 if t in txt else 0) for t in toks)
        if s: res.append((s + (0.5 if e["autor"] == "Servier" else 0), e))
    res.sort(key=lambda x: -x[0])
    return [e for _, e in res[:n]]


def _get(url, timeout=30):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 (mv-cosmos-bio)"}), timeout=timeout).read()

def _wm_thumb(url, w=1280):
    """Miniatura de Wikimedia (sí responde desde la nube; los originales dan 429). Un SVG sale como PNG de w px."""
    m = re.match(r"https://upload\.wikimedia\.org/wikipedia/commons/(\w/\w\w)/([^/]+)$", url)
    if not m: return None
    f = m.group(2); return f"https://upload.wikimedia.org/wikipedia/commons/thumb/{m.group(1)}/{f}/{w}px-{f}" + (".png" if f.lower().endswith(".svg") else "")

def _bajar(url, p):
    try:
        open(p, "wb").write(_get(url, 60)); return p
    except urllib.error.HTTPError as ex:
        if ex.code == 429:   # Wikimedia y Flickr limitan la IP de la nube: bajar el original por el PC de Cris (PowerShell) y stagearlo
            raise RuntimeError(f"429 desde la nube: bajar {url} por el PC (Invoke-WebRequest) a claude-cache\\bancos\\ y stagear") from ex
        raise

def reactome(q, n=6):
    """Reactome Icon Library (CC BY 4.0): proteínas, receptores, compuestos, tipos celulares. Descarga los SVG."""
    url = "https://reactome.org/ContentService/search/query?" + urllib.parse.urlencode(dict(query=q, types="Icon", cluster="true"))
    try: d = json.loads(_get(url))
    except Exception as ex: print("reactome:", ex); return []
    out = []
    for grp in d.get("results", []):
        for e in grp.get("entries", [])[:n]:
            p = os.path.join(BANCO, "reactome", e["stId"] + ".svg"); os.makedirs(os.path.dirname(p), exist_ok=True)
            if not os.path.exists(p): _bajar(f"https://reactome.org/icon/{e['stId']}.svg", p)
            out.append(dict(path=p, name=re.sub("<[^>]+>", "", e["name"]), cat=",".join(e.get("iconCategories", [])),
                            autor="Reactome / " + e.get("iconDesignerName", ""), lic="cc-by-4.0", fuente="Reactome"))
    return out


def nih(bioart_id):
    """NIH BioArt Source por id (búscalo con WebSearch «site:bioart.niaid.nih.gov <tema>»). Rechaza licencias NC."""
    html = _get(f"https://bioart.niaid.nih.gov/bioart/{bioart_id}").decode("utf8", "ignore")
    m = re.search(r'\\"SVG\\":(\d+)', html)
    if not m: raise ValueError("Esta entrada no tiene SVG")
    p = os.path.join(BANCO, "nih", f"{bioart_id}.svg"); os.makedirs(os.path.dirname(p), exist_ok=True)
    _bajar(f"https://bioart.niaid.nih.gov/api/bioarts/{bioart_id}/files/{m.group(1)}", p)
    txt = open(p, encoding="utf8", errors="ignore").read(3000).lower()
    lic = "public domain" if "public domain" in txt else ("cc-by-4.0" if "cc-by" in txt or "cc by" in txt else "?")
    if "nc" in re.findall(r"cc[- ]by[- ]?(nc)?", txt) or lic == "?":
        raise ValueError(f"Licencia no apta o desconocida en NIH {bioart_id}: revisar a mano")
    t = re.search(r"<title>([^<]+)", txt)
    return dict(path=p, name=t.group(1) if t else str(bioart_id), cat="nih", autor="NIAID Visual & Medical Arts", lic=lic, fuente="NIH BioArt")


# ---------------- 1b. (v1.7) Bancos SVG generales: también para matemática, física, biomecánica y deporte ----------------
LIC_ICONIFY = {"mit", "apache-2.0", "isc", "cc0-1.0", "cc-by-3.0", "cc-by-4.0", "cc-by-sa-4.0", "ofl-1.1", "unlicense"}
_ICOL = None
def _iconify_cols():
    global _ICOL
    if _ICOL is None: _ICOL = json.loads(_get("https://api.iconify.design/collections"))
    return _ICOL

def iconify(q, n=12, prefijos=()):
    """Iconify (~415.000 íconos de ~240 colecciones abiertas: Tabler, Material, Phosphor, OpenMoji, Fluent Emoji…).
    Bueno para objetos, gestos, deporte, instrumentos y símbolos. Solo colecciones con licencia abierta (nada GPL ni NC)."""
    par = dict(query=q, limit=max(n * 3, 32))
    if prefijos: par["prefixes"] = ",".join(prefijos)
    d = json.loads(_get("https://api.iconify.design/search?" + urllib.parse.urlencode(par)))
    cols = _iconify_cols(); out = []
    for ic in d.get("icons", []):
        pre, name = ic.split(":", 1); c = cols.get(pre, {}); lic = c.get("license", {}).get("spdx", "").lower()
        if lic not in LIC_ICONIFY: continue
        p = os.path.join(BANCO, "iconify", pre, name + ".svg"); os.makedirs(os.path.dirname(p), exist_ok=True)
        if not os.path.exists(p):
            svg = _get(f"https://api.iconify.design/{pre}/{name}.svg?height=512").decode()
            open(p, "w").write(svg.replace("currentColor", "#EEF1F6"))      # trazo claro: se ve sobre el fondo oscuro
        out.append(dict(path=p, name=ic, cat=c.get("name", pre), autor=c.get("author", {}).get("name", pre), lic=lic, fuente="Iconify"))
        if len(out) >= n: break
    return out

def _openverse(q, n, **extra):
    par = dict(q=q, page_size=min(20, max(n, 4)), license_type="commercial,modification", **extra)
    for k in range(3):                                   # el anónimo tiene límite por minuto y a veces tarda: 3 intentos con espera
        try: return json.loads(_get("https://api.openverse.org/v1/images/?" + urllib.parse.urlencode(par), 90)).get("results", [])
        except (urllib.error.HTTPError, TimeoutError, urllib.error.URLError) as ex:
            if k == 2 or (isinstance(ex, urllib.error.HTTPError) and ex.code != 429): raise
            time.sleep(20)

def _lic_ov(r):
    l = r.get("license", ""); v = r.get("license_version", "")
    return {"cc0": "cc0-1.0", "pdm": "pdm"}.get(l, f"cc-{l}-{v}" if v else f"cc-{l}")

def openverse_svg(q, n=8):
    """Openverse (CC Search) filtrado a SVG con licencia que permite uso comercial y modificación (excluye NC y ND).
    Casi todo viene de Wikimedia Commons: diagramas de física, geometría, anatomía, mapas, canchas, máquinas."""
    out = []
    for r in _openverse(q, n, extension="svg"):
        p = os.path.join(BANCO, "openverse", r["id"] + ".svg"); os.makedirs(os.path.dirname(p), exist_ok=True)
        try:
            if not os.path.exists(p): _bajar(r["url"], p)
        except RuntimeError as ex:
            time.sleep(3)
            try: _bajar(r["url"], p)
            except Exception: print(ex, "· (o usar su miniatura PNG con foto())"); continue
        out.append(dict(path=p, name=r.get("title") or r["id"], cat=r.get("source", ""), autor=r.get("creator") or r.get("source", ""),
                        lic=_lic_ov(r), fuente="Openverse · " + r.get("source", ""), url=r.get("foreign_landing_url")))
    return out[:n]

def buscar_svg(q, estilo, n=12, paso2=True):
    """Pasos 1 y 2 del orden con los bancos DE ESE ESTILO ("bio", "matematicas" o "general"; nunca los de otro estilo):
    1) banco especializado (Bioicons/Reactome en bio; tikz.net + Iconify de línea en matemáticas; Iconify temático +
    tikz.net en general) y 2) Openverse SVG (Wikimedia). Las figuras de tikz.net vuelven como {name, url}: su código se
    trae con tikz_codigo() y se compila con tikz()."""
    P = BANCOS[estilo]; res = []
    if P["bioicons"]:
        if os.path.isdir(os.path.join(BIOICONS, "static", "icons")): res += buscar(q, n)
        try: res += reactome(q, 4)
        except Exception as ex: print("reactome:", ex)
    if P["iconify"]:
        try: res += iconify(q, n, P["iconify"])
        except Exception as ex: print("iconify:", ex)
    if P["tikz"]:
        try: res += [dict(e, fuente="tikz.net", lic="cc-by-sa-4.0", autor="tikz.net", path=None) for e in tikz_buscar(q, 6)]
        except Exception as ex: print("tikz.net:", ex)
    if paso2:
        try: res += openverse_svg(q, 6)
        except Exception as ex: print("openverse:", ex)
    return res


# ---------------- 1c. (v1.7) Banco de CÓDIGO TikZ (matemática y física) y perfiles por estilo ----------------
def tikz_buscar(q, n=8):
    """tikz.net (CC BY-SA 4.0): cientos de figuras de física y matemática con su código TikZ (péndulos, torque, momento
    de inercia, ondas, circuitos, óptica, cinemática). Devuelve [{name, url}] para elegir."""
    html = _get("https://tikz.net/?" + urllib.parse.urlencode(dict(s=q))).decode("utf8", "ignore")
    urls = []
    for u in re.findall(r'https://tikz\.net/([a-z0-9_-]+)/', html):
        if u in ("about", "authors", "category", "comments", "data", "tag", "feed", "search", "science", "topics", "files", "page", "author", "contact", "license") or u.startswith("wp-") or u in urls: continue
        urls.append(u)
    return [dict(name=u, url=f"https://tikz.net/{u}/") for u in urls[:n]]

def tikz_codigo(url_o_nombre):
    """El código LaTeX/TikZ de una figura de tikz.net (el primer bloque <pre>), listo para editar y compilar con tikz()."""
    import html as H
    u = url_o_nombre if url_o_nombre.startswith("http") else f"https://tikz.net/{url_o_nombre}/"
    page = _get(u).decode("utf8", "ignore")
    b = re.findall(r"<pre[^>]*>(.*?)</pre>", page, re.S)
    if not b: raise ValueError("sin bloque de código")
    return H.unescape(re.sub("<[^>]+>", "", b[0])).strip()

def tikz(codigo, nombre, autor="tikz.net", lic="cc-by-sa-4.0", fuente="tikz.net"):
    """Compila código TikZ (documento standalone completo, o solo el cuerpo de un tikzpicture) a SVG con latex + dvisvgm
    y devuelve una entrada por página (una por tikzpicture) para SVGBio; se eligen con hoja_candidatos. Cada \\draw/\\fill queda como pieza animable. Claude puede escribir el TikZ él mismo
    (paso 3) con autor="propio"."""
    d = os.path.join(BANCO, "tikz", re.sub(r"[^\w-]+", "-", nombre)); os.makedirs(d, exist_ok=True)
    if "\\documentclass" not in codigo:
        codigo = "\\documentclass[border=3pt,tikz]{standalone}\n\\usepackage{amsmath}\n\\usetikzlibrary{arrows.meta,calc,decorations.pathmorphing,patterns,angles,quotes}\n\\begin{document}\n" + \
                 ("" if "\\begin{tikzpicture}" in codigo else "\\begin{tikzpicture}\n") + codigo + \
                 ("" if "\\begin{tikzpicture}" in codigo else "\n\\end{tikzpicture}") + "\n\\end{document}\n"
    open(os.path.join(d, "f.tex"), "w").write(codigo)
    for f in glob.glob(os.path.join(d, "f*.svg")): os.remove(f)
    # sin halt-on-error: una figura de tikz.net trae varias tikzpicture (una por página); las que compilan sirven
    subprocess.run("latex -interaction=nonstopmode f.tex >/dev/null 2>&1; dvisvgm --no-fonts --exact-bbox --page=1- -o 'f-%p.svg' f.dvi >/dev/null 2>&1",
                   shell=True, cwd=d)
    pags = sorted(glob.glob(os.path.join(d, "f-*.svg")), key=lambda p: int(re.findall(r"(\d+)\.svg$", p)[0]))
    if not pags: raise RuntimeError(f"TikZ no compiló: ver {d}/f.log (paquetes o archivos de datos que falten)")
    return [dict(path=p, name=f"{nombre} p{i + 1}", cat="tikz", autor=autor, lic=lic, fuente=fuente) for i, p in enumerate(pags)]

BANCOS = {   # bancos SVG especializados de cada estilo (paso 1); los tres comparten openverse_svg como paso 2
    "bio":         dict(iconify=(), tikz=False, bioicons=True),
    "matematicas": dict(iconify=("tabler", "lucide", "ph", "carbon", "mdi"), tikz=True, bioicons=False),
    "general":     dict(iconify=("healthicons", "game-icons", "tabler", "fluent-emoji-flat", "ph", "streamline-sharp"), tikz=True, bioicons=False),
}


def hoja_candidatos(lista, out=None, w=260, cols=4):
    """Hoja de contactos numerada de los candidatos (fondo oscuro, como en el video) para elegir con Read."""
    import cairosvg
    from PIL import Image as PImg, ImageDraw
    lista = [e for e in lista if e.get("path")]          # las figuras de tikz.net se ven en su página: compilarlas antes con tikz()
    out = out or os.path.join(CACHE, f"cand_{abs(hash(tuple(e['path'] for e in lista))) % 10**6}.png")
    rows = (len(lista) + cols - 1) // cols; sheet = PImg.new("RGB", (cols * w, rows * (w + 34)), (11, 15, 23)); d = ImageDraw.Draw(sheet)
    for i, e in enumerate(lista):
        tmp = os.path.join(CACHE, "_c.png")
        try:
            if e["path"].lower().endswith(".svg"):
                cairosvg.svg2png(url=limpiar(e["path"], quitar_texto=False), write_to=tmp, output_width=w - 20); src = tmp
            else: src = e["path"]
            im = PImg.open(src).convert("RGBA"); im.thumbnail((w - 20, w - 20))
            x, y = (i % cols) * w, (i // cols) * (w + 34); sheet.paste(im, (x + 10, y + 10), im)
        except Exception as ex: print("no renderiza", e["path"], ex); x, y = (i % cols) * w, (i // cols) * (w + 34)
        d.text((x + 6, y + w + 2), f"{i}: {e['name'][:30]}", fill=(255, 197, 61))
        d.text((x + 6, y + w + 17), f"{e['autor'][:18]} · {LIC_TXT.get(e['lic'], e['lic'])}", fill=(140, 150, 168))
    sheet.save(out); return out


# ---------------- 2. Limpieza: degradados → color medio, sin texto ----------------
SVGNS = "http://www.w3.org/2000/svg"; XL = "{http://www.w3.org/1999/xlink}href"

def _hex(c):
    c = c.strip()
    if c.startswith("#") and len(c) == 4: c = "#" + "".join(ch * 2 for ch in c[1:])
    return c if re.fullmatch(r"#[0-9a-fA-F]{6}", c) else None

def limpiar(path, quitar_texto=True):
    """Copia limpia en caché: prefijos ns0: fuera, cada url(#degradado) cambiado por el promedio de sus paradas
    (Manim no lee degradados; el volumen se recupera con set_sheen), y sin <text> (las etiquetas son nuestras, en inglés)."""
    out = os.path.join(CACHE, "svgclean", re.sub(r"[^\w]+", "_", path)[-120:] + ("" if quitar_texto else "_t") + ".svg")
    if os.path.exists(out) and os.path.getmtime(out) > os.path.getmtime(path): return out
    os.makedirs(os.path.dirname(out), exist_ok=True)
    raw = open(path, encoding="utf8", errors="ignore").read()
    raw = re.sub(r"<(/?)ns\d+:", r"<\1", raw).replace("xmlns:ns0=", "xmlns=")
    ET.register_namespace("", SVGNS); ET.register_namespace("xlink", "http://www.w3.org/1999/xlink")
    root = ET.fromstring(raw.encode("utf8"))
    grads = {}
    for g in root.iter():
        tag = g.tag.split("}")[-1]
        if tag in ("linearGradient", "radialGradient"):
            cols = []
            for s in g:
                st = s.get("style", ""); m = re.search(r"stop-color:\s*([^;]+)", st)
                c = _hex(s.get("stop-color") or (m.group(1) if m else ""))
                if c: cols.append(np.array(color_to_rgb(c)))
            grads[g.get("id")] = (cols, g.get(XL) or g.get("href"))
    def media(gid, depth=0):
        cols, ref = grads.get(gid, ([], None))
        if not cols and ref and depth < 5: return media(ref.lstrip("#"), depth + 1)
        return rgb_to_hex(np.mean(cols, axis=0)) if cols else "#8C96A8"
    def fix(v): return re.sub(r"url\(#([^)]+)\)", lambda m: media(m.group(1)), v)
    parent = {c: p for p in root.iter() for c in p}
    for el in list(root.iter()):
        tag = el.tag.split("}")[-1]
        if quitar_texto and tag in ("text", "flowRoot") and el in parent: parent[el].remove(el); continue
        for k in ("fill", "stroke", "style"):
            if el.get(k) and "url(#" in el.get(k): el.set(k, fix(el.get(k)))
    ET.ElementTree(root).write(out, encoding="unicode")
    return out


# ---------------- 3. SVGBio: el SVG como piezas animables ----------------
class SVGBio(VGroup):
    """Ilustración de banco (o propia) como VECTOR. s.piezas = lista de paths (orden del archivo, de atrás a delante).
    Seleccionar: s.sel(3, 5), s.por_color("#c2ddb7"), s.por_id("nucleo") (grupos <g id> de un SVG propio).
    Ver qué es cada pieza: mapa_piezas(s). Registrar el crédito es automático."""
    def __init__(self, entrada, alto=None, ancho=None, volumen=0.35, quitar_texto=True, claro=True, trazo_min=2.2, **kw):
        e = entrada if isinstance(entrada, dict) else dict(path=entrada, name=os.path.basename(entrada), autor="propio", lic="propio", fuente="propio")
        self.meta = e; self.src = limpiar(e["path"], quitar_texto)
        svg = SVGMobject(self.src, **kw)
        super().__init__(*svg.submobjects)
        self.ids = {k: v for k, v in getattr(svg, "id_to_vgroup_dict", {}).items() if not k.startswith("numbered_group") and k != "root"}
        self.piezas = [m for m in self.family_members_with_points()]
        if claro:      # (v1.7) trazos y rellenos negros (TikZ, íconos de línea) pasan a INK: si no, desaparecen en el fondo oscuro
            lum = lambda c: float(np.dot(color_to_rgb(c), [0.299, 0.587, 0.114]))
            for p in self.piezas:
                if lum(p.get_stroke_color()) < 0.18: p.set_stroke(color=INK)
                if p.get_fill_opacity() > 0 and lum(p.get_fill_color()) < 0.18: p.set_fill(color=INK)
        for p in self.piezas:      # (v1.7) TikZ dibuja a 0,4 pt: en 1080p se pierde; trazo mínimo legible
            if 0 < p.get_stroke_width() < trazo_min and p.get_stroke_opacity() > 0: p.set_stroke(width=trazo_min)
        for p in self.piezas: p._fo, p._so = p.get_fill_opacity(), p.get_stroke_opacity()   # opacidades originales
        for p in self.piezas:                                   # trazo fino propio: Servier no trae borde
            p.set_stroke(width=0) if p.get_stroke_width() == 0 else None
        if alto: self.scale_to_fit_height(alto)
        if ancho: self.scale_to_fit_width(ancho)
        if volumen:
            areas = np.array([p.width * p.height for p in self.piezas]); big = areas > np.percentile(areas, 60) if len(areas) > 3 else areas > 0
            for p, b in zip(self.piezas, big):       # brillo solo en piezas «con cuerpo»: una banda larga (membrana) se lavaría
                if b and p.get_fill_opacity() > 0.5 and max(p.width, p.height) < 3 * min(p.width, p.height) + 1e-6: p.set_sheen(volumen, UL)
        if e.get("fuente") != "propio": CREDITOS[e["path"]] = (e.get("autor", ""), e.get("fuente", ""), LIC_TXT.get(e.get("lic"), e.get("lic")))

    def sel(self, *idx): return VGroup(*[self.piezas[i] for i in idx])
    def rango(self, a, b): return VGroup(*self.piezas[a:b])
    def por_id(self, gid): return self.ids[gid]
    def colores(self):
        """{color: n.º de piezas} para reconocer partes (en Servier cada estructura tiene su color)."""
        c = {}
        for p in self.piezas: h = p.get_fill_color().to_hex().lower(); c[h] = c.get(h, 0) + 1
        return dict(sorted(c.items(), key=lambda kv: -kv[1]))
    def por_color(self, *hexes, tol=0.06):
        objs = [np.array(color_to_rgb(h)) for h in hexes]
        return VGroup(*[p for p in self.piezas if any(np.abs(np.array(color_to_rgb(p.get_fill_color().to_hex())) - o).max() < tol for o in objs)])
    def punto(self, fx, fy):
        """Punto del dibujo en fracciones (0,0 = arriba-izquierda; como en la hoja con rejilla) para etiquetas."""
        return np.array([self.get_left()[0] + fx * self.width, self.get_top()[1] - fy * self.height, 0])
    def tenir(self, color, a=0.35):
        """Corre los colores hacia el tinte de la escena (une la ilustración con el citoplasma)."""
        for p in self.piezas: p.set_fill(interpolate_color(p.get_fill_color(), ManimColor(color), a))
        return self


def mapa_piezas(s, out=None, w=1400):
    """PNG del dibujo rehecho con las piezas de Manim (colores reales) y el número de cada pieza sobre un punto de su
    borde (rojo, con guía). Mirarlo con Read antes de animar por piezas: así se sabe qué índice es cada estructura."""
    from PIL import Image as PImg, ImageDraw
    out = out or os.path.join(CACHE, "mapa_" + os.path.basename(s.src)[:-4][-60:] + ".png")
    pad = 40; sc = (w - 2 * pad) / s.width; h = int(s.height * sc) + 2 * pad
    L, T_ = s.get_left()[0], s.get_top()[1]
    px = lambda q: ((q[0] - L) * sc + pad, (T_ - q[1]) * sc + pad)
    im = PImg.new("RGB", (w, h), (11, 15, 23)); d = ImageDraw.Draw(im, "RGBA")
    for p in s.piezas:
        c = p.get_fill_color().to_rgb(); op = p.get_fill_opacity()
        for sp in p.get_subpaths():                      # curvas de Bézier cúbicas muestreadas (no los puntos de control)
            pts = []
            for k in range(0, len(sp) - 3, 4):
                a0, h1, h2, a1 = sp[k:k + 4]
                for t in np.linspace(0, 1, 7):
                    pts.append(px((1 - t) ** 3 * a0 + 3 * (1 - t) ** 2 * t * h1 + 3 * (1 - t) * t * t * h2 + t ** 3 * a1))
            if len(pts) > 2 and op > 0.05:
                d.polygon(pts, fill=tuple(int(255 * x) for x in c) + (int(255 * max(op, 0.25)),), outline=(40, 40, 50, 160))
            elif len(pts) > 1:                            # pieza de solo trazo: se dibuja como línea
                sc_ = tuple(int(255 * x) for x in p.get_stroke_color().to_rgb())
                d.line(pts, fill=sc_ + (230,), width=max(2, int(p.get_stroke_width() * 0.6)))
    for i, p in enumerate(s.piezas):
        if not len(p.get_points()): continue
        q = px(p.point_from_proportion((0.137 * i) % 1)); c = px(p.get_center())
        d.line([q, ((q[0] + c[0]) / 2, (q[1] + c[1]) / 2)], fill=(255, 40, 70, 200), width=2)
        d.ellipse([q[0] - 11, q[1] - 11, q[0] + 11, q[1] + 11], fill=(255, 40, 70, 235)); d.text((q[0] - 7, q[1] - 6), str(i), fill="white")
    im.save(out); return out


# ---------------- 4. Animaciones por piezas (lo que hace didáctico al SVG) ----------------
def _orden(s, por="area"):
    if por == "area": return sorted(s.piezas, key=lambda p: -p.width * p.height)
    if por == "x": return sorted(s.piezas, key=lambda p: p.get_center()[0])
    if por == "y": return sorted(s.piezas, key=lambda p: -p.get_center()[1])
    return list(s.piezas)

def dibujar(scene, s, rt=2.0, por="area", lag=0.08, color=None):
    """Construcción: cada pieza traza su contorno con luz y se rellena, de la más grande a la más pequeña."""
    anims = []
    for p in _orden(s, por):
        c = color or interpolate_color(p.get_fill_color(), ManimColor(WHITE), 0.45)
        anims.append(DrawBorderThenFill(p, stroke_color=c, stroke_width=1.6, rate_func=ease_in_out_cubic))
    scene.play(LaggedStart(*anims, lag_ratio=lag), run_time=rt)

def ensamblar(scene, s, rt=1.6, dist=1.6, lag=0.04, por="area", seed=2):
    """Las piezas llegan desde fuera (radial, con giro) y encajan con sobrepaso: «se arma la estructura»."""
    rng = np.random.default_rng(seed); c0 = s.get_center(); fin = {id(p): p.copy() for p in s.piezas}
    for p in s.piezas:
        v = p.get_center() - c0; v = v / (np.linalg.norm(v) + 1e-6)
        p.shift(v * dist * rng.uniform(0.6, 1.2)).rotate(rng.uniform(-0.6, 0.6)).set_opacity(0)
    scene.add(s)
    scene.play(LaggedStart(*[Transform(p, fin[id(p)], rate_func=ease_out_back_soft) for p in _orden(s, por)], lag_ratio=lag), run_time=rt)

def despiece(scene, s, grupos, dist=1.2, rt=1.0):
    """Vista explotada: cada grupo se separa del centro (para nombrar las partes) — devuelve las posiciones de vuelta."""
    c0 = s.get_center(); vuelta = []
    for g in grupos:
        v = g.get_center() - c0; v = v / (np.linalg.norm(v) + 1e-6); vuelta.append((g, -v * dist))
    scene.play(*[g.animate(rate_func=ease_out_expo).shift(-d) for g, d in vuelta], run_time=rt)
    return vuelta

def rearmar(scene, vuelta, rt=0.8):
    scene.play(*[g.animate(rate_func=ease_in_out_cubic).shift(d) for g, d in vuelta], run_time=rt)

def resaltar(scene, s, parte, color=GOLD, dim=0.22, rt=0.6):
    """Enfoca una parte: el resto se apaga, la parte gana halo y un pulso. Devuelve el halo (quitar con apagar)."""
    otras = [p for p in s.piezas if p not in parte.family_members_with_points()]
    h = glow(parte, color, opacity=0.5)
    scene.add(h); scene.bring_to_back(h)
    scene.play(*[p.animate.set_fill(opacity=p._fo * dim).set_stroke(opacity=p._so * dim) for p in otras], FadeIn(h),
               parte.animate(rate_func=there_and_back_with_pause).scale(1.06), run_time=rt)
    return h

def apagar(scene, s, h, rt=0.4):
    scene.play(*[p.animate.set_fill(opacity=p._fo).set_stroke(opacity=p._so) for p in s.piezas], FadeOut(h), run_time=rt)

def vivo(s, amp=0.012, w=0.7, seed=4, piezas=None):
    """Vida en reposo: cada pieza «respira» con su fase (como el citoplasma). Barato: escala alrededor de su centro."""
    rng = np.random.default_rng(seed); ps = piezas or s.piezas
    for p in ps:
        p._ph = rng.uniform(0, TAU); p._t = 0.0; p._k = 1.0
        def u(m, dt):
            m._t += dt; k = 1 + amp * np.sin(w * TAU * m._t + m._ph); m.scale(k / m._k); m._k = k
        p.add_updater(u)
    return s

def quieto(s):
    for p in s.piezas: p.clear_updaters()
    return s

def flujo(scene, s, piezas, color=CYAN, rt=1.4, ancho=6):
    """Un pulso de luz recorre el contorno de las piezas (corriente, señal, transporte)."""
    trazos = [p.copy().set_fill(opacity=0).set_stroke(color, ancho, 1) for p in piezas.family_members_with_points()]
    scene.play(LaggedStart(*[ShowPassingFlash(t, time_width=0.35) for t in trazos], lag_ratio=0.15), run_time=rt)

def cosmos(s, color=None, halo=0.4):
    """Tratamiento Cosmos: halo del color dominante detrás. Devuelve Group(halo, s) — moverlos juntos."""
    color = color or list(s.colores())[0]
    return Group(glow(s, color, opacity=halo), s)


# ---------------- 5. SVG propio (cuando el banco no alcanza) ----------------
def propio(nombre, svg):
    """Guarda un SVG dibujado por Claude en el banco propio (reutilizable en otras corridas) y devuelve su ruta.
    Reglas: viewBox, una <g id="..."> por parte con nombre en inglés, rellenos planos + un trazo de brillo,
    nada de <text>. Se crea con SVGBio(ruta) y se seleccionan partes con s.por_id("cristae")."""
    p = os.path.join(PROPIOS, re.sub(r"[^\w-]+", "-", nombre) + ".svg")
    open(p, "w").write(svg); global _IDX; _IDX = None
    return p



# ---------------- 7. (v1.7) Banco de imágenes gratuito (raster): paso 2 del orden ----------------
def foto(q, n=8, fuente=None):
    """Openverse con licencia comercial + modificación (fotos de Flickr, Wikimedia, museos, NASA…): baja la miniatura
    de 600 px (siempre accesible desde la nube) y, si se puede, el original. fuente="wikimedia"/"flickr"/"nasa"… filtra."""
    extra = {"source": fuente} if fuente else {}
    out = []
    for r in _openverse(q, n, **extra):
        d = os.path.join(BANCO, "fotos"); os.makedirs(d, exist_ok=True)
        ext = os.path.splitext(urllib.parse.urlparse(r["url"]).path)[1].lower() or ".jpg"
        if ext == ".svg": continue
        p = os.path.join(d, r["id"] + ext)
        if not os.path.exists(p):
            ok = False
            for u in filter(None, [_wm_thumb(r["url"], 1280), _wm_thumb(r["url"], 960), r["url"], f"https://api.openverse.org/v1/images/{r['id']}/thumb/"]):
                try:
                    _bajar(u, p)
                    from PIL import Image as PImg; PImg.open(p).verify(); ok = True; break   # una página de error no es imagen
                except Exception:
                    if os.path.exists(p): os.remove(p)
            if not ok: print("no se pudo bajar", r["url"], "(bajarlo por el PC)"); continue
        out.append(dict(path=p, name=r.get("title") or r["id"], cat=r.get("source", ""), autor=r.get("creator") or r.get("source", ""),
                        lic=_lic_ov(r), fuente="Openverse · " + r.get("source", ""), url=r.get("foreign_landing_url")))
    return out

def nih_png(bioart_id):
    """El PNG de una entrada de NIH BioArt (para cuando la entrada no trae SVG). Rechaza NC como nih()."""
    html = _get(f"https://bioart.niaid.nih.gov/bioart/{bioart_id}").decode("utf8", "ignore")
    m = re.search(r'\\"PNG\\":(\d+)', html)
    if not m: raise ValueError("Esta entrada no tiene PNG")
    if re.search(r"CC[- ]BY[- ]NC", html, re.I): raise ValueError(f"NIH {bioart_id}: licencia NC, no apta")
    p = os.path.join(BANCO, "nih", f"{bioart_id}.png"); os.makedirs(os.path.dirname(p), exist_ok=True)
    _bajar(f"https://bioart.niaid.nih.gov/api/bioarts/{bioart_id}/files/{m.group(1)}", p)
    return dict(path=p, name=str(bioart_id), cat="nih", autor="NIAID Visual & Medical Arts", lic="public domain", fuente="NIH BioArt")

def foto_cosmos(entrada, alto=4.0, borde=0.18, oscuro=0.15, vineta=True):
    """Imagen raster de banco lista para el estilo Cosmos: bordes que se desvanecen (alfa con rampa suave), un poco
    oscurecida para que el texto blanco gane, y el crédito registrado. Devuelve un ImageMobject (animarlo SIEMPRE:
    Ken Burns, deriva, fundido, nunca quieto). Con PNG de fondo transparente (NIH, Servier) no aplica el borde."""
    from PIL import Image as PImg
    e = entrada if isinstance(entrada, dict) else dict(path=entrada, name=os.path.basename(entrada), autor="", lic="", fuente="")
    im = PImg.open(e["path"]).convert("RGBA"); a = np.array(im).astype(float) / 255; h, w = a.shape[:2]
    a[..., :3] *= (1 - oscuro)
    transparente = (a[..., 3] < 0.99).mean() > 0.05
    if vineta and not transparente:
        y, x = np.mgrid[0:h, 0:w]; k = borde * min(h, w)
        d = np.minimum.reduce([x, y, w - 1 - x, h - 1 - y]).astype(float)
        a[..., 3] *= np.clip(d / k, 0, 1) ** 1.6
    out = os.path.join(CACHE, "fotos_cosmos", re.sub(r"[^\w]+", "_", e["path"])[-100:] + ".png"); os.makedirs(os.path.dirname(out), exist_ok=True)
    PImg.fromarray((a * 255).astype(np.uint8)).save(out)
    m = ImageMobject(out).set_height(alto)
    if e.get("fuente"): CREDITOS[e["path"]] = (e.get("autor", ""), e.get("fuente", ""), LIC_TXT.get(e.get("lic"), e.get("lic")))
    return m


# ---------------- 6. Créditos ----------------
def creditos_txt():
    """Líneas de crédito agrupadas por fuente y licencia (para la descripción del video y la tarjeta final)."""
    g = {}
    for autor, fuente, lic in CREDITOS.values():
        if autor == "Servier": a = "Servier Medical Art"
        elif autor == "DBCLS": a = "DBCLS TogoTV"
        elif fuente == "Bioicons": a = f"{autor} (Bioicons)"
        elif fuente.startswith("Openverse"): a = f"{autor} ({fuente.split('· ')[-1]})"
        elif fuente == "Iconify": a = f"{autor} (Iconify)"
        elif fuente == "tikz.net": a = f"{autor} (tikz.net)" if autor != "tikz.net" else "tikz.net"
        else: a = autor
        k = (a, lic)
        g[k] = g.get(k, 0) + 1
    return [f"{a} · {l}" for (a, l), n in sorted(g.items())]

def tarjeta_creditos(scene, rt=0.6, hold=2.0):
    ls = creditos_txt()
    if not ls: return
    t = VGroup(MONO_T("Illustrations", 22, GOLD), *[MONO_T(l, 18, MUTED) for l in ls]).arrange(DOWN, aligned_edge=LEFT, buff=0.14)
    t.to_corner(DL, buff=0.6)
    scene.play(LaggedStart(*[FadeIn(x, shift=UP * 0.15) for x in t], lag_ratio=0.1), run_time=rt); scene.wait(hold)
    return t

from estilo import BG, BG2, INK, MUTED, FAINT, LINE, RED, BLUE, MINT, GOLD, VIOLET, CYAN   # solo la paleta: from manim import * la pisa, y un import * pisaría rotulo_pro
