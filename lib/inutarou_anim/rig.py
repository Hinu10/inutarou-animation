"""キャラクターのリグ（骨組み）。

1キャラクター = アーマチュア 1つ + Grease Pencil オブジェクト 1つ。
GP のレイヤー 1枚 = パーツ 1つ（目・口・ほお・腕…）で、レイヤーはボーンに親子付けする。

- 動き（首・手足・伸縮）はボーンのキーフレーム
- 表情や手の形の切り替えはレイヤーの描き替え（GP のフレーム）
- ギャグの大げさな変形は「warp をかけた描き替え」をレイヤーごとに入れる

ボーンはすべて上向き（+Z）で作り、ロールを揃えているので、どのボーンでも
  loc = (右, 上)、rot = 反時計回り（度）、scale = (横, 縦)
で扱える。FK2D はこれと同じ計算を Python 側で行い、拳の位置合わせなどに使う。
"""
from __future__ import annotations

import math
from typing import Callable

import bpy
from mathutils import Vector

from . import anim, gp as gpw
from .shapes import Point, Shape
from .skeleton import FK2D, Bone, Part, Pose, PoseDict, solve_two_bone  # noqa: F401


class Rig:
    def __init__(self, design, collection, name: str | None = None, depth: float = 0.0):
        self.design = design
        self.name = name or design.NAME
        self.fk = FK2D(design.BONES)
        self.parts = {p.name: p for p in design.PARTS}
        self.depth = depth
        self._build(collection)

    # ------------------------------------------------------------ 組み立て
    def _build(self, collection) -> None:
        arm = bpy.data.armatures.new(f"{self.name}_rig")
        self.arm = bpy.data.objects.new(f"{self.name}_rig", arm)
        collection.objects.link(self.arm)
        self.arm.location = (0.0, self.depth, 0.0)
        view_layer = bpy.context.view_layer
        view_layer.objects.active = self.arm
        bpy.ops.object.mode_set(mode="EDIT")
        for b in self.design.BONES:
            eb = arm.edit_bones.new(b.name)
            eb.head = (b.head[0], 0.0, b.head[1])
            eb.tail = (b.head[0], 0.0, b.head[1] + b.length)
            eb.align_roll(Vector((0.0, -1.0, 0.0)))
            if b.parent:
                eb.parent = arm.edit_bones[b.parent]
                eb.use_connect = False
        bpy.ops.object.mode_set(mode="OBJECT")
        for pb in self.arm.pose.bones:
            pb.rotation_mode = "XYZ"
        self.arm.hide_render = True

        self.gp = gpw.new_object(self.name, collection, location=(0.0, self.depth, 0.0))
        self.layers = {}
        for part in self.design.PARTS:
            layer = self.gp.data.layers.new(part.name)
            layer.use_lights = False
            gpw.set_frame(layer, self.gp.data, 1, part.variants[part.default]())
            layer.parent = self.arm
            layer.parent_bone = part.bone
            self.layers[part.name] = layer

    # ------------------------------------------------------------ 動き
    def key(self, frame: int, bone: str, pose: Pose, interp: str | None = None,
            ease: str | None = None) -> None:
        pb = self.arm.pose.bones[bone]
        pb.location = (pose.loc[0], pose.loc[1], 0.0)
        pb.rotation_euler = (0.0, 0.0, math.radians(pose.rot))
        pb.scale = (pose.scale[0], pose.scale[1], 1.0)
        for path in ("location", "rotation_euler", "scale"):
            pb.keyframe_insert(path, frame=frame)
            anim.mark(self.arm, f'pose.bones["{bone}"].{path}', frame, interp, ease)

    def key_pose(self, frame: int, pose: PoseDict, interp: str | None = None,
                 ease: str | None = None) -> None:
        for bone, ps in pose.items():
            self.key(frame, bone, ps, interp, ease)

    # ------------------------------------------------------------ 描き替え
    def shapes(self, part: str, variant: str) -> list[Shape]:
        return self.parts[part].variants[variant]()

    def swap(self, frame: int, part: str, variant: str,
             warp: Callable[[Point], Point] | None = None) -> None:
        shapes = self.shapes(part, variant)
        if warp:
            shapes = [s.map(warp) for s in shapes]
        gpw.set_frame(self.layers[part], self.gp.data, frame, shapes)

    def swaps(self, frame: int, mapping: dict[str, str],
              warp: Callable[[Point], Point] | None = None) -> None:
        for part, variant in mapping.items():
            self.swap(frame, part, variant, warp)

    def tint(self, frame: int, parts: list[str], color: str, factor: float,
             interp: str | None = None) -> None:
        from .palette import rgba
        for part in parts:
            layer = self.layers[part]
            layer.tint_color = rgba(color)[:3]
            layer.tint_factor = factor
            for path in ("tint_color", "tint_factor"):
                dp = f'layers["{part}"].{path}'
                self.gp.data.keyframe_insert(dp, frame=frame)
                anim.mark(self.gp.data, dp, frame, interp, None)

    # ------------------------------------------------------------ 位置合わせ
    def world(self, bone: str, pose: PoseDict, p: Point) -> Point:
        return self.fk.apply(bone, pose, p)
