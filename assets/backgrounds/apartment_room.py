"""背景：海斗のアパートの部屋 — 仮背景（TEMP）。

ワールド座標（引きの画面 = 横16 × 縦9、中心 0,0）で描く。
レイヤーは奥から順。正式な背景画（PNG など）に替えるときは
docs/production/asset-replacement.md の「背景」を参照。
"""
from inutarou_anim.shapes import Shape, curve, ellipse, rect

NAME = "apartment_room"
TEMP = True

# キャラクターを置く基準位置（ショットのスクリプトが使う）
SPOTS = {
    "sofa_seat": (1.9, -1.5),      # 犬太朗が座る位置（お尻）
    "kaito_stand": (-2.7, -4.1),   # 海斗が立つ位置（足元）
    "window": (4.6, 1.3),
    "window_sill_out": (5.25, 0.2),  # 窓の外（ガラスの向こう）の止まり位置
    "desk_top": (-4.5, -1.2),      # 机の天板の中心（ポテチを置く位置）
    "door": (-6.6, -1.5),          # ドアの足元（奥の壁）
}

DOOR_W, DOOR_H = 1.7, 4.3


def door(open_: bool = False):
    """ドア（奥の壁）。open_ で開いた状態（中が暗い）。"""
    x, y = SPOTS["door"]
    cy = y + DOOR_H / 2
    frame = Shape(rect(x, cy, DOOR_W + 0.25, DOOR_H + 0.15), fill="window_frame", width=0.05)
    if open_:
        hole = Shape(rect(x, cy, DOOR_W, DOOR_H), fill="doorway", width=0.04)
        leaf = Shape([(x - DOOR_W / 2, y), (x - DOOR_W / 2 - 0.55, y - 0.35),
                      (x - DOOR_W / 2 - 0.55, y + DOOR_H + 0.25), (x - DOOR_W / 2, y + DOOR_H)],
                     fill="door_dark", width=0.05)
        return [frame, hole, leaf]
    leaf = Shape(rect(x, cy, DOOR_W, DOOR_H), fill="door", width=0.05)
    knob = Shape(ellipse(x + DOOR_W / 2 - 0.25, cy - 0.15, 0.09, 0.09), fill="gold", width=0.03)
    panel = Shape(rect(x, cy + 0.9, DOOR_W - 0.5, 1.6, r=0.05), fill="door_dark", line=None,
                  opacity=0.35)
    return [frame, leaf, panel, knob]


def desk():
    """ポテチを置く小さい机（手前の床の上）。"""
    x, y = SPOTS["desk_top"]
    top = Shape(rect(x, y, 1.9, 0.22, r=0.06), fill="desk", width=0.05)
    front = Shape(rect(x, y - 0.42, 1.7, 0.62, r=0.04), fill="desk_dark", width=0.05)
    legs = [Shape(rect(x + dx, y - 1.1, 0.16, 1.6), fill="desk_dark", width=0.05) for dx in (-0.7, 0.7)]
    drawer = Shape([(x - 0.15, y - 0.4), (x + 0.15, y - 0.4)], line="line", width=0.05, closed=False)
    return legs + [front, top, drawer]


def window_front():
    """窓の手前側（窓の外にいるものの前に重ねる枠と桟、ガラスの反射）。"""
    x, y = SPOTS["window"]
    w, h = 3.3, 2.7
    out = []
    for cx, cy, ww, hh in ((x, y + h / 2 - 0.1, w, 0.2), (x, y - h / 2 + 0.1, w, 0.2),
                           (x - w / 2 + 0.1, y, 0.2, h), (x + w / 2 - 0.1, y, 0.2, h)):
        out.append(Shape(rect(cx, cy, ww, hh), fill="window_frame", width=0.03))
    out.append(Shape([(x, y - h / 2 + 0.15), (x, y + h / 2 - 0.15)], line="window_frame", width=0.12,
                     closed=False))
    out.append(Shape(curve([(x - 1.2, y + 0.6), (x - 0.7, y + 0.8), (x - 0.3, y + 0.65)]),
                     line="white", width=0.12, closed=False, taper=1.0, opacity=0.8))
    return out


def layers():
    wall = [Shape(rect(0, 2.2, 24, 7.6), fill="wall", line=None),
            Shape(rect(0, -1.45, 24, 0.3), fill="wall_shade", line=None)]
    floor = [Shape(rect(0, -4.0, 24, 5.0), fill="floor", line=None)]
    for k in range(6):
        y = -1.9 - k * 0.55 - k * k * 0.06
        floor.append(Shape([(-12, y), (12, y)], line="floor_dark", width=0.03, closed=False))
    window = [Shape(rect(4.6, 1.3, 3.3, 2.7, r=0.05), fill="window_frame", width=0.05),
              Shape(rect(4.6, 1.3, 2.9, 2.3), fill="window_sky", width=0.03),
              Shape([(4.6, 0.15), (4.6, 2.45)], line="window_frame", width=0.12, closed=False),
              Shape(curve([(3.4, 1.9), (3.9, 2.1), (4.3, 1.95)]), line="white", width=0.12,
                    closed=False, taper=1.0)]
    clock = [Shape(ellipse(-4.2, 2.7, 0.45, 0.45), fill="white", width=0.05),
             Shape([(-4.2, 2.7), (-4.2, 3.0)], width=0.04, closed=False),
             Shape([(-4.2, 2.7), (-4.0, 2.6)], width=0.04, closed=False)]
    sofa_back = [Shape(rect(2.2, -0.75, 4.4, 1.9, r=0.35), fill="sofa", width=0.05),
                 Shape([(2.2, -1.4), (2.2, 0.0)], line="sofa_dark", width=0.04, closed=False)]
    sofa_front = [Shape(rect(0.05, -1.65, 0.62, 1.7, r=0.25), fill="sofa", width=0.05),
                  Shape(rect(4.35, -1.65, 0.62, 1.7, r=0.25), fill="sofa", width=0.05),
                  Shape(rect(2.2, -1.75, 3.8, 0.55, r=0.15), fill="sofa", width=0.05),
                  Shape(rect(2.2, -2.45, 4.7, 0.9, r=0.2), fill="sofa_dark", width=0.05)]
    return {"wall": wall, "floor": floor, "window": window, "clock": clock, "door": door(),
            "sofa_back": sofa_back, "sofa_front": sofa_front, "desk": desk()}
