"""SCENE 4（30〜41秒）: s4c01〜s4c03。仮素材。

  s4c01 犬太朗が窓を指さして「だからカラスだって！ あっちだよ！」（海斗は窓を見ない）
  s4c02 海斗のアップ「何そんな吠えてんだよ」（画面外から「ワン！」が飛んでくる・耳をふさぐ）
  s4c03 犬太朗がソファの上で地団駄「話通じねぇなこいつ！」／海斗は肩をすくめて呆れる
"""
from __future__ import annotations

from pathlib import Path

from inutarou_anim import stage

common = stage.load_module(Path(__file__).with_name("_common.py"), "ep01_common")
P, merge, mo, Pose = common.P, common.merge, common.mo, common.Pose

CUTS = ["s4c01", "s4c02", "s4c03"]


def build(ctx) -> dict:
    ep = ctx.episode
    c1, c2, c3 = (ep.cut(i) for i in CUTS)
    r = common.setup(ctx)
    inu, kai = r.inu, r.kai
    r.bgfx.draw("desk_items", 1, [])
    r.potechi_on_desk(c1.start, on=False)

    angry_face = {"eye_L": "angry", "eye_R": "angry", "brow_L": "angry", "brow_R": "angry"}
    inu.rig.swaps(c1.start, angry_face)
    kai.rig.swaps(c1.start, {"eye_L": "half", "eye_R": "half"})
    kai_look = P(head=dict(rot=-5), eye_L=dict(loc=(0.07, 0)), eye_R=dict(loc=(0.07, 0)))

    # ================================================================ s4c01 窓を指さす
    f0 = c1.start
    q = common.line(c1, "inutarou")
    sit = P(arm_L=dict(rot=-8), arm_R=dict(rot=8), eye_L=dict(loc=(-0.08, 0)), eye_R=dict(loc=(-0.08, 0)),
            head=dict(rot=4))
    inu.key(f0, sit, "CONSTANT")
    # ため → 指さし（行き過ぎて戻る）
    inu.key(f0 + 4, merge(sit, P(arm_R=dict(rot=-10), body=dict(rot=3))), ease="EASE_IN")
    inu.rig.swap(f0 + 6, "paw_R", "point")
    point = lambda a, h=-4, ex=0.1: P(arm_R=dict(rot=a), paw_R=dict(rot=0), arm_L=dict(rot=-20),
                                       paw_L=dict(rot=10), body=dict(rot=-4), head=dict(rot=h),
                                       eye_L=dict(loc=(ex, 0.05)), eye_R=dict(loc=(ex, 0.05)),
                                       ear_L=dict(rot=8), ear_R=dict(rot=-8), tail=dict(rot=15))
    inu.key(f0 + 6, point(125))
    inu.key(f0 + 9, point(108))
    inu.key(f0 + 12, point(114))
    end = common.talk(inu, q, open_=("shout", "talk"), seed=11, end_variant="shout")
    # しゃべりながら「あっち！あっち！」と腕を突き出す（海斗の方を見たり窓を見たり）
    for k, f in enumerate(range(f0 + 16, min(end + 12, c1.end - 4), 6)):
        look_kai = k % 3 == 1
        inu.key(f, point(116 if k % 2 else 106, h=4 if look_kai else -4,
                         ex=-0.09 if look_kai else 0.1), "CONSTANT")
    inu.key(c1.end, point(112), "CONSTANT")
    # 海斗は犬太朗だけを見ている（窓は見ない）
    kai.key(f0, kai_look, "CONSTANT")
    kai.key(f0 + 40, merge(kai_look, P(head=dict(rot=-7))))
    kai.key(c1.end, merge(kai_look, P(head=dict(rot=-8, loc=(0.02, 0)))))
    common.blink_every(kai, f0, c1.end, every=40, seed=12, open_="half")

    # ================================================================ s4c02 何そんな吠えてんだよ（アップ）
    f0 = c2.start
    q = common.line(c2, "kaito")
    annoyed = merge(kai_look, P(head=dict(rot=6, loc=(-0.03, 0)), spine=dict(rot=2)))
    kai.key(f0, merge(kai_look, P(head=dict(rot=-8))), "CONSTANT")
    kai.rig.swaps(f0, {"eye_L": "closed", "eye_R": "closed", "brow_L": "worried", "brow_R": "worried",
                       "mouth": "wavy"})
    # 右手（画面右＝犬太朗の側）で耳をふさぐ
    ear = kai.world("head", annoyed, (0.72, 6.15))
    cover = kai.reach(annoyed, "arm_R", "fore_R", (ear[0] + 0.3, ear[1] - 0.25), bend=-1)
    kai.key(f0 + 4, cover, ease="EASE_OUT")
    kai.key(q.frame - 2, cover)
    kai.rig.swaps(q.frame, {"eye_L": "half", "eye_R": "half", "brow_L": "default", "brow_R": "default"})
    common.talk(kai, q, open_=("talk",), seed=13, end_variant="wavy")
    kai.key(q.frame + 6, merge(cover, P(head=dict(rot=-4))))
    kai.key(c2.end, merge(cover, P(head=dict(rot=-6))))
    # 画面の外（右）から吠え声が飛んでくる
    for k, (f, txt, y, rot) in enumerate(((f0, "ワン！", 2.6, 12), (f0 + 5, "ワンワン！", 1.5, -6),
                                         (f0 + 10, "ワン！", 2.0, 8), (q.frame + 22, "ワオーン！", 2.75, -4))):
        r.bark(txt, (-0.75 - 0.15 * (k % 2), y), f, min(f + 18, c2.end + 1), size=0.36, rot=rot,
               name=f"t_bark{k}")
    r.sweat(q.frame + 4, c2.end + 1, (ear[0] + 0.15, ear[1] + 0.7), size=0.16)
    # 犬太朗（画面外）: 吠え続けている
    inu.key(f0, point(112), "CONSTANT")

    # ================================================================ s4c03 地団駄 ／ 呆れる
    f0 = c3.start
    q = common.line(c3, "inutarou")
    inu.rig.swaps(f0, {"paw_R": "default"})
    flail = lambda k: P(arm_L=dict(rot=-130 if k % 2 else -95), paw_L=dict(rot=0),
                        arm_R=dict(rot=95 if k % 2 else 130), paw_R=dict(rot=0),
                        head=dict(rot=5 if k % 2 else -5), ear_L=dict(rot=15), ear_R=dict(rot=-15),
                        tail=dict(rot=25 if k % 2 else -10), eye_L=dict(loc=(-0.06, 0)),
                        eye_R=dict(loc=(-0.06, 0)))
    seat = r.inu_seat()["root"]
    for k, f in enumerate(range(f0, f0 + 64, 4)):
        up = k % 2 == 0
        root = Pose(loc=(seat.loc[0], seat.loc[1] + (0.35 if up else 0.0)),
                    scale=(seat.scale[0] * (0.96 if up else 1.06), seat.scale[1] * (1.05 if up else 0.93)))
        inu.key(f, merge(flail(k), {"root": root}), "CONSTANT")
    common.talk(inu, q, open_=("shout",), closed="talk", seed=14, end_variant="pout")
    calm = P(arm_L=dict(rot=-6), arm_R=dict(rot=6), head=dict(rot=-6), eye_L=dict(loc=(-0.06, 0)),
             eye_R=dict(loc=(-0.06, 0)), body=dict(rot=-2))
    inu.key(f0 + 66, merge(calm, P(body=dict(scale=(1.05, 0.95)))), "CONSTANT")
    inu.key(f0 + 72, calm)
    inu.key(c3.end, merge(calm, P(head=dict(rot=-8))))
    # 海斗: 肩をすくめて首を振る
    kai.rig.swaps(f0, {"eye_L": "half", "eye_R": "half", "mouth": "default", "brow_L": "default",
                       "brow_R": "default"})
    kai.key(f0, kai_look, "CONSTANT")
    kai.rig.swaps(f0 + 30, {"eye_L": "closed", "eye_R": "closed", "brow_L": "worried",
                            "brow_R": "worried", "mouth": "wavy"})
    shrug = P(spine=dict(scale=(1.0, 1.02)), head=dict(loc=(0, -0.08)))
    hx, hy = kai.world("spine", shrug, (0, 4.5))
    shrug = kai.reach(shrug, "arm_L", "fore_L", (hx - 1.35, hy - 0.2), bend=-1)
    shrug = kai.reach(shrug, "arm_R", "fore_R", (hx + 1.35, hy - 0.2), bend=1)
    shrug["hand_L"] = Pose(rot=-60)
    shrug["hand_R"] = Pose(rot=60)
    kai.key(f0 + 28, kai_look)
    kai.key(f0 + 34, shrug, ease="EASE_OUT")
    for k, f in enumerate(range(f0 + 40, f0 + 70, 6)):
        kai.key(f, merge(shrug, P(head=dict(rot=6 if k % 2 else -6, loc=(0, -0.08)))))
    kai.key(c3.end, merge(shrug, P(head=dict(rot=0, loc=(0, -0.08)))))
    kh = kai.world("head", shrug, (0.6, 6.9))
    r.sweat(f0 + 40, c3.end + 1, (kh[0] + 0.15, kh[1]), size=0.2)

    return {"frame_start": c1.start, "frame_end": c3.end}
