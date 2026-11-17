#!/usr/bin/env bash
# Render one shot from cuts.toml and mux its cut-sheet audio.
set -euo pipefail

SHOT="${1:?shot 名を指定してください（例: s6_ending）}"
EPISODE="${EPISODE:-episode01}"
PERCENT="${PERCENT:-100}"
BLENDER="${BLENDER:-/Applications/Blender.app/Contents/MacOS/Blender}"
PYTHON="${PYTHON:-python3}"
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
OUT="$ROOT/renders/$EPISODE/$SHOT"
FRAMES="$OUT/frames"

read -r FPS COUNT < <("$PYTHON" "$ROOT/scripts/render/render_episode.py" info "$EPISODE" "$SHOT")
mkdir -p "$FRAMES"
find "$FRAMES" -maxdepth 1 -name '*.png' -delete

"$BLENDER" -b --factory-startup --python "$ROOT/scripts/build_shot.py" -- \
  --episode "$EPISODE" --shot "$SHOT" --percent "$PERCENT" \
  --out "$FRAMES" --save-blend "$OUT/$SHOT.blend"

actual=$(find "$FRAMES" -maxdepth 1 -name '*.png' | wc -l | tr -d ' ')
if [[ "$actual" != "$COUNT" ]]; then
  echo "PNG count: expected $COUNT, got $actual" >&2
  exit 1
fi

"$PYTHON" "$ROOT/scripts/audio/temp_audio.py" --episode "$EPISODE" --shot "$SHOT" --out "$OUT/audio.wav"
"$PYTHON" "$ROOT/scripts/audio/normalize.py" "$OUT/audio.wav" "$OUT/audio_normalized.wav"
ffmpeg -v error -y -framerate "$FPS" -i "$FRAMES/%04d.png" -i "$OUT/audio_normalized.wav" \
  -frames:v "$COUNT" -c:v libx264 -pix_fmt yuv420p -crf 18 -preset medium -r "$FPS" \
  -c:a aac -b:a 192k -af apad -t "$("$PYTHON" -c 'import sys; print(int(sys.argv[1])/int(sys.argv[2]))' "$COUNT" "$FPS")" \
  -movflags +faststart "$OUT/$SHOT.mp4"
"$PYTHON" "$ROOT/scripts/qc/check_output.py" "$OUT/$SHOT.mp4" --episode "$EPISODE" --shot "$SHOT" --percent "$PERCENT" --no-scan
echo "wrote $OUT/$SHOT.mp4"
