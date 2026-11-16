"""SCENE 6 前半（49〜55秒）: s6c01〜s6c04。仮素材。続きは s6_ending（試作のラスト5秒）。

  s6c01 海斗が財布を出して「しゃーねぇ、買い直しに行くか」。犬太朗はゲーム（手元にカード）。
  s6c02 海斗のアップ。財布をのぞいて「……あれ？ カードは？」
  s6c03 犬太朗の手元のアップ。コントローラーの横に海斗のカード（キラッ）。
  s6c04 海斗のアップ。スマホに通知「ゲーム内アイテム購入 ¥30,000」→「……お前か？」
        最後の姿勢は s6_ending の s6c05 の頭（スマホを胸の前に持つ）に合わせる。
"""
from __future__ import annotations

from pathlib import Path

from inutarou_anim import effects as ef
from inutarou_anim import stage

common = stage.load_module(Path(__file__).with_name("_common.py"), "ep01_common")
P, merge, mo, Pose = common.P, common.merge, common.mo, common.Pose

CUTS = ["s6c01", "s6c02", "s6c03", "s6c04"]


def build(ctx) -> dict:
    ep = ctx.episode
    c1, c2, c3, c4 = (ep.cut(i) for i in CUTS)
    r = common.setup(ctx)
    inu, kai = r.inu, r.kai
    r.bgfx.draw("desk_items", 1, [])
    r.potechi_on_desk(c1.start, on=False)

    # ---------------------------------------------------------------- 犬太朗: カードを持ったままゲーム
    inu.rig.swaps(c1.start, {"controller": "hold", "card": "hold", "eye_L": "smug", "eye_R": "smug"})
    mo.game(inu, c1.start, c4.end, seed=21, intensity=1.2)

    # ================================================================ s6c01 財布を出す
    f0 = c1.start
    q = common.line(c1, "kaito")
    kai.rig.swaps(f0, {"brow_L": "worried", "brow_R": "worried"})
    sigh = P(head=dict(rot=3, loc=(0, -0.03)), eye_L=dict(loc=(-0.03, -0.04)),
             eye_R=dict(loc=(-0.03, -0.04)))
    kai.key(f0, sigh, "CONSTANT")
    common.talk(kai, q, open_=("talk",), seed=22)
    # ひじを曲げて財布を胸の前へ（前腕を起こす）
    hold = merge(sigh, P(arm_L=dict(rot=8), fore_L=dict(rot=118), hand_L=dict(rot=-126)))
    kai.rig.swap(f0 + 10, "hand_L", "wallet")
    kai.key(f0 + 6, merge(sigh, P(arm_L=dict(rot=-10))))
    kai.key(f0 + 14, hold, ease="EASE_OUT")
    kai.key(c1.end, merge(hold, P(head=dict(rot=6, loc=(0, -0.05)))))

    # ================================================================ s6c02 カードがない（アップ）
    f0 = c2.start
    q = common.line(c2, "kaito")
    peek = merge(hold, P(head=dict(rot=8, loc=(-0.02, -0.08)), eye_L=dict(loc=(-0.05, -0.07)),
                         eye_R=dict(loc=(-0.05, -0.07))))
    peek = merge(peek, P(arm_L=dict(rot=16), fore_L=dict(rot=146), hand_L=dict(rot=-162)))
    kai.key(f0, peek, "CONSTANT")
    kai.rig.swaps(f0, {"eye_L": "dot", "eye_R": "dot", "brow_L": "raised", "brow_R": "raised"})
    common.talk(kai, q, open_=("o", "talk"), seed=23, end_variant="wavy")
    kai.key(f0 + 18, merge(peek, P(head=dict(rot=4, loc=(-0.02, -0.05)))))
    kai.key(c2.end, merge(peek, P(head=dict(rot=3, loc=(-0.02, -0.05)))))
    kh = kai.world("head", peek, (0.62, 6.85))
    r.sweat(f0 + 12, c2.end + 1, (kh[0] + 0.1, kh[1]), size=0.15)

    # ================================================================ s6c03 犬太朗の手元にカード
    f0 = c3.start
    game_pose = inu.full(P(**inu.design.MOTION["game"]["pose"]))
    card_c = inu.rig.world("paw_R", game_pose, (0.9, 0.62))
    for d, size in ((4, 0.1), (6, 0.32), (8, 0.26), (10, 0.3), (12, 0.2)):
        r.fx.draw("card_spark", f0 + d, ef.sparkle((card_c[0] + 0.15, card_c[1] + 0.12), size, rot=0.1 * d))
    r.fx.clear("card_spark", f0 + 16)

    # ================================================================ s6c04 課金通知 → お前か？
    f0 = c4.start
    q = common.line(c4, "kaito")
    # s6_ending の s6c05 と同じ持ち方（スマホを胸の前）
    phone = P(arm_L=dict(rot=22), fore_L=dict(rot=72), hand_L=dict(rot=-94), arm_R=dict(rot=4),
              eye_L=dict(loc=(-0.03, -0.06)), eye_R=dict(loc=(-0.03, -0.06)), head=dict(rot=3),
              vein=dict(scale=(0.01, 0.01)))
    kai.rig.swaps(f0, {"hand_L": "phone", "eye_L": "dot", "eye_R": "dot", "brow_L": "default",
                       "brow_R": "default", "mouth": "default"})
    kai.key(f0, phone, "CONSTANT")
    # 通知のアップ（画面の右下に大きく）
    cx, cy = -1.05, 1.55
    pr = r.props
    r.fx.draw("phone", f0, pr.phone_screen(cx, cy - 0.15, 2.9))
    r.fx.draw("notify", f0 + 1, pr.notification(cx, cy + 0.45, 1.42, 0.66))
    t1 = ctx.text("ゲーム内アイテム購入", (cx + 0.15, cy + 0.57), 0.115, color="black", outline="notify_bg",
                  outline_width=0.005, name="t_notify1", depth=-6.0)
    t1.show(f0 + 1, c4.end + 1, pop=False)
    t2 = ctx.text("¥30,000", (cx + 0.15, cy + 0.32), 0.24, color="red", outline="notify_bg",
                  outline_width=0.01, name="t_notify2", depth=-6.0)
    t2.show(f0 + 3, c4.end + 1)
    r.fx.clear("phone", c4.end + 1)
    r.fx.clear("notify", c4.end + 1)
    # 固まる → 犬太朗の方へ目だけ動かして「……お前か？」
    kai.key(f0 + 10, phone, "CONSTANT")
    kai.rig.swaps(q.frame - 3, {"eye_L": "glare", "eye_R": "glare", "brow_L": "angry", "brow_R": "angry"})
    glare = merge(phone, P(eye_L=dict(loc=(0.05, 0)), eye_R=dict(loc=(0.05, 0)), head=dict(rot=-2)))
    kai.key(q.frame - 3, glare, "CONSTANT")
    common.talk(kai, q, open_=("talk",), closed="grit", end_variant="grit", seed=24)
    kai.key(c4.end, glare, "CONSTANT")
    kai.rig.tint(f0, kai.design.FACE_PARTS, "red", 0.0, "CONSTANT")
    kai.rig.tint(c4.end, kai.design.FACE_PARTS, "red", 0.1)

    return {"frame_start": c1.start, "frame_end": c4.end}
