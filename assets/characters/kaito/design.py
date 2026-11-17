"""石村海斗 — 仮デザイン（TEMP）。正式デザインではない。

普通の青年の仮の見た目。立ち姿が基本（原点 = 足元、身長 ≒ 7.4 単位）。
L / R は「画面の左 / 右」。
"""
from inutarou_anim.skeleton import Bone, Part
from inutarou_anim.shapes import Shape, blob, capsule, curve, ellipse, rect

NAME = "kaito"
TEMP = True
VERSION = "temp-0.1"

W = 0.06

SHOULDER = {-1: (-0.72, 5.1), 1: (0.72, 5.1)}
ELBOW = {-1: (-0.86, 4.05), 1: (0.86, 4.05)}
WRIST = {-1: (-0.92, 3.1), 1: (0.92, 3.1)}

BONES = [
    Bone("root", None, (0.0, 0.0)),
    Bone("hips", "root", (0.0, 3.3)),
    Bone("leg_L", "hips", (-0.35, 3.3)),
    Bone("leg_R", "hips", (0.35, 3.3)),
    Bone("spine", "hips", (0.0, 3.4)),
    Bone("head", "spine", (0.0, 5.45)),
    Bone("hair", "head", (0.0, 6.7)),
    Bone("eye_L", "head", (-0.27, 6.28)),
    Bone("eye_R", "head", (0.27, 6.28)),
    Bone("brow_L", "head", (-0.28, 6.6)),
    Bone("brow_R", "head", (0.28, 6.6)),
    Bone("mouth", "head", (0.0, 5.85)),
    Bone("vein", "head", (0.48, 6.85)),
    Bone("arm_L", "spine", SHOULDER[-1]),
    Bone("fore_L", "arm_L", ELBOW[-1]),
    Bone("hand_L", "fore_L", WRIST[-1]),
    Bone("arm_R", "spine", SHOULDER[1]),
    Bone("fore_R", "arm_R", ELBOW[1]),
    Bone("hand_R", "fore_R", WRIST[1]),
]

UPPER_LEN = ((SHOULDER[1][0] - ELBOW[1][0]) ** 2 + (SHOULDER[1][1] - ELBOW[1][1]) ** 2) ** 0.5
FORE_LEN = ((ELBOW[1][0] - WRIST[1][0]) ** 2 + (ELBOW[1][1] - WRIST[1][1]) ** 2) ** 0.5


def _leg(s):
    return [Shape(capsule((0.35 * s, 3.25), (0.4 * s, 0.4), 0.3), fill="kaito_pants", width=W),
            Shape(ellipse(0.48 * s, 0.17, 0.42, 0.19), fill="black", width=W)]


def _torso():
    pts = blob([(-0.78, 5.22), (0, 5.36), (0.78, 5.22), (0.84, 4.4), (0.74, 3.25), (0, 3.12),
                (-0.74, 3.25), (-0.84, 4.4)])
    return [Shape(pts, fill="kaito_shirt", width=W),
            Shape(curve([(-0.22, 5.32), (0, 5.12), (0.22, 5.32)]), width=0.04, closed=False)]


def _head():
    neck = Shape(rect(0, 5.35, 0.36, 0.4, r=0.08), fill="kaito_skin", width=W)
    face = blob([(0, 6.95), (0.62, 6.65), (0.68, 6.1), (0.46, 5.66), (0, 5.46), (-0.46, 5.66),
                 (-0.68, 6.1), (-0.62, 6.65)])
    ears = [Shape(ellipse(0.68 * s, 6.18, 0.11, 0.19), fill="kaito_skin", width=0.045) for s in (-1, 1)]
    return [neck] + ears + [Shape(face, fill="kaito_skin", width=W),
                            Shape(curve([(-0.04, 6.1), (0.02, 6.0)]), width=0.03, closed=False)]


def _head_scream():
    """叫ぶときの顔（あごが下がる）。"""
    neck = Shape(rect(0, 5.35, 0.36, 0.4, r=0.08), fill="kaito_skin", width=W)
    face = blob([(0, 6.95), (0.64, 6.65), (0.7, 6.05), (0.52, 5.45), (0, 5.12), (-0.52, 5.45),
                 (-0.7, 6.05), (-0.64, 6.65)])
    ears = [Shape(ellipse(0.7 * s, 6.18, 0.11, 0.19), fill="kaito_skin", width=0.045) for s in (-1, 1)]
    return [neck] + ears + [Shape(face, fill="kaito_skin", width=W)]


def _hair():
    pts = blob([(-0.74, 6.25), (-0.82, 6.8), (-0.62, 7.2), (-0.25, 7.38), (0.18, 7.4), (0.58, 7.22),
                (0.82, 6.85), (0.74, 6.25), (0.56, 6.6), (0.3, 6.5), (0.06, 6.7), (-0.22, 6.52),
                (-0.5, 6.66)], samples=5)
    return [Shape(pts, fill="kaito_hair", width=W)]


def _eye(s, kind="default"):
    x = 0.27 * s
    if kind == "default":
        return [Shape(ellipse(x, 6.28, 0.085, 0.13), fill="black", line=None),
                Shape(ellipse(x - 0.03, 6.33, 0.03, 0.03), fill="white", line=None)]
    if kind == "glare":
        # 怒りをこらえる目（上がまぶたで切れている）
        lower = ellipse(x, 6.28, 0.1, 0.13, n=24, start=3.4, end=6.02)
        return [Shape(lower, fill="black", line=None),
                Shape([(x - 0.17 * s, 6.33), (x + 0.15 * s, 6.25)], width=0.06, closed=False)]
    if kind == "rage":
        # 白目に小さい黒目（叫び）
        return [Shape(ellipse(x, 6.3, 0.18, 0.16), fill="white", width=0.05),
                Shape(ellipse(x, 6.3, 0.035, 0.035), fill="black", line=None)]
    if kind == "closed":
        return [Shape(curve([(x - 0.13, 6.3), (x, 6.25), (x + 0.13, 6.3)]), width=0.05, closed=False)]
    if kind == "half":
        # 疑い・呆れのジト目（まぶたが水平）
        lower = ellipse(x, 6.26, 0.09, 0.12, n=24, start=3.3, end=6.12)
        return [Shape(lower, fill="black", line=None),
                Shape([(x - 0.15, 6.29), (x + 0.15, 6.29)], width=0.055, closed=False)]
    if kind == "dot":
        # ぽかん・あぜん（点の目）
        return [Shape(ellipse(x, 6.28, 0.045, 0.06), fill="black", line=None)]
    raise KeyError(kind)


def _brow(s, kind="default"):
    x = 0.28 * s
    if kind == "default":
        return [Shape(curve([(x - 0.15, 6.6), (x, 6.65), (x + 0.15, 6.6)]), line="kaito_hair",
                      width=0.06, closed=False, taper=0.8)]
    if kind == "raised":
        return [Shape(curve([(x - 0.15, 6.7), (x, 6.78), (x + 0.15, 6.71)]), line="kaito_hair",
                      width=0.06, closed=False, taper=0.8)]
    if kind == "worried":
        # 困り眉（内側が上がる）
        return [Shape([(x + 0.16 * s, 6.6), (x - 0.15 * s, 6.72)], line="kaito_hair", width=0.07,
                      closed=False, taper=0.5)]
    # 怒り眉（内側が下がる）
    inner, outer = x - 0.16 * s, x + 0.16 * s
    return [Shape([(outer, 6.7), (inner, 6.52)], line="kaito_hair", width=0.09, closed=False,
                  taper=0.5)]


def _mouth(kind="default"):
    if kind == "default":
        return [Shape(curve([(-0.14, 5.86), (0, 5.84), (0.14, 5.86)]), width=0.04, closed=False)]
    if kind == "grit":
        # 歯を食いしばる
        out = [Shape(rect(0, 5.84, 0.46, 0.16, r=0.04), fill="white", width=0.04),
               Shape([(-0.23, 5.84), (0.23, 5.84)], width=0.025, closed=False)]
        for x in (-0.12, 0.0, 0.12):
            out.append(Shape([(x, 5.76), (x, 5.92)], width=0.02, closed=False))
        return out
    if kind == "talk":
        m = blob([(-0.17, 5.88), (0, 5.89), (0.17, 5.88), (0.1, 5.76), (-0.1, 5.76)], samples=5)
        return [Shape(m, fill="kaito_mouth", width=0.04)]
    if kind == "smile":
        # 気まずい笑い
        return [Shape(curve([(-0.2, 5.9), (0, 5.8), (0.2, 5.9)]), width=0.045, closed=False, taper=0.6)]
    if kind == "wavy":
        return [Shape([(-0.2, 5.84), (-0.1, 5.88), (0, 5.84), (0.1, 5.88), (0.2, 5.84)], width=0.04,
                      closed=False, taper=0.5)]
    if kind == "o":
        return [Shape(ellipse(0, 5.82, 0.1, 0.13), fill="kaito_mouth", width=0.04)]
    if kind == "scream":
        m = blob([(-0.42, 5.98), (0, 6.02), (0.42, 5.98), (0.36, 5.55), (0.12, 5.28), (-0.12, 5.28),
                  (-0.36, 5.55)], samples=6)
        teeth = blob([(-0.36, 5.96), (0, 5.99), (0.36, 5.96), (0.3, 5.87), (-0.3, 5.87)], samples=4)
        return [Shape(m, fill="kaito_mouth", width=0.05),
                Shape(teeth, fill="white", width=0.03),
                Shape(ellipse(0, 5.38, 0.2, 0.09), fill="dog_tongue", line=None)]
    raise KeyError(kind)


def _vein(on=True):
    if not on:
        return []
    out = []
    for k in range(4):
        import math
        a = math.pi / 4 + k * math.pi / 2
        cx, cy = 0.48 + 0.1 * math.cos(a), 6.85 + 0.1 * math.sin(a)
        out.append(Shape(curve([(cx + 0.09 * math.cos(a + 1.1), cy + 0.09 * math.sin(a + 1.1)),
                                (cx - 0.03 * math.cos(a), cy - 0.03 * math.sin(a)),
                                (cx + 0.09 * math.cos(a - 1.1), cy + 0.09 * math.sin(a - 1.1))]),
                         line="kaito_vein", width=0.06, closed=False, taper=0.4))
    return out


def _upper(s):
    return [Shape(capsule(SHOULDER[s], ELBOW[s], 0.19), fill="kaito_skin", width=W),
            Shape(capsule((SHOULDER[s][0], SHOULDER[s][1] - 0.08),
                          ((SHOULDER[s][0] * 0.55 + ELBOW[s][0] * 0.45),
                           (SHOULDER[s][1] * 0.55 + ELBOW[s][1] * 0.45)), 0.23),
                  fill="kaito_shirt", width=W)]


def _fore(s):
    return [Shape(capsule(ELBOW[s], WRIST[s], 0.165), fill="kaito_skin", width=W)]


def _hand(s, kind="open"):
    x, y = WRIST[s]
    if kind == "open":
        return [Shape(ellipse(x + 0.02 * s, y - 0.12, 0.17, 0.21), fill="kaito_skin", width=W)]
    if kind == "fist":
        out = [Shape(rect(x, y - 0.12, 0.42, 0.38, r=0.13), fill="kaito_skin", width=W)]
        for k in range(3):
            yy = y - 0.02 - k * 0.09
            out.append(Shape([(x - 0.18 * s, yy), (x + 0.02 * s, yy)], width=0.025, closed=False))
        return out
    if kind == "phone":
        # スマホを持つ手（画面は海斗の方を向いている想定で、裏面が見える）
        return [Shape(rect(x + 0.05 * s, y - 0.05, 0.36, 0.62, r=0.06), fill="phone", width=0.04),
                Shape(ellipse(x + 0.02 * s, y - 0.18, 0.18, 0.18), fill="kaito_skin", width=W)]
    if kind == "potechi":
        # ポテチの袋を持つ手
        bag = rect(x + 0.05 * s, y - 0.2, 0.62, 0.8, r=0.05)
        return [Shape(bag, fill="potechi", width=0.045),
                Shape(rect(x + 0.05 * s, y + 0.17, 0.66, 0.08), fill="potechi_red", width=0.03),
                Shape(rect(x + 0.05 * s, y - 0.57, 0.66, 0.08), fill="potechi_red", width=0.03),
                Shape(ellipse(x + 0.05 * s, y - 0.22, 0.17, 0.13), fill="gold", width=0.025),
                Shape(ellipse(x + 0.02 * s, y - 0.02, 0.17, 0.21), fill="kaito_skin", width=W)]
    if kind == "wallet":
        # 開いた財布を持つ手（中身は空のカード入れ）
        out = [Shape(rect(x + 0.1 * s, y - 0.1, 0.8, 0.52, r=0.05), fill="wallet", width=0.045),
               Shape([(x + 0.1 * s, y + 0.16), (x + 0.1 * s, y - 0.36)], line="wallet_dark",
                     width=0.035, closed=False)]
        for k in range(3):
            yy = y + 0.06 - k * 0.12
            out.append(Shape([(x - 0.25 * s, yy), (x - 0.02 * s, yy)], line="wallet_dark", width=0.025,
                             closed=False))
        out.append(Shape(ellipse(x + 0.02 * s, y - 0.18, 0.17, 0.19), fill="kaito_skin", width=W))
        return out
    raise KeyError(kind)


EYES = ("default", "glare", "rage", "closed", "half", "dot")
BROWS = ("default", "angry", "raised", "worried")
MOUTHS = ("default", "grit", "o", "scream", "talk", "smile", "wavy")
HANDS = ("open", "fist", "phone", "potechi", "wallet")

PARTS = [
    Part("leg_L", "leg_L", {"default": lambda: _leg(-1)}),
    Part("leg_R", "leg_R", {"default": lambda: _leg(1)}),
    Part("torso", "spine", {"default": _torso}),
    Part("head", "head", {"default": _head, "scream": _head_scream}),
    Part("hair", "hair", {"default": _hair}),
    Part("eye_L", "eye_L", {k: (lambda k=k: _eye(-1, k)) for k in EYES}),
    Part("eye_R", "eye_R", {k: (lambda k=k: _eye(1, k)) for k in EYES}),
    Part("brow_L", "brow_L", {k: (lambda k=k: _brow(-1, k)) for k in BROWS}),
    Part("brow_R", "brow_R", {k: (lambda k=k: _brow(1, k)) for k in BROWS}),
    Part("mouth", "mouth", {k: (lambda k=k: _mouth(k)) for k in MOUTHS}),
    Part("vein", "vein", {"default": lambda: _vein(False), "on": _vein}),
    Part("arm_L", "arm_L", {"default": lambda: _upper(-1)}),
    Part("fore_L", "fore_L", {"default": lambda: _fore(-1)}),
    Part("hand_L", "hand_L", {k: (lambda k=k: _hand(-1, k)) for k in HANDS}, default="open"),
    Part("arm_R", "arm_R", {"default": lambda: _upper(1)}),
    Part("fore_R", "fore_R", {"default": lambda: _fore(1)}),
    Part("hand_R", "hand_R", {k: (lambda k=k: _hand(1, k)) for k in HANDS}, default="open"),
]

# 顔の赤み（怒り）をのせるパーツ
FACE_PARTS = ["head"]
