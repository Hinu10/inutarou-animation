"""SCENE 3（16〜30秒）: s3c01〜s3c06。仮素材。

  s3c01 海斗が戻ってきて「あれ？ ポテチどこいった？」（机にはかけらだけ）
  s3c02 犬太朗「カラスが持ってったぞ」（ゲームをしながら）
  s3c03 海斗のアップ「……お前、食った？」（ジト目）
  s3c04 犬太朗のアップ「は？ 俺じゃねぇし！」（コントローラーを放して怒鳴る）
  s3c05 映像が一時停止 → 超早口ナレーション（暗く沈んだ止め絵に一時停止マークとテロップ）
  s3c06 再開。海斗には「ワン！ワンワン！」としか聞こえていない（きょとん）
"""
from __future__ import annotations

from pathlib import Path

from inutarou_anim import stage
from inutarou_anim.shapes import Shape, rect

common = stage.load_module(Path(__file__).with_name("_common.py"), "ep01_common")
P, merge, mo, Pose = common.P, common.merge, common.mo, common.Pose

CUTS = ["s3c01", "s3c02", "s3c03", "s3c04", "s3c05", "s3c06"]


def build(ctx) -> dict:
    ep = ctx.episode
    c1, c2, c3, c4, c5, c6 = (ep.cut(i) for i in CUTS)
    r = common.setup(ctx)
    inu, kai = r.inu, r.kai
    sx, sy = r.room.SPOTS["kaito_stand"]
    r.bgfx.draw("desk_items", 1, [])
    r.potechi_on_desk(c1.start, on=False)
    game = P(**inu.design.MOTION["game"]["pose"])
    to_kai = P(eye_L=dict(loc=(-0.1, 0.02)), eye_R=dict(loc=(-0.1, 0.02)), head=dict(rot=5))

    # ---------------------------------------------------------------- 犬太朗: s3c01〜s3c03 はゲーム
    inu.rig.swap(c1.start, "controller", "hold")
    mo.game(inu, c1.start, c2.start + 2, seed=7)
    common.blink_every(inu, c1.start, c2.start, every=40, seed=8)

    # ================================================================ s3c01 戻ってくる
    f0 = c1.start
    mo.walk(kai, f0, f0 + 26, -10.0, sx, sy, scale=common.KAI_SCALE, stride=10)
    q = common.line(c1, "kaito")
    # 机を見る
    look_desk = P(head=dict(rot=7), spine=dict(rot=3), eye_L=dict(loc=(-0.07, -0.05)),
                  eye_R=dict(loc=(-0.07, -0.05)))
    kai.key(f0 + 32, look_desk, ease="EASE_OUT")
    kai.rig.swaps(q.frame, {"eye_L": "dot", "eye_R": "dot", "brow_L": "raised", "brow_R": "raised"})
    common.talk(kai, q, open_=("o", "talk"), seed=2)
    # 頭をかしげて部屋を見回す
    kai.key(q.frame + 14, merge(look_desk, P(head=dict(rot=-6), eye_L=dict(loc=(0.05, 0.02)),
                                            eye_R=dict(loc=(0.05, 0.02)))))
    kai.key(c1.end, merge(look_desk, P(head=dict(rot=-8), eye_L=dict(loc=(0.07, 0.0)),
                                       eye_R=dict(loc=(0.07, 0.0)))))

    # ================================================================ s3c02 カラスが持ってったぞ
    f0 = c2.start
    kai_look = P(head=dict(rot=-5), eye_L=dict(loc=(0.07, 0)), eye_R=dict(loc=(0.07, 0)))
    kai.key(f0, kai_look, "CONSTANT")
    kai.rig.swaps(f0, {"eye_L": "default", "eye_R": "default", "brow_L": "default", "brow_R": "default"})
    q = common.line(c2, "inutarou")
    mo.game(inu, f0 + 4, c2.end, pose=to_kai, seed=9, intensity=0.6)
    common.talk(inu, q, open_=("talk", "open"), seed=3)
    # 海斗はだんだん疑いの目に
    kai.rig.swaps(f0 + 40, {"eye_L": "half", "eye_R": "half"})
    kai.key(f0 + 40, kai_look)
    kai.key(c2.end, merge(kai_look, P(head=dict(rot=-8, loc=(0.03, 0)))))

    # ================================================================ s3c03 お前、食った？（アップ）
    f0 = c3.start
    sus = P(head=dict(rot=-9, loc=(0.04, -0.02)), spine=dict(rot=-3),
            eye_L=dict(loc=(0.08, -0.01)), eye_R=dict(loc=(0.08, -0.01)))
    kai.key(f0, merge(kai_look, P(head=dict(rot=-8, loc=(0.03, 0)))), "CONSTANT")
    kai.key(f0 + 8, sus, ease="EASE_IN_OUT")
    q = common.line(c3, "kaito")
    common.talk(kai, q, open_=("talk",), seed=4, end_variant="default")
    kai.key(c3.end - 6, merge(sus, P(head=dict(rot=-11, loc=(0.06, -0.03)))))
    kai.key(c3.end, merge(sus, P(head=dict(rot=-11, loc=(0.06, -0.03)))))
    # 犬太朗はカメラ外でゲーム（姿勢だけ合わせておく）
    mo.game(inu, f0, c3.end, pose=P(eye_L=dict(loc=(0, -0.06)), eye_R=dict(loc=(0, -0.06))), seed=10)

    # ================================================================ s3c04 俺じゃねぇし！（アップ）
    f0 = c4.start
    q = common.line(c4, "inutarou")
    # 0〜: 一瞬かたまって目が点
    inu.key(f0, merge(game, to_kai), "CONSTANT")
    inu.rig.swaps(f0, {"eye_L": "wide", "eye_R": "wide", "mouth": "default"})
    # コントローラーを放して身を乗り出す
    angry = P(head=dict(rot=6, loc=(-0.05, 0.05), scale=(1.04, 1.04)), body=dict(rot=4),
              arm_L=dict(rot=-40), paw_L=dict(rot=20), arm_R=dict(rot=50), paw_R=dict(rot=-20),
              ear_L=dict(rot=12), ear_R=dict(rot=-12), tail=dict(rot=18),
              eye_L=dict(loc=(-0.08, 0)), eye_R=dict(loc=(-0.08, 0)))
    inu.rig.swap(q.frame, "controller", "default")
    inu.rig.swaps(q.frame, {"eye_L": "angry", "eye_R": "angry", "brow_L": "angry", "brow_R": "angry"})
    inu.key(q.frame - 1, merge(game, to_kai, P(body=dict(rot=-2, scale=(1.03, 0.97)))), "CONSTANT")
    inu.key(q.frame + 1, merge(angry, P(head=dict(rot=9, loc=(-0.08, 0.1), scale=(1.07, 1.07)))))
    inu.key(q.frame + 5, angry)
    end = common.talk(inu, q, open_=("shout", "talk"), seed=5, end_variant="shout")
    for k, f in enumerate(range(q.frame + 6, c4.end + 1, 4)):
        inu.key(f, merge(angry, P(head=dict(rot=6 + (2 if k % 2 else -1)))), "CONSTANT")
    still = merge(angry, P(head=dict(rot=7, loc=(-0.05, 0.06), scale=(1.05, 1.05))))
    inu.key(c4.end, still, "CONSTANT")
    inu.rig.swap(c4.end, "mouth", "shout")
    ctx.ones.append((q.frame - 1, q.frame + 2))

    # ================================================================ s3c05 一時停止 → 超早口ナレーション
    f0 = c5.start
    inu.hold(f0, c5.end, still)
    W, H = 30, 20
    cam_c = (1.9, 1.05)
    r.over.draw("pause_tint", f0, [Shape(rect(0, 0, W, H), fill="pause_tint", line=None)])
    r.over.clear("pause_tint", c6.start)
    # 一時停止マーク（左上）
    px, py = cam_c[0] - 1.75, cam_c[1] + 0.85
    r.over.draw("pause_icon", f0, [Shape(rect(px - 0.11, py, 0.14, 0.48, r=0.03), fill="white", width=0.03),
                                   Shape(rect(px + 0.11, py, 0.14, 0.48, r=0.03), fill="white", width=0.03)])
    r.over.clear("pause_icon", c6.start)
    q = common.line(c5, "narration")
    # 帯テロップ（画面下）
    band_y = cam_c[1] - 0.95
    r.over.draw("band", q.frame, [Shape(rect(cam_c[0], band_y, 5.2, 0.62), fill="yellow", width=0.04)])
    r.over.clear("band", c6.start)
    t1 = ctx.text("ここで忠告！", (cam_c[0] + 1.05, cam_c[1] + 0.82), 0.36, color="red", outline="white",
                  rot=6, name="t_chuukoku", depth=-6.0)
    t1.show(q.frame, c6.start)
    t2 = ctx.text("犬太朗の言葉は人間には鳴き声としてしか伝わりません！", (cam_c[0], band_y), 0.17,
                  color="black", outline="yellow", outline_width=0.01, name="t_narr", depth=-6.0)
    t2.show(q.frame + 3, c6.start, pop=False)

    # ================================================================ s3c06 再開（海斗には鳴き声）
    f0 = c6.start
    # 犬太朗はまだ怒鳴っている → 吠え声に見える
    for k, f in enumerate(range(f0, f0 + 22, 4)):
        inu.rig.swap(f, "mouth", "shout" if k % 2 == 0 else "talk")
        inu.key(f, merge(angry, P(head=dict(rot=6 + (3 if k % 2 else -2)))), "CONSTANT")
    inu.rig.swap(f0 + 22, "mouth", "pout")
    inu.key(f0 + 24, merge(angry, P(head=dict(rot=3), arm_L=dict(rot=-10), arm_R=dict(rot=10),
                                    paw_L=dict(rot=0), paw_R=dict(rot=0))))
    inu.key(c6.end, merge(angry, P(head=dict(rot=2), arm_L=dict(rot=-8), arm_R=dict(rot=8),
                                   paw_L=dict(rot=0), paw_R=dict(rot=0))))
    head = inu.world("head", angry, (0.0, 2.9))
    r.bark("ワン！", (head[0] - 1.1, head[1] + 0.3), f0, f0 + 24, size=0.5, rot=10)
    r.bark("ワンワン！", (head[0] + 1.3, head[1] + 0.1), f0 + 6, f0 + 26, size=0.42, rot=-8)
    r.bark("ワン！", (head[0] - 0.4, head[1] + 1.0), f0 + 12, f0 + 28, size=0.38, rot=4)
    # 海斗: きょとん
    kai.rig.swaps(f0, {"eye_L": "dot", "eye_R": "dot", "brow_L": "raised", "brow_R": "raised",
                       "mouth": "default"})
    blank = merge(kai_look, P(head=dict(rot=-4)))
    kai.key(f0, blank, "CONSTANT")
    kai.key(f0 + 26, blank)
    kai.key(f0 + 34, merge(blank, P(head=dict(rot=-12))), ease="EASE_OUT")   # 首をかしげる
    kai.key(c6.end, merge(blank, P(head=dict(rot=-13))))
    kh = kai.world("head", blank, (0.55, 7.0))
    r.mark("？", (kh[0] + 0.35, kh[1] + 0.45), f0 + 30, c6.end + 1, size=0.7, rot=-10)

    return {"frame_start": c1.start, "frame_end": c6.end}
