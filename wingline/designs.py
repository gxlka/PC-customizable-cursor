"""Independent vector artwork for the Wingline and Windows Smooth role sets."""
from __future__ import annotations
import math
from functools import lru_cache
from .timing import ANIMATION_FRAMES
from PIL import Image, ImageDraw
from .roles import Theme


def curve(a, b, c, d, steps=24):
    out=[]
    for i in range(steps+1):
        t=i/steps; u=1-t
        out.append((u**3*a[0]+3*u*u*t*b[0]+3*u*t*t*c[0]+t**3*d[0],
                    u**3*a[1]+3*u*u*t*b[1]+3*u*t*t*c[1]+t**3*d[1]))
    return out


class Pen:
    def __init__(self, image, theme):
        self.draw=ImageDraw.Draw(image); self.n=image.width; self.theme=theme
    def pixels(self, pts):
        return [(round(x*self.n),round(y*self.n)) for x,y in pts]
    def rawline(self, pts, color, width):
        p=self.pixels(pts); w=max(1,round(width*self.n))
        self.draw.line(p,fill=color,width=w,joint='curve')
        r=w/2
        for x,y in (p[0],p[-1]):
            self.draw.ellipse((round(x-r),round(y-r),round(x+r),round(y+r)),fill=color)
    def line(self, pts, width=.032):
        self.rawline(pts,self.theme.edge,width+.024)
        self.rawline(pts,self.theme.fill,width)
    def shape(self, pts):
        p=self.pixels(pts)
        self.draw.polygon(p,fill=self.theme.fill)
        self.draw.line(p+[p[0]],fill=self.theme.edge,width=max(1,round(.018*self.n)),joint='curve')
    def disk(self,x,y,r):
        self.shape([(x+math.cos(i*math.tau/80)*r,y+math.sin(i*math.tau/80)*r) for i in range(80)])
    def ring(self,x,y,r,start=0,end=360,width=.032):
        pts=[(x+math.cos(math.radians(start+(end-start)*i/100))*r,
              y+math.sin(math.radians(start+(end-start)*i/100))*r) for i in range(101)]
        self.line(pts,width)
    def capsule(self,box,r=.08):
        x0,y0,x1,y1=box; n=self.n; edge=max(1,round(n*.018))
        coords=tuple(round(v*n) for v in box)
        self.draw.rounded_rectangle(coords,radius=round(r*n),fill=self.theme.edge)
        self.draw.rounded_rectangle((coords[0]+edge,coords[1]+edge,coords[2]-edge,coords[3]-edge),
                                    radius=max(1,round(r*n)-edge),fill=self.theme.fill)


def rotate(pts, angle):
    c,s=math.cos(angle),math.sin(angle)
    return [(.5+(x-.5)*c-(y-.5)*s,.5+(x-.5)*s+(y-.5)*c) for x,y in pts]


def resize(p, glyph, smooth):
    angle={'resize_horizontal':0,'resize_vertical':math.pi/2,
           'resize_nwse':math.pi/4,'resize_nesw':-math.pi/4}[glyph]
    if smooth:
        pts=[(.12,.5),(.32,.30)]
        pts+=curve((.32,.30),(.37,.27),(.40,.30),(.40,.35))[1:]
        pts += [(.40,.44),(.60,.44),(.60,.35)]
        pts+=curve((.60,.35),(.60,.30),(.63,.27),(.68,.30))[1:]
        pts += [(.88,.5),(.68,.70)]
        pts+=curve((.68,.70),(.63,.73),(.60,.70),(.60,.65))[1:]
        pts += [(.60,.56),(.40,.56),(.40,.65)]
        pts+=curve((.40,.65),(.40,.70),(.37,.73),(.32,.70))[1:]
        p.shape(rotate(pts,angle))
    else:
        for pts in [[(.13,.5),(.87,.5)],[ (.34,.29),(.13,.5),(.34,.71)],[(.66,.29),(.87,.5),(.66,.71)]]:
            p.line(rotate(pts,angle))


def draw_wingline(p, glyph, frame):
    if glyph=='help':
        pts=curve((.27,.30),(.27,.08),(.76,.08),(.75,.32))
        pts+=curve((.75,.32),(.74,.47),(.49,.47),(.49,.66))[1:]
        p.line(pts,.048); p.disk(.49,.84,.045)
    elif glyph=='appstarting':
        p.capsule((.10,.32,.90,.68),.09)
        x=.17+.48*(.5-.5*math.cos(frame*math.tau/8))
        p.capsule((x,.40,x+.17,.60),.05)
    elif glyph=='wait':
        for i in range(8):
            a=i*math.tau/8; r=.047+.02*(.5+.5*math.cos((i-frame)*math.tau/8))
            p.disk(.5+math.cos(a)*.30,.5+math.sin(a)*.30,r)
    elif glyph=='crosshair':
        p.ring(.5,.5,.18)
        p.line([(.5,.12),(.5,.88)]);p.line([(.12,.5),(.88,.5)])
    elif glyph=='ibeam':
        p.line([(.5,.12),(.5,.88)])
        p.line([(.22,.12),(.78,.12)]);p.line([(.22,.88),(.78,.88)])
    elif glyph=='pen':
        p.shape([(.14,.86),(.23,.63),(.70,.16),(.84,.30),(.37,.77)])
        p.line([(.23,.63),(.37,.77)],.021)
        p.line([(.67,.19),(.81,.33)],.021)
    elif glyph=='no':
        p.ring(.5,.5,.35,.0,360,.041); p.line([(.26,.74),(.74,.26)],.041)
    elif glyph.startswith('resize_'):
        resize(p,glyph,False)
    elif glyph=='move':
        for a in (0,math.pi/2):
            p.line(rotate([(.12,.5),(.88,.5)],a))
            p.line(rotate([(.28,.34),(.12,.5),(.28,.66)],a))
            p.line(rotate([(.72,.34),(.88,.5),(.72,.66)],a))
    elif glyph=='up':
        p.line([(.5,.87),(.5,.13)])
        p.line([(.20,.43),(.5,.13),(.80,.43)])
    elif glyph=='hand':
        pts=curve((.25,.48),(.14,.37),(.18,.25),(.31,.38))
        pts += [(.34,.49),(.34,.24)]
        pts+=curve((.34,.24),(.34,.14),(.46,.14),(.46,.24))[1:]
        pts += [(.46,.40),(.47,.19)]
        pts+=curve((.47,.19),(.48,.09),(.60,.10),(.60,.21))[1:]
        pts += [(.60,.40),(.62,.25)]
        pts+=curve((.62,.25),(.64,.16),(.75,.18),(.74,.30))[1:]
        pts += [(.72,.47),(.75,.37)]
        pts+=curve((.75,.37),(.80,.28),(.90,.36),(.85,.49))[1:]
        pts+=curve((.85,.49),(.82,.68),(.79,.85),(.54,.87))[1:]
        pts+=curve((.54,.87),(.36,.84),(.33,.67),(.25,.48))[1:]
        p.shape(pts)
    elif glyph=='pin':
        p.ring(.5,.37,.24,width=.032)
        p.line([(.30,.55),(.5,.89),(.70,.55)])
        p.disk(.5,.37,.045)
    elif glyph=='person':
        p.disk(.5,.27,.15)
        p.line(curve((.14,.88),(.15,.49),(.85,.49),(.86,.88)),.041)


def draw_windows(p, glyph, frame):
    if glyph=='help':
        pts=curve((.16,.38),(.16,.10),(.85,.10),(.84,.40))
        pts+=curve((.84,.40),(.84,.65),(.54,.72),(.40,.66))[1:]
        pts += [(.20,.84),(.25,.62)]
        pts+=curve((.25,.62),(.18,.56),(.16,.48),(.16,.38))[1:]
        p.shape(pts)
        q=curve((.39,.33),(.38,.22),(.64,.22),(.64,.35))
        q+=curve((.64,.35),(.64,.43),(.51,.42),(.51,.49))[1:]
        p.line(q,.026);p.disk(.51,.57,.018)
    elif glyph=='appstarting':
        for i,x in enumerate((.20,.50,.80)):
            r=.12+.055*(.5+.5*math.cos((frame+i*2)*math.tau/8))
            p.disk(x,.5,r)
    elif glyph=='wait':
        a=frame*45
        p.ring(.5,.5,.32,a+20,a+290,.073)
        p.disk(.5+math.cos(math.radians(a+320))*.32,.5+math.sin(math.radians(a+320))*.32,.044)
    elif glyph=='crosshair':
        for a in (10,100,190,280):
            p.ring(.5,.5,.32,a,a+60,.035)
        for pts in [[(.5,.10),(.5,.27)],[(.5,.73),(.5,.9)],[(.1,.5),(.27,.5)],[(.73,.5),(.9,.5)]]:
            p.line(pts,.023)
        p.disk(.5,.5,.028)
    elif glyph=='ibeam':
        # Curved serifs and a slim waist, unlike Wingline's straight I-bar.
        pts=curve((.22,.14),(.48,.24),(.48,.25),(.48,.5))
        pts+=curve((.48,.5),(.48,.75),(.48,.76),(.22,.86))[1:]
        p.line(pts,.037)
        pts=curve((.78,.14),(.52,.24),(.52,.25),(.52,.5))
        pts+=curve((.52,.5),(.52,.75),(.52,.76),(.78,.86))[1:]
        p.line(pts,.037)
    elif glyph=='pen':
        p.shape([(.14,.86),(.30,.35),(.70,.14),(.86,.30),(.65,.70)])
        p.line([(.14,.86),(.55,.45)],.022);p.disk(.55,.45,.043)
        p.line([(.30,.35),(.65,.70)],.022)
    elif glyph=='no':
        pts=[]
        for a,b,c,d in [((.22,.16),(.1,.2),(.1,.8),(.22,.84)),((.22,.84),(.35,.91),(.65,.91),(.78,.84)),
                         ((.78,.84),(.9,.8),(.9,.2),(.78,.16)),((.78,.16),(.65,.09),(.35,.09),(.22,.16))]:
            pts+=curve(a,b,c,d)
        p.line(pts+[pts[0]],.045);p.line(curve((.28,.73),(.42,.55),(.58,.45),(.72,.27)),.045)
    elif glyph.startswith('resize_'):
        resize(p,glyph,True)
    elif glyph=='move':
        p.shape([(.50,.10),(.67,.30),(.57,.30),(.57,.43),(.70,.43),(.70,.33),(.90,.50),
                 (.70,.67),(.70,.57),(.57,.57),(.57,.70),(.67,.70),(.50,.90),(.33,.70),
                 (.43,.70),(.43,.57),(.30,.57),(.30,.67),(.10,.50),(.30,.33),(.30,.43),
                 (.43,.43),(.43,.30),(.33,.30)])
    elif glyph=='up':
        pts=[(.5,.10),(.80,.40)]
        pts+=curve((.80,.40),(.84,.47),(.80,.51),(.74,.48))[1:]
        pts += [(.57,.33),(.57,.83)]
        pts+=curve((.57,.83),(.57,.93),(.43,.93),(.43,.83))[1:]
        pts += [(.43,.33),(.26,.48)]
        pts+=curve((.26,.48),(.20,.51),(.16,.47),(.20,.40))[1:]
        p.shape(pts)
    elif glyph=='hand':
        # Rounded index-finger link hand, separate from the Wingline open palm.
        pts=[(.38,.55),(.38,.18)]
        pts+=curve((.38,.18),(.38,.04),(.54,.04),(.54,.18))[1:]
        pts += [(.54,.43)]
        pts+=curve((.54,.43),(.61,.37),(.66,.39),(.66,.47))[1:]
        pts+=curve((.66,.47),(.74,.41),(.79,.45),(.79,.52))[1:]
        pts+=curve((.79,.52),(.90,.45),(.92,.55),(.88,.69))[1:]
        pts+=curve((.88,.69),(.85,.84),(.81,.89),(.62,.89))[1:]
        pts+=curve((.62,.89),(.46,.89),(.36,.77),(.21,.60))[1:]
        pts+=curve((.21,.60),(.13,.50),(.25,.42),(.38,.55))[1:]
        p.shape(pts)
    elif glyph=='pin':
        pts=curve((.5,.90),(.44,.78),(.19,.49),(.19,.34))
        pts+=curve((.19,.34),(.19,.02),(.81,.02),(.81,.34))[1:]
        pts+=curve((.81,.34),(.81,.49),(.56,.78),(.5,.90))[1:]
        p.shape(pts);p.ring(.5,.33,.095,width=.021)
    elif glyph=='person':
        p.disk(.5,.26,.15)
        pts=curve((.12,.85),(.12,.49),(.88,.49),(.88,.85))
        pts+=curve((.88,.85),(.70,.92),(.30,.92),(.12,.85))[1:]
        p.shape(pts)


def render_role(glyph: str, theme: Theme, canvas: int, frame: int, with_hotspot=False):
    image=Image.new('RGBA',(canvas,canvas))
    p=Pen(image,theme)
    from .extra_designs import DRAW_STYLES, NORMAL_HOTSPOTS
    renderer = DRAW_STYLES.get(theme.style, draw_windows if theme.style=='windows' else draw_wingline)
    renderer(p,glyph,frame*8/ANIMATION_FRAMES)
    # Fit actual opaque artwork, not the empty source canvas. Each role gets
    # a fixed 24px visible extent on a 32px Windows cursor canvas.
    bounds=image.getchannel('A').getbbox()
    if bounds is None:
        raise ValueError(f'No artwork for {theme.style}/{glyph}')
    if glyph in {'wait', 'appstarting'}:
        bounds=tuple(round(value*canvas) for value in animation_bounds(theme.style,glyph))
    cropped=image.crop(bounds)
    extent=round(canvas*.75)
    ratio=extent/max(cropped.size)
    fitted=cropped.resize((max(1,round(cropped.width*ratio)),max(1,round(cropped.height*ratio))),Image.Resampling.LANCZOS)
    result=Image.new('RGBA',(canvas,canvas))
    result.alpha_composite(fitted,((canvas-fitted.width)//2,(canvas-fitted.height)//2))
    if with_hotspot:
        x,y=NORMAL_HOTSPOTS[theme.style] if glyph == 'arrow' else (.5,.5)
        hotspot=((canvas-fitted.width)//2 + (x*canvas-bounds[0])*fitted.width/cropped.width,
                 (canvas-fitted.height)//2 + (y*canvas-bounds[1])*fitted.height/cropped.height)
        return result, hotspot
    return result


@lru_cache(maxsize=10)
def animation_bounds(style, glyph):
    from .extra_designs import DRAW_STYLES
    theme=Theme('bounds','bounds','#FFFFFF','#000000',style)
    renderer=DRAW_STYLES.get(style, draw_windows if style=='windows' else draw_wingline)
    boxes=[]
    for frame in range(ANIMATION_FRAMES):
        source=Image.new('RGBA',(512,512))
        renderer(Pen(source,theme),glyph,frame*8/ANIMATION_FRAMES)
        boxes.append(source.getchannel('A').getbbox())
    # All phases use one transform: no per-frame resizing or center drift.
    return (min(b[0] for b in boxes)/512, min(b[1] for b in boxes)/512,
            max(b[2] for b in boxes)/512, max(b[3] for b in boxes)/512)
