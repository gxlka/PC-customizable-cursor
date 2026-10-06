from __future__ import annotations

import math
from typing import Iterable

from PIL import Image, ImageDraw

from .roles import CursorRole, ROLE_ORDER, Theme
from .designs import render_role


SUPPORTED_SIZES = (32, 48, 64, 96, 128, 192, 256)
SUPERSAMPLE = 8
ANIMATION_FRAMES = 8
ARROW_SCALE = 0.84
WINDOWS_ARROW_SCALE = 0.77


def _point(point: tuple[float, float], scale: int) -> tuple[int, int]:
    return round(point[0] * scale), round(point[1] * scale)


def _cubic(
    start: tuple[float, float],
    control1: tuple[float, float],
    control2: tuple[float, float],
    end: tuple[float, float],
    steps: int = 18,
) -> list[tuple[float, float]]:
    points = [start]
    for index in range(1, steps + 1):
        t = index / steps
        inverse = 1 - t
        x = (
            inverse**3 * start[0]
            + 3 * inverse**2 * t * control1[0]
            + 3 * inverse * t**2 * control2[0]
            + t**3 * end[0]
        )
        y = (
            inverse**3 * start[1]
            + 3 * inverse**2 * t * control1[1]
            + 3 * inverse * t**2 * control2[1]
            + t**3 * end[1]
        )
        points.append((x, y))
    return points


def _arrow_path() -> list[tuple[float, float]]:
    segments = (
        ((0.15, 0.87), (0.23, 0.80), (0.42, 0.75), (0.58, 0.68)),
        ((0.58, 0.68), (0.73, 0.62), (0.87, 0.54), (0.95, 0.49)),
        ((0.95, 0.49), (0.79, 0.36), (0.61, 0.20), (0.35, 0.09)),
        ((0.35, 0.09), (0.25, 0.05), (0.20, 0.09), (0.19, 0.21)),
        ((0.19, 0.21), (0.17, 0.39), (0.14, 0.62), (0.13, 0.77)),
        ((0.13, 0.77), (0.12, 0.83), (0.12, 0.87), (0.15, 0.87)),
    )
    points: list[tuple[float, float]] = []
    for index, segment in enumerate(segments):
        curve = _cubic(*segment)
        points.extend(curve if index == 0 else curve[1:])
    tip = (0.35, 0.09)
    return [
        (tip[0] + (x - tip[0]) * ARROW_SCALE, tip[1] + (y - tip[1]) * ARROW_SCALE)
        for x, y in points
    ]


def _windows_arrow_path() -> list[tuple[float, float]]:
    segments = (
        ((0.10, 0.05), (0.075, 0.27), (0.08, 0.67), (0.13, 0.86)),
        ((0.13, 0.86), (0.18, 0.88), (0.25, 0.73), (0.34, 0.65)),
        ((0.34, 0.65), (0.39, 0.74), (0.44, 0.88), (0.48, 0.95)),
        ((0.48, 0.95), (0.53, 0.98), (0.59, 0.94), (0.62, 0.88)),
        ((0.62, 0.88), (0.58, 0.78), (0.53, 0.68), (0.49, 0.60)),
        ((0.49, 0.60), (0.60, 0.57), (0.72, 0.65), (0.80, 0.60)),
        ((0.80, 0.60), (0.64, 0.45), (0.30, 0.17), (0.10, 0.05)),
    )
    points: list[tuple[float, float]] = []
    for index, segment in enumerate(segments):
        curve = _cubic(*segment)
        points.extend(curve if index == 0 else curve[1:])
    tip = (0.10, 0.05)
    return [
        (tip[0] + (x - tip[0]) * WINDOWS_ARROW_SCALE, tip[1] + (y - tip[1]) * WINDOWS_ARROW_SCALE)
        for x, y in points
    ]


def _rounded_line(
    draw: ImageDraw.ImageDraw,
    points: Iterable[tuple[float, float]],
    color: str | tuple[int, int, int, int],
    width: int,
    scale: int,
) -> None:
    pixels = [_point(point, scale) for point in points]
    if len(pixels) < 2:
        return
    draw.line(pixels, fill=color, width=width, joint="curve")
    radius = max(1, width // 2)
    for x, y in (pixels[0], pixels[-1]):
        draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=color)


def _draw_arrow(draw: ImageDraw.ImageDraw, theme: Theme, scale: int) -> None:
    path = _windows_arrow_path() if theme.style == "windows" else _arrow_path()
    pixels = [_point(point, scale) for point in path]
    outline = max(2, round(scale * 0.022))
    draw.polygon(pixels, fill=theme.fill)
    _rounded_line(draw, pixels + [pixels[0]], theme.edge, outline, 1)


def render_cursor(
    role: CursorRole,
    theme: Theme,
    size: int,
    frame: int = 0,
) -> tuple[Image.Image, tuple[int, int]]:
    if size not in SUPPORTED_SIZES:
        raise ValueError(f"Unsupported cursor size {size}; use one of {SUPPORTED_SIZES}.")
    if role not in ROLE_ORDER:
        raise ValueError(f"Unknown cursor role: {role.key}")
    if role.glyph in ("wait", "appstarting") and not 0 <= frame < ANIMATION_FRAMES:
        raise ValueError("Animated cursor frame must be between 0 and 7.")

    canvas = size * SUPERSAMPLE
    image = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image, "RGBA")
    if role.glyph == "arrow":
        _draw_arrow(draw, theme, canvas)
    else:
        image = render_role(role.glyph, theme, canvas, frame)
    image = image.resize((size, size), Image.Resampling.LANCZOS)
    # Clear almost invisible resampling fringes and their RGB values.
    pixels = bytearray(image.tobytes())
    for index in range(0, len(pixels), 4):
        if pixels[index + 3] < 8:
            pixels[index:index + 4] = b"\x00\x00\x00\x00"
    image = Image.frombytes("RGBA", (size, size), bytes(pixels))
    if role.glyph == "arrow":
        if theme.style == "windows":
            hotspot = (round(size * 0.10), round(size * 0.05))
        else:
            hotspot = (round(size * 0.35), round(size * 0.09))
    else:
        hotspot = (size // 2, size // 2)
    return image, hotspot
