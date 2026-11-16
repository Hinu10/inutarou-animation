"""Normalize a cut-sheet mix to a provisional integrated loudness target."""
import argparse
import json
import re
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
    cmd = ["ffmpeg", "-hide_banner", "-y", "-i", str(args.source)]
    if args.bgm:
        cmd += ["-stream_loop", "-1", "-i", str(args.bgm)]
        source_filter = f"[1:a]volume={args.bgm_gain}[music];[0:a][music]amix=inputs=2:duration=first:normalize=0"
    else:
        source_filter = "[0:a]anull"
    target = f"I={args.lufs}:TP=-1.5:LRA=11"
    measure = subprocess.run(cmd + ["-filter_complex", f"{source_filter},loudnorm={target}:print_format=json[out]",
                                    "-map", "[out]", "-f", "null", "-"],
                             check=True, capture_output=True, text=True)
    blocks = re.findall(r"\{[^{}]*\}", measure.stderr)
    if not blocks:
        raise RuntimeError("ffmpeg loudnorm did not report measurements")
    values = json.loads(blocks[-1])
    measured = (f":measured_I={values['input_i']}:measured_TP={values['input_tp']}"
                f":measured_LRA={values['input_lra']}:measured_thresh={values['input_thresh']}"
                f":offset={values['target_offset']}:linear=true")
    subprocess.run(cmd + ["-filter_complex", f"{source_filter},loudnorm={target}{measured}[out]",
                          "-map", "[out]", "-ar", "48000", "-ac", "2", str(args.output)],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print("wrote", args.output)


if __name__ == "__main__":
    main()
