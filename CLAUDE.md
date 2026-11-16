# CLAUDE.md

Claude Code の担当はアニメーション実装（`lib/inutarou_anim/`・`assets/characters/`・`assets/backgrounds/`・`scenes/*/shots/`）。
担当の境界と運用は `AGENTS.md`、仕組みは `docs/production/approach.md` を参照。

- 返事・ドキュメントは日本語。
- 仮素材は `TEMP = True` のまま。正式素材ができるまで「完成」と書かない。
- 絵を変えたら `scripts/preview_characters.py` か `scripts/build_shot.py --still` で実際に書き出して目で確認する。
- `scripts/render/`・`scripts/qc/`・`scripts/audio/`・`tests/`・CI は Codex の担当。変えたいときは Issue で依頼する。
