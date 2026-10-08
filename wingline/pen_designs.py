"""Pen: a continuous pointer outline and a smooth, independent ribbon family."""
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


def draw_pen(p, glyph, frame):
    from .designs import curve
    phase=frame*math.tau/8
    if glyph=='arrow':
        # A solid, rounded barrel with one continuous outline and a writing
        # tip at the click hotspot. No arrow head or separate stem.
        outline=curve((.12,.10),(.20,.12),(.30,.14),(.36,.18))
        outline+=curve((.36,.18),(.50,.32),(.67,.49),(.80,.63))[1:]
        outline+=curve((.80,.63),(.91,.74),(.86,.84),(.77,.85))[1:]
        outline+=curve((.77,.85),(.72,.86),(.67,.83),(.64,.80))[1:]
        outline+=curve((.64,.80),(.50,.66),(.33,.49),(.20,.36))[1:]
        outline+=curve((.20,.36),(.16,.29),(.14,.17),(.12,.10))[1:]
        p.shape(outline)
        # A single fine cap seam keeps the icon recognizably a pen.
        p.rawline([(.69,.53),(.54,.69)],p.theme.edge,.018)
    elif glyph=='help':
        rounded(p,[(.14,.18),(.82,.18),(.87,.65),(.59,.65),(.39,.85),(.39,.65),(.14,.65)],.28)
        p.line(curve((.37,.35),(.37,.22),(.68,.25),(.58,.41)),.028)
        p.line(curve((.58,.41),(.53,.46),(.48,.42),(.48,.50)),.028)
        p.disk(.48,.58,.020)
    elif glyph=='wait':
        # Filled hourglass with moving sand inside a steady solid silhouette.
        rounded(p,[(.20,.13),(.80,.13),(.83,.28),(.61,.50),(.83,.72),
                   (.80,.87),(.20,.87),(.17,.72),(.39,.50),(.17,.28)],.27)
        y=.50+.20*math.sin(phase)
        p.rawline([(.50,y),(.50,y)],p.theme.edge,.055)
    elif glyph=='appstarting':
        # A solid rounded tray supporting three gently moving filled tiles.
        p.capsule((.10,.57,.90,.85),.14)
        for i in range(3):
            y=.43+.055*math.sin(phase-i*math.tau/3)
            p.capsule((.19+i*.22,y-.14,.33+i*.22,y+.14),.065)
    elif glyph=='crosshair':
        rounded(p,[(.50,.10),(.90,.50),(.50,.90),(.10,.50)],.23)
        p.rawline([(.36,.50),(.64,.50)],p.theme.edge,.024)
        p.rawline([(.50,.36),(.50,.64)],p.theme.edge,.024)
    elif glyph=='ibeam':
        rounded(p,[(.23,.12),(.77,.12),(.77,.27),(.60,.27),(.60,.73),
                   (.77,.73),(.77,.88),(.23,.88),(.23,.73),(.40,.73),
                   (.40,.27),(.23,.27)],.22)
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
        # A single filled handle with rounded end grips and a solid bridge.
        points=[(.12,.22),(.31,.22),(.31,.40),(.69,.40),(.69,.22),(.88,.22),
                (.88,.78),(.69,.78),(.69,.60),(.31,.60),(.31,.78),(.12,.78)]
        rounded(p,rotate(points,angle),.28)
    elif glyph=='move':
        # Filled four-lobed pad, with no transparent center or arrow heads.
        path=[]
        for angle in (0,math.pi/2,math.pi,3*math.pi/2):
            lobe=curve((.35,.35),(.24,.02),(.76,.02),(.65,.35))
            path+=rotate(lobe,angle)
        p.shape(path)
        p.rawline([(.44,.50),(.56,.50)],p.theme.edge,.022)
        p.rawline([(.50,.44),(.50,.56)],p.theme.edge,.022)
    elif glyph=='up':
        # A solid hooked ribbon replaces the open wire shape.
        path=curve((.22,.77),(.45,.90),(.72,.82),(.69,.48))
        path+=curve((.69,.48),(.66,.17),(.50,.07),(.29,.26))[1:]
        path+=curve((.29,.26),(.39,.40),(.45,.30),(.48,.35))[1:]
        path+=curve((.48,.35),(.58,.62),(.46,.71),(.24,.59))[1:]
        path+=curve((.24,.59),(.19,.63),(.18,.72),(.22,.77))[1:]
        p.shape(path)
    elif glyph=='hand':
        # A continuous side-on pointing hand with a rounded filled palm.
        path=curve((.38,.57),(.38,.42),(.35,.14),(.44,.13))
        path+=curve((.44,.13),(.59,.09),(.55,.38),(.59,.44))[1:]
        path+=curve((.59,.44),(.85,.43),(.88,.60),(.78,.82))[1:]
        path+=curve((.78,.82),(.70,.94),(.43,.93),(.35,.82))[1:]
        path+=curve((.35,.82),(.28,.72),(.13,.66),(.17,.56))[1:]
        path+=curve((.17,.56),(.21,.47),(.32,.54),(.38,.57))[1:]
        p.shape(path)
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
        raise ValueError(f'Unknown Pen role: {glyph}')
