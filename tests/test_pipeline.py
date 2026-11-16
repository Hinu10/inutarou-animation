"""Cut-sheet checks that run without Blender or rendered media."""
import sys
import tomllib
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))
from inutarou_anim import timeline  # noqa: E402


class CutSheetChecks(unittest.TestCase):
    def test_references_and_timing(self):
        for sheet in (ROOT / "scenes").glob("*/cuts.toml"):
            with self.subTest(sheet=sheet):
                ep = timeline.load(sheet)
                raw = tomllib.loads(sheet.read_text(encoding="utf-8"))
                cameras = raw.get("cameras", {})
                self.assertGreater(ep.fps, 0)
                self.assertGreater(ep.frames, 0)
                self.assertEqual(ep.id, sheet.parent.name)
                ids = set()
                next_frame = 1
                for cut in ep.cuts:
                    with self.subTest(cut=cut.id):
                        self.assertNotIn(cut.id, ids)
                        ids.add(cut.id)
                        self.assertEqual(cut.start, next_frame)
                        self.assertGreater(cut.frames, 0)
                        next_frame = cut.end + 1
                        camera = cut.camera
                        if "preset" in camera:
                            self.assertIn(camera["preset"], cameras)
                        shot = cut.data.get("shot")
                        if cut.data.get("status") in ("temp", "final"):
                            self.assertTrue(shot, "implemented cut needs a shot")
                        if shot:
                            self.assertTrue((sheet.parent / "shots" / f"{shot}.py").is_file(), shot)
                        for cue in cut.cues:
                            self.assertLessEqual(cut.start, cue.frame)
                            self.assertLessEqual(cue.frame, cut.end)
                            if cue.audio:
                                path = ROOT / cue.audio
                                self.assertTrue(path.is_file(), cue.audio)
                                self.assertTrue(path.resolve().is_relative_to(ROOT), cue.audio)
                self.assertEqual(next_frame - 1, ep.frames)

    def test_shots_are_contiguous_for_rendering(self):
        for sheet in (ROOT / "scenes").glob("*/cuts.toml"):
            ep = timeline.load(sheet)
            seen = set()
            previous = None
            for cut in ep.cuts:
                shot = cut.data.get("shot")
                if shot != previous:
                    self.assertNotIn(shot, seen, f"{sheet}: noncontiguous shot {shot}")
                    seen.add(previous)
                previous = shot


if __name__ == "__main__":
    unittest.main()
