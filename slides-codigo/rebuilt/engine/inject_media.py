#!/usr/bin/env python3
"""Ajusta el PPTX de pptxgenjs para 'diapositivas vivas':
 - el video arranca solo al entrar en la slide (timing de PowerPoint 2010+),
 - sin hlinkClick (un clic avanza, no pausa), sin display="0" (queda congelado visible),
 - sin transición automática; portada del video en JPG con extensión correcta;
 - mp4 sin recomprimir.
uso: python3 inject_media.py in.pptx out.pptx"""
import re, sys, zipfile

TIMING = ('<p:timing><p:tnLst><p:par><p:cTn id="1" dur="indefinite" restart="never" nodeType="tmRoot"><p:childTnLst>'
 '<p:seq concurrent="1" nextAc="seek"><p:cTn id="2" dur="indefinite" nodeType="mainSeq"><p:childTnLst>'
 '<p:par><p:cTn id="3" fill="hold"><p:stCondLst><p:cond delay="indefinite"/><p:cond evt="onBegin" delay="0"><p:tn val="2"/></p:cond></p:stCondLst><p:childTnLst>'
 '<p:par><p:cTn id="4" fill="hold"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
 '<p:par><p:cTn id="5" presetID="1" presetClass="mediacall" presetSubtype="0" fill="hold" nodeType="afterEffect"><p:stCondLst><p:cond delay="0"/></p:stCondLst><p:childTnLst>'
 '<p:cmd type="call" cmd="playFrom(0.0)"><p:cBhvr><p:cTn id="6" dur="{dur}" fill="hold"/><p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cBhvr></p:cmd>'
 '</p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par></p:childTnLst></p:cTn></p:par>'
 '</p:childTnLst></p:cTn>'
 '<p:prevCondLst><p:cond evt="onPrev" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:prevCondLst>'
 '<p:nextCondLst><p:cond evt="onNext" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:nextCondLst></p:seq>'
 '<p:video><p:cMediaNode vol="80000"><p:cTn id="7" fill="hold"><p:stCondLst><p:cond delay="indefinite"/></p:stCondLst>'
 '<p:endCondLst><p:cond evt="onStopAudio" delay="0"><p:tgtEl><p:sldTgt/></p:tgtEl></p:cond></p:endCondLst></p:cTn>'
 '<p:tgtEl><p:spTgt spid="{spid}"/></p:tgtEl></p:cMediaNode></p:video>'
 '</p:childTnLst></p:cTn></p:par></p:tnLst></p:timing>')

import json, os
src, dst = sys.argv[1], sys.argv[2]
# duración por clip (ms) desde clips/NN.json → "dur"; 12 s por defecto
durs = {}
if len(sys.argv) > 3:
    ids = sorted(f[:-4] for f in os.listdir(sys.argv[3]) if re.fullmatch(r"\d+\.mp4", f))
    for k, i in enumerate(ids, 1):
        jp = os.path.join(sys.argv[3], i + ".json")
        durs[k] = int(1000 * json.load(open(jp)).get("dur", 12)) if os.path.exists(jp) else 12000
zin = zipfile.ZipFile(src)
items = {n: zin.read(n) for n in zin.namelist()}
renames = {}
for n in list(items):
    if re.fullmatch(r"ppt/media/image-\d+-\d+\.png", n) and items[n][:3] == b"\xff\xd8\xff":
        renames[n] = n[:-4] + ".jpeg"
for old, new in renames.items():
    items[new] = items.pop(old)
n_vid = 0
for n in list(items):
    if re.fullmatch(r"ppt/slides/_rels/slide\d+\.xml\.rels", n):
        s = items[n].decode()
        for old, new in renames.items():
            s = s.replace("../media/" + old.split("/")[-1], "../media/" + new.split("/")[-1])
        items[n] = s.encode()
    if re.fullmatch(r"ppt/slides/slide\d+\.xml", n):
        s = items[n].decode()
        if "<a:videoFile" not in s:
            continue
        s = s.replace('<a:hlinkClick r:id="" action="ppaction://media"/>', "")
        assert "hlinkClick" not in s
        spid = re.search(r'<p:pic>\s*<p:nvPicPr><p:cNvPr id="(\d+)"', s).group(1)
        s = re.sub(r"<p:transition.*?</p:transition>|<p:transition[^>]*/>", "", s, flags=re.S)
        s = re.sub(r"<p:timing>.*?</p:timing>", "", s, flags=re.S)
        s = s.replace("</p:clrMapOvr>", "</p:clrMapOvr>" + TIMING.format(spid=spid, dur=durs.get(int(re.search(r"slide(\d+)\.xml", n).group(1)), 12000)), 1)
        assert 'display="0"' not in s
        items[n] = s.encode()
        n_vid += 1
ct = items["[Content_Types].xml"].decode()
if 'Extension="jpeg"' not in ct:
    ct = ct.replace("<Default ", '<Default Extension="jpeg" ContentType="image/jpeg"/><Default ', 1)
if 'Extension="mp4"' not in ct:
    ct = ct.replace("<Default ", '<Default Extension="mp4" ContentType="video/mp4"/><Default ', 1)
items["[Content_Types].xml"] = ct.encode()
with zipfile.ZipFile(dst, "w") as z:
    for n, data in items.items():
        comp = zipfile.ZIP_STORED if n.endswith(".mp4") else zipfile.ZIP_DEFLATED
        z.writestr(n, data, compress_type=comp)
print("inyectado:", n_vid, "videos →", dst)
