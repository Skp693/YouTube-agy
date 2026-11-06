"""Conservative audio preflight for Quaddis Shorts; never claims human-quality voice.

Uses only ffmpeg and numpy. It blocks near-silence and oscillator/tone-like
fallbacks, but a passing signal MUST still undergo listening and lip-sync review.
No data is uploaded to any service.
"""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
from pathlib import Path

import numpy as np

SAMPLE_RATE = 16000
MAX_SAMPLE_SECONDS = 16


def inspect_audio(path: Path) -> dict:
    path = Path(path)
    if not path.is_file():
        raise FileNotFoundError(f"Audio or video not found: {path}")
    if not shutil.which("ffmpeg"):
        raise RuntimeError("FFmpeg is required for audio preflight")
    result = subprocess.run(
        ["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", str(path),
         "-vn", "-ac", "1", "-ar", str(SAMPLE_RATE),
         "-t", str(MAX_SAMPLE_SECONDS), "-f", "s16le", "pipe:1"],
        capture_output=True, timeout=60, check=False,
    )
    if result.returncode or len(result.stdout) < SAMPLE_RATE:
        raise RuntimeError("Unable to decode at least 0.5 seconds of audio")
    y = np.frombuffer(result.stdout, dtype="<i2").astype(np.float32) / 32768.0
    rms = float(np.sqrt(np.mean(y * y)))
    peak = float(np.max(np.abs(y)))
    rms_dbfs = float(20 * np.log10(max(rms, 1e-8)))
    flags = []
    if rms < 0.003:
        flags.append("SILENCE")
    if peak >= 0.995:
        flags.append("POSSIBLE_CLIPPING_REVIEW")

    # Broad-band energy distinguishes the old 180/360/540 Hz oscillator from
    # typical recordings. It CANNOT judge whether spoken narration is natural.
    block = 2048
    hop = block // 2
    frames = np.stack([y[i:i+block] for i in range(0, len(y)-block+1, hop)])
    spectrum = np.abs(np.fft.rfft(frames * np.hanning(block), axis=1)) ** 2
    power = spectrum.mean(axis=0)
    frequencies = np.fft.rfftfreq(block, 1.0 / SAMPLE_RATE)
    high_share = float(power[frequencies >= 1000].sum() / max(power.sum(), 1e-20))
    if rms >= 0.003 and high_share < 0.003:
        flags.append("POSSIBLE_SYNTHETIC_TONE")

    blocked = "SILENCE" in flags or "POSSIBLE_SYNTHETIC_TONE" in flags
    return {
        "file": str(path),
        "decision": "BLOCK" if blocked else "HUMAN_REVIEW_REQUIRED",
        "flags": flags,
        "rms_dbfs": round(rms_dbfs, 2),
        "peak": round(peak, 4),
        "above_1khz_power_share": round(high_share, 6),
        "duration_seconds_sampled": round(len(y) / SAMPLE_RATE, 2),
        "is_natural_voice_verified": False,
        "note": "Speech naturalness, exact script, voice continuity, and lip-sync require human review."
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("media", type=Path, nargs="+")
    parser.add_argument("--report", type=Path)
    args = parser.parse_args()
    reports = [inspect_audio(p) for p in args.media]
    output = json.dumps(reports, indent=2)
    if args.report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(output + "\n", encoding="utf-8")
    print(output)
    if any(p["decision"] == "BLOCK" for p in reports):
        raise SystemExit(2)


if __name__ == "__main__":
    main()
