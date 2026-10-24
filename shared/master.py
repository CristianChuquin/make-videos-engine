# master.py — AUDIO MAESTRO: une las generaciones y recorta los silencios ANTES de sincronizar (make-videos v2.0)
# uso: python3 master.py A B C   (lee A.wav, B.wav, C.wav …)  → master.wav (48 kHz, estéreo, −16 LUFS)
# Regla de Cris: en todo el audio ningún silencio puede pasar de 1 s. Si el master no lo cumple, el script se detiene.
import sys, subprocess
import numpy as np, soundfile as sf
SR = 48000; FR = int(0.02 * SR); THR = -42          # ventanas de 20 ms; umbral de silencio en dBFS
PAUSA = 0.45        # tope de cualquier pausa interna de una generación (s)
UNION = 0.45        # pausa entre una generación y la siguiente (s)
TECHO = 1.0         # silencio máximo admitido en el master final (s)
FADE = 240          # 5 ms de fundido en cada empalme (evita clics)

def loud(x):
    m = np.abs(x).mean(1); n = len(m) // FR
    rms = np.sqrt((m[:n * FR].reshape(n, FR) ** 2).mean(1))
    return 20 * np.log10(rms + 1e-9) > THR

def fade(seg, head, tail):
    seg = seg.copy(); k = min(FADE, len(seg) // 2)
    if k:
        r = np.linspace(0, 1, k)[:, None]
        if head: seg[:k] *= r
        if tail: seg[-k:] *= r[::-1]
    return seg

def edit(x):
    """Recorta el silencio de los bordes y acorta a PAUSA toda pausa interna más larga (empalme dentro del silencio)."""
    L = loud(x); idx = np.where(L)[0]
    if not len(idx): sys.exit('Generación sin voz: regenerarla')
    s, e = max(0, idx[0] - 2), min(len(L), idx[-1] + 4)     # 40 ms antes de la voz, 80 ms después
    keep = int(round(PAUSA / 0.02)); out = []; i = s
    while i < e:
        j = i
        if L[i]:
            while j < e and L[j]: j += 1
            out.append(x[i * FR:j * FR])
        else:
            while j < e and not L[j]: j += 1
            if j - i > keep:                                    # pausa larga: se conserva su inicio y su final
                h = keep // 2
                out.append(fade(x[i * FR:(i + h) * FR], False, True))
                out.append(fade(x[(j - (keep - h)) * FR:j * FR], True, False))
            else:
                out.append(x[i * FR:j * FR])
        i = j
    return np.concatenate(out)

def silencios(x):
    """Lista de silencios (inicio s, duración s) de todo el archivo, bordes incluidos."""
    L = loud(x); res = []; i = 0
    while i < len(L):
        if L[i]: i += 1; continue
        j = i
        while j < len(L) and not L[j]: j += 1
        res.append((round(i * 0.02, 2), round((j - i) * 0.02, 2))); i = j
    return res

parts = []
for k in sys.argv[1:]:
    x, sr = sf.read(f'{k}.wav')
    assert sr == SR, f'{k}.wav: {sr} Hz (se espera 48000)'
    if x.ndim == 1: x = np.stack([x, x], 1)
    y = edit(x); parts.append(y)
    print(f'{k}: {len(x) / SR:.1f} s → {len(y) / SR:.1f} s editado')
gap = np.zeros((int(UNION * SR), 2))
seq = []
for p in parts: seq += [p, gap]
sf.write('master_raw.wav', np.concatenate(seq[:-1]), SR)
subprocess.run(['ffmpeg', '-y', '-v', 'error', '-i', 'master_raw.wav', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=11',
                '-ar', str(SR), '-ac', '2', 'master.wav'], check=True)
z, _ = sf.read('master.wav')
if z.ndim == 1: z = np.stack([z, z], 1)
S = silencios(z); peor = max(S, key=lambda t: t[1]) if S else (0, 0)
print(f'master.wav: {len(z) / SR:.2f} s · silencio más largo {peor[1]:.2f} s (en {peor[0]:.2f} s)')
largos = [s for s in S if s[1] > TECHO]
if largos: sys.exit(f'FALLA: silencios > {TECHO} s en {largos}. Bajar PAUSA/UNION o revisar la generación.')
print('OK: ningún silencio pasa de', TECHO, 's')
