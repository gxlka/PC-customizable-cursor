import unittest
from PIL import ImageChops, ImageStat
from wingline.artwork import render_cursor, ANIMATION_FRAMES
from wingline.roles import THEMES, ROLE_ORDER


class SharpHeadTests(unittest.TestCase):
    def test_all_frames_keep_visible_outline_size_hotspot_and_smooth_loop(self):
        for variant in ('White', 'Black'):
            theme = THEMES['Sharp-Head-'+variant]
            for role in ROLE_ORDER:
                with self.subTest(variant=variant,role=role.key):
                    frames = []
                    expected = render_cursor(role,theme,32,0)[1]
                    for frame in range(ANIMATION_FRAMES):
                        image, hotspot = render_cursor(role,theme,32,frame)
                        self.assertEqual(expected,hotspot)
                        bounds=image.getchannel('A').getbbox()
                        self.assertTrue(0 < bounds[0] < bounds[2] < 32)
                        self.assertTrue(0 < bounds[1] < bounds[3] < 32)
                        self.assertGreaterEqual(max(bounds[2]-bounds[0],bounds[3]-bounds[1]),23)
                        self.assertLessEqual(max(bounds[2]-bounds[0],bounds[3]-bounds[1]),28)
                        pixels=zip(*[iter(image.tobytes())]*4)
                        contrast=sum(a>=160 and (max(r,g,b)<110 if variant=='White' else min(r,g,b)>180) for r,g,b,a in pixels)
                        self.assertGreaterEqual(contrast,10)
                        if role.key=='arrow':
                            self.assertGreater(image.getchannel('A').getpixel(hotspot),0)
                        frames.append(image)
                    changes=[sum(ImageStat.Stat(ImageChops.difference(frames[i],frames[(i+1)%len(frames)])).mean) for i in range(len(frames))]
                    self.assertGreater(sum(changes),0)
                    self.assertLessEqual(changes[-1],max(changes[:-1])*1.25+.1)

    def test_pointer_head_stem_and_short_base_stay_separate(self):
        for frame in range(ANIMATION_FRAMES):
            image,_=render_cursor(ROLE_ORDER[0],THEMES['Sharp-Head-White'],32,frame)
            remaining={(x,y) for y in range(32) for x in range(32) if image.getpixel((x,y))[3]>=128}
            components=0
            while remaining:
                components+=1
                pending=[remaining.pop()]
                while pending:
                    x,y=pending.pop()
                    for dx in (-1,0,1):
                        for dy in (-1,0,1):
                            point=(x+dx,y+dy)
                            if point in remaining:
                                remaining.remove(point)
                                pending.append(point)
            self.assertEqual(3,components,f"Strokes touch in frame {frame}")

    def test_gold_band_moves_from_right_to_left(self):
        theme=THEMES['Sharp-Head-White']
        from PIL import Image
        image=Image.new('RGBA',(64,64),(252,253,255,255))
        from wingline.artwork import _light_sheen
        peaks=[]
        for frame in (16,48):
            sweep=_light_sheen(image,theme,frame)
            amounts=[255-sweep.getpixel((x,32))[2] for x in range(64)]
            peaks.append(max(range(64),key=lambda x:amounts[x]))
        self.assertGreater(peaks[0],peaks[1])
        self.assertEqual(image.tobytes(),_light_sheen(image,theme,0).tobytes())


if __name__=='__main__':
    unittest.main()
