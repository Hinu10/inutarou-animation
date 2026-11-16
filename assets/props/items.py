"""第1話の小道具 — 仮素材（TEMP）。正式な絵ではない。

ショットのスクリプトから ctx.props() で読み、効果用の GP（stage.FX）に描く。
キャラクターが手に持つ小道具は、手の variant としてキャラクター側にも入っている
（海斗の hand_*: potechi / wallet / phone、犬太朗の card / controller）。

座標はワールド座標。関数は形（Shape のリスト）を返すだけ。
"""
from inutarou_anim.shapes import Shape, ellipse, rect, transform

TEMP = True


def potechi_bag(x: float, y: float, rot: float = 0.0, scale: float = 1.0) -> list[Shape]:
    """ポテチの袋（x, y = 袋の底の中心）。"""
    w, h = 0.62 * scale, 0.82 * scale
    tf = lambda pts: transform(pts, tx=x, ty=y + h / 2, rot=rot)
    return [Shape(tf(rect(0, 0, w, h, r=0.05 * scale)), fill="potechi", width=0.045),
            Shape(tf(rect(0, h / 2 - 0.05 * scale, w * 1.06, 0.09 * scale)), fill="potechi_red",
                  width=0.03),
            Shape(tf(rect(0, -h / 2 + 0.05 * scale, w * 1.06, 0.09 * scale)), fill="potechi_red",
                  width=0.03),
            Shape(tf(ellipse(0, -0.02 * scale, 0.18 * scale, 0.14 * scale)), fill="gold", width=0.025),
            Shape(tf(ellipse(0.05 * scale, 0.02 * scale, 0.05 * scale, 0.04 * scale)), fill="white",
                  line=None, opacity=0.7)]


def crumbs(x: float, y: float, n: int = 5, seed: int = 0) -> list[Shape]:
    """袋があった跡のポテチのかけら。"""
    import random
    rnd = random.Random(seed)
    out = []
    for _ in range(n):
        cx, cy = x + rnd.uniform(-0.45, 0.45), y + rnd.uniform(-0.03, 0.05)
        out.append(Shape(ellipse(cx, cy, 0.07, 0.04, rot=rnd.uniform(0, 3)), fill="gold", width=0.02))
    return out


def phone_screen(x: float, y: float, h: float = 3.0) -> list[Shape]:
    """スマホの画面（大写し用。x, y = 中心、h = 高さ）。文字は stage.Text で上に重ねる。"""
    w = h * 0.52
    out = [Shape(rect(x, y, w, h, r=h * 0.08), fill="phone", width=0.06),
           Shape(rect(x, y, w * 0.88, h * 0.86, r=h * 0.04), fill="phone_screen", line=None),
           Shape(rect(x, y + h * 0.4, w * 0.3, h * 0.03, r=h * 0.015), fill="phone", line=None)]
    return out


def notification(x: float, y: float, w: float, h: float) -> list[Shape]:
    """通知のカード（白い角丸＋アイコン）。"""
    return [Shape(rect(x, y, w, h, r=h * 0.2), fill="notify_bg", width=0.04),
            Shape(rect(x - w / 2 + h * 0.45, y, h * 0.55, h * 0.55, r=h * 0.12), fill="red", line=None)]


def card(x: float, y: float, rot: float = 0.0, scale: float = 1.0) -> list[Shape]:
    """海斗のクレジットカード。"""
    tf = lambda pts: transform(pts, tx=x, ty=y, rot=rot)
    return [Shape(tf(rect(0, 0, 0.5 * scale, 0.32 * scale, r=0.04 * scale)), fill="card_blue",
                  width=0.035),
            Shape(tf(rect(0, -0.08 * scale, 0.5 * scale, 0.05 * scale)), fill="white", line=None,
                  opacity=0.6),
            Shape(tf(rect(-0.12 * scale, 0.03 * scale, 0.1 * scale, 0.08 * scale, r=0.015)),
                  fill="gold", width=0.015)]
