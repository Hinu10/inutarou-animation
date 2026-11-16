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
}


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
    return {"wall": wall, "floor": floor, "window": window, "clock": clock,
            "sofa_back": sofa_back, "sofa_front": sofa_front}
