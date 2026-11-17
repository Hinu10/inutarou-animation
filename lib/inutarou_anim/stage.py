"""シーン全体の準備（解像度・fps・色・カメラ・文字）。"""
from __future__ import annotations

import importlib.util
import math
import random
from pathlib import Path

import bpy

from . import anim, gp as gpw
from .palette import rgba
from .shapes import Shape

ROOT = Path(__file__).resolve().parents[2]
FONT_CANDIDATES = [
    "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc",
    "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
    "/System/Library/Fonts/Hiragino Sans GB.ttc",
]


def load_design(name: str):
    """assets/characters/<name>/design.py を読み込む。"""
    path = ROOT / "assets" / "characters" / name / "design.py"
    spec = importlib.util.spec_from_file_location(f"design_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load_module(path: Path, name: str):
    """ファイルからモジュールを読み込む（同じ name は使い回す。dataclass のため sys.modules に登録）。"""
    import sys
    if name in sys.modules and getattr(sys.modules[name], "__file__", None) == str(path):
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def reset_scene(fps: int, width: int, height: int, scale_percent: int = 100):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.fps = fps
    sc.render.resolution_x = width
    sc.render.resolution_y = height
    sc.render.resolution_percentage = scale_percent
    sc.render.engine = "BLENDER_EEVEE"
    sc.view_settings.view_transform = "Standard"
    sc.view_settings.look = "None"
    sc.render.film_transparent = False
    world = bpy.data.worlds.new("world")
    world.use_nodes = True
    world.node_tree.nodes["Background"].inputs[0].default_value = rgba("white")
    sc.world = world
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGB"
    # 仮素材であることを画面に焼き込む
    sc.render.use_stamp = True
    for attr in ("use_stamp_date", "use_stamp_time", "use_stamp_render_time", "use_stamp_frame",
                 "use_stamp_camera", "use_stamp_lens", "use_stamp_scene", "use_stamp_filename",
                 "use_stamp_memory", "use_stamp_hostname", "use_stamp_frame_range",
                 "use_stamp_sequencer_strip"):
        if hasattr(sc.render, attr):
            setattr(sc.render, attr, False)
    sc.render.use_stamp_marker = True
    sc.render.use_stamp_frame = True
    sc.render.use_stamp_note = True
    sc.render.stamp_note_text = "TEMP ASSETS / PROTOTYPE"
    sc.render.stamp_font_size = 18
    sc.render.stamp_background = (0, 0, 0, 0.45)
    return sc


# ---------------------------------------------------------------- カメラ

class CameraRig:
    """カット切り替え（CONSTANT）用の親と、揺れ用の子を持つカメラ。"""

    def __init__(self, collection):
        self.cut = bpy.data.objects.new("camera_cut", None)
        collection.objects.link(self.cut)
        cam = bpy.data.cameras.new("camera")
        cam.type = "ORTHO"
        cam.ortho_scale = 16
        cam.clip_start, cam.clip_end = 0.1, 100
        self.cam_data = cam
        self.cam = bpy.data.objects.new("camera", cam)
        collection.objects.link(self.cam)
        self.cam.parent = self.cut
        self.cam.rotation_euler = (math.pi / 2, 0, 0)
        self.cut.location = (0, -30, 0)
        bpy.context.scene.camera = self.cam

    def frame(self, frame: int, center, scale: float, interp: str = "CONSTANT",
              ease: str | None = None):
        self.cut.location = (center[0], -30, center[1])
        self.cut.keyframe_insert("location", frame=frame)
        anim.mark(self.cut, "location", frame, interp, ease)
        self.cam_data.ortho_scale = scale
        self.cam_data.keyframe_insert("ortho_scale", frame=frame)
        anim.mark(self.cam_data, "ortho_scale", frame, interp, ease)

    def shake(self, start: int, end: int, amp: float, seed: int = 0, every: int = 1,
              decay: bool = True):
        rnd = random.Random(seed)
        for f in range(start, end + 1, every):
            k = 1 - (f - start) / max(1, end - start) if decay else 1.0
            self.cam.location = (rnd.uniform(-amp, amp) * k, 0, rnd.uniform(-amp, amp) * k)
            self.cam.keyframe_insert("location", frame=f)
            anim.mark(self.cam, "location", f, "CONSTANT", None)
        self.cam.location = (0, 0, 0)
        self.cam.keyframe_insert("location", frame=end + 1)
        anim.mark(self.cam, "location", end + 1, "CONSTANT", None)


# ---------------------------------------------------------------- 文字（擬音・テロップ）

def _font():
    for path in FONT_CANDIDATES:
        if Path(path).exists():
            return bpy.data.fonts.load(path, check_existing=True)
    return None


class Text:
    """縁取りつきの文字（擬音・テロップ）。

    Blender の文字オブジェクトは GP の絵より奥に回ってしまうので、文字の輪郭を
    取り出して GP のストロークとして描く（キャラクターと同じように重なり順が効く）。
    """

    def __init__(self, collection, body: str, pos, size: float, color: str = "yellow",
                 outline: str = "black", outline_width: float = 0.06, rot: float = 0.0,
                 depth: float = -5.0, name: str = "text"):
        self.ob = gpw.new_object(name, collection, location=(pos[0], depth, pos[1]))
        self.ob.rotation_euler = (0.0, -math.radians(rot), 0.0)
        self.layer = self.ob.data.layers.new("text")
        self.layer.use_lights = False
        contours = _glyph_contours(body, size)
        self.shapes = ([Shape(c, fill=None, line=outline, width=outline_width * 2 + size * 0.06)
                        for c in contours] +
                       [Shape(c, fill=color, line=None) for c in contours])
        gpw.set_frame(self.layer, self.ob.data, 1, [])

    def show(self, start: int, end: int | None = None, pop: bool = True):
        _write_text(self.layer, self.ob.data, start, self.shapes)
        if pop:
            for f, s in ((start, 0.4), (start + 2, 1.15), (start + 4, 1.0)):
                self.ob.scale = (s, s, s)
                self.ob.keyframe_insert("scale", frame=f)
                anim.mark(self.ob, "scale", f, "LINEAR", None)
        if end is not None:
            gpw.set_frame(self.layer, self.ob.data, end, [])


def _write_text(layer, data, frame, shapes):
    """文字は全体で1つの塗り番号にする（「ロ」などの穴が抜けるように）。"""
    gpw.set_frame(layer, data, frame, shapes)
    for f in layer.frames:
        if f.frame_number == frame:
            for st in f.drawing.strokes:
                if st.fill_id:
                    st.fill_id = 1
            f.drawing.tag_positions_changed()


def _glyph_contours(body: str, size: float) -> list[list[tuple[float, float]]]:
    from mathutils.geometry import interpolate_bezier
    cu = bpy.data.curves.new("_tmp_text", "FONT")
    cu.body = body
    font = _font()
    if font:
        cu.font = font
    cu.size = size
    cu.align_x = "CENTER"
    cu.align_y = "CENTER"
    ob = bpy.data.objects.new("_tmp_text", cu)
    bpy.context.scene.collection.objects.link(ob)
    dg = bpy.context.evaluated_depsgraph_get()
    ev = ob.evaluated_get(dg)
    curve = ev.to_curve(dg)
    out = []
    for sp in curve.splines:
        pts = sp.bezier_points
        n = len(pts)
        poly = []
        for i in range(n):
            a, b = pts[i], pts[(i + 1) % n]
            seg = interpolate_bezier(a.co, a.handle_right, b.handle_left, b.co, 6)
            poly.extend((v.x, v.y) for v in seg[:-1])
        if len(poly) >= 3:
            out.append(poly)
    ev.to_curve_clear()
    bpy.data.objects.remove(ob)
    bpy.data.curves.remove(cu)
    return out


# ---------------------------------------------------------------- 効果（GP）

class FX:
    """効果用の GP オブジェクト。レイヤーごとに表示区間を描き込む。"""

    def __init__(self, collection, name: str = "fx", depth: float = -2.0):
        self.ob = gpw.new_object(name, collection, location=(0, depth, 0))
        self.data = self.ob.data
        self.layers = {}

    def layer(self, name: str):
        if name not in self.layers:
            lay = self.data.layers.new(name)
            lay.use_lights = False
            gpw.set_frame(lay, self.data, 1, [])
            self.layers[name] = lay
        return self.layers[name]

    def draw(self, name: str, frame: int, shapes: list[Shape]):
        gpw.set_frame(self.layer(name), self.data, frame, shapes)

    def clear(self, name: str, frame: int):
        gpw.set_frame(self.layer(name), self.data, frame, [])


def background(collection, layers: dict[str, list[Shape]], name: str = "bg", depth: float = 10.0):
    fx = FX(collection, name=name, depth=depth)
    for lname, shapes in layers.items():
        fx.draw(lname, 1, shapes)
    return fx


def add_marker(frame: int, name: str):
    bpy.context.scene.timeline_markers.new(name, frame=frame)
