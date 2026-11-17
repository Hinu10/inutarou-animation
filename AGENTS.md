# AGENTS.md — Codex など AI エージェント向けの作業ルール

このリポジトリは『犬太朗』の 2D アニメ制作環境。Claude Code と Codex で分担している。
まず `README.md` と `docs/production/` を読むこと。

## 担当と編集してよい場所

| 場所 | 主担当 | もう一方 |
| --- | --- | --- |
| `lib/inutarou_anim/`（リグ・描画・効果・タイミング） | Claude Code | 読むだけ。直したいときは Issue で依頼 |
| `assets/characters/`・`assets/backgrounds/`（仮デザインのデータ） | Claude Code | 読むだけ |
| `scenes/<episode>/shots/`（各ショットの演技） | Claude Code | 読むだけ |
| `scripts/build_shot.py`・`scripts/preview_characters.py` | Claude Code | 読むだけ |
| `scripts/render/`（書き出しの自動化） | **Codex** | Claude Code は読むだけ（`render_shot.sh` は暫定版として Claude Code が置いた。以後 Codex が引き継ぐ） |
| `scripts/qc/`（品質チェック） | **Codex** | 読むだけ |
| `scripts/audio/`（音声の配置・ミックス・口パク） | **Codex** | 読むだけ（`temp_audio.py` は暫定版。以後 Codex が引き継ぐ） |
| `tests/`・`.github/`（CI） | **Codex** | `tests/test_basics.py` は Claude Code が置いた最低限のもの。追加・整理は Codex |
| `scenes/<episode>/cuts.toml`（カット表） | 共有 | 触る前に Issue で宣言する。秒数・セリフの変更はオーナーの OK を取る |
| `assets/` の正式素材、`docs/characters/` | オーナー（人） | AI は差し替え手順に沿って組み込むだけ |

## 同じファイルを同時に編集しないための運用

1. 作業の前に、対応する Issue に「着手します（Codex）」とコメントし、担当ラベルを確認する。
2. ブランチ名は `codex/<Issue番号>-<内容>`（Claude Code は `claude/...`）。`main` へは PR でマージ。
3. 上の表で自分の担当でない場所を変える必要が出たら、変更せずに Issue を立てて依頼する。
4. `cuts.toml` を変える PR は、それだけの小さな PR にする（ほかの変更と混ぜない）。
5. 1つの作業 = 1コミット（または 1 PR）。コミットメッセージに Issue 番号を書く。

## よく使うコマンド

```sh
python3 -m unittest discover -s tests                 # Blender なしのテスト
scripts/render/render_shot.sh s6_ending               # 試作を MP4 まで（1920x1080, 約1分）
PERCENT=50 scripts/render/render_shot.sh s6_ending    # 確認用の半分サイズ
```

`Blender` は `/Applications/Blender.app`（5.2.3 LTS）。別の場所なら `BLENDER=...` を付ける。

## Codex に最初にお願いしたい作業（優先順）

| 優先 | Issue | 内容 | 今あるもの |
| --- | --- | --- | --- |
| 1 | #54 (6-6) | CI: PR ごとに `python3 -m unittest discover -s tests` を動かす（Blender 不要の範囲） | テスト 11 件 |
| 2 | #51 (6-3) | 出力の検査スクリプト `scripts/qc/`: 解像度 1920x1080・24fps・尺・H.264/AAC・黒コマ・無音区間 | `render_shot.sh` の最後に ffprobe 表示だけ |
| 3 | #52 (6-4) / #53 (6-5) | カット表と書き出した尺のずれ、参照ファイル（`audio = ...`、shot、preset）の存在チェック | `tests/test_basics.py` に一部 |
| 4 | #49 (6-1) / #50 (6-2) | 書き出しの一般化: カット単位・話全体、shot ごとの MP4 を結合、未実装カットは黒＋カット名の仮画面で埋める | `scripts/render/render_shot.sh`（ショット単位のみ） |
| 5 | #45 (5-5) / #48 (5-8) | 音の自動配置の引き継ぎ、ラウドネス正規化（例: -24 LUFS 前後。基準はオーナーと決める） | `scripts/audio/temp_audio.py`（ピーク正規化のみ） |
| 6 | #46 (5-6) | 口パク: 音声から口の形とタイミングを出し、`cuts.toml` か別ファイルに書き出す形式を提案 | 口の variant: 犬太朗 default/smug/open/ouch、海斗 default/grit/o/scream |
| 7 | #55 (6-7) | 大きいファイルの方針（`.blend`・音声・動画）。今は `renders/` を Git に入れていない | `.gitignore` |

注意: 仮の音や絵を「完成」と報告しないこと。`status = "temp"` は仮素材で実装済み、`"final"` は正式素材で完成。
