"""ショット（いくつかのカットのまとまり）を Blender で組み立て、連番 PNG に書き出す。

  blender -b --factory-startup --python scripts/build_shot.py -- \
      --episode episode01 --shot s6_ending [--out renders/episode01/s6_ending/frames]
      [--percent 50] [--still 1421] [--save-blend renders/episode01/s6_ending/s6_ending.blend]
      [--no-render]

- カメラ（カットごとの位置と大きさ）とマーカーは cuts.toml から自動で入れる。
- 動きは scenes/<episode>/shots/<shot>.py の build(ctx) が入れる。
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))

import bpy  # noqa: E402

from inutarou_anim import anim, stage, timeline  # noqa: E402


class Ctx:
    def __init__(self, episode, collection, camera):
        self.episode = episode
        self.collection = collection
        self.camera = camera
        self.ones: list[tuple[int, int]] = []
        self._designs = {}

    def design(self, name: str):
        if name not in self._designs:
            self._designs[name] = stage.load_design(name)
        return self._designs[name]

    def background_module(self, name: str):
        return stage.load_module(ROOT / "assets" / "backgrounds" / f"{name}.py", f"bg_{name}")

    def text(self, body, pos, size, **kw):
        return stage.Text(self.collection, body, pos, size, **kw)


def camera_for(ep_raw_cams: dict, cut) -> tuple[tuple[float, float], float]:
    cam = dict(cut.camera)
    if "preset" in cam:
        base = dict(ep_raw_cams[cam["preset"]])
        base.update({k: v for k, v in cam.items() if k != "preset"})
        cam = base
    return tuple(cam.get("center", (0.0, 0.0))), float(cam.get("scale", 16.0))


def main(argv: list[str]) -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--episode", default="episode01")
    ap.add_argument("--shot", required=True)
    ap.add_argument("--out", default=None, help="連番 PNG の出力先フォルダ")
    ap.add_argument("--percent", type=int, default=100, help="解像度の倍率（確認用に 50 など）")
    ap.add_argument("--still", default=None, help="このコマだけ書き出す（絶対フレーム。カンマ区切りで複数）")
    ap.add_argument("--save-blend", default=None)
    ap.add_argument("--no-render", action="store_true")
    args = ap.parse_args(argv)

    import tomllib
    ep = timeline.load(args.episode)
    raw = tomllib.loads((ROOT / "scenes" / args.episode / "cuts.toml").read_text(encoding="utf-8"))
    cuts = ep.cuts_of_shot(args.shot)
    if not cuts:
        sys.exit(f"cuts.toml に shot = \"{args.shot}\" のカットがありません")

    sc = stage.reset_scene(ep.fps, ep.width, ep.height, args.percent)
    col = sc.collection
    cam = stage.CameraRig(col)
    for c in cuts:
        center, scale = camera_for(raw.get("cameras", {}), c)
        cam.frame(c.start, center, scale)
        stage.add_marker(c.start, c.id)

    shot = stage.load_module(ROOT / "scenes" / args.episode / "shots" / f"{args.shot}.py",
                             f"shot_{args.shot}")
    ctx = Ctx(ep, col, cam)
    info = shot.build(ctx) or {}

    ids = []
    for ob in bpy.data.objects:
        ids.append(ob)
        if ob.data is not None:
            ids.append(ob.data)
    anim.finalize(ids, anim.segments([(c.start, c.end) for c in cuts], ctx.ones, step=2))
    # カメラは 1コマ打ち（揺れ）、文字の表示切り替えも 1コマ単位
    for ob in [cam.cam, cam.cut] + [o for o in bpy.data.objects if o.type == "FONT" or
                                     o.name.endswith("_root")]:
        for fc in anim.fcurves(ob):
            for m in list(fc.modifiers):
                fc.modifiers.remove(m)
    for fc in anim.fcurves(cam.cam_data):
        for m in list(fc.modifiers):
            fc.modifiers.remove(m)

    sc.frame_start = info.get("frame_start", cuts[0].start)
    sc.frame_end = info.get("frame_end", cuts[-1].end)

    if args.save_blend:
        Path(args.save_blend).parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(Path(args.save_blend).resolve()))
        print("saved", args.save_blend)

    if args.no_render:
        return
    out = Path(args.out or ROOT / "renders" / args.episode / args.shot / "frames").resolve()
    out.mkdir(parents=True, exist_ok=True)
    if args.still is not None:
        for f in [int(x) for x in str(args.still).split(",")]:
            sc.frame_set(f)
            sc.render.filepath = str(out / f"still_{f:04d}.png")
            bpy.ops.render.render(write_still=True)
            print("wrote", sc.render.filepath)
        return
    # 出力の番号は 1 から（ショットの頭 = 0001）
    for i, f in enumerate(range(sc.frame_start, sc.frame_end + 1), start=1):
        sc.frame_set(f)
        sc.render.filepath = str(out / f"{i:04d}.png")
        bpy.ops.render.render(write_still=True)
    print("wrote", sc.frame_end - sc.frame_start + 1, "frames to", out)


if __name__ == "__main__":
    main(sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else [])
