import unittest
from PIL import ImageChops, ImageStat
from wingline.artwork import render_cursor, ANIMATION_FRAMES
from wingline.roles import THEMES, ROLE_ORDER


class NibTests(unittest.TestCase):
    def test_all_frames_keep_visible_filled_icons_fixed_hotspots_and_clean_loops(self):
        for variant in ('White','Black'):
            theme=THEMES['Nib-'+variant]
            for role in ROLE_ORDER:
                with self.subTest(variant=variant,role=role.key):
                    first,hotspot=render_cursor(role,theme,32)
                    frames=[]
                    for frame in range(ANIMATION_FRAMES):
                        image,actual=render_cursor(role,theme,32,frame)
                        self.assertEqual(hotspot,actual)
                        bounds=image.getchannel('A').getbbox()
                        self.assertTrue(0<bounds[0]<bounds[2]<32 and 0<bounds[1]<bounds[3]<32)
                        self.assertGreaterEqual(max(bounds[2]-bounds[0],bounds[3]-bounds[1]),23)
                        if role.key not in {'wait','appstarting'}:
                            self.assertEqual(first.getchannel('A').tobytes(),image.getchannel('A').tobytes(),'Nib must not swing, scale or shift')
                        frames.append(image)
                    changes=[sum(ImageStat.Stat(ImageChops.difference(frames[i],frames[(i+1)%ANIMATION_FRAMES])).mean) for i in range(ANIMATION_FRAMES)]
                    self.assertGreater(sum(changes),0)
                    self.assertLessEqual(changes[-1],max(changes[:-1])*1.25+.1)
                    colors=list(zip(*[iter(first.tobytes())]*4))
                    solid=sum(a>=200 for r,g,b,a in colors)
                    fill=sum(a>=200 and (min(r,g,b)>200 if variant=='White' else max(r,g,b)<65) for r,g,b,a in colors)
                    self.assertGreaterEqual(fill,35)
                    self.assertGreaterEqual(fill,solid*.30)

    def test_main_click_tip_is_visible_at_all_native_sizes(self):
        from wingline.artwork import SUPPORTED_SIZES
        for variant in ('White','Black'):
            for size in SUPPORTED_SIZES:
                image,hotspot=render_cursor(ROLE_ORDER[0],THEMES['Nib-'+variant],size)
                self.assertGreater(image.getchannel('A').getpixel(hotspot),0)
