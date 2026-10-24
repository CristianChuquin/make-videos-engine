# transcribe.py — marcas por palabra (faster-whisper base, modelo local en ./wmodel)
# (v2.4.1) el audio se decodifica con ffmpeg a numpy: la versión de PyAV de la nube rompe faster_whisper.decode_audio
import json, sys, subprocess, numpy as np
from faster_whisper import WhisperModel
m = WhisperModel(__import__('os').environ.get('WM','small'), device='cpu', compute_type='int8')
def load(f):
    raw = subprocess.run(['ffmpeg', '-v', 'error', '-i', f, '-f', 'f32le', '-ac', '1', '-ar', '16000', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.float32).copy()
for k in sys.argv[1:]:
    segs, _ = m.transcribe(load(f'{k}.wav'), language='es', word_timestamps=True, beam_size=1)
    W = [[round(w.start, 2), round(w.end, 2), w.word] for s in segs for w in s.words]
    json.dump(W, open(f'words_{k}.json', 'w'), ensure_ascii=False)
    print(f'===== {k}  ({W[-1][1]:.1f} s)'); print(' '.join(f'{w[2].strip()}@{w[0]}' for w in W), flush=True)
