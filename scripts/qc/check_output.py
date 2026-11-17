"""Inspect an MP4 against the cut sheet. Exit nonzero on a failed check."""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from fractions import Fraction
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lib"))
from inutarou_anim import timeline  # noqa: E402


def probe(path: Path) -> dict:
    p = subprocess.run(["ffprobe", "-v", "error", "-show_streams", "-show_format",
                        "-of", "json", str(path)], check=True, capture_output=True, text=True)
    return json.loads(p.stdout)


def detect(path: Path, filter_name: str) -> str:
    p = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(path),
                        "-vf" if filter_name == "blackdetect" else "-af",
                        "blackdetect=d=0:pix_th=0.10" if filter_name == "blackdetect"
                        else "silencedetect=noise=-50dB:d=0.5", "-f", "null", "-"],
                       capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError(p.stderr[-1500:])
    return p.stderr


def check(path: Path, ep: timeline.Episode, shot: str | None, *, cut_id: str | None = None,
          allow_black: bool = False, allow_silence: bool = False,
          percent: int = 100, scan: bool = True, require_final: bool = False) -> list[str]:
    errors: list[str] = []
    cuts = [ep.cut(cut_id)] if cut_id else ep.cuts_of_shot(shot) if shot else ep.cuts
    if not cuts:
        return [f"unknown shot: {shot}"]
    if require_final:
        unfinished = [c.id for c in cuts if c.data.get("status") != "final"]
        if unfinished:
            errors.append(f"non-final cuts: {unfinished}")
    expected = sum(c.frames for c in cuts)
    info = probe(path)
    video = next((s for s in info["streams"] if s["codec_type"] == "video"), None)
    audio = next((s for s in info["streams"] if s["codec_type"] == "audio"), None)
    if video is None:
        return ["video stream missing"]
    size = (round(ep.width * percent / 100), round(ep.height * percent / 100))
    if (video.get("width"), video.get("height")) != size:
        errors.append(f"size: expected {size}, got {video.get('width')}x{video.get('height')}")
    if Fraction(video.get("avg_frame_rate", "0/1")) != ep.fps:
        errors.append(f"fps: expected {ep.fps}, got {video.get('avg_frame_rate')}")
    if video.get("codec_name") != "h264":
        errors.append(f"video codec: {video.get('codec_name')}")
    if audio is None or audio.get("codec_name") != "aac":
        errors.append(f"audio codec: {audio.get('codec_name') if audio else 'missing'}")
    frames = int(video.get("nb_frames") or round(float(video.get("duration") or info["format"]["duration"]) * ep.fps))
    if frames != expected:
        errors.append(f"frames: expected {expected}, got {frames}")
    duration = float(info["format"]["duration"])
    if abs(duration - expected / ep.fps) > 1 / ep.fps + 0.03:
        errors.append(f"duration: expected {expected / ep.fps:.3f}s, got {duration:.3f}s")
    if scan:
        if not allow_black:
            black = re.findall(r"black_start:([\d.]+).*?black_end:([\d.]+)", detect(path, "blackdetect"))
            if black:
                errors.append(f"black intervals: {black}")
        if audio and not allow_silence:
            report = detect(path, "silencedetect")
            silence = re.findall(r"silence_start: ([\d.]+).*?silence_end: ([\d.]+)",
                                 report, re.DOTALL)
            starts = re.findall(r"silence_start: ([\d.]+)", report)
            if len(starts) > len(silence):
                silence.append((starts[-1], f"{duration:.3f}"))
            if silence:
                errors.append(f"silence intervals: {silence}")
    return errors


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("file", type=Path)
    ap.add_argument("--episode", default="episode01")
    ap.add_argument("--shot")
    ap.add_argument("--cut")
    ap.add_argument("--percent", type=int, default=100)
    ap.add_argument("--allow-black", action="store_true", help="intentional placeholder/black screen")
    ap.add_argument("--allow-silence", action="store_true", help="intentional silent passage")
    ap.add_argument("--no-scan", action="store_true", help="skip black/silence scan")
    ap.add_argument("--require-final", action="store_true", help="reject temp/todo cuts")
    args = ap.parse_args()
    try:
        errors = check(args.file, timeline.load(args.episode), args.shot, cut_id=args.cut,
                       allow_black=args.allow_black, allow_silence=args.allow_silence,
                       percent=args.percent, scan=not args.no_scan,
                       require_final=args.require_final)
    except (OSError, subprocess.CalledProcessError, ValueError, RuntimeError) as e:
        errors = [str(e)]
    for error in errors:
        print("FAIL:", error)
    if errors:
        return 1
    print("PASS:", args.file)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
