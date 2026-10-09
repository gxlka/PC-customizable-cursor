"""Unpublished Windows Flow concept: new geometry for all seventeen roles."""
import math
from PIL import Image, ImageDraw
from .designs import curve
from .pen_designs import rotate

FRAMES=48

def render(glyph,size=64,frame=0,dark=False):
    n=size*4; im=Image.new('RGBA',(n,n));d=ImageDraw.Draw(im)
    fill='#20242a' if dark else '#ffffff';edge='#ffffff' if dark else '#20242a'
    phase=math.tau*frame/FRAMES;wave=(1-math.cos(phase))/2
    accent=tuple(round(a+(b-a)*wave) for a,b in zip((110,120,132),(180,188,197)))
    def coords(pts):return [(round(x*n),round(y*n)) for x,y in pts]
    def line(pts,w=.052,color=None):
        color=color or fill; px=coords(pts);wid=round(w*n)
        d.line(px,fill=color,width=wid,joint='curve')
        for x,y in (px[0],px[-1]):d.ellipse((x-wid/2,y-wid/2,x+wid/2,y+wid/2),fill=color)
    def stroke(pts,w=.07):line(pts,w+.045,edge);line(pts,w,fill)
    def shape(pts):
        px=coords(pts);d.polygon(px,fill=fill);d.line(px+[px[0]],fill=edge,width=round(.026*n),joint='curve')
    def roundpoly(pts,r=.18):
        path=[]
        for i,c in enumerate(pts):
            a=tuple(v+(p-v)*r for v,p in zip(c,pts[i-1]));b=tuple(v+(p-v)*r for v,p in zip(c,pts[(i+1)%len(pts)]))
            for j in range(13):
                t=j/12;u=1-t;path.append(tuple(u*u*x+2*u*t*y+t*t*z for x,y,z in zip(a,c,b)))
        shape(path)
    def box(b,r=.06,color=None):
        b=tuple(round(v*n) for v in b);d.rounded_rectangle(b,round(r*n),fill=edge)
        e=round(.024*n);d.rounded_rectangle((b[0]+e,b[1]+e,b[2]-e,b[3]-e),max(1,round(r*n)-e),fill=color or fill)
    def disk(x,y,r,color=None):
        if color:d.ellipse(tuple(round(v*n) for v in (x-r,y-r,x+r,y+r)),fill=color)
        else:shape([(x+r*math.cos(t*math.tau/64),y+r*math.sin(t*math.tau/64)) for t in range(64)])
    if glyph=='arrow':
        # Continuous Windows arrow; sharp click tip, gently curved heel.
        p=[(.12,.08)]
        p+=curve((.12,.08),(.10,.27),(.11,.59),(.14,.80))[1:]
        p+=curve((.14,.80),(.17,.85),(.27,.71),(.34,.64))[1:]
        p+=[(.49,.89)]
        p+=curve((.49,.89),(.53,.96),(.68,.88),(.64,.81))[1:]
        p+=[(.49,.56)]
        p+=curve((.49,.56),(.61,.56),(.78,.63),(.79,.57))[1:]
        p+=curve((.79,.57),(.57,.39),(.32,.20),(.12,.08))[1:];shape(p)
        # Gentle breathing inset, no moving pointer or slash.
        line([(.50,.77),(.55,.84)],.024,accent)
    elif glyph=='help':
        # Open information booklet, not a bubble, ticket or badge.
        roundpoly([(.12,.22),(.42,.15),(.50,.22),(.58,.15),(.88,.22),(.88,.82),(.58,.75),(.50,.82),(.42,.75),(.12,.82)],.12)
        line([(.50,.25),(.50,.69)],.022,edge)
        q=curve((.62,.36),(.60,.25),(.81,.27),(.77,.38))+curve((.77,.38),(.74,.44),(.69,.43),(.69,.51))[1:]
        line(q,.026,edge);disk(.69,.61,.026,accent)
        line([(.23,.36),(.37,.33)],.025,accent);line([(.23,.48),(.37,.45)],.025,accent)
    elif glyph=='appstarting':
        # Two softly stacked document cards, with a travelling progress dot.
        box((.31,.15,.85,.68),.08);box((.15,.33,.69,.85),.08)
        line([(.26,.48),(.57,.48)],.026,edge);line([(.26,.59),(.48,.59)],.026,edge)
        disk(.29+.26*wave,.73,.045,accent)
    elif glyph=='wait':
        # Three curved beans circulate around a stable empty center.
        for i in range(3):
            a=phase+i*math.tau/3
            pts=[]
            for j in range(19):
                t=a+j/18*.9;pts.append((.5+.28*math.cos(t),.5+.28*math.sin(t)))
            stroke(pts,.13)
    elif glyph=='crosshair':
        # A connected slim diamond scope with axis needles.
        roundpoly([(.5,.15),(.85,.5),(.5,.85),(.15,.5)],.30)
        for pts in [[(.5,.07),(.5,.32)],[(.5,.68),(.5,.93)],[(.07,.5),(.32,.5)],[(.68,.5),(.93,.5)]]:stroke(pts,.044)
        disk(.5,.5,.038,accent)
    elif glyph=='ibeam':
        # Asymmetric rounded serifs on a continuous insertion stem.
        roundpoly([(.27,.10),(.72,.10),(.72,.22),(.55,.22),(.55,.77),(.66,.77),(.66,.90),(.21,.90),(.21,.77),(.43,.77),(.43,.22),(.27,.22)],.25)
        line([(.48,.37),(.48,.62)],.022,accent)
    elif glyph=='pen':
        # Upright capped felt-tip, separate from all diagonal pen/nib artwork.
        roundpoly([(.38,.12),(.62,.12),(.67,.20),(.67,.63),(.60,.72),(.50,.89),(.40,.72),(.33,.63),(.33,.20)],.18)
        line([(.36,.29),(.64,.29)],.027,edge);line([(.5,.42),(.5,.59)],.025,accent)
    elif glyph=='no':
        # Rounded shield with a single filled minus.
        pts=curve((.16,.18),(.35,.12),(.65,.12),(.84,.18))
        pts+=curve((.84,.18),(.86,.63),(.72,.78),(.5,.90))[1:]
        pts+=curve((.5,.90),(.28,.78),(.14,.63),(.16,.18))[1:];shape(pts)
        line([(.32,.45),(.68,.45)],.065,edge)
        line([(.4,.64),(.6,.64)],.022,accent)
    elif glyph.startswith('resize_'):
        a={'resize_horizontal':0,'resize_vertical':math.pi/2,'resize_nwse':math.pi/4,'resize_nesw':-math.pi/4}[glyph]
        # Broad curved fins, no old grips, arrow-tip paths or bridge.
        for side in [0,math.pi]:
            pts=curve((.12,.5),(.23,.26),(.35,.25),(.38,.30))
            pts+=curve((.38,.30),(.30,.43),(.30,.57),(.38,.70))[1:]
            pts+=curve((.38,.70),(.35,.75),(.23,.74),(.12,.5))[1:];shape(rotate(pts,a+side))
        roundpoly(rotate([(.5,.40),(.60,.5),(.5,.60),(.40,.5)],a),.28)
        x=.5+.026*math.sin(phase)
        xx,yy=rotate([(x,.5)],a)[0];disk(xx,yy,.027,accent)
    elif glyph=='move':
        # Four smooth compass fins surround a filled central circular hub.
        for a in [0,math.pi/2,math.pi,3*math.pi/2]:
            pts=curve((.5,.08),(.38,.19),(.35,.28),(.39,.33))
            pts+=curve((.39,.33),(.46,.28),(.54,.28),(.61,.33))[1:]
            pts+=curve((.61,.33),(.65,.28),(.62,.19),(.5,.08))[1:];shape(rotate(pts,a))
        disk(.5,.5,.12);disk(.5,.5,.036,accent)
    elif glyph=='up':
        # Connected rounded lift arrow anchored on a shallow tray.
        roundpoly([(.5,.10),(.75,.38),(.59,.38),(.59,.67),(.82,.67),(.82,.84),(.18,.84),(.18,.67),(.41,.67),(.41,.38),(.25,.38)],.20)
        line([(.34,.76),(.66,.76)],.025,accent)
    elif glyph=='hand':
        # Link control is a fingertip tapping a wide soft oval button.
        box((.12,.52,.88,.88),.15)
        pts=curve((.41,.60),(.40,.51),(.40,.18),(.47,.12))
        pts+=curve((.47,.12),(.62,.08),(.60,.26),(.59,.39))[1:]
        pts+=curve((.59,.39),(.74,.40),(.78,.56),(.72,.68))[1:]
        pts+=curve((.72,.68),(.62,.76),(.43,.73),(.41,.60))[1:];shape(pts)
        line([(.22,.69),(.29,.69)],.028,accent)
    elif glyph=='pin':
        # Round beacon on a curved two-leg stand, no teardrop or flag.
        p=curve((.23,.83),(.31,.72),(.36,.63),(.43,.52))
        stroke(p,.08);stroke([(.57,.52),(.77,.83)],.08)
        disk(.5,.34,.23);disk(.5,.34,.055,accent)
        stroke([(.19,.87),(.81,.87)],.06)
    elif glyph=='person':
        # Rounded identity card with its own engraved profile.
        box((.16,.12,.84,.88),.13)
        disk(.50,.34,.115,edge)
        line(curve((.31,.68),(.31,.47),(.69,.47),(.69,.68)),.067,edge)
        line([(.36,.78),(.64,.78)],.023,accent)
    else:raise ValueError(glyph)
    return im.resize((size,size),Image.Resampling.LANCZOS)
