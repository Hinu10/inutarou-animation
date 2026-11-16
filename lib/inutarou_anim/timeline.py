"""カット表（scenes/<episode>/cuts.toml）を読み、秒数をフレームに直す。Blender 不要。

- カットの開始位置は書かない。上から順に長さを足して決める
  → 1カットの長さを変えると、後ろのカットは自動でずれる。
- 長さは seconds（秒）か frames（コマ）のどちらかで書く。
- セリフ・効果音の位置はカットの頭からの相対時間（at 秒 / at_frame コマ）。
- フレーム番号は 1 始まり（0.0 秒 = フレーム 1）。
"""
from __future__ import annotations

import tomllib
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


@dataclass
class Cue:
    kind: str            # "line" / "sfx"
    frame: int           # 絶対フレーム
    cut: str
    speaker: str = ""
    text: str = ""
    name: str = ""
    heard_by_humans: str = ""   # 犬太朗のセリフ: 人間には "bark" に聞こえる
    audio: str = ""      # 正式な音声ファイル（無ければ仮音声を作る）
    voice: str = ""      # 仮音声の声（macOS say の名前）
    rate: int = 0        # 仮音声の速さ
    gain: float = 1.0


@dataclass
class Cut:
    id: str
    scene: int
    start: int           # 絶対フレーム（このカットの最初のコマ）
    frames: int
    data: dict = field(default_factory=dict)
    cues: list[Cue] = field(default_factory=list)

    @property
    def end(self) -> int:
        """最後のコマ（含む）。"""
        return self.start + self.frames - 1

    def f(self, local: int) -> int:
        """カット内の相対コマ → 絶対フレーム。"""
        return self.start + local

    @property
    def camera(self) -> dict:
        return self.data.get("camera", {})


@dataclass
class Episode:
    id: str
    title: str
    fps: int
    width: int
    height: int
    cuts: list[Cut]

    def cut(self, cut_id: str) -> Cut:
        for c in self.cuts:
            if c.id == cut_id:
                return c
        raise KeyError(cut_id)

    def cuts_of_shot(self, shot: str) -> list[Cut]:
        return [c for c in self.cuts if c.data.get("shot") == shot]

    @property
    def frames(self) -> int:
        return sum(c.frames for c in self.cuts)

    def cues(self, start: int | None = None, end: int | None = None) -> list[Cue]:
        out = [q for c in self.cuts for q in c.cues]
        if start is not None:
            out = [q for q in out if q.frame >= start]
        if end is not None:
            out = [q for q in out if q.frame <= end]
        return sorted(out, key=lambda q: q.frame)


def _frames(spec: dict, fps: int, what: str) -> int:
    if "frames" in spec:
        return int(spec["frames"])
    if "seconds" in spec:
        return max(1, round(float(spec["seconds"]) * fps))
    raise ValueError(f"{what}: seconds か frames が必要です")


def _at(spec: dict, fps: int) -> int:
    if "at_frame" in spec:
        return int(spec["at_frame"])
    return round(float(spec.get("at", 0.0)) * fps)


def load(episode: str | Path) -> Episode:
    path = Path(episode)
    if not path.suffix:
        path = ROOT / "scenes" / str(episode) / "cuts.toml"
    raw = tomllib.loads(path.read_text(encoding="utf-8"))
    ep = raw["episode"]
    fps = int(ep["fps"])
    voices = raw.get("temp_voices", {})
    cuts: list[Cut] = []
    frame = 1
    for c in raw["cut"]:
        n = _frames(c, fps, c["id"])
        cut = Cut(id=c["id"], scene=int(c["scene"]), start=frame, frames=n, data=c)
        for ln in c.get("line", []):
            v = voices.get(ln.get("speaker", ""), {})
            cut.cues.append(Cue("line", frame + _at(ln, fps), cut.id, speaker=ln.get("speaker", ""),
                                text=ln.get("text", ""),
                                heard_by_humans=ln.get("heard_by_humans", ""),
                                audio=ln.get("audio", ""), voice=ln.get("voice", v.get("voice", "")),
                                rate=int(ln.get("rate", v.get("rate", 0))),
                                gain=float(ln.get("gain", 1.0))))
        for sx in c.get("sfx", []):
            cut.cues.append(Cue("sfx", frame + _at(sx, fps), cut.id, name=sx["name"],
                                text=sx.get("text", ""), audio=sx.get("audio", ""),
                                gain=float(sx.get("gain", 1.0))))
        cuts.append(cut)
        frame += n
    return Episode(ep["id"], ep["title"], fps, int(ep["width"]), int(ep["height"]), cuts)
