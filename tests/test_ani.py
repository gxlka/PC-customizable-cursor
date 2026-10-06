import struct
import unittest

from PIL import Image

from wingline.ani import encode_ani
from wingline.cur import encode_cur


def sample_frames():
    frames = []
    for index in range(8):
        image = Image.new("RGBA", (64, 64), (20 + index, 30, 40, 255))
        frames.append(encode_cur([(image, (60, 31))]))
    return frames


def read_chunk(data, offset):
    chunk_id = data[offset : offset + 4]
    size = struct.unpack_from("<I", data, offset + 4)[0]
    payload_start = offset + 8
    payload_end = payload_start + size
    return chunk_id, data[payload_start:payload_end], payload_end + (size & 1)


class AniEncodingTests(unittest.TestCase):
    def test_ani_has_eight_frames_seven_jiffy_steps_and_looping_sequence(self):
        frames = sample_frames()

        data = encode_ani(frames)

        self.assertEqual(b"RIFF", data[:4])
        self.assertEqual(len(data) - 8, struct.unpack_from("<I", data, 4)[0])
        self.assertEqual(b"ACON", data[8:12])

        chunks = []
        offset = 12
        while offset < len(data):
            chunk_id, payload, offset = read_chunk(data, offset)
            chunks.append((chunk_id, payload))
        self.assertEqual(len(data), offset)

        anih = next(payload for chunk_id, payload in chunks if chunk_id == b"anih")
        self.assertEqual((36, 8, 8, 64, 64, 32, 1, 7, 3), struct.unpack("<9I", anih))

        rate = next(payload for chunk_id, payload in chunks if chunk_id == b"rate")
        self.assertEqual((7,) * 8, struct.unpack("<8I", rate))
        sequence = next(payload for chunk_id, payload in chunks if chunk_id == b"seq ")
        self.assertEqual(tuple(range(8)), struct.unpack("<8I", sequence))

        frames_list = next(payload for chunk_id, payload in chunks if chunk_id == b"LIST")
        self.assertEqual(b"fram", frames_list[:4])
        icons = []
        offset = 4
        while offset < len(frames_list):
            chunk_id, payload, offset = read_chunk(frames_list, offset)
            self.assertEqual(b"icon", chunk_id)
            icons.append(payload)
        self.assertEqual(frames, icons)
        self.assertEqual(len(frames_list), offset)

    def test_ani_rejects_empty_or_incomplete_frame_sets(self):
        with self.assertRaises(ValueError):
            encode_ani([])
        with self.assertRaises(ValueError):
            encode_ani(sample_frames()[:-1])

    def test_ani_rejects_nonpositive_frame_delay(self):
        with self.assertRaises(ValueError):
            encode_ani(sample_frames(), frame_jiffies=0)

    def test_ani_rejects_frame_with_truncated_bitmap_payload(self):
        frame = bytearray(sample_frames()[0])
        data_length = struct.unpack_from("<I", frame, 14)[0]
        struct.pack_into("<I", frame, 14, data_length - 1)
        frames = sample_frames()
        frames[0] = bytes(frame[:-1])

        with self.assertRaisesRegex(ValueError, "complete 64x64 CUR image"):
            encode_ani(frames)


if __name__ == "__main__":
    unittest.main()
