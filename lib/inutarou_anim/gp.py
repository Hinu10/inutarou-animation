"""Grease Pencil（Blender 5.x / GPv3）にストロークを書き込む道具。

注意（Blender 5.2 で確認したこと）
- 塗りを出すにはストロークの fill_id を 1 以上にする必要がある。
- add_strokes で作った点は opacity が 0 になることがあるので 1 を入れる。
- マテリアルは「線の色 color」と「塗りの色 fill_color」を両方持ち、
  線を消したいストロークは hide_stroke=True にする。
"""
from __future__ import annotations

import math

import bpy

from .palette import PALETTE, rgba
from .shapes import Shape

_mat_cache: dict[tuple[int, str, str], int] = {}


def material_index(gp: bpy.types.GreasePencil, line: str | None, fill: str | None) -> int:
    key = (gp.session_uid, line or "-", fill or "-")
    if key in _mat_cache:
        return _mat_cache[key]
    name = f"{line or 'noline'}__{fill or 'nofill'}"
    mat = bpy.data.materials.get(name)
    if mat is None:
        mat = bpy.data.materials.new(name)
        bpy.data.materials.create_gpencil_data(mat)
        mat.grease_pencil.color = rgba(line or "line")
        mat.grease_pencil.fill_color = rgba(fill or "white")
    for i, m in enumerate(gp.materials):
        if m == mat:
            _mat_cache[key] = i
            return i
    gp.materials.append(mat)
    _mat_cache[key] = len(gp.materials) - 1
    return _mat_cache[key]


def _radius_profile(n: int, width: float, taper: float, closed: bool) -> list[float]:
    r = width / 2
    if closed or taper <= 0 or n < 3:
        return [r] * n
    out = []
    for i in range(n):
        t = i / (n - 1)
        k = math.sin(math.pi * t) ** taper
        out.append(r * (0.25 + 0.75 * k))
    return out


def write(drawing, gp: bpy.types.GreasePencil, shapes: list[Shape]) -> None:
    """drawing に shapes を追記する。"""
    shapes = [s for s in shapes if len(s.pts) >= 2]
    if not shapes:
        return
    start = len(drawing.strokes)
    drawing.add_strokes([len(s.pts) for s in shapes])
    for k, shape in enumerate(shapes):
        st = drawing.strokes[start + k]
        st.cyclic = shape.closed
        st.material_index = material_index(gp, shape.line, shape.fill)
        st.fill_id = start + k + 1 if shape.fill else 0  # 塗りごとに別の番号（同じ番号だと穴あきになる）
        st.hide_stroke = shape.line is None
        st.fill_opacity = shape.opacity
        radii = _radius_profile(len(shape.pts), shape.width, shape.taper, shape.closed)
        for p, (x, y), r in zip(st.points, shape.pts, radii):
            p.position = (x, 0.0, y)
            p.radius = r
            p.opacity = shape.opacity
    drawing.tag_positions_changed()


def set_frame(layer, gp, frame: int, shapes: list[Shape]) -> None:
    """layer の frame に描き替え（キーフレーム）を置く。既にあれば中身を差し替える。"""
    fr = None
    for f in layer.frames:
        if f.frame_number == frame:
            fr = f
            break
    if fr is None:
        fr = layer.frames.new(frame)
    d = fr.drawing
    if len(d.strokes):
        d.remove_strokes()
    write(d, gp, shapes)


def new_object(name: str, collection, location=(0.0, 0.0, 0.0)):
    data = bpy.data.grease_pencils.new(name)
    ob = bpy.data.objects.new(name, data)
    ob.location = location
    collection.objects.link(ob)
    return ob
