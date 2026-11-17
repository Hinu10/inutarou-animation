"""カラス — 仮デザイン（TEMP）。正式デザインではない。

横向き（右向き）が基本。原点 = 足元。左右反転は root の scale.x = -1 で行う。
羽ばたきは wing の描き替え（up / mid / down）と回転で作る。
"""
from inutarou_anim.skeleton import Bone, Part
from inutarou_anim.shapes import Shape, blob, curve, ellipse

NAME = "karasu"
TEMP = True
VERSION = "temp-0.1"

W = 0.045

BONES = [
    Bone("root", None, (0.0, 0.0)),
    Bone("body", "root", (0.0, 0.35)),
    Bone("head", "body", (0.45, 0.95)),
    Bone("beak", "head", (0.78, 1.05)),
    Bone("wing", "body", (0.05, 0.8)),
    Bone("legs", "body", (0.0, 0.3)),
    Bone("tail", "body", (-0.45, 0.6)),
]


def _body():
    return [Shape(blob([(0.55, 0.95), (0.4, 0.45), (0.0, 0.3), (-0.45, 0.45), (-0.55, 0.75),
                        (-0.2, 0.95), (0.2, 1.02)]), fill="crow", width=W)]


def _tail():
    return [Shape(blob([(-0.4, 0.65), (-0.95, 0.42), (-1.0, 0.55), (-0.45, 0.8)], samples=4),
                  fill="crow", width=W)]


def _head():
    return [Shape(ellipse(0.5, 1.05, 0.3, 0.27), fill="crow", width=W),
            Shape(ellipse(0.58, 1.12, 0.06, 0.06), fill="white", line=None),
            Shape(ellipse(0.6, 1.12, 0.03, 0.03), fill="black", line=None)]


def _beak(open_=False, holding=False):
    out = [Shape([(0.74, 1.12), (1.12, 1.03), (0.74, 0.98)], fill="crow_beak", width=0.035)]
    if open_:
        out = [Shape([(0.74, 1.14), (1.1, 1.12), (0.74, 1.04)], fill="crow_beak", width=0.035),
               Shape([(0.74, 1.0), (1.06, 0.92), (0.74, 0.95)], fill="crow_beak", width=0.035)]
    if holding:
        # ポテチの袋をくわえる
        from inutarou_anim.shapes import rect, transform
        bag = transform(rect(0, 0, 0.42, 0.55, r=0.05), tx=1.1, ty=0.8, rot=-0.3)
        out = [Shape(bag, fill="potechi", width=0.04)] + out
    return out


def _wing(kind):
    if kind == "up":
        pts = [(0.15, 0.85), (-0.1, 1.6), (-0.5, 1.95), (-0.45, 1.5), (-0.3, 0.95)]
    elif kind == "down":
        pts = [(0.15, 0.8), (-0.05, 0.25), (-0.35, -0.15), (-0.45, 0.25), (-0.3, 0.7)]
    else:
        pts = [(0.2, 0.85), (-0.3, 0.95), (-0.85, 0.85), (-0.55, 0.7), (-0.1, 0.65)]
    return [Shape(blob(pts, samples=5), fill="crow", width=W)]


def _legs():
    return [Shape([(-0.05, 0.32), (-0.08, 0.0), (-0.2, -0.04)], line="crow_beak", width=0.04,
                  closed=False),
            Shape([(0.1, 0.32), (0.08, 0.0), (0.2, -0.04)], line="crow_beak", width=0.04,
                  closed=False)]


PARTS = [
    Part("tail", "tail", {"default": _tail}),
    Part("legs", "legs", {"default": _legs}),
    Part("body", "body", {"default": _body}),
    Part("head", "head", {"default": _head}),
    Part("beak", "beak", {"default": _beak, "open": lambda: _beak(True),
                          "hold": lambda: _beak(False, True)}),
    Part("wing", "wing", {"default": lambda: _wing("mid"), "up": lambda: _wing("up"),
                          "down": lambda: _wing("down")}),
]

FACE_PARTS = ["head", "beak"]
