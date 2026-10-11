import sys
import wave
import struct
import math
from pathlib import Path

# Add project root to sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

def create_ambient_sample(output_path: Path, duration_sec: float = 30.0) -> None:
    sample_rate = 24000
    num_samples = int(sample_rate * duration_sec)
    
    with wave.open(str(output_path), "w") as wf:
        wf.setnchannels(2)  # Stereo
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)

        raw = bytearray()
        # Soft ambient chord (C major 9th: C, E, G, B, D)
        freqs = [130.81, 164.81, 196.00, 246.94, 293.66]

        for i in range(num_samples):
            t = i / sample_rate
            # Very slow gentle LFO modulation
            lfo = 0.5 * (1.0 + math.sin(2.0 * math.pi * 0.1 * t))
            sample = 0.0
            for idx, f in enumerate(freqs):
                sample += math.sin(2.0 * math.pi * f * t) * (0.2 / (idx + 1))
            
            # Very low soft amplitude
            val = int(sample * lfo * 1500.0)
            val = max(-32767, min(32767, val))
            raw.extend(struct.pack("<hh", val, val))

        wf.writeframes(raw)

if __name__ == "__main__":
    from config.settings import settings
    settings.ensure_directories()
    out = settings.MUSIC_DIR / "ambient_sample.wav"
    create_ambient_sample(out)
    print(f"Created ambient sample at {out}")
