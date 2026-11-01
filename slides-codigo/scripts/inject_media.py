#!/usr/bin/env python3
"""
inject_media.py — convierte cada video del deck en una «diapositiva viva»:

  · arranca SOLO al entrar en la slide (Iniciar: Automáticamente), sin clic ni botón
  · NO se rebobina ni se oculta al terminar: se congela en su último frame = la slide final
  · la slide NO avanza sola: espera el clic / tecla / control de Cris
  · se quita la acción «clic = pausar» del video, para que un clic avance la slide
  · el video ocupa la diapositiva exacta (sin bordes por redondeo)

  python3 inject_media.py deck_raw.pptx -o deck.pptx
"""
import argparse
import json
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from lxml import etree

P = "http://schemas.openxmlformats.org/presentationml/2006/main"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
NS = {"p": P, "a": A, "r": R}


def slide_order(z):
    pres = etree.fromstring(z.read("ppt/presentation.xml"))
    rels = etree.fromstring(z.read("ppt/_rels/presentation.xml.rels"))
    rmap = {r.get("Id"): r.get("Target") for r in rels}
    sz = pres.find("p:sldSz", NS)
    order = ["ppt/" + rmap[s.get(f"{{{R}}}id")].lstrip("/").replace("ppt/", "") for s in pres.find("p:sldIdLst", NS)]
    return order, int(sz.get("cx")), int(sz.get("cy"))


def media_duration_ms(z, slide_part, rid):
    rels_part = slide_part.replace("slides/", "slides/_rels/") + ".rels"
    rels = etree.fromstring(z.read(rels_part))
    target = next(r.get("Target") for r in rels if r.get("Id") == rid)
    name = "ppt/" + target.replace("../", "")
    with tempfile.NamedTemporaryFile(suffix=".mp4") as f:
        f.write(z.read(name)); f.flush()
        out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", f.name],
                             capture_output=True, text=True, check=True).stdout
    return int(round(float(json.loads(out)["format"]["duration"]) * 1000)), name


def timing(spid, dur_ms):
    return (f'<p:timing xmlns:p="{P}"><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
            f'<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
            f'<p:par><p:cTn id="3" fill="hold"><p:stCondLst><p:cond delay="indefinite"/>'
            f'<p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond></p:stCondLst><p:childTnLst>'
            f'<p:par><p:cTn id="4" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
            f'<p:par><p:cTn id="5" presetID="1" presetClass="mediacall" presetSubtype="0" fill="hold" nodeType="afterEffect">'
            f'<p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
            f'<p:cmd type="call" cmd="playFrom(0.0)"><p:cBhvr><p:cTn id="6" dur="{dur_ms}" fill="hold"/>'
            f'<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:cmd>'
            f'</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>'
            f'</p:childTnLst></p:cTn><p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
            f'<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
            # cMediaNode SIN display="0": el video sigue visible al detenerse (congelado en el último frame)
            f'<p:video><p:cMediaNode vol="80000"><p:cTn id="7" fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst>'
            f'</p:cTn><p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cMediaNode></p:video>'
            f'</p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("deck")
    ap.add_argument("-o", "--out", required=True)
    a = ap.parse_args()
    with zipfile.ZipFile(a.deck) as z:
        order, cx, cy = slide_order(z)
        data = {n: z.read(n) for n in z.namelist()}
        infos = z.infolist()
        report = []
        for i, part in enumerate(order, 1):
            root = etree.fromstring(data[part])
            pics = [p for p in root.iter(f"{{{P}}}pic") if p.find(".//a:videoFile", NS) is not None]
            if len(pics) != 1:
                sys.exit(f"ERROR slide {i}: se esperaba 1 video y hay {len(pics)}")
            pic = pics[0]
            cnv = pic.find("p:nvPicPr/p:cNvPr", NS)
            spid = cnv.get("id")
            for h in cnv.findall("a:hlinkClick", NS):      # clic sobre el video = avanzar, no pausar
                cnv.remove(h)
            xfrm = pic.find("p:spPr/a:xfrm", NS)
            xfrm.find("a:off", NS).set("x", "0"); xfrm.find("a:off", NS).set("y", "0")
            xfrm.find("a:ext", NS).set("cx", str(cx)); xfrm.find("a:ext", NS).set("cy", str(cy))
            rid = pic.find(".//a:videoFile", NS).get(f"{{{R}}}link")
            dur, media = media_duration_ms(z, part, rid)
            for old in root.findall("p:timing", NS) + root.findall("p:transition", NS):
                root.remove(old)
            anchor = root.find("p:clrMapOvr", NS)
            root.insert(list(root).index(anchor) + 1, etree.fromstring(timing(spid, dur)))
            data[part] = etree.tostring(root, xml_declaration=True, encoding="UTF-8", standalone=True)
            report.append((i, spid, dur, Path(media).name))
    with zipfile.ZipFile(a.out, "w", zipfile.ZIP_DEFLATED) as zo:
        for it in infos:
            # los mp4 ya están comprimidos: se guardan sin recomprimir
            ct = zipfile.ZIP_STORED if it.filename.endswith(".mp4") else zipfile.ZIP_DEFLATED
            zo.writestr(it.filename, data[it.filename], compress_type=ct)
    for i, spid, dur, m in report:
        print(f"slide {i:02d}: video {m} · {dur / 1000:.2f}s · arranque automático · congela al final · avanza con clic")
    print(f"OK → {a.out}")


if __name__ == "__main__":
    main()
