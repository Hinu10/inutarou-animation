"""骨組みのデータと 2D の計算（Blender に依存しない）。

design.py（キャラクターの定義）はここだけを import するので、Blender なしで
読み込み・検査（tests/）ができる。
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable

from .shapes import Point, Shape


@dataclass
class Bone:
    name: str
    parent: str | None
    head: Point
    length: float = 0.3


@dataclass
class Part:
    """パーツ（= GP レイヤー）。variants は 名前 → 形を返す関数。"""
    name: str
    bone: str
    variants: dict[str, Callable[[], list[Shape]]]
    default: str = "default"


@dataclass
class Pose:
    loc: Point = (0.0, 0.0)
    rot: float = 0.0          # 度
    scale: Point = (1.0, 1.0)


PoseDict = dict[str, Pose]


class Design:
    """design.py（assets/characters/<name>/design.py）が用意する中身。"""
    NAME: str
    TEMP: bool
    BONES: list[Bone]
    PARTS: list[Part]


class FK2D:
    """Blender と同じ順番でボーンの変形を計算する（テスト・位置合わせ用、bpy 不要）。"""

    def __init__(self, bones: list[Bone]):
        self.bones = {b.name: b for b in bones}

    def apply(self, bone: str, pose: PoseDict, p: Point) -> Point:
        b = self.bones[bone]
        ps = pose.get(bone, Pose())
        x, y = p[0] - b.head[0], p[1] - b.head[1]
        x, y = x * ps.scale[0], y * ps.scale[1]
        a = math.radians(ps.rot)
        x, y = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)
        x, y = x + b.head[0] + ps.loc[0], y + b.head[1] + ps.loc[1]
        if b.parent:
            return self.apply(b.parent, pose, (x, y))
        return (x, y)

    def world_angle(self, bone: str, pose: PoseDict) -> float:
        a = 0.0
        while bone:
            a += pose.get(bone, Pose()).rot
            bone = self.bones[bone].parent
        return a


def solve_two_bone(shoulder: Point, l1: float, l2: float, target: Point, bend: int = 1
                   ) -> tuple[float, float]:
    """2本の骨（上腕・前腕）で target に届く角度（ワールド角, 度）を返す。

    返り値は (上腕の向き, 前腕の向き)。向きは「上向き=0、反時計回り+」。
    """
    dx, dy = target[0] - shoulder[0], target[1] - shoulder[1]
    d = max(1e-6, min(math.hypot(dx, dy), l1 + l2 - 1e-4))
    base = math.atan2(dy, dx)
    cos_a = (l1 * l1 + d * d - l2 * l2) / (2 * l1 * d)
    a = math.acos(max(-1.0, min(1.0, cos_a)))
    upper = base + bend * a
    ex, ey = shoulder[0] + l1 * math.cos(upper), shoulder[1] + l1 * math.sin(upper)
    lower = math.atan2(target[1] - ey, target[0] - ex)
    # 「上向き=0」に直す
    return (math.degrees(upper) - 90.0, math.degrees(lower) - 90.0)
