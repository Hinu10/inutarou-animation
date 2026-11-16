# 素材の差し替え方法

今の素材はすべて**仮（TEMP）**。正式な素材ができたら、ここの手順で入れ替える。
どの方法でも、**ボーン名・パーツ名・variant 名を変えない**ことが一番大事
（ショットのスクリプトは名前で指示しているので、名前が同じなら動きはそのまま使える）。

## キャラクター

場所: `assets/characters/<name>/design.py`（inutarou / kaito / karasu）

| 定義 | 中身 |
| --- | --- |
| `BONES` | 骨の名前・親・付け根の位置（休み姿勢の座標） |
| `PARTS` | パーツ（= GP レイヤー）の名前・付くボーン・variant（絵の種類）。上から奥→手前の順 |
| `FACE_PARTS` | ギャグの変形で一緒にゆがめるパーツ |
| `TEMP` | 仮なら `True`。正式に差し替えたら `False` にする |

`L` / `R` は**画面の左 / 右**（キャラクターから見た左右ではない）。

### 方法 A: 形のデータを書き換える（今のやり方）

各 variant の関数が返す `Shape`（点列・塗り色名・線色名・太さ）を、正式デザインの形に合わせて書き換える。
色は `lib/inutarou_anim/palette.py` の色名で指定するので、色だけ直すならパレットを変えればよい。
変更後は確認シートで見る:

```sh
/Applications/Blender.app/Contents/MacOS/Blender -b --factory-startup \
  --python scripts/preview_characters.py -- renders/preview/characters.png
```

### 方法 B: 正式デザインを Blender で手描きする

1. `scripts/render/render_shot.sh s6_ending` で出る `renders/episode01/s6_ending/s6_ending.blend` を開く。
2. キャラクターの GP オブジェクト（`inutarou` など）の、パーツ名のレイヤーに描き直す。
   各レイヤーはボーンに付いているので、描き直した絵もそのまま動く。
3. 描いた絵を design.py に取り込む仕組み（.blend から点列を書き出して variant にする）はまだ無い → 今後の課題。
   取り込むまでは、手描きした .blend は「その場で直した1回分」として扱う。

### 方法 C: SVG で受け取る（未実装）

デザイナーから SVG（パーツごとに 1ファイル、variant ごとにレイヤー）で受け取り、変換して design.py を作る案。
受け取り方が決まったら実装する。

### 守ること

- 付け根（ボーンの head）の位置を大きく変えたら `BONES` も合わせる。目・口などの位置合わせはボーン基準。
- 犬太朗の `FACE_PARTS` の絵は、変形したときに崩れないよう、閉じた形（closed）で描く。
- 正式デザインを入れたら `TEMP = False`・`VERSION` を更新し、`tests/` を通す。

## 背景

場所: `assets/backgrounds/<name>.py`。`layers()` がレイヤー名 → 形の一覧を返す。`SPOTS` はキャラクターを置く位置。
正式な背景画（PNG）に替える場合は、GP の代わりに画像を貼った板を置く仕組みを足す（未実装）。

## 小道具

今はキャラクターのパーツとして入っている（例: 犬太朗の `card`、海斗の `hand_L: phone`）。
話が進んで小道具が増えたら `assets/props/` に分ける。

## 音声・効果音

`scenes/episode01/cuts.toml` の `[[cut.line]]` / `[[cut.sfx]]` に `audio = "assets/audio/....wav"` を書くと、
仮音声（say / 合成音）の代わりにそのファイルが使われる。置き場所は `assets/audio/`。

## 擬音・テロップ

フォントは macOS のヒラギノ（`lib/inutarou_anim/stage.py` の `FONT_CANDIDATES`）。
正式なフォントが決まったらここを変える。
