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
            {
                "Wingline-White",
                "Wingline-Black",
                "Windows-Smooth-White",
                "Windows-Smooth-Black",
                "Hand-White", "Hand-Black",
                "macOS-White", "macOS-Black",
                "I-Beam-White", "I-Beam-Black",
            },
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

    def test_every_role_has_its_own_distinct_artwork(self):
        for theme in THEMES.values():
            with self.subTest(theme=theme.key):
                rendered = [
                    render_cursor(role, theme, 64, frame=0)[0].tobytes()
                    for role in ROLE_ORDER
                ]
                self.assertEqual(len(ROLE_ORDER), len(set(rendered)))

    def test_every_role_has_a_distinct_silhouette_not_just_a_different_color(self):
        for theme in THEMES.values():
            with self.subTest(theme=theme.key):
                silhouettes = [
                    render_cursor(role, theme, 64, frame=0)[0]
                    .getchannel("A")
                    .tobytes()
                    for role in ROLE_ORDER
                ]
                self.assertEqual(len(ROLE_ORDER), len(set(silhouettes)))

    def test_windows_smooth_uses_separate_artwork_for_every_role(self):
        for role in ROLE_ORDER:
            with self.subTest(role=role.key):
                wing = render_cursor(role, THEMES["Wingline-White"], 64)[0]
                windows = render_cursor(role, THEMES["Windows-Smooth-White"], 64)[0]
                self.assertNotEqual(wing.getchannel("A").tobytes(), windows.getchannel("A").tobytes())

    def test_all_five_styles_have_unique_silhouettes_for_all_roles(self):
        silhouettes = {}
        for theme in THEMES.values():
            if not theme.key.endswith("-White"):
                continue
            for role in ROLE_ORDER:
                silhouette = render_cursor(role, theme, 64)[0].getchannel("A").tobytes()
                label = f"{theme.key}/{role.key}"
                self.assertNotIn(silhouette, silhouettes, f"{label} repeats {silhouettes.get(silhouette)}")
                silhouettes[silhouette] = label
        self.assertEqual(85, len(silhouettes))

    def test_new_normal_pointer_hotspots_are_on_visible_artwork(self):
        arrow = ROLE_ORDER[0]
        for name in ("Hand", "macOS", "I-Beam"):
            for size in (32, 48, 64, 96, 128, 192, 256):
                with self.subTest(style=name, size=size):
                    image, hotspot = render_cursor(arrow, THEMES[f"{name}-White"], size)
                    self.assertGreater(image.getchannel("A").getpixel(hotspot), 0)

    def test_macos_pointer_has_a_broader_silhouette_than_windows_smooth(self):
        widths = []
        for style in ("Windows-Smooth", "macOS"):
            image, _ = render_cursor(ROLE_ORDER[0], THEMES[f"{style}-White"], 32)
            bounds = image.getchannel("A").point(lambda value: 255 if value >= 128 else 0).getbbox()
            widths.append(bounds[2]-bounds[0])
        self.assertGreaterEqual(widths[1], widths[0]+3)

    def test_visible_artwork_stays_large_and_unclipped_at_every_native_size(self):
        from wingline.artwork import SUPPORTED_SIZES
        for theme in THEMES.values():
            for role in ROLE_ORDER:
                for size in SUPPORTED_SIZES:
                    with self.subTest(theme=theme.key, role=role.key, size=size):
                        image, _ = render_cursor(role, theme, size)
                        alpha = image.getchannel("A")
                        # Count visible pixels, so a faint antialiasing fringe
                        # cannot disguise an undersized icon.
                        bounds = alpha.point(lambda value: 255 if value >= 128 else 0).getbbox()
                        self.assertIsNotNone(bounds)
                        left, top, right, bottom = bounds
                        extent = max(right-left, bottom-top)
                        self.assertGreaterEqual(extent, round(size*.70)-1)
                        self.assertLessEqual(extent, round(size*.80)+1)
                        self.assertGreater(left, 0)
                        self.assertGreater(top, 0)
                        self.assertLess(right, size)
                        self.assertLess(bottom, size)

    def test_all_animated_frames_keep_the_fixed_visible_size(self):
        for theme in THEMES.values():
            for role in ROLE_ORDER:
                if role.key not in {"wait", "appstarting"}:
                    continue
                for frame in range(8):
                    with self.subTest(theme=theme.key, role=role.key, frame=frame):
                        image, _ = render_cursor(role, theme, 32, frame=frame)
                        x0, y0, x1, y1 = image.getchannel("A").getbbox()
                        self.assertGreaterEqual(max(x1-x0, y1-y0), 23)
                        self.assertLessEqual(max(x1-x0, y1-y0), 28)

    def test_arrow_hotspot_is_at_the_top_corner(self):
        self.assertIsNotNone(render_cursor)
        arrow = next(role for role in ROLE_ORDER if role.key == "arrow")
        image, hotspot = render_cursor(arrow, THEMES["Wingline-White"], 64)
        self.assertEqual((64, 64), image.size)
        self.assertEqual((22, 6), hotspot)
        image, hotspot = render_cursor(arrow, THEMES["Wingline-White"], 32)
        alpha = image.getchannel("A")
        bounds = alpha.getbbox()
        self.assertLessEqual(bounds[2] - bounds[0], 26)
        self.assertLessEqual(bounds[3] - bounds[1], 25)
        self.assertEqual((11, 3), hotspot)
        self.assertGreater(alpha.getpixel(hotspot), 0)

    def test_windows_smooth_pointer_uses_the_upper_left_arrow_tip(self):
        arrow = next(role for role in ROLE_ORDER if role.key == "arrow")
        image, hotspot = render_cursor(arrow, THEMES["Windows-Smooth-White"], 64)
        self.assertEqual((6, 3), hotspot)
        self.assertGreater(image.getchannel("A").getpixel(hotspot), 0)

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
                    self.assertGreaterEqual(max(right - left, bottom - top), 23)
                    self.assertLessEqual(max(right - left, bottom - top), 28)

    def test_non_pointer_roles_render_near_main_pointer_scale_at_64px(self):
        for theme in THEMES.values():
            for role in ROLE_ORDER:
                if role.key == "arrow":
                    continue
                with self.subTest(theme=theme.key, role=role.key):
                    image, _ = render_cursor(role, theme, 64, frame=0)
                    left, top, right, bottom = image.getchannel("A").getbbox()
                    largest_dimension = max(right - left, bottom - top)
                    self.assertGreaterEqual(largest_dimension, 40)
                    self.assertLessEqual(largest_dimension, 56)

    def test_working_in_background_remains_a_horizontal_progress_cursor(self):
        role = next(role for role in ROLE_ORDER if role.key == "appstarting")
        image, _ = render_cursor(role, THEMES["Windows-Smooth-White"], 64, frame=0)
        left, top, right, bottom = image.getchannel("A").getbbox()
        self.assertGreater(right - left, (bottom - top) * 1.5)


if __name__ == "__main__":
    unittest.main()
