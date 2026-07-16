"""Gera o ícone do PrintQuote by BMR (calculadora de custos e precificação
para impressão 3D).

Identidade própria, independente do NozzleNote: usa a mesma paleta violeta
do app (theme.py), mas o símbolo é uma etiqueta de preço minimalista —
sem nenhuma referência ao ícone/nozzle do NozzleNote.

Uso: python scripts/generate_icon.py
Gera calc3d/ui/assets/icon.ico e PNGs em vários tamanhos.
"""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / "calc3d" / "ui" / "assets"
ASSETS.mkdir(parents=True, exist_ok=True)

CANVAS = 512
GRADIENT_START = (167, 139, 250)  # violet-400 (mesma paleta do app)
GRADIENT_END = (109, 40, 217)     # violet-700 (mesma paleta do app)


def _diagonal_gradient(size: int, start, end) -> Image.Image:
    grad = Image.new("RGB", (size, size))
    pixels = grad.load()
    max_t = (size - 1) * 2
    for y in range(size):
        for x in range(size):
            t = (x + y) / max_t
            r = round(start[0] + (end[0] - start[0]) * t)
            g = round(start[1] + (end[1] - start[1]) * t)
            b = round(start[2] + (end[2] - start[2]) * t)
            pixels[x, y] = (r, g, b)
    return grad


def _tag_polygon(size: int) -> list:
    body_left = size * 0.12
    body_right = size * 0.60
    top = size * 0.18
    bottom = size * 0.82
    tip_x = size * 0.92
    mid_y = size * 0.50
    return [
        (body_left, top),
        (body_right, top),
        (tip_x, mid_y),
        (body_right, bottom),
        (body_left, bottom),
    ]


def build_icon() -> Image.Image:
    gradient = _diagonal_gradient(CANVAS, GRADIENT_START, GRADIENT_END)

    mask = Image.new("L", (CANVAS, CANVAS), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.polygon(_tag_polygon(CANVAS), fill=255)

    hole_cx, hole_cy = CANVAS * 0.245, CANVAS * 0.335
    hole_r = CANVAS * 0.052
    mask_draw.ellipse(
        [hole_cx - hole_r, hole_cy - hole_r, hole_cx + hole_r, hole_cy + hole_r],
        fill=0,
    )

    icon = Image.new("RGBA", (CANVAS, CANVAS), (0, 0, 0, 0))
    icon.paste(gradient, (0, 0), mask)
    return icon


def main():
    icon = build_icon()
    icon.save(ASSETS / "icon_512.png")

    for size in (256, 128, 64, 32):
        icon.resize((size, size), Image.LANCZOS).save(ASSETS / f"icon_{size}.png")

    icon.save(
        ASSETS / "icon.ico",
        sizes=[(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
    )
    print(f"Ícones gerados em {ASSETS}")


if __name__ == "__main__":
    main()
