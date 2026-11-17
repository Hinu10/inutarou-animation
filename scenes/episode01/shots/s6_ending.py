"""第1話 ラスト5秒（試作）: s6c05〜s6c09。

  s6c05 海斗が怒りをこらえて犬太朗を見る（震え・青筋・赤面）
  s6c06 犬太朗が無言でグッドサイン → 片目がキラン
  s6c07 一瞬の静寂
  s6c08 海斗「テメェェェ！！！」
  s6c09 アッパー → ほお・口・目・輪郭がぐにゃっと持ち上がる → 止め絵

カットの長さ・カメラ・効果音の位置は cuts.toml から読む。ここに書くのは
「カットの頭から何コマ目に何をするか」だけなので、カットの長さを変えても壊れにくい。
キーは原則 2コマ打ち。インパクト前後だけ 1コマ打ち（ONES）。
"""
from __future__ import annotations

import math
import random

from inutarou_anim import effects as ef
from inutarou_anim import stage
from inutarou_anim.actor import Actor, P, merge
from inutarou_anim.rig import Pose, Rig
from inutarou_anim.shapes import Shape, compose, dent_warp, inflate_warp, rect, transform

CUTS = ["s6c05", "s6c06", "s6c07", "s6c08", "s6c09"]


def build(ctx) -> dict:
    ep = ctx.episode
    c05, c06, c07, c08, c09 = (ep.cut(i) for i in CUTS)
    col = ctx.collection
    room = ctx.background_module("apartment_room")

    # ---------------------------------------------------------------- 背景と効果
    bg = stage.background(col, room.layers(), name="bg_room", depth=10.0)
    bgfx = stage.FX(col, name="bg_fx", depth=5.0)       # 背景の上・キャラの後ろ
    fx = stage.FX(col, name="fx", depth=-2.0)          # キャラの前
    flash = stage.FX(col, name="flash", depth=-4.0)
    # 机の上（カラスが持ち去ったポテチのかけら。SCENE 2 からのつながり）
    dx, dy = room.SPOTS["desk_top"]
    bgfx.draw("desk_items", 1, ctx.props("items").crumbs(dx + 0.1, dy + 0.13, n=6, seed=3))

    # ---------------------------------------------------------------- キャラクター
    inu_d = ctx.design("inutarou")
    kai_d = ctx.design("kaito")
    inu = Actor(Rig(inu_d, col, depth=0.0),
                P(root=Pose(loc=room.SPOTS["sofa_seat"], scale=(1.15, 1.15))))
    kai = Actor(Rig(kai_d, col, depth=-0.5),
                P(root=Pose(loc=room.SPOTS["kaito_stand"], scale=(0.95, 0.95))))

    # ================================================================ s6c05 怒りをこらえる
    f0 = c05.start
    k_base = P(arm_L=dict(rot=22), fore_L=dict(rot=72), hand_L=dict(rot=-94),
               arm_R=dict(rot=4), eye_L=dict(loc=(0.05, 0)), eye_R=dict(loc=(0.05, 0)),
               vein=dict(scale=(0.01, 0.01)))
    kai.rig.swaps(f0, {"eye_L": "glare", "eye_R": "glare", "brow_L": "angry", "brow_R": "angry",
                       "mouth": "grit", "hand_L": "phone", "hand_R": "fist", "vein": "on"})
    kai.rig.tint(f0, kai_d.FACE_PARTS, "red", 0.0)
    kai.rig.tint(c05.end, kai_d.FACE_PARTS, "red", 0.3)
    rnd = random.Random(5)
    for k, f in enumerate(range(f0, c05.end + 1, 2)):
        amp = 1.0 + 0.6 * (f - f0) / c05.frames
        pose = merge(k_base, P(
            spine=dict(rot=rnd.uniform(-0.9, 0.9) * amp),
            head=dict(rot=rnd.uniform(-1.6, 1.6) * amp, loc=(rnd.uniform(-0.02, 0.02), 0)),
            fore_R=dict(rot=rnd.uniform(-3, 3) * amp)))
        if f - f0 >= 6:   # 青筋がポンと出る
            s = {6: 0.3, 8: 1.45, 10: 0.9}.get(f - f0, 1.0 + 0.12 * ((f - f0) // 2 % 2))
            pose["vein"] = Pose(scale=(s, s))
        kai.key(f, pose, "CONSTANT")
    # プルプル線
    for k, f in enumerate(range(f0 + 4, c05.end + 1, 4)):
        c = kai.rig.world("spine", kai.full(k_base), (0, 4.3))
        fx.draw("tremble", f, ef.tremble_lines((c[0] + 0.03 * (k % 2), c[1]), 1.9, 2.4))
    fx.clear("tremble", c06.start)

    i_base = P(eye_L=dict(loc=(-0.05, 0)), eye_R=dict(loc=(-0.05, 0)),
               arm_R=dict(rot=12), paw_R=dict(rot=-20))
    inu.rig.swaps(f0, {"eye_L": "smug", "eye_R": "smug", "mouth": "smug", "card": "hold"})
    inu.key(f0, merge(i_base, P(head=dict(rot=2), tail=dict(rot=-8))))
    inu.key(f0 + 12, merge(i_base, P(head=dict(rot=5), tail=dict(rot=10), body=dict(rot=1))))
    inu.key(c05.end, merge(i_base, P(head=dict(rot=3), tail=dict(rot=-6))))

    # ================================================================ s6c06 グッドサイン → キラン
    f0 = c06.start
    i_close = P(arm_R=dict(rot=12), paw_R=dict(rot=-20))
    # 0: 得意げ（カメラ目線）
    inu.key(f0, merge(i_close, P(head=dict(rot=3), tail=dict(rot=-6))), "CONSTANT")
    inu.key(f0 + 3, merge(i_close, P(head=dict(rot=3), tail=dict(rot=8))))
    # 4〜6: ため（腕を少し沈める）
    inu.key(f0 + 6, merge(i_close, P(head=dict(rot=-2), body=dict(rot=-2, scale=(1.03, 0.97)),
                                     arm_L=dict(rot=18), tail=dict(rot=-6))), ease="EASE_IN")
    inu.rig.swap(f0 + 8, "paw_L", "thumb")
    # 8〜: 腕を振り上げてグッド（行き過ぎ → 戻る）
    up = lambda a, h, s=1.0: merge(i_close, P(
        arm_L=dict(rot=a, scale=(1.0, s)), paw_L=dict(rot=-a), head=dict(rot=h),
        body=dict(rot=2, scale=(0.98, 1.03)), tail=dict(rot=12)))
    inu.key(f0 + 8, up(-95, 6, 1.12))
    inu.key(f0 + 10, up(-138, 9, 1.05))
    inu.key(f0 + 13, up(-122, 7))
    inu.key(f0 + 16, up(-126, 8))
    thumb_pose = up(-126, 8)
    inu.key(c06.end, thumb_pose)
    # キラン（右目の上）
    kiran = next(q for q in c06.cues if q.name == "kiran")
    kf = kiran.frame
    eye = inu.rig.world("eye_R", inu.full(thumb_pose), (0.38 + 0.08, 2.36))
    inu.rig.swap(kf - 1, "eye_R", "spark")
    inu.rig.swap(kf + 4, "eye_R", "smug")
    for k, (d, size) in enumerate(((-1, 0.08), (0, 0.3), (2, 0.24), (4, 0.28), (6, 0.22), (8, 0.25))):
        fx.draw("kiran", kf + d, ef.sparkle(eye, size, rot=0.15 * k))
    fx.clear("kiran", kf + 10)
    t = ctx.text("キラーン♪", (eye[0] + 1.15, eye[1] + 0.55), 0.3, color="yellow", rot=8,
                 name="t_kiran")
    t.show(kf, c06.end + 1)

    # ================================================================ s6c07 静寂（全員止まる）
    f0 = c07.start
    inu.key(f0, thumb_pose, "CONSTANT")
    inu.key(c07.end, thumb_pose, "CONSTANT")
    kai_still = merge(k_base, P(vein=dict(scale=(1.0, 1.0))))
    kai.key(f0, kai_still, "CONSTANT")
    kai.key(c07.end, kai_still, "CONSTANT")
    kai.rig.tint(c07.end, kai_d.FACE_PARTS, "red", 0.3, "CONSTANT")

    # ================================================================ s6c08 テメェェェ！！！
    f0 = c08.start
    line = c08.cues[0]
    burst_f = line.frame
    head_c = kai.rig.world("head", kai.full(kai_still), (0, 6.2))
    # ため
    kai.key(f0, merge(kai_still, P(head=dict(rot=-2, scale=(1.04, 0.94)), spine=dict(rot=1),
                                   hair=dict(scale=(1, 0.95)))), ease="EASE_IN")
    kai.rig.swaps(f0, {"eye_L": "closed", "eye_R": "closed", "mouth": "grit"})
    kai.key(burst_f - 1, merge(kai_still, P(head=dict(rot=-4, scale=(1.08, 0.88), loc=(0, -0.05)),
                                            spine=dict(rot=1.5, scale=(1.02, 0.97)),
                                            hair=dict(scale=(1, 0.9)))), "CONSTANT")
    # 爆発
    kai.rig.swaps(burst_f, {"head": "scream", "eye_L": "rage", "eye_R": "rage", "mouth": "scream",
                            "hand_L": "fist"})
    kai.rig.tint(burst_f - 1, kai_d.FACE_PARTS, "red", 0.3, "CONSTANT")
    kai.rig.tint(burst_f, kai_d.FACE_PARTS, "red", 0.5)
    rnd = random.Random(8)
    for f in range(burst_f, c08.end + 1, 2):
        k = (f - burst_f) / max(1, c08.end - burst_f)
        st = 1.28 - 0.12 * min(1.0, k * 3)
        mouth = 1.1 if (f - burst_f) % 4 == 0 else 0.96
        kai.key(f, merge(kai_still, P(
            head=dict(scale=(1.08, st), rot=rnd.uniform(-2, 2), loc=(0, 0.06)),
            spine=dict(rot=-1.5, scale=(1.0, 1.03)),
            hair=dict(scale=(1.05, 1.18)),
            mouth=dict(scale=(1.0, mouth)),
            vein=dict(scale=(1.35, 1.35)))), "CONSTANT")
    ctx.camera.shake(burst_f, c08.end, 0.09, seed=3, every=1, decay=False)
    for f in range(burst_f, c08.end + 1, 2):
        bgfx.draw("focus", f, [Shape(rect(head_c[0], head_c[1], 12, 8), fill="focus_bg", line=None)]
                  + ef.focus_lines(head_c, 1.05, 5.0, n=110, seed=f))
    bgfx.draw("focus", f0, [Shape(rect(head_c[0], head_c[1], 12, 8), fill="focus_bg", line=None)])
    bgfx.clear("focus", c09.start)
    t = ctx.text("テメェェェ！！！", (head_c[0] - 0.1, head_c[1] + 1.0), 0.46, color="red",
                 outline="black", rot=-4, name="t_teme")
    t.show(burst_f, c09.start)

    # ================================================================ s6c09 アッパー → 止め絵
    f0 = c09.start
    hit = next(q for q in c09.cues if q.name == "bokaa").frame
    swing = next(q for q in c09.cues if q.name == "whoosh").frame
    hit2 = hit + 2
    ctx.ones.append((swing - 1, hit2 + 2))

    kai.rig.swaps(f0, {"head": "default", "eye_L": "rage", "eye_R": "rage", "mouth": "scream",
                       "hand_R": "fist", "hand_L": "fist"})
    kai.rig.tint(f0, kai_d.FACE_PARTS, "red", 0.45, "CONSTANT")
    root0 = room.SPOTS["kaito_stand"]
    k_root = lambda dx, dy=0.0: Pose(loc=(root0[0] + dx, root0[1] + dy), scale=(0.95, 0.95))
    # 0〜: しゃがんで腕を引く（ため）
    crouch = P(root=k_root(0.1), hips=dict(loc=(0, -0.45)), spine=dict(rot=-14),
               head=dict(rot=6), leg_L=dict(rot=-8), leg_R=dict(rot=10),
               arm_R=dict(rot=22), fore_R=dict(rot=-28), arm_L=dict(rot=25), fore_L=dict(rot=40),
               eye_L=dict(loc=(0.06, 0)), eye_R=dict(loc=(0.06, 0)), vein=dict(scale=(1.3, 1.3)))
    kai.key(f0, crouch, "CONSTANT")
    kai.key(swing - 1, merge(crouch, P(hips=dict(loc=(0, -0.55)), arm_R=dict(rot=30),
                                        fore_R=dict(rot=-35))), "CONSTANT")

    # インパクトの位置（犬太朗の左ほお）。顔の変形と拳の位置を同じ点から決める
    # 拳がほおの下からめり込み（dent）、押された肉が上に盛り上がる（inflate）。
    # 頭・顔パーツ（FACE_PARTS）すべてに同じ変形をかけるので、輪郭・ほお・目・口が連動する。
    contact_rest = (-0.7, 1.45)        # 休み姿勢での、あご左下の輪郭上の点
    warps = {hit: compose(dent_warp((-0.8, 1.1), (0.2, 1.0), 0.55, 0.6),
                          inflate_warp((-0.8, 1.9), 0.45, 0.22)),
             hit2: compose(dent_warp((-0.8, 1.05), (0.25, 1.0), 0.62, 0.8),
                           inflate_warp((-0.75, 2.0), 0.5, 0.3))}
    inu_hit = {
        hit: merge(i_close, P(head=dict(rot=-7, loc=(0.06, 0.12), scale=(0.97, 1.06)),
                              body=dict(rot=-4, loc=(0.05, 0.05), scale=(0.97, 1.05)),
                              ear_L=dict(rot=-25), ear_R=dict(rot=-35),
                              arm_L=dict(rot=-70), paw_L=dict(rot=20), arm_R=dict(rot=60),
                              paw_R=dict(rot=-30), leg_L=dict(rot=20, loc=(0, 0.1)),
                              leg_R=dict(rot=35, loc=(0, 0.15)), tail=dict(rot=25))),
        hit2: merge(i_close, P(head=dict(rot=-11, loc=(0.1, 0.22), scale=(0.96, 1.08)),
                               body=dict(rot=-6, loc=(0.08, 0.1), scale=(0.95, 1.08)),
                               ear_L=dict(rot=-40), ear_R=dict(rot=-50),
                               arm_L=dict(rot=-85), paw_L=dict(rot=30), arm_R=dict(rot=80),
                               paw_R=dict(rot=-40), leg_L=dict(rot=28, loc=(0, 0.16)),
                               leg_R=dict(rot=48, loc=(0, 0.22)), tail=dict(rot=40))),
    }

    upper = kai_d.UPPER_LEN * 0.95
    fore = kai_d.FORE_LEN * 0.95
    rest_up = math.degrees(math.atan2(kai_d.ELBOW[1][1] - kai_d.SHOULDER[1][1],
                                      kai_d.ELBOW[1][0] - kai_d.SHOULDER[1][0])) - 90
    rest_fore = math.degrees(math.atan2(kai_d.WRIST[1][1] - kai_d.ELBOW[1][1],
                                        kai_d.WRIST[1][0] - kai_d.ELBOW[1][0])) - 90

    def punch_pose(target, body, up_w, fore_w):
        """前腕の向き fore_w（ワールド角: 上=0・反時計回り+）を決めて、拳を target に当てる。

        アッパーらしい形（上腕は下向き・前腕で突き上げる）を崩さないため、
        高さは上腕の角度で、左右は体の位置（root.x）で合わせる。足は床から浮かせない。
        up_w は上腕の向きの目安（高さが合わないときだけ変わる）。
        """
        pose = kai.full(body)
        parent = kai.rig.fk.world_angle("spine", pose)
        sc_ = pose["arm_R"].scale[1]
        shoulder = kai.rig.world("arm_R", pose, kai_d.SHOULDER[1])
        l1 = upper * sc_
        l2 = (fore + 0.14) * sc_
        c = (target[1] - shoulder[1] - l2 * math.cos(math.radians(fore_w))) / l1
        if -1.0 <= c <= 1.0:
            up_w = -math.degrees(math.acos(c))
        pose["arm_R"] = Pose(rot=up_w - rest_up - parent, scale=pose["arm_R"].scale)
        pose["fore_R"] = Pose(rot=(fore_w - rest_fore) - (up_w - rest_up))
        fist = kai.rig.world("hand_R", pose, (kai_d.WRIST[1][0], kai_d.WRIST[1][1] - 0.14))
        r = pose["root"]
        pose["root"] = Pose(loc=(r.loc[0] + target[0] - fist[0], r.loc[1]), scale=r.scale)
        return pose

    lunge = P(root=k_root(2.05, 0.0), hips=dict(loc=(0, -0.15)), spine=dict(rot=-8),
              head=dict(rot=10, loc=(-0.05, 0)), leg_L=dict(rot=-22), leg_R=dict(rot=18),
              arm_L=dict(rot=40), fore_L=dict(rot=55), eye_L=dict(loc=(0.06, 0.02)),
              eye_R=dict(loc=(0.06, 0.02)), vein=dict(scale=(1.3, 1.3)))
    lunge2 = merge(lunge, P(root=k_root(2.15, 0.1), hips=dict(loc=(0, 0.08)), spine=dict(rot=-4)))
    targets = {}
    arm_angles = {hit: (-150, -40), hit2: (-128, -30)}
    for f, body in ((hit, lunge), (hit2, lunge2)):
        cw = warps[f](contact_rest)
        tgt = inu.rig.world("head", inu.full(inu_hit[f]), (cw[0], cw[1] - 0.2))
        targets[f] = tgt
        kai.key(f, punch_pose(tgt, body, *arm_angles[f]), "CONSTANT")

    # 振り抜き途中（スミア）: 腰の横から拳を振り上げる。左右は ため → インパクト の間
    def swing_pose(t, up_w, fore_w, body):
        pose = kai.full(body)
        parent = kai.rig.fk.world_angle("spine", pose)
        x0 = room.SPOTS["kaito_stand"][0] + 0.1
        x1 = kai.full(punch_pose(targets[hit], lunge, *arm_angles[hit]))["root"].loc[0]
        pose["root"] = k_root(x0 + (x1 - x0) * t - room.SPOTS["kaito_stand"][0])
        pose["arm_R"] = Pose(rot=up_w - rest_up - parent, scale=(1.0, 1.12))
        pose["fore_R"] = Pose(rot=(fore_w - rest_fore) - (up_w - rest_up), scale=(1.0, 1.1))
        return pose

    mid = swing_pose(0.55, -178, -105, merge(lunge, P(hips=dict(loc=(0, -0.45)), spine=dict(rot=-20))))
    kai.key(swing, mid, "CONSTANT")
    kai.key(swing + 1, swing_pose(0.85, -168, -55, merge(lunge, P(hips=dict(loc=(0, -0.3)),
                                                                   spine=dict(rot=-22)))), "CONSTANT")
    kai.key(c09.end, punch_pose(targets[hit2], lunge2, *arm_angles[hit2]), "CONSTANT")
    sh = kai.rig.world("arm_R", kai.full(mid), kai_d.SHOULDER[1])
    fx.draw("swing", swing, ef.motion_arc((sh[0], sh[1]), 1.35, -1.75, -0.55, n=6, seed=2))
    fx.draw("swing", swing + 1, ef.motion_arc((sh[0] + 0.2, sh[1]), 1.45, -1.3, -0.15, n=6, seed=4))
    fx.clear("swing", hit)

    # 犬太朗：振りかぶり中はまだ得意げ → インパクトで顔ごと変形
    inu.key(f0, thumb_pose, "CONSTANT")
    inu.key(hit - 1, thumb_pose, "CONSTANT")
    inu.rig.swap(swing, "eye_L", "default")
    inu.rig.swap(swing, "eye_R", "default")
    inu.rig.swap(swing, "mouth", "open")
    for f in (hit, hit2):
        inu.key(f, inu_hit[f], "CONSTANT")
        variants = {"eye_L": "squeeze", "eye_R": "squeeze", "mouth": "ouch", "paw_L": "default",
                    "card": "default"}
        for part in inu_d.FACE_PARTS:
            v = variants.get(part, "default")
            inu.rig.swap(f, part, v, warp=warps[f])
        inu.rig.swaps(f, {"paw_L": "default", "card": "default"})
    inu.key(c09.end, inu_hit[hit2], "CONSTANT")

    # 効果：フラッシュ・衝撃・汗・飛んでいくカード・止め絵の背景
    W, H = 30, 20
    flash.draw("flash", hit, [Shape(rect(0, 0, W, H), fill="flash", line=None, opacity=0.75)])
    flash.clear("flash", hit + 1)
    ct = targets[hit]
    head_w = inu.rig.world("head", inu.full(inu_hit[hit2]), (0.4, 2.6))
    drops = []
    for k, (dx, dy, r) in enumerate(((0.7, 0.5, -0.6), (1.1, 0.0, -1.2), (0.4, 0.9, -0.2))):
        drops += ef.sweat((head_w[0] + dx, head_w[1] + dy), 0.16, rot=r)
    fx.draw("sweat", hit2, drops)
    card = transform(rect(0, 0, 0.5, 0.32, r=0.04), tx=head_w[0] + 1.6, ty=head_w[1] + 0.3, rot=0.9)
    fx.draw("card", hit, [Shape(transform(card, tx=-0.5, ty=-0.6), fill="card_blue", width=0.035)])
    fx.draw("card", hit2, [Shape(card, fill="card_blue", width=0.035)])
    # 止め絵の背景（部屋 → 放射状の衝撃背景）
    stripes = []
    for k in range(18):
        a0 = 2 * math.pi * k / 18
        stripes.append(Shape([ct, (ct[0] + 20 * math.cos(a0), ct[1] + 20 * math.sin(a0)),
                              (ct[0] + 20 * math.cos(a0 + 0.17), ct[1] + 20 * math.sin(a0 + 0.17))],
                             fill="impact_bg2", line=None))
    bgfx.draw("impact_bg", hit, [Shape(rect(ct[0], ct[1], 40, 30), fill="impact_bg", line=None)]
              + stripes)
    # 衝撃のギザギザはキャラの後ろ（顔の変形が隠れないように）
    bgfx.draw("burst", hit, ef.burst((ct[0] - 0.2, ct[1] - 0.3), 1.4, 0.65, points=13, seed=1,
                                     fill="red"))
    bgfx.draw("burst", hit2, ef.burst((ct[0] - 0.3, ct[1] - 0.3), 1.8, 0.8, points=13, seed=2,
                                      fill="red"))
    ctx.camera.shake(hit, hit2 + 3, 0.18, seed=11, every=1)
    t = ctx.text("ボカァッ！！", (ct[0] - 4.6, ct[1] + 0.4), 0.85, color="white", outline="black",
                 rot=10, name="t_boka")
    t.show(hit)

    return {"frame_start": c05.start, "frame_end": c09.end}
