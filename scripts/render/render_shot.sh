#!/usr/bin/env bash
# ショットを MP4（H.264 / AAC）まで書き出す。
#
#   scripts/render/render_shot.sh s6_ending            # 本番解像度 1920x1080
#   PERCENT=50 scripts/render/render_shot.sh s6_ending # 確認用（960x540）
#
# 出力: renders/<episode>/<shot>/<shot>.mp4（連番 PNG・音声・.blend も同じフォルダ）
# 暫定版。今後の自動化・検査は Codex の担当（AGENTS.md 参照）。
set -euo pipefail

SHOT="${1:?shot 名を指定してください（例: s6_ending）}"
EPISODE="${EPISODE:-episode01}"
PERCENT="${PERCENT:-100}"
BLENDER="${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}"
PYTHON="${PYTHON:-python3}"

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/renders/$EPISODE/$SHOT"
FRAMES="$OUT/frames"
FPS="$(grep -m1 '^fps' "$ROOT/scenes/$EPISODE/cuts.toml" | tr -dc '0-9')"

mkdir -p "$OUT"
rm -f "$FRAMES"/*.png 2>/dev/null || true

echo "== 1/3 映像（Blender）"
"$BLENDER" -b --factory-startup --python "$ROOT/scripts/build_shot.py" -- \
  --episode "$EPISODE" --shot "$SHOT" --percent "$PERCENT" \
  --out "$FRAMES" --save-blend "$OUT/$SHOT.blend" 2>&1 | grep -E "wrote|saved|Error|Traceback|File \"" | grep -v "Not freed" || true
ls "$FRAMES"/0001.png >/dev/null

echo "== 2/3 仮音声"
"$PYTHON" "$ROOT/scripts/audio/temp_audio.py" --episode "$EPISODE" --shot "$SHOT" --out "$OUT/audio.wav"

echo "== 3/3 MP4"
ffmpeg -v error -y -framerate "$FPS" -i "$FRAMES/%04d.png" -i "$OUT/audio.wav" \
  -c:v libx264 -pix_fmt yuv420p -crf 18 -preset medium -r "$FPS" \
  -c:a aac -b:a 192k -shortest -movflags +faststart "$OUT/$SHOT.mp4"
ffprobe -v error -show_entries stream=codec_name,width,height,r_frame_rate:format=duration \
  -of compact "$OUT/$SHOT.mp4"
echo "wrote $OUT/$SHOT.mp4"
