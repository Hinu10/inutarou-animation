"""SCENE 2（8〜16秒）: s2c01〜s2c03。仮素材。

  s2c01 窓からカラスが入ってきて、部屋を横切って机にとまる（犬太朗はゲームに夢中）。
  s2c02 カラスがポテチの袋をくわえて飛び去る（机にはかけらが残る）。
  s2c03 窓から出ていくカラスを犬太朗が一瞬見て「……は？何だあいつ」→ ゲームに戻る。
"""
from __future__ import annotations

from pathlib import Path

from inutarou_anim import stage

common = stage.load_module(Path(__file__).with_name("_common.py"), "ep01_common")
P, merge, mo, Pose, at = common.P, common.merge, common.mo, common.Pose, common.at

CUTS = ["s2c01", "s2c02", "s2c03"]
CS = common.CROW_SCALE


def bezier(p0, p1, p2, p3):
    def fn(t):
        u = 1 - t
        return tuple(u * u * u * a + 3 * u * u * t * b + 3 * u * t * t * c + t * t * t * d
                     for a, b, c, d in zip(p0, p1, p2, p3))
    return fn


def build(ctx) -> dict:
    ep = ctx.episode
    c1, c2, c3 = (ep.cut(i) for i in CUTS)
    r = common.setup(ctx, kai=False, crow=True)
    inu, crow = r.inu, r.crow
    desk = r.room.SPOTS["desk_top"]
    perch = (desk[0] + 0.7, desk[1] + 0.11)      # 机の天板の上（袋の右）
    r.bgfx.draw("desk_items", 1, [])
    r.potechi_on_desk(c1.start)

    # ---------------------------------------------------------------- 犬太朗: ゲーム（s2c03 で一瞬見る）
    inu.rig.swap(c1.start, "controller", "hold")
    mo.game(inu, c1.start, c3.start + 3, seed=3)
    common.blink_every(inu, c1.start, c2.end, every=40, seed=4)

    # ================================================================ s2c01 侵入 → 机にとまる
    f0 = c1.start
    land = f0 + 46
    crow.key(f0, at((12.0, 3.0), CS, flip=True), "CONSTANT")
    mo.flap(crow, f0 + 2, land - 2, bezier((9.5, 2.4), (3.5, 4.2), (-2.0, 3.2), (perch[0], perch[1] + 0.3)),
            scale=CS, flip=True)
    # 着地（羽を広げてブレーキ → たたむ）
    sit = at(perch, CS, flip=True)
    crow.rig.swap(land, "wing", "up")
    crow.key(land, merge(sit, P(body=dict(rot=12, scale=(1.05, 0.92)))), "CONSTANT")
    crow.rig.swap(land + 2, "wing", "default")
    crow.key(land + 4, merge(sit, P(body=dict(rot=-4, scale=(0.97, 1.04)))))
    crow.key(land + 8, sit)
    # 袋を見つける（首をかしげる）
    look = merge(sit, P(head=dict(rot=-14)))
    crow.key(land + 14, look)
    crow.key(c1.end, merge(sit, P(head=dict(rot=-18))))

    # ================================================================ s2c02 くわえて飛び去る
    f0 = c2.start
    crow.key(f0, merge(sit, P(head=dict(rot=-18))), "CONSTANT")
    crow.key(f0 + 6, merge(sit, P(head=dict(rot=6))))            # きょろきょろ
    crow.key(f0 + 10, merge(sit, P(head=dict(rot=-10))))
    # つつく（前にかがむ）
    peck = merge(sit, P(body=dict(rot=-28), head=dict(rot=-12)))
    crow.key(f0 + 14, peck, ease="EASE_IN")
    crow.rig.swap(f0 + 16, "beak", "hold")
    r.potechi_on_desk(f0 + 16, on=False)
    crow.key(f0 + 20, merge(sit, P(body=dict(rot=10), head=dict(rot=10))), "BACK")
    crow.key(f0 + 24, merge(sit, P(body=dict(scale=(1.08, 0.85)))))         # ため
    # 向きを変えて右上へ（窓の方）
    mo.flap(crow, f0 + 26, c2.end, bezier(perch, (perch[0] + 1.0, perch[1] + 1.2),
                                           (-1.0, 1.4), (1.8, 2.6)), scale=CS, flip=False)
    ctx.ones.append((f0 + 14, f0 + 18))

    # ================================================================ s2c03 犬太朗が一瞬見る
    f0 = c3.start
    # カラスが窓から出ていく（画面の奥へ）
    mo.flap(crow, f0, f0 + 14, bezier((0.2, 0.9), (1.8, 1.9), (3.6, 1.8), (5.4, 1.4)),
            scale=CS, flip=False)
    crow.key(f0 + 16, at((30.0, 0.0), CS), "CONSTANT")
    q = common.line(c3, "inutarou")
    look_r = merge(P(**inu.design.MOTION["game"]["pose"]),
                   P(eye_L=dict(loc=(0.13, 0.03)), eye_R=dict(loc=(0.13, 0.03)), head=dict(rot=-7),
                     ear_R=dict(rot=-12), ear_L=dict(rot=6)))
    inu.key(f0 + 4, look_r, "CONSTANT")
    inu.rig.swaps(f0 + 4, {"brow_R": "raised", "brow_L": "angry", "eye_L": "smug", "eye_R": "smug"})
    common.talk(inu, q, open_=("talk",), end_variant="pout", seed=5)
    inu.key(f0 + 30, look_r, "CONSTANT")
    # すぐにゲームへ戻る
    inu.rig.swaps(f0 + 34, {"brow_R": "default", "brow_L": "default", "mouth": "default",
                            "eye_L": "default", "eye_R": "default"})
    mo.game(inu, f0 + 34, c3.end, seed=6, intensity=1.3)

    return {"frame_start": c1.start, "frame_end": c3.end}
