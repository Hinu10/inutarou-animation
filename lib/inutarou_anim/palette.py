"""色の一覧（仮）。正式な色指定が決まったらここを差し替える。

名前で色を参照するので、キャラクターの design.py は色コードを直接持たない。
"""
from __future__ import annotations

PALETTE: dict[str, str] = {
    # 共通
    "line": "#2b1d14",        # 主線（こげ茶）
    "white": "#ffffff",
    "black": "#1a1410",
    "shadow": "#00000033",
    "red": "#e8312a",
    "yellow": "#ffe14d",
    "gold": "#f5c542",
    "pink": "#f4a1a8",
    "sweat": "#bfe6ff",
    "flash": "#fffbe8",
    # 犬太朗（仮）
    "dog_fur": "#e7a25a",
    "dog_fur_dark": "#c97d36",
    "dog_white": "#fff6e8",
    "dog_nose": "#2a1c16",
    "dog_inner_ear": "#f2b8a0",
    "dog_tongue": "#ef7a86",
    "dog_mouth": "#7a2e2e",
    # 海斗（仮）
    "kaito_skin": "#ffdcc0",
    "kaito_skin_red": "#ff9a8a",
    "kaito_hair": "#2a2a35",
    "kaito_shirt": "#4b7bd1",
    "kaito_shirt_dark": "#3a62ad",
    "kaito_pants": "#3b3f4a",
    "kaito_mouth": "#7a1f1f",
    "kaito_vein": "#e8312a",
    # カラス（仮）
    "crow": "#25262e",
    "crow_beak": "#3d3f4a",
    # 背景（仮）
    "wall": "#f3e7d3",
    "wall_shade": "#e6d6bd",
    "floor": "#c9935f",
    "floor_dark": "#b07c4b",
    "window_sky": "#bfe3ff",
    "window_frame": "#f9f9f6",
    "sofa": "#6f9e7a",
    "sofa_dark": "#5b8466",
    "card_blue": "#2f5fb3",
    "phone": "#30323a",
    "phone_screen": "#e9f4ff",
    "potechi": "#f2c230",
    "focus_bg": "#fff3d6",
    "impact_bg": "#ffcc33",
    "impact_bg2": "#ff7a1a",
}


def rgba(name: str) -> tuple[float, float, float, float]:
    """色名 → (r, g, b, a)。Blender のマテリアルは linear なので sRGB から変換する。"""
    h = PALETTE.get(name, name).lstrip("#")
    r, g, b = (int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))
    a = int(h[6:8], 16) / 255 if len(h) == 8 else 1.0

    def lin(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    return (lin(r), lin(g), lin(b), a)
