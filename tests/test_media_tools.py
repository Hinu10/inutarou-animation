"""Media calculations tested without ffmpeg or Blender."""
import array
import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


qc = module("qc", "scripts/qc/check_output.py")
lip = module("lip", "scripts/audio/lip_sync.py")


class MediaToolsTest(unittest.TestCase):
    def test_render_duration_mismatch_is_rejected(self):
        ep = qc.timeline.load("episode01")
        shot = "s6_ending"
        expected = sum(c.frames for c in ep.cuts_of_shot(shot))
        info = {"streams": [
            {"codec_type": "video", "codec_name": "h264", "width": 1920, "height": 1080,
             "avg_frame_rate": "24/1", "nb_frames": str(expected - 10)},
            {"codec_type": "audio", "codec_name": "aac"}],
            "format": {"duration": str((expected - 10) / 24)}}
        with patch.object(qc, "probe", return_value=info):
            errors = qc.check(Path("fake.mp4"), ep, shot, scan=False)
        self.assertTrue(any("frames:" in error for error in errors))

    def test_mouth_keys_follow_audio_energy(self):
        data = array.array("h", [0] * 2000 + [16000] * 2000 + [0] * 2000)
        keys = lip.mouth_frames(data, 24, 1, 3, 0.03)
        self.assertEqual(keys[0], {"frame": 1, "state": "closed"})
        self.assertIn({"frame": 2, "state": "open"}, keys)


if __name__ == "__main__":
    unittest.main()
