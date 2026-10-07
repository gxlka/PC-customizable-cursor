from __future__ import annotations

import math
from typing import Iterable
from functools import lru_cache

from PIL import Image, ImageDraw

from .roles import CursorRole, ROLE_ORDER, Theme
from .designs import render_role


SUPPORTED_SIZES = (32, 48, 64, 96, 128, 192, 256)
SUPERSAMPLE = 8
from .timing import ANIMATION_FRAMES
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
    outline = max(2, round(scale * 0.040))
    draw.polygon(pixels, fill=theme.fill)
    _rounded_line(draw, pixels + [pixels[0]], theme.edge, outline, 1)


@lru_cache(maxsize=1400)
def _render_base_cursor(
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
        raise ValueError(f"Animated cursor frame must be between 0 and {ANIMATION_FRAMES-1}.")

    canvas = size * SUPERSAMPLE
    image = Image.new("RGBA", (canvas, canvas), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image, "RGBA")
    custom_hotspot = None
    if theme.style in {"hand", "macos", "beam"}:
        image, custom_hotspot = render_role(role.glyph, theme, canvas, frame, with_hotspot=True)
    elif role.glyph == "arrow":
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
    if custom_hotspot is not None and role.glyph == "arrow":
        hotspot = tuple(max(0,min(size-1,round(value/SUPERSAMPLE))) for value in custom_hotspot)
    elif role.glyph == "arrow":
        if theme.style == "windows":
            hotspot = (round(size * 0.10), round(size * 0.05))
        else:
            hotspot = (round(size * 0.35), round(size * 0.09))
    else:
        hotspot = (size // 2, size // 2)
    return image, hotspot


def render_cursor(role: CursorRole, theme: Theme, size: int, frame: int = 0):
    """Render quiet, role-specific motion around a stationary click point."""
    if not 0 <= frame < ANIMATION_FRAMES:
        raise ValueError(f"Animated cursor frame must be between 0 and {ANIMATION_FRAMES-1}.")
    if role.glyph in ("wait", "appstarting"):
        image, hotspot = _render_base_cursor(role, theme, size, frame)
        return image.copy(), hotspot
    base, hotspot = _render_base_cursor(role, theme, size, 0)
    wave = math.sin(frame * math.tau / ANIMATION_FRAMES)
    if abs(wave) < 1e-10:
        return base.copy(), hotspot
    sx = sy = 1.0
    angle = 0.0
    if role.key == "arrow":
        if theme.style == "beam":
            sx += .035 * wave  # A small serif opening, not a tint sweep.
        else:
            angle = .85 * wave  # Tip-anchored settle; no hotspot drift.
    elif role.key == "ibeam":
        sx += .040 * wave
    elif role.key in {"sizens", "sizewe", "sizenwse", "sizenesw", "sizeall", "uparrow"}:
        # Extend along the role's direction, leaving the center anchored.
        if role.key == "sizewe": sx += .024 * wave
        elif role.key in {"sizens", "uparrow"}: sy += .024 * wave
        else: sx += .016 * wave; sy += .016 * wave
    elif role.key == "nwpen":
        angle = 1.1 * wave
    elif role.key == "hand":
        angle = .7 * wave
        sy += .008 * wave
    elif role.key in {"help", "person", "pin"}:
        sy += .014 * wave
    else:
        sx += .012 * wave
        sy += .012 * wave
    # Warp a high-resolution neutral render, never repeatedly resample the
    # previous frame. Both palettes keep the original fill and border colors.
    source, _ = _render_base_cursor(role, theme, 256, 0)
    hx, hy = (value * 256 / size for value in hotspot)
    t = math.radians(angle)
    a, b = math.cos(t)/sx, math.sin(t)/sx
    d, e = -math.sin(t)/sy, math.cos(t)/sy
    matrix = (a, b, hx-a*hx-b*hy, d, e, hy-d*hx-e*hy)
    image = source.transform(source.size, Image.Transform.AFFINE, matrix,
                             resample=Image.Resampling.BICUBIC)
    if size != 256:
        image = image.resize((size,size), Image.Resampling.LANCZOS)
    if role.key == "arrow" and theme.style != "beam":
        # Keep the fingertip region completely still, with a soft transition
        # into the moving body. This also protects the small top margin.
        limit = hotspot[1] + max(1, round(size*.025))
        fade = max(2, round(size*.08))
        mask = Image.new("L", (1,size))
        mask.putdata([max(0,min(255,round(255*(limit+fade-y)/fade))) for y in range(size)])
        mask = mask.resize((size,size),Image.Resampling.NEAREST)
        image = Image.composite(base,image,mask)
    pixels = bytearray(image.tobytes())
    for i in range(0,len(pixels),4):
        if pixels[i+3] < 8: pixels[i:i+4] = b"\x00\x00\x00\x00"
    return Image.frombytes("RGBA",(size,size),bytes(pixels)), hotspot
