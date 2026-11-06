"""Check a Short's audio continuity against its approved master narration.

A speech-envelope fingerprint can detect deleted, replaced, delayed or wildly
re-timed audio. It cannot verify spoken words, speaker identity, or lip-sync.
Works offline with FFmpeg and NumPy; no cloud APIs or tokens.
"""
import argparse
import json
import shutil
import subprocess
from pathlib import Path

import numpy as np

RATE = 8000
FRAME = 160  # 20ms audio envelope bins
MAX_OFFSET_FRAMES = 5  # allow up to 100ms codec delay


def read_envelope(media):
    media = Path(media)
    if not media.is_file():
        raise FileNotFoundError(f"Missing audio master/output: {media}")
    if not shutil.which('ffmpeg'):
        raise RuntimeError('FFmpeg is required for continuity checking')
    proc = subprocess.run(
        ['ffmpeg', '-v', 'error', '-i', str(media), '-vn',
         '-ac', '1', '-ar', str(RATE), '-t', '61',
         '-f', 's16le', 'pipe:1'],
        capture_output=True, timeout=65, check=False)
    if proc.returncode or len(proc.stdout) < RATE * 2:
        raise RuntimeError(f'Cannot decode audio from {media.name}')
    sound = np.frombuffer(proc.stdout, dtype='<i2').astype(np.float32)/32768
    count = len(sound)//FRAME
    envelope = np.sqrt(np.mean(sound[:count*FRAME].reshape(count, FRAME)**2, axis=1))
    return envelope, len(sound)/RATE


def compare_audio(master, final, min_similarity=0.90):
    source, master_duration = read_envelope(master)
    rendered, output_duration = read_envelope(final)
    duration_delta = output_duration-master_duration
    master_rms = float(np.sqrt(np.mean(source**2)))
    output_rms = float(np.sqrt(np.mean(rendered**2)))
    if master_rms < 0.003 or output_rms < 0.003:
        return {'decision':'BLOCK', 'reason':'Master or output is effectively silent',
                'envelope_similarity':0.0, 'offset_ms':None,
                'duration_difference_sec':round(duration_delta, 3),
                'spoken_content_verified':False}

    best = (-1.0, 0)
    original = np.log1p(source*100)
    candidate = np.log1p(rendered*100)
    for lag in range(-MAX_OFFSET_FRAMES, MAX_OFFSET_FRAMES+1):
        left = original[max(0, lag):]
        right = candidate[max(0, -lag):]
        size = min(len(left), len(right))
        if size < 100:
            continue
        a, b = left[:size], right[:size]
        sa, sb = float(a.std()), float(b.std())
        if sa < 1e-4 or sb < 1e-4:
            continue
        correlation = float(np.mean((a-a.mean())*(b-b.mean()))/(sa*sb))
        if correlation > best[0]:
            best = (correlation, lag)

    similarity, lag = best
    valid = similarity >= min_similarity and abs(duration_delta) <= 0.35
    reason = 'Audio activity timing matches the supplied master' if valid else (
        'Significant audio mismatch, shift or duration difference'
    )
    return {'decision':'CONTINUITY_PASS' if valid else 'BLOCK',
            'reason':reason, 'envelope_similarity':round(max(similarity,0), 4),
            'offset_ms':lag*20, 'duration_difference_sec':round(duration_delta, 3),
            'spoken_content_verified':False,
            'warning':'An envelope match does not prove spoken words, natural voice or avatar lip-sync.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('master', type=Path)
    parser.add_argument('rendered', type=Path)
    parser.add_argument('--report', type=Path)
    args = parser.parse_args()
    result = compare_audio(args.master, args.rendered)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(json.dumps(result, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(result, indent=2))
    if result['decision'] != 'CONTINUITY_PASS':
        raise SystemExit(2)


if __name__ == '__main__':
    main()
