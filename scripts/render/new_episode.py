"""Create an episode cut-sheet skeleton without copying character assets."""
import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("episode", help="for example episode02")
    ap.add_argument("--title", default="新しい話")
    args = ap.parse_args()
    if not args.episode.startswith("episode") or not args.episode[7:].isdigit():
        ap.error("episode must look like episode02")
    folder = ROOT / "scenes" / args.episode
    if folder.exists():
        ap.error(f"already exists: {folder}")
    (folder / "shots").mkdir(parents=True)
    (folder / "cuts.toml").write_text(
        f'''[episode]
id = "{args.episode}"
title = "{args.title}"
fps = 24
width = 1920
height = 1080

[cameras]
wide = {{ center = [0.0, 0.0], scale = 16.0 }}

[[cut]]
id = "c01"
scene = 1
seconds = 2.0
camera = {{ preset = "wide" }}
action = "内容を記入"
status = "todo"
# shot = "s1_example"  # 実装したら shots/s1_example.py を作成
''', encoding="utf-8")
    print("created", folder)


if __name__ == "__main__":
    main()
