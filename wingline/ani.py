from __future__ import annotations

import struct
from collections.abc import Sequence


from .timing import ANIMATION_FRAMES as _FRAME_COUNT, FRAME_JIFFIES
_FRAME_SIZES = (64, 256)
_ANI_HEADER_SIZE = 36
_FLAG_ICON = 0x1
_FLAG_SEQUENCE = 0x2


def _chunk(chunk_id: bytes, payload: bytes) -> bytes:
    if len(chunk_id) != 4:
        raise ValueError("RIFF chunk identifiers must be four bytes.")
    if len(payload) > 0xFFFFFFFF:
        raise ValueError("RIFF chunk data is too large.")
    padding = b"\x00" if len(payload) & 1 else b""
    return chunk_id + struct.pack("<I", len(payload)) + payload + padding


def _validate_cursor_frame(frame: bytes) -> None:
    if len(frame) < 22:
        raise ValueError("ANI frames must contain a single 64px or 256px CUR image.")
    reserved, file_type, image_count = struct.unpack_from("<HHH", frame, 0)
    if reserved != 0 or file_type != 2 or image_count != 1:
        raise ValueError("ANI frames must contain a single 64px or 256px CUR image.")

    width, height, _, _, hot_x, hot_y, data_length, data_offset = struct.unpack_from(
        "<BBBBHHII", frame, 6
    )
    width = width or 256
    height = height or 256
    if (
        width not in _FRAME_SIZES
        or height != width
        or not (0 <= hot_x < width and 0 <= hot_y < height)
        or data_offset < 22
        or data_length == 0
        or data_offset + data_length > len(frame)
    ):
        raise ValueError("ANI frames must contain a valid single 64px or 256px CUR image.")
    if data_offset + 40 > len(frame):
        raise ValueError("ANI frames must contain a complete 64px or 256px CUR image.")
    dib_size, dib_width, doubled_height, planes, bit_count = struct.unpack_from(
        "<IiiHH", frame, data_offset
    )
    if (dib_size, dib_width, doubled_height, planes, bit_count) != (40, width, width*2, 1, 32):
        raise ValueError("ANI frames must contain a complete 64px or 256px CUR image.")
    xor_stride = ((width * bit_count + 31) // 32) * 4
    mask_stride = ((width + 31) // 32) * 4
    expected_data_length = dib_size + (xor_stride + mask_stride) * width
    if data_length != expected_data_length:
        raise ValueError("ANI frames must contain a complete 64px or 256px CUR image.")


def encode_ani(frames: Sequence[bytes], frame_jiffies: int = FRAME_JIFFIES) -> bytes:
    """Wrap smooth single-image 256 px CUR frames in a looping RIFF ANI file."""
    if len(frames) != _FRAME_COUNT:
        raise ValueError(f"ANI files require exactly {_FRAME_COUNT} cursor frames.")
    if (
        not isinstance(frame_jiffies, int)
        or isinstance(frame_jiffies, bool)
        or not 1 <= frame_jiffies <= 0xFFFFFFFF
    ):
        raise ValueError("Frame delay must be a positive 32-bit integer.")
    for frame in frames:
        _validate_cursor_frame(frame)
    sizes = {frame[6] or 256 for frame in frames}
    if len(sizes) != 1:
        raise ValueError("ANI frames must use one consistent canvas size.")
    frame_size = sizes.pop()

    header = struct.pack(
        "<9I",
        _ANI_HEADER_SIZE,
        _FRAME_COUNT,
        _FRAME_COUNT,
        frame_size,
        frame_size,
        32,
        1,
        frame_jiffies,
        _FLAG_ICON | _FLAG_SEQUENCE,
    )
    rates = struct.pack(f"<{_FRAME_COUNT}I", *(frame_jiffies for _ in frames))
    sequence = struct.pack(f"<{_FRAME_COUNT}I", *range(_FRAME_COUNT))
    animation_frames = b"".join(_chunk(b"icon", frame) for frame in frames)
    frame_list = _chunk(b"LIST", b"fram" + animation_frames)
    body = b"ACON" + _chunk(b"anih", header) + _chunk(b"rate", rates)
    body += _chunk(b"seq ", sequence) + frame_list
    if len(body) > 0xFFFFFFFF:
        raise ValueError("ANI file is too large for a RIFF size field.")
    return b"RIFF" + struct.pack("<I", len(body)) + body

