"""カット表のセリフ・効果音から、仮の音声トラック（WAV）を作る。

- セリフ: line の audio（正式な音声ファイル）があればそれを使う。無ければ macOS の say で仮音声を作る。
- 効果音: sfx の audio があればそれを使う。無ければ簡単な合成音（仮）を作る。
- 作った音は「仮」。完成した音声として扱わない。

  python3 scripts/audio/temp_audio.py --episode episode01 --shot s6_ending \
      --out renders/episode01/s6_ending/audio.wav

Python 3.11 以上の標準ライブラリと ffmpeg だけで動く（numpy 不要）。
"""
from __future__ import annotations

import argparse
import array
import json
import math
import random
import shutil
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "lib"))

from inutarou_anim import timeline  # noqa: E402

SR = 48000


# ---------------------------------------------------------------- 合成音（仮）
def _env(n: int, attack: float, release: float) -> list[float]:
    a, r = max(1, int(attack * SR)), max(1, int(release * SR))
    out = []
    for i in range(n):
        e = min(1.0, i / a)
        if i > n - r:
            e *= max(0.0, (n - i) / r)
        out.append(e)
    return out


def sfx_kiran() -> list[float]:
    n = int(0.6 * SR)
    env = _env(n, 0.005, 0.5)
    out = []
    for i in range(n):
        t = i / SR
        f = 1800 + 2600 * min(1.0, t / 0.12)
        v = (math.sin(2 * math.pi * f * t) * 0.5 + math.sin(2 * math.pi * f * 1.5 * t) * 0.25
             + math.sin(2 * math.pi * 5200 * t) * 0.15 * math.exp(-t * 6))
        out.append(v * env[i] * math.exp(-t * 3.0))
    return out


def sfx_whoosh() -> list[float]:
    rnd = random.Random(1)
    n = int(0.28 * SR)
    out, lp = [], 0.0
    for i in range(n):
        t = i / n
        k = 0.05 + 0.4 * math.sin(math.pi * t)
        lp += k * (rnd.uniform(-1, 1) - lp)
        out.append(lp * math.sin(math.pi * t) * 1.6)
    return out


def sfx_bokaa() -> list[float]:
    rnd = random.Random(2)
    n = int(0.55 * SR)
    out, lp, ph = [], 0.0, 0.0
    for i in range(n):
        t = i / SR
        f = 40 + 110 * math.exp(-t * 18)
        ph += 2 * math.pi * f / SR
        thump = math.sin(ph) * math.exp(-t * 7)
        lp += 0.25 * (rnd.uniform(-1, 1) - lp)
        crack = lp * math.exp(-t * 30) * 1.5
        v = thump * 1.2 + crack
        out.append(math.tanh(v * 2.2) * 0.9)
    return out


def sfx_notify() -> list[float]:
    out = []
    for f, dur in ((1320, 0.09), (0, 0.03), (1760, 0.14)):
        n = int(dur * SR)
        env = _env(n, 0.003, 0.05)
        out += [math.sin(2 * math.pi * f * i / SR) * 0.5 * env[i] if f else 0.0 for i in range(n)]
    return out


def sfx_wings() -> list[float]:
    rnd = random.Random(3)
    n = int(0.8 * SR)
    out, lp = [], 0.0
    for i in range(n):
        t = i / SR
        lp += 0.2 * (rnd.uniform(-1, 1) - lp)
        out.append(lp * max(0.0, math.sin(2 * math.pi * 7 * t)) * 1.4)
    return out


SFX = {"kiran": sfx_kiran, "whoosh": sfx_whoosh, "bokaa": sfx_bokaa, "notify": sfx_notify,
       "wings": sfx_wings}


# ---------------------------------------------------------------- 読み書き
def read_wav(path: Path) -> list[float]:
    """どんな音声ファイルでも ffmpeg で 48kHz モノラルに直して読む。"""
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / "a.wav"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", str(path), "-ac", "1", "-ar", str(SR),
                        "-sample_fmt", "s16", str(tmp)], check=True)
        with wave.open(str(tmp)) as w:
            data = array.array("h", w.readframes(w.getnframes()))
    return [s / 32768 for s in data]


def say(text: str, voice: str, rate: int) -> list[float]:
    if not shutil.which("say"):
        return []
    with tempfile.TemporaryDirectory() as td:
        tmp = Path(td) / "v.wav"
        cmd = ["say", "-o", str(tmp), f"--data-format=LEI16@{SR}"]
        if voice:
            cmd += ["-v", voice]
        if rate:
            cmd += ["-r", str(rate)]
        subprocess.run(cmd + [text], check=True)
        return read_wav(tmp)


def write_wav(path: Path, samples: list[float]) -> None:
    peak = max(1e-9, max(abs(s) for s in samples))
    gain = min(1.0, 0.89 / peak)   # 最大 -1 dBFS
    data = array.array("h", (int(max(-1, min(1, s * gain)) * 32767) for s in samples))
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(data.tobytes())


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--episode", default="episode01")
    ap.add_argument("--shot", default=None, help="このショットの範囲だけ（省略で話全体）")
    ap.add_argument("--narration-rate", type=int, help="仮ナレーションの速度を比較する場合の上書き値")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    ep = timeline.load(args.episode)
    if args.shot:
        cuts = ep.cuts_of_shot(args.shot)
        start, end = cuts[0].start, cuts[-1].end
    else:
        start, end = 1, ep.frames
    n = round((end - start + 1) / ep.fps * SR)
    mix = [0.0] * n
    report = []
    for q in ep.cues(start, end):
        if q.audio:
            src, kind = read_wav(ROOT / q.audio), "file"
        elif q.kind == "line":
            rate = args.narration_rate if q.speaker == "narration" and args.narration_rate else q.rate
            src, kind = say(q.text, q.voice, rate), "temp_say"
        elif q.name in SFX:
            src, kind = SFX[q.name](), "temp_synth"
        else:
            src, kind = [], "missing"
        off = round((q.frame - start) / ep.fps * SR)
        for i, v in enumerate(src):
            if 0 <= off + i < n:
                mix[off + i] += v * q.gain
        report.append({"frame": q.frame, "shot_frame": q.frame - start + 1, "cut": q.cut,
                       "kind": q.kind, "name": q.name or q.speaker, "text": q.text, "source": kind,
                       "seconds": round(len(src) / SR, 3)})
    out = Path(args.out)
    write_wav(out, mix)
    out.with_suffix(".cues.json").write_text(json.dumps(report, ensure_ascii=False, indent=2),
                                             encoding="utf-8")
    for r in report:
        print(f"  {r['shot_frame']:>4}f  {r['kind']:<4} {r['name']:<10} {r['source']:<11} {r['text']}")
    print("wrote", out)


if __name__ == "__main__":
    main()
