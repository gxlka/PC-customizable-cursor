import unittest
from PIL import Image, ImageChops, ImageStat
from wingline.roles import ROLE_ORDER, THEMES
from wingline.artwork import render_cursor
from wingline.fluent_prototype import render, FRAMES
from build_windows_flow import cursor, animated, verify_ani

class FlowTests(unittest.TestCase):
    def test_new_nonpointer_silhouettes_do_not_duplicate_existing_sets(self):
        def signature(image):
            a=image.getchannel('A').point(lambda v:255 if v>128 else 0)
            a=a.crop(a.getbbox());a.thumbnail((64,64))
            normalized=Image.new('L',(64,64));normalized.paste(a,((64-a.width)//2,(64-a.height)//2))
            return normalized.tobytes()
        old={signature(render_cursor(r,t,128)[0]) for t in THEMES.values() if t.key.endswith('White') for r in ROLE_ORDER[1:]}
        new=[signature(render(r.glyph,128)) for r in ROLE_ORDER[1:]]
        self.assertEqual(16,len(set(new)))
        self.assertFalse(old.intersection(new))

    def test_visible_fills_fixed_hotspots_and_seamless_loops(self):
        for dark in (False,True):
            for role in ROLE_ORDER:
                with self.subTest(role=role.key,dark=dark):
                    frames=[cursor(role,32,f,dark) for f in range(FRAMES)]
                    self.assertEqual(1,len({h for _,h in frames}))
                    for image,_ in frames:
                        b=image.getbbox();self.assertTrue(b)
                        self.assertGreaterEqual(max(b[2]-b[0],b[3]-b[1]),25)
                        self.assertTrue(0<=b[0]<b[2]<=32 and 0<=b[1]<b[3]<=32)
                    self.assertEqual(render(role.glyph,32,0,dark).tobytes(),render(role.glyph,32,FRAMES,dark).tobytes())
                    differences=[sum(ImageStat.Stat(ImageChops.difference(frames[i][0],frames[(i+1)%FRAMES][0])).mean) for i in range(FRAMES)]
                    self.assertGreater(sum(differences),0)
                    self.assertLessEqual(differences[-1],max(differences)+.01)
                    if role.key not in ('wait','appstarting'):
                        self.assertEqual(1,len({im.getchannel('A').tobytes() for im,_ in frames}))

    def test_native_animation_headers_and_embedded_cursor_frames(self):
        for dark in (False,True):
            for role in (ROLE_ORDER[0],ROLE_ORDER[3]):
                verify_ani(animated(role,64,dark),64)

if __name__=='__main__':unittest.main()
