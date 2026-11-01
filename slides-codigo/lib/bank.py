#!/usr/bin/env python3
"""bank.py — búsqueda en Bioicons (índice local) + Reactome, sin Manim. Licencias sin NC."""
import glob, os, re, sys, json, subprocess, urllib.request, urllib.parse
B = os.path.expanduser("~/.mv_cache/bancos")

def preparar():
    """Clona Bioicons (solo static/icons) la primera vez; mismo caché que cosmos/svgbank.py."""
    d = f"{B}/bioicons"
    if not os.path.isdir(f"{d}/static/icons"):
        os.makedirs(B, exist_ok=True)
        subprocess.run(f"git clone -q --depth 1 --filter=blob:none --sparse https://github.com/duerrsimon/bioicons.git {d} "
                       f"&& cd {d} && git sparse-checkout set static/icons", shell=True, check=True)
OK = {"cc-0", "cc-by-3.0", "cc-by-4.0", "cc-by-sa-3.0", "cc-by-sa-4.0", "bsd", "mit"}
def idx():
    preparar()
    out = []
    for p in glob.glob(f"{B}/bioicons/static/icons/*/*/*/*.svg"):
        lic, cat, autor = p.split(os.sep)[-4:-1]
        if lic in OK: out.append(dict(path=p, name=os.path.basename(p)[:-4], cat=cat, autor=autor, lic=lic, fuente="Bioicons"))
    return out
def buscar(q, n=15):
    toks = re.findall(r"\w+", q.lower()); res = []
    for e in idx():
        t = (e["name"] + " " + e["cat"]).lower().replace("_", " ").replace("-", " ")
        s = sum(2 if re.search(r"\b" + re.escape(k), t) else (1 if k in t else 0) for k in toks)
        if s: res.append((s + (0.5 if e["autor"] == "Servier" else 0), e))
    return [e for _, e in sorted(res, key=lambda x: -x[0])[:n]]
def reactome(q, n=6):
    url = "https://reactome.org/ContentService/search/query?" + urllib.parse.urlencode(dict(query=q, types="Icon", cluster="true"))
    try: d = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"}), timeout=30).read())
    except Exception as ex: print("reactome:", ex, file=sys.stderr); return []
    out = []
    for g in d.get("results", []):
        for e in g.get("entries", [])[:n]:
            p = f"{B}/reactome/{e['stId']}.svg"; os.makedirs(os.path.dirname(p), exist_ok=True)
            if not os.path.exists(p):
                open(p, "wb").write(urllib.request.urlopen(urllib.request.Request(f"https://reactome.org/icon/{e['stId']}.svg", headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read())
            out.append(dict(path=p, name=re.sub("<[^>]+>", "", e["name"]), cat=",".join(e.get("iconCategories", [])), autor="Reactome", lic="cc-by-4.0", fuente="Reactome"))
    return out
if __name__ == "__main__":
    for q in sys.argv[1:]:
        print(f"## {q}")
        for e in buscar(q) + (reactome(q) if not q.startswith("@") else []):
            print(f"  {e['fuente']:9} {e['lic']:12} {e['autor'][:18]:18} {e['cat'][:22]:22} {e['name']}")
