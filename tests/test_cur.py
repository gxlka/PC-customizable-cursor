import struct
import unittest

from PIL import Image, ImageDraw

try:
    from wingline.cur import encode_cur
except ImportError:
    encode_cur = None


CURSOR_SIZES = (32, 48, 64, 96, 128, 192, 256)


def sample_images():
    images = []
    for size in CURSOR_SIZES:
        image = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        ImageDraw.Draw(image).rectangle(
            (0, 0, size // 2, size // 2),
            fill=(220, 40, 60, 255),
        )
        images.append((image, (size - 2, size // 2)))
    return images


def parse_cur(data):
    reserved, file_type, count = struct.unpack_from("<HHH", data, 0)
    entries = []
    for index in range(count):
        position = 6 + index * 16
        width, height, colors, entry_reserved, hot_x, hot_y, length, offset = (
            struct.unpack_from("<BBBBHHII", data, position)
        )
        entries.append(
            {
                "width": width or 256,
                "height": height or 256,
                "colors": colors,
                "reserved": entry_reserved,
                "hotspot": (hot_x, hot_y),
                "length": length,
                "offset": offset,
            }
        )
    return (reserved, file_type, count), entries


class CurEncodingTests(unittest.TestCase):
    def test_cur_directory_has_all_sizes_and_valid_hotspots_and_offsets(self):
        self.assertIsNotNone(encode_cur)
        data = encode_cur(sample_images())
        header, entries = parse_cur(data)

        self.assertEqual((0, 2, len(CURSOR_SIZES)), header)
        self.assertEqual(list(CURSOR_SIZES), [entry["width"] for entry in entries])
        for size, entry in zip(CURSOR_SIZES, entries):
            with self.subTest(size=size):
                self.assertEqual(size, entry["height"])
                self.assertEqual((size - 2, size // 2), entry["hotspot"])
                self.assertEqual(0, entry["colors"])
                self.assertEqual(0, entry["reserved"])
                self.assertGreaterEqual(entry["offset"], 6 + 16 * len(entries))
                self.assertGreater(entry["length"], 40)
                self.assertLessEqual(entry["offset"] + entry["length"], len(data))

                dib_size, width, doubled_height, planes, bit_count = struct.unpack_from(
                    "<IiiHH", data, entry["offset"]
                )
                self.assertEqual(40, dib_size)
                self.assertEqual(size, width)
                self.assertEqual(size * 2, doubled_height)
                self.assertEqual((1, 32), (planes, bit_count))

    def test_and_mask_marks_transparent_pixels(self):
        self.assertIsNotNone(encode_cur)
        data = encode_cur(sample_images())
        _, entries = parse_cur(data)
        entry = entries[0]
        size = entry["width"]
        xor_stride = size * 4
        and_stride = ((size + 31) // 32) * 4
        mask_start = entry["offset"] + 40 + xor_stride * size
        bottom_left_mask_byte = data[mask_start]
        self.assertTrue(bottom_left_mask_byte & 0x80)
        top_row_mask = mask_start + and_stride * (size - 1)
        self.assertEqual(0, data[top_row_mask] & 0x80)
        self.assertTrue(data[top_row_mask + 2] & 0x40)
        self.assertGreaterEqual(entry["length"], 40 + xor_stride * size + and_stride * size)

    def test_encoder_rejects_hotspot_outside_its_image(self):
        self.assertIsNotNone(encode_cur)
        images = sample_images()
        image, _ = images[0]
        images[0] = (image, (image.width, 0))
        with self.assertRaises(ValueError):
            encode_cur(images)

    def test_encoder_rejects_duplicate_sizes(self):
        self.assertIsNotNone(encode_cur)
        images = sample_images()
        images[-1] = (Image.new("RGBA", (32, 32)), (1, 1))
        with self.assertRaises(ValueError):
            encode_cur(images)

    def test_encoder_rejects_unsupported_and_nonsquare_images(self):
        self.assertIsNotNone(encode_cur)
        invalid_images = (
            Image.new("RGBA", (40, 40), (20, 30, 40, 255)),
            Image.new("RGBA", (32, 31), (20, 30, 40, 255)),
        )
        for image in invalid_images:
            with self.subTest(size=image.size), self.assertRaises(ValueError):
                encode_cur([(image, (1, 1))])

    def test_encoder_accepts_one_supported_size_for_ani_frames(self):
        self.assertIsNotNone(encode_cur)
        image = Image.new("RGBA", (64, 64), (20, 30, 40, 255))

        data = encode_cur([(image, (60, 31))])

        header, entries = parse_cur(data)
        self.assertEqual((0, 2, 1), header)
        self.assertEqual(64, entries[0]["width"])
        self.assertEqual(64, entries[0]["height"])
        self.assertEqual((60, 31), entries[0]["hotspot"])


if __name__ == "__main__":
    unittest.main()
