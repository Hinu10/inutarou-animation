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
       ("ouch", {"mouth": "ouch", "eye_L": "squeeze", "eye_R": "squeeze"}),
       ("angry", {"mouth": "shout", "eye_L": "angry", "eye_R": "angry", "brow_L": "angry",
                  "brow_R": "angry", "paw_R": "point"}),
       ("wide", {"mouth": "talk", "eye_L": "wide", "eye_R": "wide", "controller": "hold"}),
       ("pout", {"mouth": "pout", "eye_L": "smug", "eye_R": "smug"})]
INU_POSE = {"angry": {"arm_R": Pose(rot=95)},
            "wide": {"arm_L": Pose(rot=35), "paw_L": Pose(rot=-35), "arm_R": Pose(rot=-35),
                     "paw_R": Pose(rot=35)}}
KAI = [("default", {}), ("glare", {"eye_L": "glare", "eye_R": "glare", "brow_L": "angry",
                                   "brow_R": "angry", "mouth": "grit", "vein": "on", "hand_L": "phone"}),
       ("scream", {"head": "scream", "eye_L": "rage", "eye_R": "rage", "brow_L": "angry",
                   "brow_R": "angry", "mouth": "scream", "vein": "on", "hand_R": "fist"}),
       ("half", {"eye_L": "half", "eye_R": "half", "mouth": "talk", "hand_R": "potechi"}),
       ("dot", {"eye_L": "dot", "eye_R": "dot", "brow_L": "worried", "brow_R": "worried",
                "mouth": "wavy", "hand_L": "wallet"}),
       ("sorry", {"eye_L": "closed", "eye_R": "closed", "brow_L": "worried", "brow_R": "worried",
                  "mouth": "smile"})]

inu_d = stage.load_design("inutarou")
kai_d = stage.load_design("kaito")
cro_d = stage.load_design("karasu")

for i, (label, sw) in enumerate(INU):
    r = Rig(inu_d, col, name=f"inu_{label}", depth=float(i))
    r.key(1, "root", Pose(loc=(-6.9 + i * 2.0, 0.6), scale=(0.55, 0.55)))
    for b, ps in INU_POSE.get(label, {}).items():
        r.key(1, b, ps)
    r.swaps(1, sw)
    t = stage.Text(col, f"犬太朗 {label}", (-6.9 + i * 2.0, 0.15), 0.26, color="white", name=f"t{i}")
    t.show(1, pop=False)
for i, (label, sw) in enumerate(KAI):
    r = Rig(kai_d, col, name=f"kai_{label}", depth=float(i))
    r.key(1, "root", Pose(loc=(-6.9 + i * 1.75, -4.2), scale=(0.5, 0.5)))
    r.swaps(1, sw)
    if label == "scream":
        r.tint(1, ["head"], "kaito_skin_red", 0.5)
    t = stage.Text(col, f"海斗 {label}", (-6.9 + i * 1.75, -4.35), 0.26, color="white", name=f"k{i}")
    t.show(1, pop=False)
for i, wing in enumerate(("up", "default", "down")):
    r = Rig(cro_d, col, name=f"crow_{wing}", depth=float(i))
    r.key(1, "root", Pose(loc=(4.3 + i * 1.3, -3.0), scale=(0.65, 0.65)))
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
