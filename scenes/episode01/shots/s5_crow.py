"""SCENE 5（41〜49秒）: s5c01〜s5c03。仮素材。

  s5c01 窓の外にポテチの袋をくわえたカラスが飛んできて、窓枠で小躍りする（あおり）。
  s5c02 海斗が窓を見て「……あ、カラスか」→ 頭をかいて「悪かったな」。犬太朗は腕組みでジト目。
  s5c03 犬太朗のアップ「ったく、ふざけんなよ」→ そっぽを向いてゲームに戻る。

カラスは「背景（depth 10）」と「窓の手前の枠（depth 9）」の間（depth 9.5）に置いて、
ガラスの向こうにいるように見せる。
"""
from __future__ import annotations

from pathlib import Path

from inutarou_anim import stage

common = stage.load_module(Path(__file__).with_name("_common.py"), "ep01_common")
P, merge, mo, Pose, at = common.P, common.merge, common.mo, common.Pose, common.at

CUTS = ["s5c01", "s5c02", "s5c03"]


def build(ctx) -> dict:
    ep = ctx.episode
    c1, c2, c3 = (ep.cut(i) for i in CUTS)
    r = common.setup(ctx, crow=True, crow_depth=9.5)
    inu, kai, crow = r.inu, r.kai, r.crow
    win = stage.FX(ctx.collection, name="window_front", depth=9.0)
    win.draw("frame", 1, r.room.window_front())
    r.bgfx.draw("desk_items", 1, [])
    r.potechi_on_desk(c1.start, on=False)
    sill = r.room.SPOTS["window_sill_out"]
    S = 0.7

    # ================================================================ s5c01 カラスが窓の外に来る
    f0 = c1.start
    crow.rig.swap(f0, "beak", "hold")
    land = f0 + 18
    wings = ("up", "default", "down", "default")
    for k, f in enumerate(range(f0, land, 2)):
        t = (f - f0) / (land - f0)
        s = 0.22 + (S - 0.22) * t * t
        x = 4.9 + (sill[0] - 4.9) * t
        y = 1.9 + (sill[1] + 0.25 - 1.9) * t
        crow.rig.swap(f, "wing", wings[k % 4])
        crow.key(f, merge(at((x, y), s, flip=True), P(legs=dict(rot=-20, scale=(1, 0.7)))), "CONSTANT")
    perch = at(sill, S, flip=True)
    crow.rig.swap(land, "wing", "up")
    crow.key(land, merge(perch, P(body=dict(scale=(1.06, 0.9)))), "CONSTANT")
    crow.rig.swap(land + 2, "wing", "default")
    crow.key(land + 4, perch)
    # 小躍り（左右に跳ねて、袋を見せびらかす）
    def taunt(start, end, seed=0):
        for k, f in enumerate(range(start, end, 4)):
            hop = k % 2 == 0
            p = merge(at((sill[0] + (0.06 if k % 4 < 2 else -0.06), sill[1] + (0.12 if hop else 0.0)), S,
                         flip=True),
                      P(body=dict(rot=8 if hop else -6), head=dict(rot=-12 if hop else 10),
                        tail=dict(rot=14 if hop else -8)))
            crow.key(f, p, "CONSTANT")
            crow.rig.swap(f, "wing", "up" if k % 4 == 0 else "default")
    taunt(land + 10, c2.end + 1)

    # 部屋の中の2人（このカットでは見えないが、姿勢をそろえておく）
    kai.rig.swaps(c1.start, {"eye_L": "half", "eye_R": "half"})
    inu.rig.swaps(c1.start, {"eye_L": "smug", "eye_R": "smug", "brow_L": "angry", "brow_R": "angry",
                             "mouth": "pout"})
    fold = P(arm_L=dict(rot=48), paw_L=dict(rot=-30), arm_R=dict(rot=-48), paw_R=dict(rot=30),
             eye_L=dict(loc=(-0.08, 0)), eye_R=dict(loc=(-0.08, 0)), head=dict(rot=-4))
    inu.key(c1.start, fold, "CONSTANT")
    kai_look = P(head=dict(rot=-5), eye_L=dict(loc=(0.07, 0)), eye_R=dict(loc=(0.07, 0)))
    kai.key(c1.start, kai_look, "CONSTANT")

    # ================================================================ s5c02 あ、カラスか → 悪かったな
    f0 = c2.start
    q1 = common.line(c2, "kaito", 0)
    q2 = common.line(c2, "kaito", 1)
    to_win = P(head=dict(rot=-10), eye_L=dict(loc=(0.1, 0.06)), eye_R=dict(loc=(0.1, 0.06)))
    kai.key(f0, kai_look, "CONSTANT")
    kai.key(f0 + 4, to_win, ease="EASE_OUT")
    kai.rig.swaps(q1.frame, {"eye_L": "dot", "eye_R": "dot", "brow_L": "raised", "brow_R": "raised"})
    common.talk(kai, q1, open_=("o",), seed=15)
    kai.key(q2.frame - 8, to_win)
    # 頭をかいて謝る（左手を頭の後ろへ）
    sorry = P(head=dict(rot=-4, loc=(0, -0.03)), eye_L=dict(loc=(0.06, 0)), eye_R=dict(loc=(0.06, 0)),
              spine=dict(rot=2))
    hd = kai.world("head", sorry, (-0.62, 6.7))
    sorry = kai.reach(sorry, "arm_L", "fore_L", hd, bend=1)
    sorry["hand_L"] = Pose(rot=150)
    kai.key(q2.frame - 2, sorry, ease="EASE_OUT")
    kai.rig.swaps(q2.frame - 2, {"eye_L": "closed", "eye_R": "closed", "brow_L": "worried",
                                 "brow_R": "worried"})
    common.talk(kai, q2, open_=("talk",), end_variant="smile", seed=16)
    for k, f in enumerate(range(q2.frame + 2, c2.end, 4)):   # ぽりぽり
        kai.key(f, merge(sorry, P(fore_L=dict(rot=sorry["fore_L"].rot + (8 if k % 2 else 0)))),
                "CONSTANT")
    kai.key(c2.end, sorry, "CONSTANT")
    # 犬太朗: 窓をちらっと見て → 海斗をジト目で見る
    inu.key(f0, fold, "CONSTANT")
    inu.key(f0 + 8, merge(fold, P(eye_L=dict(loc=(0.1, 0.05)), eye_R=dict(loc=(0.1, 0.05)),
                                  head=dict(rot=-6))))
    inu.key(q2.frame - 4, merge(fold, P(eye_L=dict(loc=(-0.1, 0)), eye_R=dict(loc=(-0.1, 0)),
                                        head=dict(rot=3))))
    inu.key(c2.end, merge(fold, P(eye_L=dict(loc=(-0.1, 0)), eye_R=dict(loc=(-0.1, 0)),
                                  head=dict(rot=5))))

    # ================================================================ s5c03 ったく、ふざけんなよ
    f0 = c3.start
    q = common.line(c3, "inutarou")
    away = merge(fold, P(head=dict(rot=-8, loc=(0.03, 0)), eye_L=dict(loc=(0.11, -0.02)),
                         eye_R=dict(loc=(0.11, -0.02)), ear_L=dict(rot=-6), ear_R=dict(rot=-10)))
    inu.key(f0, merge(fold, P(head=dict(rot=5))), "CONSTANT")
    inu.key(f0 + 4, away, ease="EASE_OUT")
    common.talk(inu, q, open_=("talk",), closed="pout", end_variant="pout", seed=17)
    inu.key(f0 + 26, away)
    # コントローラーを拾ってゲームに戻る
    inu.rig.swap(f0 + 30, "controller", "hold")
    inu.rig.swaps(f0 + 30, {"brow_L": "default", "brow_R": "default", "eye_L": "smug", "eye_R": "smug"})
    mo.game(inu, f0 + 30, c3.end, pose=P(eye_L=dict(loc=(0, -0.06)), eye_R=dict(loc=(0, -0.06))),
            seed=18, intensity=1.4)
    kai.key(c3.end, sorry, "CONSTANT")

    return {"frame_start": c1.start, "frame_end": c3.end}
