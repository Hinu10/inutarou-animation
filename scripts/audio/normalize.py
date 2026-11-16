"""Normalize a cut-sheet mix to a provisional integrated loudness target."""
import argparse
import subprocess
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("source", type=Path)
    ap.add_argument("output", type=Path)
    ap.add_argument("--lufs", type=float, default=-24.0,
                    help="provisional target; owner can choose the final delivery target")
    ap.add_argument("--bgm", type=Path, help="optional episode-long background music")
    ap.add_argument("--bgm-gain", type=float, default=0.25)
    args = ap.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(args.source)]
    if args.bgm:
        cmd += ["-stream_loop", "-1", "-i", str(args.bgm), "-filter_complex",
                f"[1:a]volume={args.bgm_gain}[music];[0:a][music]amix=inputs=2:duration=first:normalize=0,loudnorm=I={args.lufs}:TP=-1.5:LRA=11[out]",
                "-map", "[out]"]
    else:
        cmd += ["-af", f"loudnorm=I={args.lufs}:TP=-1.5:LRA=11"]
    cmd += ["-ar", "48000", "-ac", "2", str(args.output)]
    subprocess.run(cmd, check=True)
    print("wrote", args.output)


if __name__ == "__main__":
    main()
