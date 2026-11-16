"""仮キャラクターの確認用シート（表情・手の形）を1枚の PNG に書き出す。

使い方:
  blender -b --factory-startup --python scripts/preview_characters.py -- OUT.png
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "lib"))

import bpy  # noqa: E402

from inutarou_anim import anim, stage  # noqa: E402
from inutarou_anim.rig import Pose, Rig  # noqa: E402

out = sys.argv[sys.argv.index("--") + 1] if "--" in sys.argv else str(ROOT / "renders/preview/characters.png")

sc = stage.reset_scene(24, 1920, 1080)
sc.render.use_stamp = True
col = sc.collection
cam = stage.CameraRig(col)
cam.frame(1, (0, 0), 16)

INU = [("default", {}), ("smug", {"eye_L": "smug", "eye_R": "smug", "mouth": "smug", "paw_L": "thumb",
                                  "card": "hold"}),
       ("open", {"mouth": "open", "eye_L": "spark", "eye_R": "spark"}),
       ("ouch", {"mouth": "ouch", "eye_L": "squeeze", "eye_R": "squeeze"})]
KAI = [("default", {}), ("glare", {"eye_L": "glare", "eye_R": "glare", "brow_L": "angry",
                                   "brow_R": "angry", "mouth": "grit", "vein": "on", "hand_L": "phone"}),
       ("scream", {"head": "scream", "eye_L": "rage", "eye_R": "rage", "brow_L": "angry",
                   "brow_R": "angry", "mouth": "scream", "vein": "on", "hand_R": "fist"})]

inu_d = stage.load_design("inutarou")
kai_d = stage.load_design("kaito")
cro_d = stage.load_design("karasu")

for i, (label, sw) in enumerate(INU):
    r = Rig(inu_d, col, name=f"inu_{label}", depth=float(i))
    r.key(1, "root", Pose(loc=(-6.6 + i * 2.3, 0.6), scale=(0.62, 0.62)))
    r.swaps(1, sw)
    t = stage.Text(col, f"犬太朗 {label}", (-6.6 + i * 2.3, 0.15), 0.3, color="white", name=f"t{i}")
    t.show(1, pop=False)
for i, (label, sw) in enumerate(KAI):
    r = Rig(kai_d, col, name=f"kai_{label}", depth=float(i))
    r.key(1, "root", Pose(loc=(-5.5 + i * 2.6, -4.2), scale=(0.52, 0.52)))
    r.swaps(1, sw)
    if label == "scream":
        r.tint(1, ["head"], "kaito_skin_red", 0.5)
    t = stage.Text(col, f"海斗 {label}", (-5.5 + i * 2.6, -4.35), 0.3, color="white", name=f"k{i}")
    t.show(1, pop=False)
for i, wing in enumerate(("up", "default", "down")):
    r = Rig(cro_d, col, name=f"crow_{wing}", depth=float(i))
    r.key(1, "root", Pose(loc=(3.2 + i * 1.6, -3.0), scale=(0.8, 0.8)))
    r.swaps(1, {"wing": wing, "beak": "hold" if i == 1 else "default"})

title = stage.Text(col, "仮キャラクター（TEMP・正式デザインではありません）", (2.6, 3.9), 0.42,
                   color="white", name="title")
title.show(1, pop=False)
anim.finalize([o for o in bpy.data.objects] + [o.data for o in bpy.data.objects if o.data], [])
sc.frame_start = sc.frame_end = 1
sc.frame_set(1)
Path(out).parent.mkdir(parents=True, exist_ok=True)
sc.render.filepath = str(Path(out).resolve())
bpy.ops.render.render(write_still=True)
print("wrote", out)
