"""漫画・アニメ的な効果の形（キラン、集中線、衝撃、汗、動きの線）。Blender 不要。"""
from __future__ import annotations

import math
import random

from .shapes import Point, Shape, curve, ellipse, star


def sparkle(c: Point, size: float, rot: float = 0.0) -> list[Shape]:
    """キラン（4本の光）。"""
    big = star(c[0], c[1], size, size * 0.18, points=4, rot=rot)
    small = star(c[0], c[1], size * 0.55, size * 0.12, points=4, rot=rot + math.pi / 4)
    return [Shape(small, fill="yellow", line=None, opacity=0.9),
            Shape(big, fill="white", line="gold", width=size * 0.06),
            Shape(ellipse(c[0], c[1], size * 0.16, size * 0.16), fill="white", line=None)]


def focus_lines(c: Point, r_in: float, r_out: float, n: int = 70, seed: int = 0,
                color: str = "black") -> list[Shape]:
    """集中線。r_in より内側は空ける。"""
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        a = 2 * math.pi * (i + rnd.uniform(-0.35, 0.35)) / n
        r0 = r_in * rnd.uniform(0.95, 1.35)
        w = rnd.uniform(0.04, 0.16)
        p0 = (c[0] + r0 * math.cos(a), c[1] + r0 * math.sin(a))
        p1 = (c[0] + r_out * math.cos(a - w * 0.08), c[1] + r_out * math.sin(a - w * 0.08))
        p2 = (c[0] + r_out * math.cos(a + w * 0.08), c[1] + r_out * math.sin(a + w * 0.08))
        out.append(Shape([p0, p1, p2], fill=color, line=None))
    return out


def burst(c: Point, r_out: float, r_in: float, points: int = 12, seed: int = 0,
          fill: str = "white", line: str | None = "black", rot: float = 0.0) -> list[Shape]:
    """衝撃（ギザギザの爆発）。"""
    return [Shape(star(c[0], c[1], r_out, r_in, points=points, rot=rot, jitter=0.25, seed=seed),
                  fill=fill, line=line, width=0.06)]


def sweat(c: Point, size: float, rot: float = 0.0) -> list[Shape]:
    """汗のしずく（rot = 尖った方の向き、0 で上）。"""
    pts = []
    for i in range(24):
        t = 2 * math.pi * i / 24
        u, v = math.cos(t), math.sin(t) * math.sin(t / 2)   # (1, 0) が尖り
        pts.append((-v * size * 0.75, u * size))
    c_, s_ = math.cos(rot), math.sin(rot)
    pts = [(c[0] + x * c_ - y * s_, c[1] + x * s_ + y * c_) for x, y in pts]
    return [Shape(pts, fill="sweat", width=0.035)]


def motion_arc(center: Point, radius: float, a0: float, a1: float, n: int = 5,
               spread: float = 0.35, seed: int = 0) -> list[Shape]:
    """振り抜きの線（円弧の束）。角度はラジアン。"""
    rnd = random.Random(seed)
    out = []
    for i in range(n):
        r = radius + (i - n / 2) * spread / n
        b0 = a0 + rnd.uniform(0, 0.25) * (a1 - a0)
        pts = [(center[0] + r * math.cos(b0 + (a1 - b0) * k / 8),
                center[1] + r * math.sin(b0 + (a1 - b0) * k / 8)) for k in range(9)]
        out.append(Shape(pts, line="black", width=0.07, closed=False, taper=1.2))
    return out


def tremble_lines(c: Point, w: float, h: float) -> list[Shape]:
    """怒りで震える「プルプル」線（体の両脇）。"""
    out = []
    for s in (-1, 1):
        for k in range(3):
            x = c[0] + s * (w / 2 + 0.12 * k)
            y0 = c[1] - h * 0.15 + k * 0.12
            pts = [(x + (0.06 if j % 2 else -0.06), y0 + j * h * 0.06) for j in range(5)]
            out.append(Shape(pts, line="line", width=0.035, closed=False))
    return out


def stars_orbit(c: Point, r: float, n: int = 3, phase: float = 0.0) -> list[Shape]:
    out = []
    for i in range(n):
        a = phase + 2 * math.pi * i / n
        p = (c[0] + r * math.cos(a), c[1] + 0.35 * r * math.sin(a))
        out.append(Shape(star(p[0], p[1], 0.16, 0.07, points=5, rot=a), fill="yellow", width=0.03))
    return out
