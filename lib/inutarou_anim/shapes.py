"""2D の形を作る道具（Blender に依存しない純粋な Python）。

座標は (x, y)。x が画面の右、y が画面の上。Blender では (x, 0, y) に置く。
キャラクターのパーツはすべて「休み姿勢（rest）」の座標で定義し、
動きは骨（ボーン）で、描き替えは形の差し替えや warp で作る。
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field, replace
from typing import Callable, Iterable, Sequence

Point = tuple[float, float]


@dataclass
class Shape:
    """1本のストローク。

    pts:   点列
    fill:  塗りの色名（palette のキー）。None なら塗らない
    line:  線の色名。None なら線を描かない
    width: 線の太さ（半径ではなく見た目の太さ、ワールド単位）
    closed: 閉じた形か
    taper: 開いた線の両端を細くする（0 なら一定）
    """

    pts: list[Point]
    fill: str | None = None
    line: str | None = "line"
    width: float = 0.05
    closed: bool = True
    taper: float = 0.0
    opacity: float = 1.0
    tags: tuple[str, ...] = field(default_factory=tuple)

    def map(self, fn: Callable[[Point], Point]) -> "Shape":
        return replace(self, pts=[fn(p) for p in self.pts])

    def moved(self, dx: float = 0.0, dy: float = 0.0) -> "Shape":
        return self.map(lambda p: (p[0] + dx, p[1] + dy))


# ---------------------------------------------------------------- 基本図形

def ellipse(cx: float, cy: float, rx: float, ry: float, n: int = 48, rot: float = 0.0,
            start: float = 0.0, end: float = 2 * math.pi) -> list[Point]:
    full = abs(end - start - 2 * math.pi) < 1e-9
    count = n if full else n + 1
    c, s = math.cos(rot), math.sin(rot)
    out = []
    for i in range(count):
        a = start + (end - start) * i / (n if full else n)
        x, y = rx * math.cos(a), ry * math.sin(a)
        out.append((cx + x * c - y * s, cy + x * s + y * c))
    return out


def catmull(ctrl: Sequence[Point], closed: bool = True, samples: int = 8) -> list[Point]:
    """制御点を通るなめらかな曲線（Catmull-Rom）。"""
    pts = list(ctrl)
    n = len(pts)
    if n < 3:
        return pts
    out: list[Point] = []
    segs = n if closed else n - 1
    for i in range(segs):
        p0 = pts[(i - 1) % n] if closed or i > 0 else pts[0]
        p1 = pts[i]
        p2 = pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if closed or i + 2 < n else pts[-1]
        for k in range(samples):
            t = k / samples
            t2, t3 = t * t, t * t * t
            out.append(tuple(
                0.5 * ((2 * p1[j]) + (-p0[j] + p2[j]) * t
                       + (2 * p0[j] - 5 * p1[j] + 4 * p2[j] - p3[j]) * t2
                       + (-p0[j] + 3 * p1[j] - 3 * p2[j] + p3[j]) * t3)
                for j in range(2)))
    if not closed:
        out.append(pts[-1])
    return out


def blob(ctrl: Sequence[Point], samples: int = 8) -> list[Point]:
    return catmull(ctrl, closed=True, samples=samples)


def curve(ctrl: Sequence[Point], samples: int = 8) -> list[Point]:
    return catmull(ctrl, closed=False, samples=samples)


def rect(cx: float, cy: float, w: float, h: float, r: float = 0.0, n: int = 6) -> list[Point]:
    """角丸の長方形。"""
    if r <= 0:
        return [(cx - w / 2, cy - h / 2), (cx + w / 2, cy - h / 2),
                (cx + w / 2, cy + h / 2), (cx - w / 2, cy + h / 2)]
    out: list[Point] = []
    corners = [(cx + w / 2 - r, cy - h / 2 + r, -math.pi / 2), (cx + w / 2 - r, cy + h / 2 - r, 0),
               (cx - w / 2 + r, cy + h / 2 - r, math.pi / 2), (cx - w / 2 + r, cy - h / 2 + r, math.pi)]
    for x, y, a0 in corners:
        for i in range(n + 1):
            a = a0 + (math.pi / 2) * i / n
            out.append((x + r * math.cos(a), y + r * math.sin(a)))
    return out


def star(cx: float, cy: float, r_out: float, r_in: float, points: int = 4, rot: float = 0.0,
         jitter: float = 0.0, seed: int = 0) -> list[Point]:
    import random
    rnd = random.Random(seed)
    out = []
    for i in range(points * 2):
        a = rot + math.pi * i / points + math.pi / 2
        r = r_out if i % 2 == 0 else r_in
        if jitter:
            r *= 1 + rnd.uniform(-jitter, jitter)
        out.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return out


def capsule(a: Point, b: Point, r: float, n: int = 10) -> list[Point]:
    """2点を結ぶ太い棒（腕・脚用）。"""
    ang = math.atan2(b[1] - a[1], b[0] - a[0])
    out = ellipse(b[0], b[1], r, r, n=n * 2, start=ang - math.pi / 2, end=ang + math.pi / 2)
    out += ellipse(a[0], a[1], r, r, n=n * 2, start=ang + math.pi / 2, end=ang + 3 * math.pi / 2)
    return out


# ---------------------------------------------------------------- 変形

def transform(pts: Iterable[Point], tx: float = 0, ty: float = 0, sx: float = 1, sy: float = 1,
              rot: float = 0.0, pivot: Point = (0.0, 0.0)) -> list[Point]:
    c, s = math.cos(rot), math.sin(rot)
    out = []
    for x, y in pts:
        x, y = (x - pivot[0]) * sx, (y - pivot[1]) * sy
        out.append((pivot[0] + x * c - y * s + tx, pivot[1] + x * s + y * c + ty))
    return out


def smoothstep(e0: float, e1: float, x: float) -> float:
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def push_warp(center: Point, direction: Point, radius: float, strength: float,
              squash: float = 0.0) -> Callable[[Point], Point]:
    """center の近くを direction 方向へ押し出す warp。

    ギャグの「ほおが持ち上がる」変形用。近いほど大きく動き、radius で 0 になる。
    squash > 0 なら押した方向と直角に少し広がる（つぶれた肉が逃げる感じ）。
    """
    dx, dy = direction
    ln = math.hypot(dx, dy) or 1.0
    ux, uy = dx / ln, dy / ln
    px, py = -uy, ux

    def fn(p: Point) -> Point:
        rx, ry = p[0] - center[0], p[1] - center[1]
        d = math.hypot(rx, ry)
        w = 1.0 - smoothstep(0.0, radius, d)
        w = w * w * (3 - 2 * w)
        side = rx * px + ry * py
        spread = squash * w * (side / radius)
        return (p[0] + ux * strength * w + px * spread,
                p[1] + uy * strength * w + py * spread)

    return fn


def dent_warp(center: Point, direction: Point, sigma: float, strength: float) -> Callable[[Point], Point]:
    """拳がめり込むような押し込み（ガウス分布）。

    center は押す物（拳）の中心。近い点ほど direction に強く動く。
    strength < 1.1 * sigma くらいに収めると、線が折り返さずに「へこみ」になる。
    """
    dx, dy = direction
    ln = math.hypot(dx, dy) or 1.0
    ux, uy = dx / ln, dy / ln

    def fn(p: Point) -> Point:
        d2 = (p[0] - center[0]) ** 2 + (p[1] - center[1]) ** 2
        w = math.exp(-d2 / (2 * sigma * sigma))
        return (p[0] + ux * strength * w, p[1] + uy * strength * w)

    return fn


def inflate_warp(center: Point, sigma: float, amount: float) -> Callable[[Point], Point]:
    """center のまわりをふくらませる（押されて逃げた肉が盛り上がる感じ）。"""

    def fn(p: Point) -> Point:
        dx, dy = p[0] - center[0], p[1] - center[1]
        d = math.hypot(dx, dy)
        if d < 1e-9:
            return p
        k = amount * (d / sigma) * math.exp(0.5 - d * d / (2 * sigma * sigma))
        return (p[0] + dx / d * k, p[1] + dy / d * k)

    return fn


def compose(*fns: Callable[[Point], Point]) -> Callable[[Point], Point]:
    def fn(p: Point) -> Point:
        for f in fns:
            p = f(p)
        return p
    return fn


def lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t
