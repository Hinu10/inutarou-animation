# 制作環境

2026-11-13 に確認した環境。別の Mac で再現するときはこれに合わせる。

| ソフト | バージョン | 用途 | 入れ方 |
| --- | --- | --- | --- |
| macOS | 27.0.1（Apple Silicon / arm64） | — | — |
| Blender | **5.2.3 LTS** | 作画（Grease Pencil v3）・リグ・レンダリング | https://www.blender.org/download/ から `/Applications/Blender.app` |
| Blender 内蔵 Python | 3.13.13 | `scripts/build_shot.py` などを実行 | Blender に同梱 |
| Python（システム） | 3.13.9（3.11 以上なら可） | 仮音声の生成・テスト | 標準ライブラリだけで動く（numpy 不要） |
| ffmpeg / ffprobe | 9.0.2（libx264 入り） | 連番 PNG → MP4（H.264 / AAC） | `brew install ffmpeg` |
| say（macOS 標準） | — | 仮音声（セリフ） | macOS に同梱。日本語の声 Reed / Rocko / Kyoko を使用 |
| フォント | ヒラギノ角ゴシック W8 / W6 | 擬音・テロップ（仮） | macOS に同梱 |

今回の作業で**追加インストールしたものはありません**（Blender・ffmpeg は元から入っていた）。

## Blender の場所を変えたいとき

```sh
BLENDER=/path/to/Blender scripts/render/render_shot.sh s6_ending
```

## 注意

- Blender 4.2 以前の Grease Pencil（v2）とは API が違うので動かない。5.x を使う。
- レンダリングエンジンは EEVEE。色は Standard（Filmic / AgX を使うと色がくすむ）。
- ディスクの空きに注意。試作 5 秒の書き出し（PNG 120 枚＋.blend＋MP4）で約 170MB。
