"""Blender なしで動く基本テスト（python3 -m unittest discover -s tests）。

ここにあるのは Claude Code が実装時に置いた最低限のもの。
品質チェックの拡充（6-3〜6-5）は Codex の担当。
"""
import importlib.util
import math
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))

from inutarou_anim import timeline  # noqa: E402
from inutarou_anim.shapes import compose, dent_warp, ellipse, inflate_warp  # noqa: E402
from inutarou_anim.skeleton import FK2D, Bone, Pose, solve_two_bone  # noqa: E402

CHARACTERS = ["inutarou", "kaito", "karasu"]


def load_design(name):
    path = ROOT / "assets" / "characters" / name / "design.py"
    spec = importlib.util.spec_from_file_location(f"design_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


class TimelineTest(unittest.TestCase):
    def setUp(self):
        self.ep = timeline.load("episode01")

    def test_total_about_60_seconds(self):
        self.assertAlmostEqual(self.ep.frames / self.ep.fps, 60.0, delta=3.0)

    def test_cuts_are_contiguous(self):
        f = 1
        for c in self.ep.cuts:
            self.assertEqual(c.start, f, c.id)
            f += c.frames

    def test_unique_ids(self):
        ids = [c.id for c in self.ep.cuts]
        self.assertEqual(len(ids), len(set(ids)))

    def test_cues_inside_their_cut(self):
        for c in self.ep.cuts:
            for q in c.cues:
                self.assertTrue(c.start <= q.frame <= c.end, f"{c.id} {q.text or q.name}")

    def test_prototype_shot_is_3_to_5_seconds(self):
        cuts = self.ep.cuts_of_shot("s6_ending")
        sec = sum(c.frames for c in cuts) / self.ep.fps
        self.assertTrue(3.0 <= sec <= 5.0, sec)

    def test_camera_presets_exist(self):
        import tomllib
        raw = tomllib.loads((ROOT / "scenes/episode01/cuts.toml").read_text(encoding="utf-8"))
        for c in self.ep.cuts:
            preset = c.camera.get("preset")
            if preset:
                self.assertIn(preset, raw["cameras"], c.id)


class DesignTest(unittest.TestCase):
    def test_parts_reference_existing_bones_and_default_variant(self):
        for name in CHARACTERS:
            d = load_design(name)
            bones = {b.name for b in d.BONES}
            for b in d.BONES:
                if b.parent:
                    self.assertIn(b.parent, bones, f"{name}:{b.name}")
            for p in d.PARTS:
                self.assertIn(p.bone, bones, f"{name}:{p.name}")
                self.assertIn(p.default, p.variants, f"{name}:{p.name}")
                for v, fn in p.variants.items():
                    for s in fn():
                        self.assertGreaterEqual(len(s.pts), 2, f"{name}:{p.name}:{v}")
            for part in getattr(d, "FACE_PARTS", []):
                self.assertIn(part, {p.name for p in d.PARTS}, f"{name}:{part}")

    def test_temp_flag(self):
        # 正式デザインが来るまでは仮であることを明示しておく
        for name in CHARACTERS:
            self.assertTrue(load_design(name).TEMP, name)


class GeometryTest(unittest.TestCase):
    def test_fk_rotation_about_bone_head(self):
        fk = FK2D([Bone("root", None, (0, 0)), Bone("arm", "root", (1, 1))])
        p = fk.apply("arm", {"arm": Pose(rot=90)}, (1, 0))
        self.assertAlmostEqual(p[0], 2.0)
        self.assertAlmostEqual(p[1], 1.0)

    def test_two_bone_reaches_target(self):
        s, t = (0.0, 0.0), (1.2, 0.5)
        up, lo = solve_two_bone(s, 1.0, 1.0, t)
        e = (s[0] - math.sin(math.radians(up)), s[1] + math.cos(math.radians(up)))
        w = (e[0] - math.sin(math.radians(lo)), e[1] + math.cos(math.radians(lo)))
        self.assertAlmostEqual(w[0], t[0], places=4)
        self.assertAlmostEqual(w[1], t[1], places=4)

    def test_impact_warp_does_not_fold_outline(self):
        """ほおの変形で輪郭が折り返さない（自己交差しない）こと。"""
        warp = compose(dent_warp((-0.8, 1.05), (0.25, 1.0), 0.62, 0.8),
                       inflate_warp((-0.75, 2.0), 0.5, 0.3))
        pts = [warp(p) for p in ellipse(0, 2.1, 1.0, 0.8, n=96)]
        area = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1]
                   for i in range(len(pts))) / 2
        self.assertGreater(area, 0.5)   # 向きが反転していない
        n = len(pts)
        for i in range(n):
            a, b = pts[i], pts[(i + 1) % n]
            for j in range(i + 2, n):
                if (j + 1) % n == i:
                    continue
                c, d = pts[j], pts[(j + 1) % n]
                self.assertFalse(_cross(a, b, c, d), (i, j))


def _cross(a, b, c, d):
    def o(p, q, r):
        return (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
    return o(a, b, c) * o(a, b, d) < 0 and o(c, d, a) * o(c, d, b) < 0


if __name__ == "__main__":
    unittest.main()
