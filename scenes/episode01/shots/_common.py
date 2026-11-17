"""第1話のショットで共通の準備（部屋・役者の配置・吠え声の文字など）。

ショットのスクリプトから
    common = stage.load_module(Path(__file__).with_name("_common.py"), "ep01_common")
で読み込む。ショットそのものではない（cuts.toml の shot には書かない）。
"""
from __future__ import annotations

import random
from dataclasses import dataclass

from inutarou_anim import effects as ef
from inutarou_anim import lipsync
from inutarou_anim import motions as mo
from inutarou_anim import stage
from inutarou_anim.actor import Actor, P, at, merge
from inutarou_anim.rig import Pose, Rig

INU_SCALE = 1.15
KAI_SCALE = 0.95
CROW_SCALE = 0.85


@dataclass
class Room:
    ctx: object
    room: object       # 背景モジュール（apartment_room）
    props: object      # 小道具モジュール（assets/props/items.py）
    bg: object         # 背景（GP）
    bgfx: object       # 背景の上・キャラの後ろ（机の上の物・集中線など）
    fx: object         # キャラの前（汗・キラン・記号）
    over: object       # いちばん前（フラッシュ・一時停止の色）
    inu: Actor | None = None
    kai: Actor | None = None
    crow: Actor | None = None

    # ------------------------------------------------------------ 位置
    def inu_seat(self) -> dict:
        return at(self.room.SPOTS["sofa_seat"], INU_SCALE)

    def kai_stand(self, dx: float = 0.0) -> dict:
        x, y = self.room.SPOTS["kaito_stand"]
        return at((x + dx, y), KAI_SCALE)

    # ------------------------------------------------------------ 小道具
    def potechi_on_desk(self, frame: int, on: bool = True) -> None:
        x, y = self.room.SPOTS["desk_top"]
        if on:
            self.bgfx.draw("desk_items", frame, self.props.potechi_bag(x + 0.1, y + 0.1, rot=0.05))
        else:
            self.bgfx.draw("desk_items", frame, self.props.crumbs(x + 0.1, y + 0.13, n=6, seed=3))

    # ------------------------------------------------------------ 記号・文字
    def bark(self, text: str, pos, start: int, end: int, size: float = 0.42, rot: float = 0.0,
             name: str = "t_bark") -> None:
        """人間（海斗）に聞こえている「吠え声」を文字で見せる。"""
        t = self.ctx.text(text, pos, size, color="white", outline="line", rot=rot,
                          name=f"{name}_{start}")
        t.show(start, end)

    def sweat(self, frame: int, end: int, pos, size: float = 0.22, rot: float = -0.5,
              layer: str = "sweat") -> None:
        self.fx.draw(layer, frame, ef.sweat(pos, size, rot=rot))
        self.fx.draw(layer, frame + 6, ef.sweat((pos[0] + 0.03, pos[1] - 0.12), size, rot=rot))
        self.fx.draw(layer, frame + 12, ef.sweat((pos[0] + 0.05, pos[1] - 0.22), size, rot=rot))
        self.fx.clear(layer, end)

    def mark(self, text: str, pos, start: int, end: int, size: float = 0.6, color: str = "white",
             rot: float = 0.0) -> None:
        """「？」「！」などの記号。"""
        self.ctx.text(text, pos, size, color=color, outline="line", rot=rot,
                      name=f"t_mark_{start}").show(start, end)


def setup(ctx, inu: bool = True, kai: bool = True, crow: bool = False,
          crow_depth: float = -1.0) -> Room:
    global _episode
    _episode = ctx.episode
    col = ctx.collection
    room_mod = ctx.background_module("apartment_room")
    r = Room(ctx=ctx, room=room_mod, props=ctx.props("items"),
             bg=stage.background(col, room_mod.layers(), name="bg_room", depth=10.0),
             bgfx=stage.FX(col, name="bg_fx", depth=5.0),
             fx=stage.FX(col, name="fx", depth=-2.0),
             over=stage.FX(col, name="over", depth=-4.0))
    if inu:
        r.inu = Actor(Rig(ctx.design("inutarou"), col, depth=0.0), r.inu_seat())
    if kai:
        r.kai = Actor(Rig(ctx.design("kaito"), col, depth=-0.5), r.kai_stand())
    if crow:
        r.crow = Actor(Rig(ctx.design("karasu"), col, depth=crow_depth),
                       at((20.0, 0.0), CROW_SCALE))
    return r


_episode = None   # setup() で入る。talk() が lip_sync.json を引くのに使う


def line(cut, speaker: str | None = None, n: int = 0):
    """カットのセリフ（n 番目）。"""
    qs = [q for q in cut.cues if q.kind == "line" and (speaker is None or q.speaker == speaker)]
    return qs[n]


def talk(actor, cue, open_=("talk", "open"), closed="default", end_variant=None, seed=0,
         fps: int = 24, frames: int | None = None, ep=None) -> int:
    """セリフの口パク。

    収録音声（line.audio）の lip_sync.json があればその開閉タイミングを使う（#63）。
    開いた口は JSON の open_variant（犬太朗 open / 海斗 o）、閉じた口と言い終わりは
    ショットで指定した closed / end_variant（ふくれ顔のまましゃべる、などの演技を残すため）。
    無ければ従来どおり仮の口パク（ランダムに開け閉め）。
    """
    have = actor.rig.parts["mouth"].variants
    ep = ep or _episode
    if ep is not None:
        hit = lipsync.keys_for(cue, ep.id, ep.cut(cue.cut).end, ep.fps)
        if hit:
            tr, keys = hit
            op = tr.open_variant if tr.open_variant in have else next(
                (v for v in open_ if v in have), "talk")
            return mo.talk_keys(actor, keys, open_=op, closed=closed, end_variant=end_variant,
                                end=ep.cut(cue.cut).end)
    n = frames or mo.speech_frames(cue.text, cue.rate, fps)
    open_ = tuple(v for v in open_ if v in have) or ("talk",)
    return mo.talk(actor, cue.frame, n, open_=open_, closed=closed, end_variant=end_variant,
                   seed=seed)


def blink_every(actor, start: int, end: int, every: int = 50, seed: int = 0, **kw) -> None:
    rnd = random.Random(seed)
    f = start + rnd.randint(8, every)
    frames = []
    while f < end - 3:
        frames.append(f)
        f += every + rnd.randint(-12, 12)
    mo.blink(actor, frames, **kw)


__all__ = ["Room", "setup", "line", "talk", "blink_every", "P", "merge", "Pose", "at", "mo", "ef"]
