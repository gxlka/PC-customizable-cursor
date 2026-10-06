from __future__ import annotations

import struct
from collections.abc import Sequence

from PIL import Image

from .artwork import SUPPORTED_SIZES


_BITMAPINFOHEADER_SIZE = 40
_CUR_DIRECTORY_HEADER_SIZE = 6
_CUR_DIRECTORY_ENTRY_SIZE = 16


def _dib_image(image: Image.Image) -> bytes:
    rgba = image.convert("RGBA")
    width, height = rgba.size
    if width != height:
        raise ValueError("CUR images must be square.")

    xor_stride = width * 4
    xor_mask = bytearray()
    pixels = rgba.load()
    for y in range(height - 1, -1, -1):
        for x in range(width):
            red, green, blue, alpha = pixels[x, y]
            xor_mask.extend((blue, green, red, alpha))

    and_stride = ((width + 31) // 32) * 4
    and_mask = bytearray(and_stride * height)
    for y in range(height):
        row = height - 1 - y
        for x in range(width):
            if pixels[x, y][3] == 0:
                and_mask[row * and_stride + x // 8] |= 0x80 >> (x % 8)

    info = struct.pack(
        "<IiiHHIIiiII",
        _BITMAPINFOHEADER_SIZE,
        width,
        height * 2,
        1,
        32,
        0,
        len(xor_mask),
        0,
        0,
        0,
        0,
    )
    return info + xor_mask + and_mask


def encode_cur(images: Sequence[tuple[Image.Image, tuple[int, int]]]) -> bytes:
    """Encode one supported frame or the complete multi-resolution CUR set."""
    if len(images) not in (1, len(SUPPORTED_SIZES)):
        raise ValueError(
            f"CUR files require one image or images at sizes {SUPPORTED_SIZES}."
        )

    entries: list[tuple[int, int, bytes]] = []
    found_sizes: set[int] = set()
    for image, hotspot in images:
        if image.width != image.height or image.width not in SUPPORTED_SIZES:
            raise ValueError(f"CUR images must be square at one of {SUPPORTED_SIZES}.")
        size = image.width
        if size in found_sizes:
            raise ValueError(f"Duplicate CUR image size: {size}.")
        found_sizes.add(size)
        if (
            len(hotspot) != 2
            or any(not isinstance(value, int) or isinstance(value, bool) for value in hotspot)
            or not (0 <= hotspot[0] < size and 0 <= hotspot[1] < size)
        ):
            raise ValueError(f"Hotspot {hotspot!r} is outside the {size}x{size} image.")
        entries.append((size, size, _dib_image(image)))

    if len(images) > 1 and found_sizes != set(SUPPORTED_SIZES):
        raise ValueError(f"CUR files require exactly these sizes: {SUPPORTED_SIZES}.")

    entries.sort(key=lambda item: item[0])
    directory_size = _CUR_DIRECTORY_HEADER_SIZE + _CUR_DIRECTORY_ENTRY_SIZE * len(entries)
    data_offset = (directory_size + 3) & ~3
    directory = bytearray(struct.pack("<HHH", 0, 2, len(entries)))
    image_data = bytearray()

    for (image, hotspot), (width, height, dib) in zip(
        sorted(images, key=lambda item: item[0].width),
        sorted((entry[0], entry[1], entry[2]) for entry in entries),
    ):
        if data_offset > 0xFFFFFFFF or len(dib) > 0xFFFFFFFF:
            raise ValueError("CUR data is too large for its directory entry.")
        directory.extend(
            struct.pack(
                "<BBBBHHII",
                width & 0xFF,
                height & 0xFF,
                0,
                0,
                hotspot[0],
                hotspot[1],
                len(dib),
                data_offset,
            )
        )
        image_data.extend(b"\x00" * (data_offset - directory_size - len(image_data)))
        image_data.extend(dib)
        data_offset += len(dib)

    return bytes(directory + image_data)
