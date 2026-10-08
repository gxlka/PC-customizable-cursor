import unittest
from unittest.mock import patch

try:
    from wingline.roles import ROLE_ORDER, THEMES
except ImportError:
    ROLE_ORDER = ()
    THEMES = {}

try:
    from wingline.artwork import render_cursor
    from wingline.timing import ANIMATION_FRAMES
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
                "Pen-White", "Pen-Black",
                "Nib-White", "Nib-Black",
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

    def test_all_styles_have_unique_silhouettes_for_all_roles(self):
        silhouettes = {}
        for theme in THEMES.values():
            if not theme.key.endswith("-White"):
                continue
            for role in ROLE_ORDER:
                silhouette = render_cursor(role, theme, 64)[0].getchannel("A").tobytes()
                label = f"{theme.key}/{role.key}"
                self.assertNotIn(silhouette, silhouettes, f"{label} repeats {silhouettes.get(silhouette)}")
                silhouettes[silhouette] = label
        self.assertEqual(len(THEMES)//2*len(ROLE_ORDER), len(silhouettes))

    def test_new_normal_pointer_hotspots_are_on_visible_artwork(self):
        arrow = ROLE_ORDER[0]
        for name in ("Hand", "macOS", "I-Beam", "Pen", "Nib"):
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
                        self.assertGreaterEqual(extent, round(size*(.84 if theme.style in {'pen','nib'} else .70))-1)
                        self.assertLessEqual(extent, round(size*(.90 if theme.style in {'pen','nib'} else .80))+1)
                        self.assertGreater(left, 0)
                        self.assertGreater(top, 0)
                        self.assertLess(right, size)
                        self.assertLess(bottom, size)

    def test_all_animated_frames_keep_the_fixed_visible_size(self):
        for theme in THEMES.values():
            for role in ROLE_ORDER:
                for frame in range(ANIMATION_FRAMES):
                    with self.subTest(theme=theme.key, role=role.key, frame=frame):
                        image, _ = render_cursor(role, theme, 32, frame=frame)
                        x0, y0, x1, y1 = image.getchannel("A").getbbox()
                        self.assertGreaterEqual(max(x1-x0, y1-y0), 23)
                        self.assertLessEqual(max(x1-x0, y1-y0), 31 if theme.style in {'pen','nib'} else 28)

    def test_animations_change_and_have_no_discontinuous_loop_seam(self):
        from PIL import ImageChops, ImageStat
        for theme in THEMES.values():
            for role in ROLE_ORDER:
                with self.subTest(theme=theme.key, role=role.key):
                    frames=[render_cursor(role,theme,64,frame=i)[0] for i in range(ANIMATION_FRAMES)]
                    self.assertGreater(len({image.tobytes() for image in frames}),8)
                    changes=[sum(ImageStat.Stat(ImageChops.difference(frames[i],frames[(i+1)%ANIMATION_FRAMES])).mean)
                             for i in range(ANIMATION_FRAMES)]
                    self.assertGreater(sum(changes),0)
                    self.assertLessEqual(changes[-1],max(changes[:-1])*1.25+.1)

    def test_motion_is_visible_at_actual_desktop_size(self):
        from PIL import ImageChops, ImageStat
        for theme in THEMES.values():
            for role in ROLE_ORDER:
                with self.subTest(theme=theme.key, role=role.key):
                    rest, _ = render_cursor(role, theme, 32, 0)
                    # Symmetric spinners can repeat at a quarter turn.
                    changes = []
                    for frame in (ANIMATION_FRAMES//8, ANIMATION_FRAMES//4, 3*ANIMATION_FRAMES//8):
                        peak, _ = render_cursor(role, theme, 32, frame)
                        difference = ImageChops.difference(rest, peak) if role.key in {"wait", "appstarting"} or theme.style=="nib" else ImageChops.difference(rest.getchannel("A"), peak.getchannel("A"))
                        changes.append(sum(ImageStat.Stat(difference).sum))
                    self.assertGreater(max(changes), 500)

    def test_state_motion_keeps_hotspots_and_neutral_frame_stable(self):
        for theme in THEMES.values():
            for role in ROLE_ORDER:
                if role.key in {"wait", "appstarting"}:
                    continue
                with self.subTest(theme=theme.key, role=role.key):
                    first, hotspot = render_cursor(role, theme, 32, 0)
                    for frame in range(ANIMATION_FRAMES):
                        image, actual_hotspot = render_cursor(role, theme, 32, frame)
                        self.assertEqual(hotspot, actual_hotspot)
                        bounds = image.getchannel("A").getbbox()
                        self.assertGreater(bounds[0],0)
                        self.assertGreater(bounds[1],0)
                        self.assertLess(bounds[2],32)
                        self.assertLess(bounds[3],32)
                        if role.key == "arrow":
                            self.assertGreater(image.getchannel("A").getpixel(hotspot),0)
                    neutral, _ = render_cursor(role,theme,32,ANIMATION_FRAMES//2)
                    self.assertEqual(first.getchannel("A").tobytes(),neutral.getchannel("A").tobytes()) if theme.style == "pen" else self.assertEqual(first.tobytes(),neutral.tobytes())

    def test_light_sheen_preserves_motion_alpha_and_contrast_edges(self):
        from wingline.artwork import _light_sheen
        for theme in THEMES.values():
            for role in ROLE_ORDER:
                with self.subTest(theme=theme.key, role=role.key):
                    changed=False
                    for frame in (ANIMATION_FRAMES//4, ANIMATION_FRAMES//2, 3*ANIMATION_FRAMES//4):
                        with patch("wingline.artwork._light_sheen", side_effect=lambda image, theme, frame: image):
                            original, hotspot = render_cursor(role, theme, 64, frame)
                        animated, actual_hotspot = render_cursor(role, theme, 64, frame)
                        self.assertEqual(hotspot, actual_hotspot)
                        self.assertEqual(original.getchannel("A").tobytes(), animated.getchannel("A").tobytes())
                        changed |= original.tobytes() != animated.tobytes()
                        light = theme.key.endswith("-White")
                        for before, after in zip(zip(*[iter(original.tobytes())]*4), zip(*[iter(animated.tobytes())]*4)):
                            if before[3] >= 160 and (max(before[:3]) < 110 if light else min(before[:3]) > 180):
                                self.assertEqual(before, after)
                        self.assertEqual(original.tobytes(), _light_sheen(original, theme, 0).tobytes())
                    self.assertTrue(changed, "Sheen missing from exported animation frames")

    def test_sheen_has_noticeable_fill_contrast_at_32px(self):
        from PIL import ImageChops
        for theme in THEMES.values():
            for role in ROLE_ORDER:
                with self.subTest(theme=theme.key, role=role.key):
                    peaks = []
                    for frame in (ANIMATION_FRAMES//4, ANIMATION_FRAMES//2, 3*ANIMATION_FRAMES//4):
                        with patch("wingline.artwork._light_sheen", side_effect=lambda image, theme, frame: image):
                            original, _ = render_cursor(role, theme, 32, frame)
                        animated, _ = render_cursor(role, theme, 32, frame)
                        difference = ImageChops.difference(original, animated)
                        peaks.append(max(upper for lower, upper in difference.getextrema()[:3]))
                    self.assertGreaterEqual(max(peaks), 20)

    def test_all_cursors_have_visible_edges_on_matching_backgrounds(self):
        for theme in THEMES.values():
            light = theme.key.endswith("-White")
            for role in ROLE_ORDER:
                for frame in (0, ANIMATION_FRAMES//4, ANIMATION_FRAMES//2, 3*ANIMATION_FRAMES//4):
                    with self.subTest(theme=theme.key, role=role.key, frame=frame):
                        image, _ = render_cursor(role, theme, 32, frame)
                        pixels = zip(*[iter(image.tobytes())]*4)
                        # Count visible, strongly contrasting border pixels at
                        # actual desktop size, including every loop quarter.
                        count = sum(a >= 160 and (max(r,g,b) < 110 if light else min(r,g,b) > 180)
                                    for r,g,b,a in pixels)
                        self.assertGreaterEqual(count, 10)

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
                    self.assertLessEqual(max(right - left, bottom - top), 31 if theme.style in {'pen','nib'} else 28)

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
                    self.assertLessEqual(largest_dimension, 61 if theme.style in {'pen','nib'} else 56)

    def test_working_in_background_remains_a_horizontal_progress_cursor(self):
        role = next(role for role in ROLE_ORDER if role.key == "appstarting")
        image, _ = render_cursor(role, THEMES["Windows-Smooth-White"], 64, frame=0)
        left, top, right, bottom = image.getchannel("A").getbbox()
        self.assertGreater(right - left, (bottom - top) * 1.5)


if __name__ == "__main__":
    unittest.main()
