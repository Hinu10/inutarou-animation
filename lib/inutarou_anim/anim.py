"""キーフレームの後処理（補間の種類・イージング・2コマ打ち）。

アニメのタイミングは「なめらかに作ってから 2コマ打ち（on twos）に落とす」。
- interp: "CONSTANT"（パッと切り替え）/ "LINEAR" / "BEZIER"（既定）/ "BACK"（行き過ぎて戻る）など
- ease:   "EASE_IN" / "EASE_OUT" / "EASE_IN_OUT"
"""
from __future__ import annotations

import bpy

_marks: dict[tuple[int, str, int], tuple[str | None, str | None]] = {}


def mark(id_, data_path: str, frame: int, interp: str | None, ease: str | None) -> None:
    _marks[(id_.session_uid, data_path, int(frame))] = (interp, ease)


def fcurves(id_) -> list:
    ad = getattr(id_, "animation_data", None)
    if not ad or not ad.action:
        return []
    act = ad.action
    try:
        from bpy_extras import anim_utils
        bag = anim_utils.action_get_channelbag_for_slot(act, ad.action_slot)
        return list(bag.fcurves) if bag else []
    except (ImportError, AttributeError):
        return list(act.fcurves)


def segments(cuts: list[tuple[int, int]], ones: list[tuple[int, int]], step: int = 2
             ) -> list[tuple[int, int, int]]:
    """カット（開始, 終了）ごとに (開始, 終了, 何コマ打ちか) を作る。ones の区間は 1コマ打ち。

    2コマ打ちの刻みはカットの頭にそろえる（カットが変わった瞬間に前の絵が残らないように）。
    """
    out: list[tuple[int, int, int]] = []
    for a, b in cuts:
        cur = a
        for oa, ob in sorted(ones):
            if ob < cur or oa > b:
                continue
            if oa > cur:
                out.append((cur, oa - 1, step))
            out.append((max(oa, cur), min(ob, b), 1))
            cur = min(ob, b) + 1
        if cur <= b:
            out.append((cur, b, step))
    return out


def finalize(ids, segs: list[tuple[int, int, int]]) -> None:
    """補間を設定し、区間ごとに N コマ打ちにする。"""
    for id_ in ids:
        for fc in fcurves(id_):
            for kp in fc.keyframe_points:
                key = (id_.session_uid, fc.data_path, int(round(kp.co[0])))
                interp, ease = _marks.get(key, (None, None))
                kp.interpolation = interp or "BEZIER"
                if ease:
                    kp.easing = ease
                if kp.interpolation == "BEZIER":
                    kp.handle_left_type = kp.handle_right_type = "AUTO_CLAMPED"
            fc.update()
            for a, b, step in segs:
                if step <= 1:
                    continue
                m = fc.modifiers.new("STEPPED")
                m.frame_step = step
                m.frame_offset = a
                m.use_frame_start = m.use_frame_end = True
                # 終了を先に入れる（開始 > 終了 になると開始が切り詰められるため）
                m.frame_end = b
                m.frame_start = a
