import subprocess
from pathlib import Path

in_dir = Path("audio/burn_cd/data")
out_dir = Path("audio/burn_cd/raw")
out_dir.mkdir(parents=True, exist_ok=True)

for i, f in enumerate(sorted(in_dir.glob("*.wav")), start=1):
    out_path = out_dir / f"track{i:02d}.raw"
    subprocess.run([
        "ffmpeg", "-y", "-i", str(f),
        "-f", "s16le", "-ar", "44100", "-ac", "2",
        str(out_path)
    ])
    print(f"✅ Converted {f.name} to {out_path.name}")
