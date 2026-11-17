"""犬太朗 — 仮デザイン（TEMP）。正式デザインではない。

柴犬ふうの仮の見た目。座った姿勢が基本（原点 = お尻の接地点、1単位 ≒ 頭の半分）。
L / R は「画面の左 / 右」。犬太朗から見た左右ではない。

差し替えるときは BONES の名前と PARTS の名前・variant 名を保ったまま形だけ変える
（docs/production/asset-replacement.md を参照）。
"""
from inutarou_anim.skeleton import Bone, Part
from inutarou_anim.shapes import Shape, blob, capsule, curve, ellipse, rect, transform

NAME = "inutarou"
TEMP = True
VERSION = "temp-0.1"

W = 0.055  # 主線の太さ

BONES = [
    Bone("root", None, (0.0, 0.0)),
    Bone("body", "root", (0.0, 0.15)),
    Bone("tail", "body", (0.6, 0.35)),
    Bone("leg_L", "body", (-0.38, 0.2)),
    Bone("leg_R", "body", (0.38, 0.2)),
    Bone("head", "body", (0.0, 1.35)),
    Bone("ear_L", "head", (-0.6, 2.75)),
    Bone("ear_R", "head", (0.6, 2.75)),
    Bone("cheek_L", "head", (-0.55, 1.8)),
    Bone("cheek_R", "head", (0.55, 1.8)),
    Bone("eye_L", "head", (-0.38, 2.25)),
    Bone("eye_R", "head", (0.38, 2.25)),
    Bone("brow_L", "head", (-0.4, 2.55)),
    Bone("brow_R", "head", (0.4, 2.55)),
    Bone("mouth", "head", (0.0, 1.78)),
    Bone("arm_L", "body", (-0.62, 1.05)),
    Bone("paw_L", "arm_L", (-0.8, 0.42)),
    Bone("arm_R", "body", (0.62, 1.05)),
    Bone("paw_R", "arm_R", (0.8, 0.42)),
]


# ---------------------------------------------------------------- 形
def _head():
    pts = blob([(0, 2.92), (0.55, 2.85), (0.95, 2.45), (1.05, 2.0), (0.88, 1.6), (0.45, 1.4),
                (0, 1.36), (-0.45, 1.4), (-0.88, 1.6), (-1.05, 2.0), (-0.95, 2.45), (-0.55, 2.85)])
    return [Shape(pts, fill="dog_fur", width=W)]


def _face_white():
    pts = blob([(0, 2.1), (0.35, 2.05), (0.7, 1.92), (0.94, 1.72), (0.8, 1.52), (0.42, 1.43),
                (0, 1.4), (-0.42, 1.43), (-0.8, 1.52), (-0.94, 1.72), (-0.7, 1.92), (-0.35, 2.05)])
    return [Shape(pts, fill="dog_white", line=None)]


def _cheek(side):
    x = 0.55 * side
    return [Shape(ellipse(x, 1.74, 0.36, 0.27), fill="dog_white", line=None),
            Shape(curve([(x - 0.18 * side, 1.62), (x + 0.05 * side, 1.58), (x + 0.25 * side, 1.66)]),
                  line="dog_fur_dark", width=0.03, closed=False, taper=1.0)]


def _muzzle():
    return [Shape(ellipse(0, 1.8, 0.36, 0.25), fill="dog_white", width=0.035)]


def _nose():
    return [Shape(blob([(-0.15, 1.98), (0, 2.0), (0.15, 1.98), (0.08, 1.88), (0, 1.86),
                        (-0.08, 1.88)]), fill="dog_nose", line="dog_nose", width=0.02),
            Shape(ellipse(-0.05, 1.96, 0.04, 0.02), fill="white", line=None)]


def _ear(side):
    s = side
    outer = blob([(0.98 * s, 2.5), (0.92 * s, 3.05), (0.8 * s, 3.45), (0.58 * s, 3.15),
                  (0.28 * s, 2.82)], samples=6)
    inner = blob([(0.86 * s, 2.62), (0.82 * s, 3.0), (0.77 * s, 3.25), (0.6 * s, 3.02),
                  (0.42 * s, 2.82)], samples=6)
    return [Shape(outer, fill="dog_fur", width=W), Shape(inner, fill="dog_inner_ear", line=None)]


def _eye_open(side, big_highlight=False):
    x = 0.38 * side
    hl = 0.06 if big_highlight else 0.04
    return [Shape(ellipse(x, 2.25, 0.12, 0.16), fill="black", line="black", width=0.02),
            Shape(ellipse(x - 0.04, 2.31, hl, hl), fill="white", line=None)]


def _eye_smug(side):
    """半目（得意げ）。"""
    x = 0.38 * side
    lower = ellipse(x, 2.25, 0.12, 0.16, n=24, start=3.35, end=6.07)
    return [Shape(lower, fill="black", line="black", width=0.02),
            Shape(curve([(x - 0.2, 2.22), (x, 2.27), (x + 0.2, 2.23)]), line="line", width=0.06,
                  closed=False, taper=1.0)]


def _eye_closed(side):
    x = 0.38 * side
    return [Shape(curve([(x - 0.15, 2.22), (x, 2.3), (x + 0.15, 2.22)]), line="black", width=0.06,
                  closed=False, taper=1.0)]


def _eye_squeeze(side):
    """ぎゅっとつぶった目（> <）。"""
    x = 0.38 * side
    d = -side
    return [Shape([(x - 0.14 * d, 2.36), (x + 0.12 * d, 2.25), (x - 0.14 * d, 2.13)], line="black",
                  width=0.06, closed=False, taper=0.6)]


def _brow(side, raised=False):
    x = 0.4 * side
    y = 2.6 if raised else 2.55
    return [Shape(ellipse(x, y, 0.1, 0.06, rot=0.25 * side), fill="dog_fur_dark", line=None)]


def _brow_angry(side):
    """怒り眉（内側が下がる）。"""
    return [Shape(ellipse(0.36 * side, 2.5, 0.15, 0.055, rot=0.6 * side), fill="dog_fur_dark",
                  line=None)]


def _eye_angry(side):
    """怒った目（内側が下がったまぶたで上が切れる）。"""
    x = 0.38 * side
    lower = ellipse(x, 2.23, 0.13, 0.15, n=24, start=3.3, end=6.12)
    lid = [(x + 0.2 * side, 2.33), (x - 0.18 * side, 2.2)]
    return [Shape(lower + [(x - 0.12 * side, 2.24)], fill="black", line="black", width=0.02),
            Shape(lid, line="line", width=0.07, closed=False, taper=0.6)]


def _eye_wide(side):
    """驚き・あわて（白目に小さい黒目）。"""
    x = 0.38 * side
    return [Shape(ellipse(x, 2.26, 0.17, 0.2), fill="white", line="black", width=0.04),
            Shape(ellipse(x, 2.24, 0.07, 0.09), fill="black", line=None),
            Shape(ellipse(x - 0.02, 2.27, 0.025, 0.025), fill="white", line=None)]


def _mouth_default():
    return [Shape(curve([(0, 1.88), (0, 1.8)]), width=0.035, closed=False),
            Shape(curve([(-0.26, 1.8), (-0.13, 1.7), (0, 1.8)]), width=0.035, closed=False, taper=0.5),
            Shape(curve([(0, 1.8), (0.13, 1.7), (0.26, 1.8)]), width=0.035, closed=False, taper=0.5)]


def _mouth_smug():
    return [Shape(curve([(0, 1.88), (0, 1.79)]), width=0.035, closed=False),
            Shape(curve([(-0.24, 1.76), (-0.08, 1.72), (0.12, 1.76), (0.3, 1.88)]), width=0.04,
                  closed=False, taper=0.6),
            Shape(curve([(0.27, 1.92), (0.32, 1.86), (0.3, 1.8)]), width=0.03, closed=False, taper=1.0)]


def _mouth_open():
    m = blob([(-0.2, 1.8), (0, 1.76), (0.2, 1.8), (0.12, 1.6), (-0.12, 1.6)], samples=6)
    return [Shape(curve([(0, 1.88), (0, 1.8)]), width=0.035, closed=False),
            Shape(m, fill="dog_mouth", width=0.035),
            Shape(ellipse(0, 1.64, 0.09, 0.05), fill="dog_tongue", line=None)]


def _mouth_talk():
    """しゃべる口（小さく開く）。"""
    m = blob([(-0.16, 1.8), (0, 1.77), (0.16, 1.8), (0.09, 1.67), (-0.09, 1.67)], samples=6)
    return [Shape(curve([(0, 1.88), (0, 1.8)]), width=0.035, closed=False),
            Shape(m, fill="dog_mouth", width=0.035)]


def _mouth_shout():
    """怒鳴る口（大きく開いて牙が見える）。"""
    m = blob([(-0.3, 1.82), (0, 1.78), (0.3, 1.82), (0.22, 1.5), (0, 1.44), (-0.22, 1.5)], samples=6)
    return [Shape(curve([(0, 1.88), (0, 1.81)]), width=0.035, closed=False),
            Shape(m, fill="dog_mouth", width=0.04),
            Shape([(-0.2, 1.79), (-0.15, 1.69), (-0.1, 1.79)], fill="white", width=0.02),
            Shape([(0.1, 1.79), (0.15, 1.69), (0.2, 1.79)], fill="white", width=0.02),
            Shape(ellipse(0, 1.52, 0.13, 0.06), fill="dog_tongue", line=None)]


def _mouth_pout():
    """ぼやく口（への字）。"""
    return [Shape(curve([(0, 1.88), (0, 1.8)]), width=0.035, closed=False),
            Shape(curve([(-0.22, 1.7), (-0.1, 1.77), (0.05, 1.74), (0.22, 1.68)]), width=0.04,
                  closed=False, taper=0.6)]


def _mouth_ouch():
    """殴られた瞬間の口（ゆがんで開く）。"""
    m = blob([(-0.34, 1.8), (-0.1, 1.74), (0.18, 1.78), (0.36, 1.72), (0.2, 1.52), (-0.05, 1.5),
              (-0.28, 1.58)], samples=6)
    teeth = [(-0.18, 1.75), (-0.13, 1.68), (-0.08, 1.75)]
    return [Shape(m, fill="dog_mouth", width=0.04),
            Shape(teeth, fill="white", width=0.02),
            Shape(ellipse(0.05, 1.56, 0.12, 0.05), fill="dog_tongue", line=None)]


def _body():
    pts = blob([(0, 1.45), (0.45, 1.38), (0.72, 1.0), (0.82, 0.45), (0.6, 0.05), (0, -0.05),
                (-0.6, 0.05), (-0.82, 0.45), (-0.72, 1.0), (-0.45, 1.38)])
    return [Shape(pts, fill="dog_fur", width=W),
            Shape(ellipse(0, 0.62, 0.42, 0.55), fill="dog_white", line=None)]


def _leg(side):
    x = 0.38 * side
    return [Shape(ellipse(x, 0.02, 0.27, 0.17), fill="dog_white", width=W),
            Shape(curve([(x - 0.06, -0.06), (x - 0.04, 0.04)]), width=0.025, closed=False),
            Shape(curve([(x + 0.06, -0.06), (x + 0.04, 0.04)]), width=0.025, closed=False)]


def _tail():
    pts = blob([(0.6, 0.3), (0.95, 0.42), (1.12, 0.8), (0.98, 1.08), (0.74, 1.0), (0.86, 0.78),
                (0.72, 0.55)], samples=6)
    return [Shape(pts, fill="dog_fur", width=W)]


def _arm(side):
    s = side
    return [Shape(capsule((0.62 * s, 1.05), (0.8 * s, 0.5), 0.16), fill="dog_fur", width=W)]


def _paw(side):
    x = 0.8 * side
    return [Shape(ellipse(x, 0.42, 0.19, 0.16), fill="dog_white", width=W),
            Shape(curve([(x - 0.06, 0.3), (x - 0.05, 0.38)]), width=0.025, closed=False),
            Shape(curve([(x + 0.06, 0.3), (x + 0.05, 0.38)]), width=0.025, closed=False)]


def _paw_thumb(side):
    """親指を立てた手（グッドサイン）。"""
    x = 0.8 * side
    return [Shape(capsule((x, 0.5), (x, 0.8), 0.075), fill="dog_white", width=0.045),
            Shape(rect(x, 0.42, 0.38, 0.32, r=0.12), fill="dog_white", width=W),
            Shape(curve([(x - 0.17 * side, 0.46), (x + 0.02 * side, 0.46)]), width=0.025, closed=False),
            Shape(curve([(x - 0.17 * side, 0.37), (x + 0.02 * side, 0.37)]), width=0.025, closed=False)]


def _paw_point(side):
    """指さしの手（1本指を腕の向きに伸ばす）。"""
    x = 0.8 * side
    d = (0.275 * side, -0.96)   # 休み姿勢での腕の向き
    tip = (x + d[0] * 0.3, 0.42 + d[1] * 0.3)
    return [Shape(capsule((x, 0.42), tip, 0.085), fill="dog_white", width=0.045),
            Shape(ellipse(x - 0.03 * side, 0.47, 0.17, 0.15), fill="dog_white", width=W),
            Shape(curve([(x - 0.1 * side, 0.36), (x - 0.12 * side, 0.46)]), width=0.025, closed=False)]


def _controller():
    """ゲームのコントローラー（両手で持つ。body に付く）。"""
    body = blob([(-0.46, 0.62), (0, 0.66), (0.46, 0.62), (0.52, 0.42), (0.36, 0.3), (0.15, 0.42),
                 (-0.15, 0.42), (-0.36, 0.3), (-0.52, 0.42)], samples=6)
    out = [Shape(body, fill="controller", width=0.045),
           Shape(rect(-0.25, 0.52, 0.14, 0.045), fill="controller_btn", line=None),
           Shape(rect(-0.25, 0.52, 0.045, 0.14), fill="controller_btn", line=None)]
    for (bx, by, c) in ((0.2, 0.55, "red"), (0.29, 0.5, "yellow"), (0.2, 0.47, "card_blue")):
        out.append(Shape(ellipse(bx, by, 0.035, 0.035), fill=c, line=None))
    return out


def _card():
    """海斗のクレジットカード（小道具）。"""
    c = rect(0, 0, 0.5, 0.32, r=0.04)
    chip = rect(-0.12, 0.03, 0.1, 0.08, r=0.015)
    band = rect(0, -0.08, 0.5, 0.05)
    tf = lambda pts: transform(pts, tx=0.88, ty=0.6, rot=0.35)
    return [Shape(tf(c), fill="card_blue", width=0.035),
            Shape(tf(band), fill="white", line=None, opacity=0.6),
            Shape(tf(chip), fill="gold", width=0.015)]


def _empty():
    return []


PARTS = [
    Part("tail", "tail", {"default": _tail}),
    Part("ear_L", "ear_L", {"default": lambda: _ear(-1)}),
    Part("ear_R", "ear_R", {"default": lambda: _ear(1)}),
    Part("body", "body", {"default": _body}),
    Part("leg_L", "leg_L", {"default": lambda: _leg(-1)}),
    Part("leg_R", "leg_R", {"default": lambda: _leg(1)}),
    Part("head", "head", {"default": _head}),
    Part("face_white", "head", {"default": _face_white}),
    Part("cheek_L", "cheek_L", {"default": lambda: _cheek(-1)}),
    Part("cheek_R", "cheek_R", {"default": lambda: _cheek(1)}),
    Part("muzzle", "mouth", {"default": _muzzle}),
    Part("mouth", "mouth", {"default": _mouth_default, "smug": _mouth_smug, "open": _mouth_open,
                            "ouch": _mouth_ouch, "talk": _mouth_talk, "shout": _mouth_shout,
                            "pout": _mouth_pout}),
    Part("nose", "mouth", {"default": _nose}),
    Part("eye_L", "eye_L", {"default": lambda: _eye_open(-1), "smug": lambda: _eye_smug(-1),
                            "closed": lambda: _eye_closed(-1), "squeeze": lambda: _eye_squeeze(-1),
                            "spark": lambda: _eye_open(-1, True), "angry": lambda: _eye_angry(-1),
                            "wide": lambda: _eye_wide(-1)}),
    Part("eye_R", "eye_R", {"default": lambda: _eye_open(1), "smug": lambda: _eye_smug(1),
                            "closed": lambda: _eye_closed(1), "squeeze": lambda: _eye_squeeze(1),
                            "spark": lambda: _eye_open(1, True), "angry": lambda: _eye_angry(1),
                            "wide": lambda: _eye_wide(1)}),
    Part("brow_L", "brow_L", {"default": lambda: _brow(-1), "raised": lambda: _brow(-1, True),
                              "angry": lambda: _brow_angry(-1)}),
    Part("brow_R", "brow_R", {"default": lambda: _brow(1), "raised": lambda: _brow(1, True),
                              "angry": lambda: _brow_angry(1)}),
    Part("arm_R", "arm_R", {"default": lambda: _arm(1)}),
    Part("arm_L", "arm_L", {"default": lambda: _arm(-1)}),
    Part("controller", "body", {"default": _empty, "hold": _controller}),
    Part("card", "paw_R", {"default": _empty, "hold": _card}),
    Part("paw_R", "paw_R", {"default": lambda: _paw(1), "point": lambda: _paw_point(1)}),
    Part("paw_L", "paw_L", {"default": lambda: _paw(-1), "thumb": lambda: _paw_thumb(-1)}),
]

# 顔まわり（ギャグの変形で一緒にゆがめるパーツ）
FACE_PARTS = ["head", "face_white", "cheek_L", "cheek_R", "muzzle", "mouth", "nose",
              "eye_L", "eye_R", "brow_L", "brow_R", "ear_L", "ear_R"]

# 汎用モーション（lib/inutarou_anim/motions.py）が使う姿勢
MOTION = {
    # コントローラーを両手で持つ（腕を内側に寄せ、手は上向きのまま）
    "game": {"pose": {"arm_L": {"rot": 35}, "paw_L": {"rot": -35}, "arm_R": {"rot": -35},
                      "paw_R": {"rot": 35}, "eye_L": {"loc": (0.0, -0.06)},
                      "eye_R": {"loc": (0.0, -0.06)}, "head": {"rot": 0}}},
}
