"""Sharp Head: a continuous pointer outline and a smooth, independent ribbon family."""
import math


def rotate(points, angle):
    c, s = math.cos(angle), math.sin(angle)
    return [(.5+(x-.5)*c-(y-.5)*s, .5+(x-.5)*s+(y-.5)*c) for x,y in points]


def rounded(p, points, softness=.22):
    """Round each polygon corner with an actual quadratic curve."""
    path=[]
    for i,corner in enumerate(points):
        previous, following=points[i-1],points[(i+1)%len(points)]
        start=tuple(c+(a-c)*softness for c,a in zip(corner,previous))
        end=tuple(c+(b-c)*softness for c,b in zip(corner,following))
        for step in range(13):
            t=step/12;u=1-t
            path.append(tuple(u*u*a+2*u*t*c+t*t*b for a,c,b in zip(start,corner,end)))
    p.shape(path)


def draw_sharp(p, glyph, frame):
    from .designs import curve
    phase=frame*math.tau/8
    if glyph=='arrow':
        # One external contour joins the head, neck, stem and short rounded foot.
        # No separately stroked line can cross the head or leave a seam.
        outline=curve((.18,.08),(.35,.27),(.60,.45),(.80,.55))
        outline+=curve((.80,.55),(.66,.44),(.47,.42),(.48,.51))[1:]
        outline+=curve((.48,.51),(.49,.60),(.55,.73),(.60,.83))[1:]
        outline+=curve((.60,.83),(.65,.81),(.69,.81),(.66,.85))[1:]
        outline+=curve((.66,.85),(.63,.89),(.51,.91),(.49,.88))[1:]
        outline+=curve((.49,.88),(.47,.85),(.52,.85),(.49,.78))[1:]
        outline+=curve((.49,.78),(.45,.69),(.42,.60),(.39,.55))[1:]
        outline+=curve((.39,.55),(.36,.50),(.23,.60),(.18,.66))[1:]
        outline+=curve((.18,.66),(.26,.43),(.25,.23),(.18,.08))[1:]
        # A shorter stem lets the actual arrow head occupy more of the fitted
        # Windows canvas instead of spending its height on the narrow tail.
        outline=[(x, y if y<=.55 else .55+(y-.55)*.70) for x,y in outline]
        p.shape(outline)
    elif glyph=='help':
        rounded(p,[(.14,.18),(.82,.18),(.87,.65),(.59,.65),(.39,.85),(.39,.65),(.14,.65)],.28)
        p.line(curve((.37,.35),(.37,.22),(.68,.25),(.58,.41)),.028)
        p.line(curve((.58,.41),(.53,.46),(.48,.42),(.48,.50)),.028)
        p.disk(.48,.58,.020)
    elif glyph=='wait':
        # A flowing infinity track, with two orbiting beads and no spinner ring.
        track=curve((.50,.50),(.06,.05),(.06,.95),(.50,.50),48)
        track+=curve((.50,.50),(.94,.05),(.94,.95),(.50,.50),48)[1:]
        p.line(track,.060)
        for offset in (0,.5):
            at=((frame/8+offset)%1)*(len(track)-1)
            index=int(at);fraction=at-index
            a,b=track[index],track[min(index+1,len(track)-1)]
            x,y=(a[i]+(b[i]-a[i])*fraction for i in (0,1))
            p.disk(x,y,.049)
    elif glyph=='appstarting':
        # Three soft pebbles rock inside a steady open cradle.
        p.line(curve((.11,.59),(.10,.88),(.90,.88),(.89,.59)),.034)
        for i in range(3):
            y=.45+.055*math.sin(phase-i*math.tau/3)
            p.capsule((.19+i*.22,y-.14,.33+i*.22,y+.14),.065)
    elif glyph=='crosshair':
        for angle in (0,math.pi/2,math.pi,3*math.pi/2):
            hook=curve((.18,.12),(.12,.28),(.17,.40),(.34,.40))
            p.line(rotate(hook,angle),.040)
        p.disk(.5,.5,.036)
    elif glyph=='ibeam':
        p.line([(.5,.22),(.5,.78)],.050)
        top=curve((.21,.19),(.32,.07),(.66,.29),(.79,.16))
        p.line(top,.038)
        p.line(rotate(top,math.pi),.038)
    elif glyph=='pen':
        nib=curve((.22,.70),(.12,.36),(.59,.10),(.82,.17))
        nib+=curve((.82,.17),(.89,.39),(.59,.75),(.22,.70))[1:]
        p.shape(nib)
        p.line(curve((.21,.82),(.34,.59),(.44,.50),(.66,.30)),.026)
        p.disk(.17,.88,.038)
    elif glyph=='no':
        p.capsule((.13,.13,.87,.87),.23)
        p.line([(.33,.59),(.49,.33)],.047)
        p.line([(.51,.67),(.67,.41)],.047)
    elif glyph.startswith('resize_'):
        angle={'resize_horizontal':0,'resize_vertical':math.pi/2,'resize_nwse':math.pi/4,'resize_nesw':-math.pi/4}[glyph]
        # Rounded opposed grips, without conventional arrow heads.
        grip=curve((.31,.22),(.08,.23),(.08,.77),(.31,.78))
        p.line(rotate(grip,angle),.061)
        p.line(rotate([(1-x,y) for x,y in grip],angle),.061)
        p.line(rotate([(.31,.50),(.69,.50)],angle),.045)
        p.disk(.5,.5,.047)
    elif glyph=='move':
        for angle in (0,math.pi/2,math.pi,3*math.pi/2):
            lobe=curve((.41,.37),(.23,.10),(.77,.10),(.59,.37))
            p.line(rotate(lobe,angle),.048)
        p.disk(.5,.5,.048)
    elif glyph=='up':
        p.line(curve((.23,.78),(.77,.91),(.67,.20),(.50,.15)),.064)
        p.line(curve((.27,.34),(.38,.15),(.53,.14),(.73,.28)),.038)
    elif glyph=='hand':
        # Tap target with a soft bent finger stroke; no chain or copied palm.
        p.ring(.41,.59,.27,15,315,.036)
        stroke=curve((.40,.63),(.41,.35),(.40,.10),(.51,.13))
        stroke+=curve((.51,.13),(.63,.13),(.55,.44),(.67,.47))[1:]
        stroke+=curve((.67,.47),(.84,.49),(.83,.65),(.76,.79))[1:]
        p.line(stroke,.060)
    elif glyph=='pin':
        p.line(curve((.28,.85),(.27,.56),(.25,.24),(.29,.12)),.047)
        flag=curve((.31,.16),(.54,.05),(.60,.34),(.81,.22))
        flag+=curve((.81,.22),(.77,.50),(.53,.48),(.31,.38))[1:]
        p.shape(flag)
        p.line(curve((.17,.88),(.34,.97),(.57,.94),(.65,.84)),.027)
    elif glyph=='person':
        # Side profile with a continuous curved neck, rather than a front bust.
        profile=curve((.22,.84),(.21,.69),(.48,.63),(.43,.51))
        profile+=curve((.43,.51),(.13,.28),(.45,.05),(.66,.18))[1:]
        profile+=curve((.66,.18),(.73,.23),(.65,.34),(.80,.41))[1:]
        profile+=[(.69,.47),(.70,.58),(.59,.62)]
        profile+=curve((.59,.62),(.56,.77),(.82,.74),(.84,.86))[1:]
        p.shape(profile)
    else:
        raise ValueError(f'Unknown Sharp Head role: {glyph}')
