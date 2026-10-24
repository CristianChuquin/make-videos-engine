# sync.py — sincronización absoluta: LA VOZ MANDA, EL VIDEO SE ADAPTA (make-videos v2.0)
# uso: python3 sync.py cfg.json   → video_sync.mp4 + <out> + plan.json
# El audio (master.wav) NO se toca: ni se estira, ni se rellena con silencio. Cada tramo del video mudo entre dos anclas
# se re-cronometra para durar EXACTAMENTE lo que dura su tramo de voz: cámara lenta si la voz es más larga,
# aceleración si es más corta. Los cortes se calculan en fotogramas acumulados, así no hay deriva.
import json, sys, re, subprocess, unicodedata
import soundfile as sf
cfg = json.load(open(sys.argv[1]))
FPS = cfg.get('fps', 30)
VMAX = cfg.get('vmax', 2.0)          # aceleración máxima admitida (×2); más que eso se corrige en el render
SLOW = cfg.get('slow_max', 3.0)      # cámara lenta máxima (×3); más que eso sobra texto en ese tramo
PRE = 0.15                           # el corte de audio cae 0,15 s antes de la palabra ancla
def norm(s):
    s = unicodedata.normalize('NFD', s.lower())
    return re.sub(r'[^a-z0-9]', '', ''.join(c for c in s if unicodedata.category(c) != 'Mn'))
info = sf.info(cfg['audio']); ADUR = info.frames / info.samplerate
W = json.load(open(cfg['words']))    # [[t0, t1, palabra], ...] de transcribe.py sobre master.wav
cur, A, T = 0, [], []
for phrase, tv in cfg['anchors']:
    toks = [norm(p) for p in phrase.split()]; i = cur
    while i < len(W):
        if all(i + j < len(W) and norm(W[i + j][2]) == t for j, t in enumerate(toks)): break
        i += 1
    else: sys.exit(f'Ancla no encontrada: «{phrase}» (copiarla de la transcripción impresa, no del guion)')
    cur = i + 1; A.append(max(0.0, W[i][0] - PRE)); T.append(tv)
A[0] = 0.0; A.append(ADUR); T.append(cfg['vend'])
pieces, errs = [], []
for n in range(len(T) - 1):
    a, v = A[n + 1] - A[n], T[n + 1] - T[n]
    if a <= 0 or v <= 0: sys.exit(f'Tramo {n}: anclas fuera de orden (audio {a:.2f} s, video {v:.2f} s)')
    f = a / v                        # >1 cámara lenta · <1 aceleración
    if f < 1 / VMAX: errs.append(f'tramo {n} ({T[n]:.1f}-{T[n+1]:.1f} s del mudo): la voz dura {a:.1f} s y el video {v:.1f} s '
                                 f'→ ×{1/f:.2f} de aceleración. Bajar WF de esa escena y volver a renderizarla.')
    if f > SLOW: errs.append(f'tramo {n}: cámara lenta ×{f:.2f}. Sobra texto para esa escena: recortar el guion.')
    f0, f1 = round(A[n] * FPS), round(A[n + 1] * FPS)
    pieces.append(dict(n=n, v0=T[n], v1=T[n + 1], a0=round(A[n], 3), a1=round(A[n + 1], 3), f=round(f, 3), frames=f1 - f0))
for p in pieces: print(p)
if errs: sys.exit('NO SE SINCRONIZA:\n- ' + '\n- '.join(errs))
json.dump(dict(pieces=pieces, words=[(round(w[0], 2), w[2].strip()) for w in W], total=ADUR),
          open('plan.json', 'w'), ensure_ascii=False)
run = lambda *a: subprocess.run(list(a), check=True)
with open('vl.txt', 'w') as L:
    for p in pieces:
        o = f"vp{p['n']:02d}.mp4"
        run('ffmpeg', '-y', '-v', 'error', '-ss', str(p['v0']), '-to', str(p['v1']), '-i', cfg['video'],   # -ss/-to ANTES de -i
            '-vf', f"setpts=(PTS-STARTPTS)*{p['f']:.6f},fps={FPS},tpad=stop_mode=clone:stop_duration=1",
            '-frames:v', str(p['frames']), '-an', '-c:v', 'libx264', '-crf', str(cfg.get('crf', 14)), '-preset', 'medium', '-pix_fmt', 'yuv420p', o)   # (v2.2) Paper: "crf": 18
        L.write(f"file '{o}'\n")
run('ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0', '-i', 'vl.txt', '-c', 'copy', 'video_sync.mp4')
run('ffmpeg', '-y', '-v', 'error', '-i', 'video_sync.mp4', '-i', cfg['audio'], '-map', '0:v', '-map', '1:a',
    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-movflags', '+faststart', cfg['out'])
vd = float(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', 'video_sync.mp4'],
                          capture_output=True, text=True).stdout)
print(f'voz {ADUR:.2f} s · video {vd:.2f} s · diferencia {abs(vd - ADUR):.3f} s')
if abs(vd - ADUR) > 1.5 / FPS: sys.exit('FALLA: el video no dura lo mismo que la voz')
