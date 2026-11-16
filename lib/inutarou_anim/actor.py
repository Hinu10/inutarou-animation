"""ショットで使う「役者」（Rig を包んで、全ボーンをまとめてキーする）と姿勢の書き方。

  P(head=dict(rot=5), arm_L=dict(rot=-120))   … 姿勢（ボーン名 → Pose）の短縮
  merge(a, b, ...)                             … 後ろの姿勢で上書き
  actor.key(frame, pose)                       … 指定のないボーンは base（なければ休み姿勢）
  actor.reach(pose, "arm_R", "fore_R", target) … 2本の骨で手首を target に届かせる（IK）
"""
from __future__ import annotations

import math

from .skeleton import Pose, PoseDict, solve_two_bone


def P(**kw) -> PoseDict:
    """Pose(loc, rot, scale) の短縮。P(head=dict(rot=5), arm_L=Pose(rot=-120))"""
    out = {}
    for bone, v in kw.items():
        out[bone] = v if isinstance(v, Pose) else Pose(**v)
    return out


def merge(*poses: PoseDict) -> PoseDict:
    out: PoseDict = {}
    for p in poses:
        out.update(p)
    return out


def at(pos, scale: float = 1.0, flip: bool = False) -> PoseDict:
    """root を pos に置く（flip で左右反転）。"""
    return {"root": Pose(loc=tuple(pos), scale=(-scale if flip else scale, scale))}


class Actor:
    """全ボーンをまとめてキーする（指定のないボーンは base の姿勢）。"""

    def __init__(self, rig, base: PoseDict):
        self.rig = rig
        self.design = rig.design
        self.base = dict(base)
        self.bones = [b.name for b in rig.design.BONES]
        self.last: PoseDict = self.full({})

    def full(self, pose: PoseDict) -> PoseDict:
        p = {b: Pose() for b in self.bones}
        p.update(self.base)
        p.update(pose)
        return p

    def key(self, frame: int, pose: PoseDict, interp: str | None = None,
            ease: str | None = None) -> PoseDict:
        full = self.full(pose)
        self.rig.key_pose(frame, full, interp, ease)
        self.last = full
        return full

    def hold(self, a: int, b: int, pose: PoseDict | None = None) -> PoseDict:
        """a〜b を同じ姿勢で止める（止め絵・静寂）。"""
        pose = self.last if pose is None else pose
        self.key(a, pose, "CONSTANT")
        return self.key(b, pose, "CONSTANT")

    def world(self, bone: str, pose: PoseDict, p) -> tuple[float, float]:
        return self.rig.world(bone, self.full(pose), p)

    # ------------------------------------------------------------ 腕の IK
    def reach(self, pose: PoseDict, upper: str, fore: str, target, bend: int = 1,
              hand: str | None = None, hand_rot: float | None = None) -> PoseDict:
        """upper/fore の2本の骨で、fore の先端（子の骨の付け根）を target（ワールド）に届かせる。

        bend = +1 / -1 でひじの曲がる向きが変わる。hand_rot を渡すと手のワールド角をそろえる。
        返り値は pose に upper/fore（と hand）を書き足したもの。
        """
        bones = self.rig.fk.bones
        full = self.full(pose)
        tip_bone = hand or next(b.name for b in bones.values() if b.parent == fore)
        s_rest, e_rest, w_rest = bones[upper].head, bones[fore].head, bones[tip_bone].head
        shoulder = self.rig.world(upper, full, s_rest)
        l1 = math.dist(shoulder, self.rig.world(upper, full, e_rest))
        elbow_now = self.rig.world(upper, full, e_rest)
        l2 = math.dist(elbow_now, self.rig.world(fore, full, w_rest))
        up_w, lo_w = solve_two_bone(shoulder, l1, l2, target, bend)
        if full["root"].scale[0] < 0:
            raise NotImplementedError("左右反転した役者の IK は未対応")
        parent = self.rig.fk.world_angle(bones[upper].parent, full)
        rest_up = math.degrees(math.atan2(e_rest[1] - s_rest[1], e_rest[0] - s_rest[0])) - 90
        rest_lo = math.degrees(math.atan2(w_rest[1] - e_rest[1], w_rest[0] - e_rest[0])) - 90
        out = dict(pose)
        out[upper] = Pose(rot=up_w - rest_up - parent, scale=full[upper].scale)
        out[fore] = Pose(rot=(lo_w - rest_lo) - (up_w - rest_up), scale=full[fore].scale)
        if hand_rot is not None:
            out[tip_bone] = Pose(rot=hand_rot - lo_w)
        return out
