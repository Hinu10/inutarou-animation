"""SCENE 1（0〜8秒）: s1c01〜s1c02。仮素材。

  s1c01 海斗が机にポテチを置き「ちょっとトイレ行ってくるわ」。犬太朗はソファでゲーム。
  s1c02 犬太朗は無言でゲームを続ける。海斗は左へ歩いて部屋を出る。

テレビはカメラの側（画面のこちら）にある想定。犬太朗は画面の手前を見てゲームをしている。
"""
from __future__ import annotations

from pathlib import Path

from inutarou_anim import stage

common = stage.load_module(Path(__file__).with_name("_common.py"), "ep01_common")
P, merge, mo = common.P, common.merge, common.mo

CUTS = ["s1c01", "s1c02"]


def build(ctx) -> dict:
    ep = ctx.episode
    c1, c2 = (ep.cut(i) for i in CUTS)
    r = common.setup(ctx)
    inu, kai = r.inu, r.kai
    desk = r.room.SPOTS["desk_top"]

    # ---------------------------------------------------------------- 犬太朗: ずっとゲーム
    inu.rig.swap(c1.start, "controller", "hold")
    mo.game(inu, c1.start, c2.end, seed=1)
    common.blink_every(inu, c1.start, c2.end, every=44, seed=2)

    # ================================================================ s1c01 ポテチを置く
    f0 = c1.start
    kai.rig.swap(f0, "hand_L", "potechi")
    stand = P(arm_L=dict(rot=-6), fore_L=dict(rot=10))
    kai.key(f0, stand)
    kai.key(f0 + 8, stand)
    # 机へ手をのばす（体を左へ少し傾ける）
    lean = P(spine=dict(rot=9), head=dict(rot=4), hips=dict(loc=(-0.05, -0.05)))
    put = kai.reach(lean, "arm_L", "fore_L", (desk[0] + 0.25, desk[1] + 0.95), bend=1)
    kai.key(f0 + 16, put, ease="EASE_IN_OUT")
    put_low = kai.reach(merge(lean, P(spine=dict(rot=11))), "arm_L", "fore_L",
                        (desk[0] + 0.2, desk[1] + 0.8), bend=1)
    kai.key(f0 + 20, put_low)
    # 置いた
    kai.rig.swap(f0 + 21, "hand_L", "open")
    r.bgfx.draw("desk_items", 1, [])
    r.potechi_on_desk(f0 + 21)
    kai.key(f0 + 26, merge(put_low, P(spine=dict(rot=8))))
    # 体を戻して、犬太朗の方を見ながら言う
    talk_pose = P(head=dict(rot=-3), eye_L=dict(loc=(0.07, 0)), eye_R=dict(loc=(0.07, 0)),
                  arm_R=dict(rot=-4), arm_L=dict(rot=-4), fore_L=dict(rot=6))
    kai.key(f0 + 32, talk_pose, ease="EASE_OUT")
    q = common.line(c1, "kaito")
    common.talk(kai, q, open_=("talk", "o"), seed=1)
    # 「ちょっと」と軽く手を上げる
    wave = merge(talk_pose, P(arm_R=dict(rot=28), fore_R=dict(rot=70), hand_R=dict(rot=-20)))
    kai.key(q.frame + 4, wave, ease="EASE_OUT")
    kai.key(q.frame + 10, merge(wave, P(fore_R=dict(rot=78))))
    kai.key(c1.end - 10, wave)
    kai.key(c1.end, talk_pose)

    # ================================================================ s1c02 歩いて出ていく
    f0 = c2.start
    kai.key(f0 + 6, talk_pose)
    x0 = r.room.SPOTS["kaito_stand"][0]
    walk_base = P(eye_L=dict(loc=(-0.06, 0)), eye_R=dict(loc=(-0.06, 0)))
    mo.walk(kai, f0 + 10, f0 + 64, x0, -10.5, r.room.SPOTS["kaito_stand"][1], walk_base,
            scale=common.KAI_SCALE, stride=10)
    kai.key(c2.end, merge(walk_base, P(root=dict(loc=(-10.5, r.room.SPOTS["kaito_stand"][1]),
                                                scale=(common.KAI_SCALE, common.KAI_SCALE)))),
            "CONSTANT")
    # 犬太朗は耳だけぴくっと動く（無言）
    for f, a in ((f0 + 20, -12), (f0 + 23, 0)):
        inu.rig.key(f, "ear_L", common.Pose(rot=a))
        inu.rig.key(f, "ear_R", common.Pose(rot=-a))

    return {"frame_start": c1.start, "frame_end": c2.end}
