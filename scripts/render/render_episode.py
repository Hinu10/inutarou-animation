"""Render a shot, cut, or whole episode from cuts.toml.

Usage: python3 scripts/render/render_episode.py {episode|cut|shot} episode01 [id]
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lib"))
from inutarou_anim import timeline  # noqa: E402


def run(*args: str) -> None:
    subprocess.run([str(a) for a in args], check=True)


def shot_path(episode: str, shot: str) -> Path:
    return ROOT / "renders" / episode / shot / f"{shot}.mp4"


def render_shot(episode: str, shot: str, percent: int = 100) -> Path:
    subprocess.run([str(ROOT / "scripts/render/render_shot.sh"), shot], check=True,
                   env={**os.environ, "EPISODE": episode, "PERCENT": str(percent)})
    return shot_path(episode, shot)


def placeholder(path: Path, cut: timeline.Cut, ep: timeline.Episode, percent: int) -> None:
    width, height = round(ep.width * percent / 100), round(ep.height * percent / 100)
    # ffmpeg builds without drawtext are common; draw a tiny bitmap label ourselves.
    font = {
        "0": ("111", "101", "101", "101", "111"), "1": ("010", "110", "010", "010", "111"),
        "2": ("111", "001", "111", "100", "111"), "3": ("111", "001", "111", "001", "111"),
        "4": ("101", "101", "111", "001", "001"), "5": ("111", "100", "111", "001", "111"),
        "6": ("111", "100", "111", "101", "111"), "7": ("111", "001", "001", "001", "001"),
        "8": ("111", "101", "111", "101", "111"), "9": ("111", "101", "111", "001", "111"),
        "s": ("111", "100", "111", "001", "111"), "c": ("111", "100", "100", "100", "111"),
        "_": ("000", "000", "000", "000", "111"),
    }
    label = cut.id.lower()
    scale = max(2, min(width // max(1, len(label) * 5), height // 12, 12))
    pixels = bytearray(width * height * 3)
    x0 = max(0, (width - len(label) * 4 * scale) // 2)
    y0 = max(0, (height - 5 * scale) // 2)
    for index, char in enumerate(label):
        for row, bits in enumerate(font.get(char, ("111", "101", "101", "101", "111"))):
            for col, bit in enumerate(bits):
                if bit == "1":
                    for dy in range(scale):
                        for dx in range(scale):
                            x, y = x0 + (index * 4 + col) * scale + dx, y0 + row * scale + dy
                            if 0 <= x < width and 0 <= y < height:
                                offset = (y * width + x) * 3
                                pixels[offset:offset + 3] = b"\xff\xff\xff"
    image = path.with_suffix(".ppm")
    image.write_bytes(f"P6\n{width} {height}\n255\n".encode() + pixels)
    run("ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", str(ep.fps),
        "-i", image, "-f", "lavfi", "-i", "anullsrc=r=48000:cl=stereo",
        "-frames:v", str(cut.frames), "-t", str(cut.frames / ep.fps),
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", str(path))


def extract_cut(path: Path, source: Path, cut: timeline.Cut, first: int, ep: timeline.Episode) -> None:
    offset = cut.start - first
    run("ffmpeg", "-v", "error", "-y", "-i", source,
        "-vf", f"trim=start_frame={offset}:end_frame={offset + cut.frames},setpts=PTS-STARTPTS",
        "-af", f"atrim=start={offset / ep.fps}:duration={cut.frames / ep.fps},asetpts=PTS-STARTPTS",
        "-frames:v", str(cut.frames), "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p",
        "-c:a", "aac", str(path))


def render_episode(name: str, cut_id: str | None, percent: int, bgm: Path | None = None) -> Path:
    ep = timeline.load(name)
    cuts = [ep.cut(cut_id)] if cut_id else ep.cuts
    output = ROOT / "renders" / name / (f"{cut_id}.mp4" if cut_id else f"{name}.mp4")
    output.parent.mkdir(parents=True, exist_ok=True)
    shot_sources: dict[str, Path] = {}
    with tempfile.TemporaryDirectory(prefix="inutarou-render-") as tmp:
        folder = Path(tmp)
        pieces = []
        for index, cut in enumerate(cuts):
            piece = folder / f"{index:04d}.mp4"
            shot = cut.data.get("shot")
            script = ROOT / "scenes" / name / "shots" / f"{shot}.py" if shot else None
            if cut.data.get("status") == "todo" or script is None or not script.is_file():
                placeholder(piece, cut, ep, percent)
            else:
                if shot not in shot_sources:
                    shot_sources[shot] = render_shot(name, shot, percent)
                first = ep.cuts_of_shot(shot)[0].start
                extract_cut(piece, shot_sources[shot], cut, first, ep)
            pieces.append(piece)
        manifest = folder / "list.txt"
        manifest.write_text("".join(f"file '{p}'\n" for p in pieces))
        silent_video = folder / "video.mp4"
        run("ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", manifest,
            "-an", "-c:v", "libx264", "-crf", "18", "-pix_fmt", "yuv420p", silent_video)
        if cut_id:
            # Use the cut's extracted track when building one cut.
            run("ffmpeg", "-v", "error", "-y", "-i", silent_video, "-i", pieces[0],
                "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "copy", output)
        else:
            wav = folder / "audio.wav"
            normalized = folder / "normalized.wav"
            run(sys.executable, ROOT / "scripts/audio/temp_audio.py", "--episode", name, "--out", wav)
            normalize_args = [sys.executable, ROOT / "scripts/audio/normalize.py", wav, normalized]
            if bgm:
                normalize_args += ["--bgm", bgm]
            run(*normalize_args)
            run("ffmpeg", "-v", "error", "-y", "-i", silent_video, "-i", normalized,
                "-map", "0:v:0", "-map", "1:a:0", "-c:v", "copy", "-c:a", "aac", "-b:a", "192k",
                "-af", "apad", "-t", str(ep.frames / ep.fps), output)
    qc_args = [sys.executable, ROOT / "scripts/qc/check_output.py", output, "--episode", name,
               "--percent", str(percent), "--no-scan"]
    if cut_id:
        qc_args += ["--cut", cut_id]
    run(*qc_args)
    return output


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("mode", choices=["info", "shot", "cut", "episode"])
    ap.add_argument("episode", nargs="?", default="episode01")
    ap.add_argument("id", nargs="?")
    ap.add_argument("--percent", type=int, default=100)
    ap.add_argument("--bgm", type=Path, help="optional episode-long BGM file")
    args = ap.parse_args()
    ep = timeline.load(args.episode)
    if args.mode == "info":
        cuts = ep.cuts_of_shot(args.id)
        if not cuts:
            ap.error(f"unknown shot: {args.id}")
        print(ep.fps, sum(c.frames for c in cuts))
    elif args.mode == "shot":
        if not args.id:
            ap.error("shot id required")
        print(render_shot(args.episode, args.id, args.percent))
    else:
        print(render_episode(args.episode, args.id if args.mode == "cut" else None,
                             args.percent, args.bgm))


if __name__ == "__main__":
    main()
