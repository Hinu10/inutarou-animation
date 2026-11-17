"""よく使う動き（第2話以降でも使う汎用モーション）。

どれも「役者（Actor）」と「フレーム範囲」を受け取ってキーや描き替えを入れるだけ。
姿勢の数値はキャラクターの design.py の MOTION（あれば）から読むので、
正式デザインに差し替えても呼び出し側は変えなくてよい。

  talk(actor, start, frames)                   口パク（仮。ランダムに開け閉め）
  talk_keys(actor, keys)                       音声から出した開閉キーで口パク（lipsync.py / #63）
  blink(actor, frames)                         まばたき
  walk(actor, start, end, x0, x1, y)           横移動の歩き（足の振り・上下動・腕振り）
  flap(actor, start, end, path)                羽ばたきながら path に沿って飛ぶ（カラス）
  game(actor, start, end)                      コントローラーをカチャカチャ操作する（犬太朗）
  tremble(actor, start, end, pose, amp)        怒りなどで震える
  bounce(actor, start, end, pose, height)      その場で跳ねる（地団駄）
"""
from __future__ import annotations

import math
import random
from typing import Callable, Sequence

from .actor import P, merge
from .skeleton import Pose, PoseDict


# ---------------------------------------------------------------- 口・目
def speech_frames(text: str, rate: int, fps: int = 24) -> int:
    """仮音声（say）のおおよその長さ（コマ）。rate 190 で 1秒に約6文字。"""
    n = sum(1 for ch in text if ch not in " 　、。！？!?…「」『』（）")
    cps = max(3.0, (rate or 190) / 30.0)
    return max(8, round(n / cps * fps))


def talk(actor, start: int, frames: int, open_: Sequence[str] = ("open",),
         closed: str = "default", end_variant: str | None = None, every: int = 4,
         part: str = "mouth", seed: int = 0) -> int:
    """start から frames コマのあいだ口を開け閉めする（仮の口パク）。終わりのコマを返す。"""
    rnd = random.Random(seed)
    f, k = start, 0
    end = start + frames
    while f < end:
        v = open_[rnd.randrange(len(open_))] if k % 2 == 0 else closed
        actor.rig.swap(f, part, v)
        f += every + (rnd.choice((0, 0, 2)) if k % 2 == 0 else 0)
        k += 1
    actor.rig.swap(end, part, end_variant or closed)
    return end


def talk_keys(actor, keys: Sequence[tuple[int, bool]], open_: str = "open",
              closed: str = "default", end_variant: str | None = None, end: int | None = None,
              tail: int = 4, part: str = "mouth") -> int:
    """音声から出した (フレーム, 開いているか) のキーで口を開け閉めする。終わりのコマを返す。

    最後のキーが「開」のまま終わっているときは tail コマ後に閉じる（end を超えない）。
    """
    for f, is_open in keys:
        actor.rig.swap(f, part, open_ if is_open else closed)
    last, last_open = keys[-1]
    stop = last
    if last_open:
        stop = max(last + 1, min(last + tail, end) if end is not None else last + tail)
    if last_open or end_variant:
        actor.rig.swap(stop, part, end_variant or closed)
    return stop


def talk_cue(actor, cue, fps: int = 24, **kw) -> int:
    return talk(actor, cue.frame, speech_frames(cue.text, cue.rate, fps), **kw)


def blink(actor, frames: Sequence[int], eyes=("eye_L", "eye_R"), closed: str = "closed",
          open_: str = "default", length: int = 2) -> None:
    """frames のコマで length コマだけ目を閉じる。"""
    for f in frames:
        for e in eyes:
            actor.rig.swap(f, e, closed)
            actor.rig.swap(f + length, e, open_)


def look(x: float, y: float = 0.0, eyes=("eye_L", "eye_R")) -> PoseDict:
    """視線（目のボーンを少しずらす）。x, y はおおよそ ±0.1。"""
    return {e: Pose(loc=(x, y)) for e in eyes}


# ---------------------------------------------------------------- 歩く
def walk(actor, start: int, end: int, x0: float, x1: float, y: float, pose: PoseDict | None = None,
         stride: int = 12, scale: float = 1.0, leg_swing: float = 16.0, arm_swing: float = 10.0,
         bob: float = 0.08) -> PoseDict:
    """start〜end で x0 → x1 へ歩く（2コマごとにキー）。正面向きのまま横に歩く仮の歩き。

    stride = 1歩のコマ数。最後は両足をそろえて止まる（最後の姿勢を返す）。
    """
    pose = pose or {}
    n = max(1, end - start)
    last = None
    for f in range(start, end + 1, 2):
        t = (f - start) / n
        # 歩き出しと止まりは少しゆっくり
        tt = t * t * (3 - 2 * t) * 0.35 + t * 0.65
        ph = 2 * math.pi * (f - start) / (2 * stride)
        fade = min(1.0, (f - start) / 4, (end - f) / 4)
        sw = math.sin(ph) * fade
        lift = abs(math.cos(ph)) * fade
        add = {"leg_L": leg_swing * sw, "leg_R": -leg_swing * sw, "arm_L": -arm_swing * sw,
               "arm_R": arm_swing * sw, "spine": 1.5 * sw, "head": -1.0 * sw}
        p = merge(pose, {"root": Pose(loc=(x0 + (x1 - x0) * tt, y + bob * scale * lift),
                                      scale=(scale, scale))})
        for b, r in add.items():
            q = pose.get(b, Pose())
            p[b] = Pose(loc=q.loc, rot=q.rot + r, scale=q.scale)
        last = actor.key(f, p)
    stop = merge(pose, {"root": Pose(loc=(x1, y), scale=(scale, scale))})
    return actor.key(end, stop) if last is not None else stop


# ---------------------------------------------------------------- 飛ぶ（カラス）
def flap(actor, start: int, end: int, path: Callable[[float], tuple[float, float]],
         scale: float = 1.0, flip: bool = False, every: int = 2,
         wings: Sequence[str] = ("up", "default", "down", "default"), tilt: float = 8.0) -> None:
    """path(t) → (x, y)（t = 0〜1）に沿って羽ばたきながら飛ぶ。flip で左向き。"""
    n = max(1, end - start)
    for k, f in enumerate(range(start, end + 1, every)):
        t = (f - start) / n
        x, y = path(t)
        x2, y2 = path(min(1.0, t + 0.05))
        ang = math.degrees(math.atan2(y2 - y, abs(x2 - x) + 1e-6))
        actor.rig.swap(f, "wing", wings[k % len(wings)])
        actor.key(f, {"root": Pose(loc=(x, y), scale=(-scale if flip else scale, scale)),
                      "body": Pose(rot=max(-25, min(25, ang * 0.6)) + tilt * math.sin(k)),
                      "legs": Pose(rot=-20, scale=(1, 0.7)),
                      "tail": Pose(rot=6 * math.sin(k * 1.7))}, "LINEAR")


# ---------------------------------------------------------------- ゲーム操作（犬太朗）
def game(actor, start: int, end: int, pose: PoseDict | None = None, seed: int = 0,
         every: int = 2, intensity: float = 1.0) -> PoseDict:
    """コントローラーを持ってカチャカチャ操作する。design.MOTION["game"] の腕の角度を使う。"""
    m = actor.design.MOTION["game"]
    rnd = random.Random(seed)
    base = merge(P(**m["pose"]), pose or {})
    last = base
    for f in range(start, end + 1, every):
        j = intensity
        p = merge(base, P(
            paw_L=dict(rot=base.get("paw_L", Pose()).rot + rnd.uniform(-6, 6) * j,
                       loc=(0, rnd.choice((0.0, 0.0, -0.03)) * j)),
            paw_R=dict(rot=base.get("paw_R", Pose()).rot + rnd.uniform(-6, 6) * j,
                       loc=(0, rnd.choice((0.0, -0.03, 0.0)) * j)),
            body=dict(rot=base.get("body", Pose()).rot + rnd.uniform(-1.2, 1.2) * j),
        ))
        last = actor.key(f, p, "CONSTANT")
    return last


# ---------------------------------------------------------------- 震える・跳ねる
def tremble(actor, start: int, end: int, pose: PoseDict, amp: float = 1.0, seed: int = 0,
            bones: Sequence[str] = ("spine", "head")) -> PoseDict:
    rnd = random.Random(seed)
    last = pose
    for f in range(start, end + 1, 2):
        p = dict(pose)
        for b in bones:
            if b not in actor.bones:
                continue
            q = pose.get(b, Pose())
            p[b] = Pose(loc=(q.loc[0] + rnd.uniform(-0.015, 0.015) * amp, q.loc[1]),
                        rot=q.rot + rnd.uniform(-1.5, 1.5) * amp, scale=q.scale)
        last = actor.key(f, p, "CONSTANT")
    return last


def bounce(actor, start: int, end: int, pose: PoseDict, height: float = 0.3, period: int = 8,
           squash: float = 0.08, bone: str = "root") -> PoseDict:
    """その場で跳ねる（着地でつぶれる）。"""
    last = pose
    base = pose.get(bone, Pose())
    for f in range(start, end + 1, 2):
        ph = ((f - start) % period) / period
        h = math.sin(math.pi * ph) * height
        land = ph < 0.15 or ph > 0.85
        sq = (1 + squash, 1 - squash) if land else (1 - squash * 0.5, 1 + squash * 0.5)
        p = dict(pose)
        p[bone] = Pose(loc=(base.loc[0], base.loc[1] + h), rot=base.rot,
                       scale=(base.scale[0] * sq[0], base.scale[1] * sq[1]))
        last = actor.key(f, p, "CONSTANT")
    return actor.key(end, pose, "CONSTANT") if last is not None else pose
