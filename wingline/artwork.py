from __future__ import annotations

import math
from typing import Iterable

from PIL import Image, ImageDraw

from .roles import CursorRole, ROLE_ORDER, Theme


SUPPORTED_SIZES = (32, 48, 64, 96, 128, 192, 256)
SUPERSAMPLE = 8
ANIMATION_FRAMES = 8
ARROW_SCALE = 0.64
ROLE_SCALE = 2.0


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


def _outlined_line(
    draw: ImageDraw.ImageDraw,
    points: Iterable[tuple[float, float]],
    theme: Theme,
    width: int,
    scale: int,
) -> None:
    points = list(points)
    _rounded_line(draw, points, theme.edge, width + max(2, width // 2), scale)
    _rounded_line(draw, points, theme.fill, width, scale)


def _draw_arrow(draw: ImageDraw.ImageDraw, theme: Theme, scale: int) -> None:
    path = _arrow_path()
    pixels = [_point(point, scale) for point in path]
    outline = max(4, round(scale * ARROW_SCALE * 0.055))
    draw.polygon(pixels, fill=theme.fill)
    _rounded_line(draw, pixels + [pixels[0]], theme.edge, outline, 1)


def _draw_circle(
    draw: ImageDraw.ImageDraw,
    center: tuple[float, float],
    radius: float,
    theme: Theme,
    scale: int,
    fill: str | tuple[int, int, int, int] | None = None,
    width: int | None = None,
) -> None:
    cx, cy = _point(center, scale)
    r = round(radius * scale)
    draw.ellipse(
        (cx - r, cy - r, cx + r, cy + r),
        fill=fill,
        outline=theme.edge,
        width=width or max(3, round(scale * 0.035)),
    )


def _draw_arrowheads(
    draw: ImageDraw.ImageDraw,
    start: tuple[float, float],
    end: tuple[float, float],
    theme: Theme,
    scale: int,
) -> None:
    dx, dy = end[0] - start[0], end[1] - start[1]
    angle = math.atan2(dy, dx)
    size = 0.075

    def head(tip: tuple[float, float], direction: float) -> list[tuple[float, float]]:
        left = (
            tip[0] - size * math.cos(direction - math.pi / 5),
            tip[1] - size * math.sin(direction - math.pi / 5),
        )
        right = (
            tip[0] - size * math.cos(direction + math.pi / 5),
            tip[1] - size * math.sin(direction + math.pi / 5),
        )
        return [left, tip, right]

    width = max(5, round(scale * 0.045))
    _outlined_line(draw, head(start, angle + math.pi), theme, width, scale)
    _outlined_line(draw, head(end, angle), theme, width, scale)


def _draw_spinner(
    draw: ImageDraw.ImageDraw,
    theme: Theme,
    scale: int,
    frame: int,
) -> None:
    center = (0.50, 0.50)
    radius = 0.115
    dot_radius = 0.025
    for index in range(8):
        angle = 2 * math.pi * index / 8 - math.pi / 2
        location = (
            center[0] + math.cos(angle) * radius,
            center[1] + math.sin(angle) * radius,
        )
        alpha = 150 + ((index - frame) % 8) * 15
        rgb = tuple(int(theme.fill[i : i + 2], 16) for i in (1, 3, 5))
        _draw_circle(
            draw,
            location,
            dot_radius,
            theme,
            scale,
            fill=(*rgb, min(alpha, 255)),
            width=1,
        )


def _draw_role_mark(
    draw: ImageDraw.ImageDraw,
    role: CursorRole,
    theme: Theme,
    scale: int,
    frame: int,
) -> None:
    width = max(4, round(scale * 0.04))
    if role.glyph == "arrow":
        return
    if role.glyph == "help":
        path = _cubic((0.40, 0.39), (0.40, 0.31), (0.47, 0.29), (0.52, 0.33), 10)
        path += _cubic((0.52, 0.33), (0.57, 0.37), (0.54, 0.41), (0.49, 0.45), 8)[1:]
        path += [(0.49, 0.49)]
        _outlined_line(draw, path, theme, width, scale)
        _draw_circle(draw, (0.49, 0.55), 0.012, theme, scale, fill=theme.fill, width=1)
    elif role.glyph == "appstarting":
        progress = frame / (ANIMATION_FRAMES - 1)
        outline_width = max(4, round(scale * 0.035))
        track = tuple(_point(point, scale) for point in ((0.18, 0.38), (0.82, 0.62)))
        radius = max(4, round(scale * 0.045))
        draw.rounded_rectangle(track, radius=radius, outline=theme.edge, width=outline_width)
        x = 0.24 + progress * 0.48
        slider = tuple(_point(point, scale) for point in ((x, 0.40), (x + 0.12, 0.60)))
        draw.rounded_rectangle(slider, radius=radius, fill=theme.fill, outline=theme.edge, width=outline_width)
    elif role.glyph == "wait":
        _draw_spinner(draw, theme, scale, frame)
    elif role.glyph == "crosshair":
        _draw_circle(draw, (0.50, 0.50), 0.075, theme, scale, width=width)
        _outlined_line(draw, [(0.34, 0.50), (0.66, 0.50)], theme, width, scale)
        _outlined_line(draw, [(0.50, 0.34), (0.50, 0.66)], theme, width, scale)
    elif role.glyph == "ibeam":
        _outlined_line(draw, [(0.50, 0.30), (0.50, 0.70)], theme, width, scale)
        _outlined_line(draw, [(0.40, 0.30), (0.60, 0.30)], theme, width, scale)
        _outlined_line(draw, [(0.40, 0.70), (0.60, 0.70)], theme, width, scale)
    elif role.glyph == "pen":
        _outlined_line(draw, [(0.35, 0.57), (0.55, 0.34)], theme, width + 1, scale)
        _outlined_line(draw, [(0.34, 0.61), (0.39, 0.56)], theme, width, scale)
        _outlined_line(draw, [(0.53, 0.36), (0.57, 0.32)], theme, width, scale)
    elif role.glyph == "no":
        _draw_circle(draw, (0.50, 0.50), 0.10, theme, scale, width=width)
        _outlined_line(draw, [(0.43, 0.57), (0.57, 0.43)], theme, width, scale)
    elif role.glyph == "resize_vertical":
        start, end = (0.50, 0.68), (0.50, 0.32)
        _outlined_line(draw, [start, end], theme, width, scale)
        _draw_arrowheads(draw, start, end, theme, scale)
    elif role.glyph == "resize_horizontal":
        start, end = (0.32, 0.50), (0.68, 0.50)
        _outlined_line(draw, [start, end], theme, width, scale)
        _draw_arrowheads(draw, start, end, theme, scale)
    elif role.glyph in ("resize_nwse", "resize_nesw"):
        if role.glyph == "resize_nwse":
            start, end = (0.32, 0.32), (0.68, 0.68)
        else:
            start, end = (0.68, 0.32), (0.32, 0.68)
        _outlined_line(draw, [start, end], theme, width, scale)
        _draw_arrowheads(draw, start, end, theme, scale)
    elif role.glyph == "move":
        center = (0.50, 0.50)
        _outlined_line(draw, [(center[0], 0.30), (center[0], 0.70)], theme, width, scale)
        _outlined_line(draw, [(0.30, center[1]), (0.70, center[1])], theme, width, scale)
        for start, end in (
            ((0.50, 0.40), (0.50, 0.30)),
            ((0.50, 0.60), (0.50, 0.70)),
            ((0.40, 0.50), (0.30, 0.50)),
            ((0.60, 0.50), (0.70, 0.50)),
        ):
            _outlined_line(draw, [start, end], theme, width, scale)
    elif role.glyph == "up":
        _outlined_line(draw, [(0.50, 0.70), (0.50, 0.30)], theme, width, scale)
        _outlined_line(draw, [(0.39, 0.42), (0.50, 0.30), (0.61, 0.42)], theme, width, scale)
    elif role.glyph == "hand":
        palm = [
            (0.39, 0.46),
            (0.40, 0.37),
            (0.45, 0.35),
            (0.47, 0.43),
            (0.48, 0.31),
            (0.53, 0.31),
            (0.54, 0.44),
            (0.56, 0.36),
            (0.60, 0.37),
            (0.59, 0.49),
            (0.56, 0.59),
            (0.48, 0.62),
            (0.42, 0.58),
        ]
        pixels = [_point(point, scale) for point in palm]
        draw.polygon(pixels, fill=theme.fill)
        _rounded_line(draw, pixels + [pixels[0]], theme.edge, width, 1)
        _outlined_line(draw, [(0.40, 0.49), (0.35, 0.45)], theme, width, scale)
    elif role.glyph == "pin":
        _draw_circle(draw, (0.47, 0.42), 0.095, theme, scale, fill=theme.fill, width=width)
        _outlined_line(draw, [(0.40, 0.48), (0.47, 0.60), (0.54, 0.48)], theme, width, scale)
        _draw_circle(draw, (0.47, 0.42), 0.025, theme, scale, fill=theme.fill, width=1)
    elif role.glyph == "person":
        _draw_circle(draw, (0.47, 0.38), 0.05, theme, scale, fill=theme.fill, width=width)
        shoulders = _cubic((0.35, 0.58), (0.35, 0.48), (0.59, 0.48), (0.59, 0.58), 12)
        _outlined_line(draw, shoulders, theme, width, scale)


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
        enlarged_canvas = round(canvas * ROLE_SCALE)
        role_image = Image.new("RGBA", (enlarged_canvas, enlarged_canvas), (0, 0, 0, 0))
        _draw_role_mark(ImageDraw.Draw(role_image, "RGBA"), role, theme, enlarged_canvas, frame)
        crop_offset = (enlarged_canvas - canvas) // 2
        image.alpha_composite(role_image.crop((crop_offset, crop_offset, crop_offset + canvas, crop_offset + canvas)))
    image = image.resize((size, size), Image.Resampling.LANCZOS)
    if role.glyph == "arrow":
        hotspot = (round(size * 0.35), round(size * 0.09))
    else:
        hotspot = (size // 2, size // 2)
    return image, hotspot
