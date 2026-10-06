import unittest
from unittest.mock import patch

try:
    from wingline.roles import ROLE_ORDER, THEMES
except ImportError:
    ROLE_ORDER = ()
    THEMES = {}

try:
    from wingline.artwork import render_cursor
except ImportError:
    render_cursor = None


EXPECTED_ROLE_KEYS = (
    "arrow",
    "help",
    "appstarting",
    "wait",
    "crosshair",
    "ibeam",
    "nwpen",
    "no",
    "sizens",
    "sizewe",
    "sizenwse",
    "sizenesw",
    "sizeall",
    "uparrow",
    "hand",
    "pin",
    "person",
)


class ArtworkTests(unittest.TestCase):
    def test_manifest_contains_every_windows_role_in_scheme_order(self):
        self.assertEqual(
            EXPECTED_ROLE_KEYS,
            tuple(role.key for role in ROLE_ORDER),
        )

    def test_two_theme_keys_share_the_full_role_set(self):
        self.assertEqual(
            {"Wingline-White", "Wingline-Black"},
            set(THEMES),
        )
        self.assertTrue(all(THEMES.values()))

    def test_every_role_renders_visible_transparent_rgba_at_32px(self):
        self.assertIsNotNone(render_cursor)
        for theme in THEMES.values():
            for role in ROLE_ORDER:
                with self.subTest(theme=theme.key, role=role.key):
                    image, hotspot = render_cursor(role, theme, 32)
                    self.assertEqual("RGBA", image.mode)
                    self.assertEqual((32, 32), image.size)
                    alpha = image.getchannel("A")
                    self.assertIsNotNone(alpha.getbbox())
                    self.assertLess(alpha.getextrema()[0], 255)
                    self.assertGreater(alpha.getextrema()[1], 0)
                    self.assertGreaterEqual(hotspot[0], 0)
                    self.assertGreaterEqual(hotspot[1], 0)
                    self.assertLess(hotspot[0], 32)
                    self.assertLess(hotspot[1], 32)

    def test_arrow_hotspot_is_at_the_top_corner(self):
        self.assertIsNotNone(render_cursor)
        arrow = next(role for role in ROLE_ORDER if role.key == "arrow")
        image, hotspot = render_cursor(arrow, THEMES["Wingline-White"], 64)
        self.assertEqual((64, 64), image.size)
        self.assertEqual((22, 6), hotspot)
        image, _ = render_cursor(arrow, THEMES["Wingline-White"], 32)
        alpha = image.getchannel("A")
        bounds = alpha.getbbox()
        self.assertLessEqual(bounds[2] - bounds[0], 23)
        self.assertLessEqual(bounds[3] - bounds[1], 23)
        self.assertGreater(alpha.getpixel((30, 16)), 0)

    def test_renderer_rejects_unsupported_canvas_sizes(self):
        self.assertIsNotNone(render_cursor)
        arrow = next(role for role in ROLE_ORDER if role.key == "arrow")
        with self.assertRaises(ValueError):
            render_cursor(arrow, THEMES["Wingline-White"], 40)

    def test_normal_pointer_has_no_trailing_wing_lines(self):
        self.assertIsNotNone(render_cursor)
        arrow = next(role for role in ROLE_ORDER if role.key == "arrow")
        image, _ = render_cursor(arrow, THEMES["Wingline-White"], 64)
        self.assertGreaterEqual(image.getchannel("A").getbbox()[0], 2)

    def test_role_cursors_do_not_use_the_normal_pointer_underlay(self):
        self.assertIsNotNone(render_cursor)
        help_role = next(role for role in ROLE_ORDER if role.key == "help")
        with patch("wingline.artwork._draw_arrow") as draw_arrow:
            render_cursor(help_role, THEMES["Wingline-White"], 64)
        draw_arrow.assert_not_called()

    def test_non_pointer_cursor_hotspots_are_centered(self):
        self.assertIsNotNone(render_cursor)
        for role in ROLE_ORDER:
            if role.key == "arrow":
                continue
            with self.subTest(role=role.key):
                _, hotspot = render_cursor(role, THEMES["Wingline-White"], 64)
                self.assertEqual((32, 32), hotspot)

    def test_every_non_pointer_role_is_large_enough_to_see_at_32px(self):
        for theme in THEMES.values():
            for role in ROLE_ORDER:
                if role.key == "arrow":
                    continue
                with self.subTest(theme=theme.key, role=role.key):
                    image, _ = render_cursor(role, theme, 32, frame=0)
                    left, top, right, bottom = image.getchannel("A").getbbox()
                    self.assertGreaterEqual(max(right - left, bottom - top), 12)


if __name__ == "__main__":
    unittest.main()
