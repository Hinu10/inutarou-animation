"""Derive simple open/closed mouth cues from recorded dialogue audio.

Writes a sidecar JSON; it does not modify cuts.toml or animation code.
"""
import argparse
import array
import json
import math
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lib"))
from inutarou_anim import timeline  # noqa: E402

SR = 48000
OPEN = {"inutarou": "open", "kaito": "o"}


def samples(path: Path) -> array.array:
    p = subprocess.run(["ffmpeg", "-v", "error", "-i", str(path), "-f", "s16le",
                        "-ac", "1", "-ar", str(SR), "-"], check=True, capture_output=True)
    data = array.array("h")
    data.frombytes(p.stdout)
    if not data:
        raise ValueError(f"音声が空です: {path}")
    return data


def mouth_frames(data: array.array, fps: int, start: int, end: int,
                 threshold: float) -> list[dict]:
    length = SR / fps
    out = []
    last = None
    for frame in range(start, end + 1):
        offset = frame - start
        block = data[round(offset * length):round((offset + 1) * length)]
        rms = math.sqrt(sum(x * x for x in block) / len(block)) / 32768 if block else 0.0
        state = "open" if rms >= threshold else "closed"
        if state != last:
            out.append({"frame": frame, "state": state})
            last = state
    return out


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--episode", default="episode01")
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--threshold", type=float, default=0.035)
    args = ap.parse_args()
    ep = timeline.load(args.episode)
    result = []
    for cut in ep.cuts:
        for cue in cut.cues:
            if cue.kind != "line" or cue.speaker not in OPEN or not cue.audio:
                continue
            source = ROOT / cue.audio
            data = samples(source)
            audio_end = cue.frame + (len(data) * ep.fps + SR - 1) // SR - 1
            last = min(cut.end, audio_end)
            keys = mouth_frames(data, ep.fps, cue.frame, last, args.threshold)
            result.append({"cut": cut.id, "speaker": cue.speaker, "source": cue.audio,
                           "part": "mouth", "open_variant": OPEN[cue.speaker],
                           "closed_variant": "default", "end_frame": last,
                           "truncated": audio_end > cut.end, "keys": keys})
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps({"episode": ep.id, "fps": ep.fps, "tracks": result},
                                   ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"wrote {args.out} ({len(result)} recorded dialogue tracks)")


if __name__ == "__main__":
    main()
