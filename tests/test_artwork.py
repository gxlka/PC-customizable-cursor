import unittest

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

    def test_arrow_hotspot_is_at_the_right_facing_tip(self):
        self.assertIsNotNone(render_cursor)
        arrow = next(role for role in ROLE_ORDER if role.key == "arrow")
        image, hotspot = render_cursor(arrow, THEMES["Wingline-White"], 64)
        self.assertEqual((64, 64), image.size)
        self.assertGreaterEqual(hotspot[0], 56)

    def test_renderer_rejects_unsupported_canvas_sizes(self):
        self.assertIsNotNone(render_cursor)
        arrow = next(role for role in ROLE_ORDER if role.key == "arrow")
        with self.assertRaises(ValueError):
            render_cursor(arrow, THEMES["Wingline-White"], 40)


if __name__ == "__main__":
    unittest.main()
