"""収録音声から出した口の開閉タイミング（lip_sync.json）を読む。Blender 不要。

lip_sync.json は Codex 担当の scripts/audio/lip_sync.py が書き出す（#46 / #63）:

  {"episode": "episode01", "fps": 24,
   "tracks": [{"cut": "s3c02", "speaker": "inutarou", "source": "assets/audio/...wav",
               "part": "mouth", "open_variant": "open", "closed_variant": "default",
               "keys": [{"frame": 401, "state": "open"}, {"frame": 404, "state": "closed"}, ...]}]}

- 置き場所は renders/<episode>/lip_sync.json。環境変数 INUTAROU_LIP_SYNC で別のファイルを指せる。
- セリフ（cuts.toml の line）と track は「カット・話者・audio のパス」が一致したときだけ対応させる。
  → audio を差し替えたのに JSON を作り直していない場合は使わない（仮の口パクに戻る）。
- keys の frame は絶対フレーム。カットの秒数を変えてセリフの位置がずれた場合は、
  最初のキーをセリフの頭に合わせてずらし、警告を出す（作り直すのが正しい）。
"""
from __future__ import annotations

import json
import os
import sys
from dataclasses import dataclass
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ENV = "INUTAROU_LIP_SYNC"


@dataclass
class Track:
    cut: str
    speaker: str
    source: str
    open_variant: str
    closed_variant: str
    keys: list[tuple[int, bool]]   # (絶対フレーム, 開いているか)


_cache: dict[Path, dict[tuple[str, str, str], Track]] = {}


def path_for(episode_id: str) -> Path:
    env = os.environ.get(ENV)
    return Path(env) if env else ROOT / "renders" / episode_id / "lip_sync.json"


def _norm(p: str) -> str:
    return Path(p).as_posix().lstrip("./")


def load(episode_id: str, fps: int | None = None) -> dict[tuple[str, str, str], Track]:
    """(cut, speaker, source) → Track。ファイルが無ければ空。"""
    path = path_for(episode_id)
    if path in _cache:
        return _cache[path]
    tracks: dict[tuple[str, str, str], Track] = {}
    if path.is_file():
        raw = json.loads(path.read_text(encoding="utf-8"))
        if raw.get("episode") not in (None, episode_id):
            print(f"[lipsync] {path} は {raw.get('episode')} 用なので使いません", file=sys.stderr)
        elif fps is not None and raw.get("fps") not in (None, fps):
            print(f"[lipsync] {path} の fps={raw.get('fps')} がカット表（{fps}）と違うので使いません",
                  file=sys.stderr)
        else:
            for t in raw.get("tracks", []):
                if t.get("part", "mouth") != "mouth" or not t.get("keys"):
                    continue
                keys = sorted((int(k["frame"]), k["state"] == "open") for k in t["keys"])
                tr = Track(t["cut"], t["speaker"], _norm(t["source"]),
                           t.get("open_variant", "open"), t.get("closed_variant", "default"), keys)
                tracks[(tr.cut, tr.speaker, tr.source)] = tr
    _cache[path] = tracks
    return tracks


def keys_for(cue, episode_id: str, cut_end: int, fps: int | None = None
             ) -> tuple[Track, list[tuple[int, bool]]] | None:
    """セリフ（timeline.Cue）に対応する口の開閉キー。無ければ None。

    キーはセリフの頭に揃え、カットの最後のコマ（cut_end）より後ろは捨てる。
    """
    if not cue.audio:
        return None
    tr = load(episode_id, fps).get((cue.cut, cue.speaker, _norm(cue.audio)))
    if tr is None:
        return None
    shift = cue.frame - tr.keys[0][0]
    if shift:
        print(f"[lipsync] {cue.cut}/{cue.speaker}: セリフの位置が {shift:+d} コマずれています。"
              f"lip_sync.json を作り直してください（今回はずらして使います）", file=sys.stderr)
    keys = [(f + shift, o) for f, o in tr.keys if f + shift <= cut_end]
    return (tr, keys) if keys else None
