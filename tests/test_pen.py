import unittest
from PIL import ImageChops, ImageStat
from wingline.artwork import render_cursor, ANIMATION_FRAMES
from wingline.roles import THEMES, ROLE_ORDER


class PenTests(unittest.TestCase):
    def test_formerly_hollow_roles_have_solid_centers(self):
        filled={'wait','crosshair','ibeam','sizens','sizewe','sizenwse','sizenesw','sizeall','hand'}
        for variant in ('White','Black'):
            for role in ROLE_ORDER:
                if role.key not in filled: continue
                image,_=render_cursor(role,THEMES['Pen-'+variant],32)
                r,g,b,a=image.getpixel((16,16))
                self.assertGreaterEqual(a,230,(variant,role.key,'transparent center'))

    def test_exported_frames_have_large_solid_palette_interiors_at_desktop_size(self):
        import struct
        from PIL import Image
        from wingline.cur import encode_cur
        for variant in ('White', 'Black'):
            for role in ROLE_ORDER:
                for size in (32,64):
                    with self.subTest(variant=variant,role=role.key,size=size):
                        frame=encode_cur([render_cursor(role,THEMES['Pen-'+variant],size)])
                        offset=struct.unpack_from('<I',frame,18)[0]+40
                        # Decode Windows' premultiplied BGRA bitmap, including
                        # its bottom-up rows, then simulate normal desktop size.
                        pixels=bytearray()
                        for y in range(size-1,-1,-1):
                            for x in range(size):
                                b,g,r,a=frame[offset+(y*size+x)*4:offset+(y*size+x+1)*4]
                                pixels.extend((min(255,round(r*255/a)) if a else 0,
                                               min(255,round(g*255/a)) if a else 0,
                                               min(255,round(b*255/a)) if a else 0,a))
                        image=Image.frombytes('RGBA',(size,size),bytes(pixels)).resize((32,32),Image.Resampling.LANCZOS)
                        alpha=image.getchannel('A')
                        bounds=alpha.point(lambda a:255 if a>=128 else 0).getbbox()
                        self.assertGreaterEqual(max(bounds[2]-bounds[0],bounds[3]-bounds[1]),27)
                        colors=list(zip(*[iter(image.tobytes())]*4))
                        solid=sum(a>=200 for r,g,b,a in colors)
                        fill=sum(a>=200 and (min(r,g,b)>200 if variant=='White' else max(r,g,b)<65) for r,g,b,a in colors)
                        self.assertGreaterEqual(fill,50)
                        self.assertGreaterEqual(fill,solid*.30)

    def test_all_frames_keep_visible_outline_size_hotspot_and_smooth_loop(self):
        for variant in ('White', 'Black'):
            theme = THEMES['Pen-'+variant]
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
                        self.assertGreaterEqual(max(bounds[2]-bounds[0],bounds[3]-bounds[1]),27)
                        self.assertLessEqual(max(bounds[2]-bounds[0],bounds[3]-bounds[1]),31)
                        pixels=zip(*[iter(image.tobytes())]*4)
                        contrast=sum(a>=160 and (max(r,g,b)<110 if variant=='White' else min(r,g,b)>180) for r,g,b,a in pixels)
                        self.assertGreaterEqual(contrast,10)
                        if role.key=='arrow':
                            self.assertGreater(image.getchannel('A').getpixel(hotspot),0)
                        frames.append(image)
                    changes=[sum(ImageStat.Stat(ImageChops.difference(frames[i],frames[(i+1)%len(frames)])).mean) for i in range(len(frames))]
                    self.assertGreater(sum(changes),0)
                    self.assertLessEqual(changes[-1],max(changes[:-1])*1.25+.1)

    def test_pen_is_one_connected_shape(self):
        for frame in range(ANIMATION_FRAMES):
            image,_=render_cursor(ROLE_ORDER[0],THEMES['Pen-White'],32,frame)
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
            self.assertEqual(1,components,f"Gap in connected pointer frame {frame}")

    def test_yellow_slash_leaves_most_of_the_base_color_visible(self):
        from PIL import Image
        from wingline.artwork import _light_sheen
        for color in ((252,253,255,255),(23,26,32,255)):
            theme=THEMES['Pen-White' if color[0]>128 else 'Pen-Black']
            original=Image.new('RGBA',(64,64),color)
            animated=_light_sheen(original,theme,32)
            differences=ImageChops.difference(original,animated)
            changed=sum(max(pixel[:3])>=15 for pixel in zip(*[iter(differences.tobytes())]*4))
            self.assertGreater(changed,0)
            self.assertLess(changed,64*64*.4)

    def test_gold_band_moves_from_right_to_left(self):
        theme=THEMES['Pen-White']
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
