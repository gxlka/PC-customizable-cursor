"""Three independent cursor families drawn as supersampled vector paths."""
import math


def turn(points, angle):
    c, s = math.cos(angle), math.sin(angle)
    return [(.5+(x-.5)*c-(y-.5)*s, .5+(x-.5)*s+(y-.5)*c) for x,y in points]


def ellipse(p, x, y, rx, ry):
    p.shape([(x+math.cos(i*math.tau/80)*rx, y+math.sin(i*math.tau/80)*ry) for i in range(80)])


def question(p, x=.5, y=.44, scale=1):
    from .designs import curve
    points=curve((x-.13*scale,y-.10*scale),(x-.13*scale,y-.28*scale),(x+.17*scale,y-.28*scale),(x+.14*scale,y-.08*scale))
    points+=curve(points[-1],(x+.12*scale,y+.02*scale),(x,y+.01*scale),(x,y+.12*scale))[1:]
    p.line(points,.032);p.disk(x,y+.25*scale,.022)


def direction(glyph):
    return {'resize_horizontal':0,'resize_vertical':math.pi/2,
            'resize_nwse':math.pi/4,'resize_nesw':-math.pi/4}[glyph]


def draw_hand(p, glyph, frame):
    from .designs import curve
    if glyph=='arrow':
        # The normal pointer is a fingertip, while Link Select is a chain.
        pts=curve((.36,.52),(.34,.38),(.34,.14),(.38,.10))
        pts+=curve((.38,.10),(.43,.05),(.50,.08),(.50,.16))[1:]
        pts+=[(.50,.46)]
        pts+=curve((.50,.46),(.54,.38),(.64,.39),(.64,.49))[1:]
        pts+=curve((.64,.49),(.71,.43),(.78,.49),(.76,.57))[1:]
        pts+=curve((.76,.57),(.85,.51),(.89,.61),(.83,.72))[1:]
        pts+=curve((.83,.72),(.78,.87),(.67,.91),(.48,.87))[1:]
        pts+=curve((.48,.87),(.34,.82),(.23,.64),(.16,.54))[1:]
        pts+=curve((.16,.54),(.09,.41),(.24,.37),(.36,.52))[1:]
        p.shape(pts);p.line([(.50,.48),(.50,.66)],.016)
    elif glyph=='help':
        # Diamond information badge.
        p.shape([(.5,.08),(.91,.5),(.5,.92),(.09,.5)])
        question(p,scale=.68)
    elif glyph=='appstarting':
        p.line([(.13,.74),(.87,.74)],.024)
        for i in range(4):
            height=.16+.36*((frame+i*2)%8)/7
            p.capsule((.16+i*.19,.66-height,.26+i*.19,.66),.045)
    elif glyph=='wait':
        # An animated hourglass, rather than a ring or dot wheel.
        p.shape([(.20,.13),(.80,.13),(.76,.31),(.58,.5),(.76,.69),(.80,.87),(.20,.87),(.24,.69),(.42,.5),(.24,.31)])
        y=.25+.020*frame
        p.line([(.34,y),(.66,y)],.026)
        p.line([(.34,.77),(.66,.77)],.026)
    elif glyph=='crosshair':
        p.shape([(.5,.28),(.72,.5),(.5,.72),(.28,.5)])
        for a in (0,math.pi/2):
            p.line(turn([(.10,.5),(.24,.5)],a));p.line(turn([(.76,.5),(.90,.5)],a))
    elif glyph=='ibeam':
        p.line([(.43,.13),(.32,.13),(.32,.87),(.43,.87)],.028)
        p.line([(.57,.13),(.68,.13),(.68,.87),(.57,.87)],.028)
        p.line([(.5,.29),(.5,.71)],.025)
    elif glyph=='pen':
        pts=curve((.17,.82),(.20,.56),(.47,.26),(.73,.14))
        pts+=curve((.73,.14),(.88,.42),(.56,.69),(.17,.82))[1:]
        p.shape(pts);p.line([(.17,.82),(.68,.28)],.021)
    elif glyph=='no':
        p.shape([(.30,.12),(.70,.12),(.88,.30),(.88,.70),(.70,.88),(.30,.88),(.12,.70),(.12,.30)])
        p.line([(.34,.34),(.66,.66)],.033);p.line([(.66,.34),(.34,.66)],.033)
    elif glyph.startswith('resize_'):
        a=direction(glyph)
        p.line(turn([(.21,.5),(.79,.5)],a),.027)
        for x in (.13,.87):
            p.shape(turn([(x,.5),(x+(.10 if x<.5 else -.10),.37),(x+(.18 if x<.5 else -.18),.5),(x+(.10 if x<.5 else -.10),.63)],a))
    elif glyph=='move':
        p.ring(.5,.5,.13,width=.025)
        for a in (0,math.pi/2,math.pi,3*math.pi/2):
            p.shape(turn([(.10,.5),(.27,.38),(.27,.62)],a))
            p.line(turn([(.28,.5),(.36,.5)],a),.023)
    elif glyph=='up':
        p.shape([(.5,.10),(.76,.39),(.62,.39),(.62,.87),(.38,.87),(.38,.39),(.24,.39)])
        p.line([(.43,.74),(.57,.74)],.022)
    elif glyph=='hand':
        # Two interlocking oblique links: no repeated normal hand.
        for x,y in ((.36,.64),(.64,.36)):
            pts=curve((x-.17,y+.12),(x-.31,y-.02),(x-.02,y-.31),(x+.12,y-.17))
            pts+=curve(pts[-1],(x+.31,y+.02),(x+.02,y+.31),(x-.17,y+.12))[1:]
            p.line(pts,.049)
    elif glyph=='pin':
        p.shape([(.30,.13),(.70,.13),(.63,.35),(.72,.55),(.55,.55),(.5,.9),(.45,.55),(.28,.55),(.37,.35)])
        p.line([(.41,.24),(.59,.24)],.018)
    elif glyph=='person':
        ellipse(p,.5,.28,.14,.18)
        p.shape([(.36,.51),(.64,.51),(.77,.70),(.71,.88),(.29,.88),(.23,.70)])


def draw_macos(p, glyph, frame):
    from .designs import curve
    if glyph=='arrow':
        p.shape([(.17,.08),(.17,.84),(.37,.66),(.51,.93),(.65,.85),(.51,.59),(.79,.59)])
    elif glyph=='help':
        p.disk(.5,.5,.38);question(p,scale=.88)
    elif glyph=='appstarting':
        # Two rotating brackets with a center progress pill.
        a=frame*45
        p.ring(.5,.5,.34,a,a+115,.045);p.ring(.5,.5,.34,a+180,a+295,.045)
        p.capsule((.39,.42,.61,.58),.065)
    elif glyph=='wait':
        for i in range(12):
            a=i*math.tau/12
            r=.17+.07*((i-frame*1.5)%12)/12
            p.line([(.5+math.cos(a)*r,.5+math.sin(a)*r),(.5+math.cos(a)*.36,.5+math.sin(a)*.36)],.035)
    elif glyph=='crosshair':
        for a in (0,math.pi/2,math.pi,3*math.pi/2):
            p.line(turn([(.15,.35),(.15,.15),(.35,.15)],a),.024)
        p.line([(.38,.5),(.62,.5)],.023);p.line([(.5,.38),(.5,.62)],.023)
    elif glyph=='ibeam':
        p.shape([(.28,.10),(.72,.10),(.72,.16),(.55,.21),(.55,.79),(.72,.84),(.72,.9),(.28,.9),(.28,.84),(.45,.79),(.45,.21),(.28,.16)])
    elif glyph=='pen':
        pts=curve((.18,.82),(.23,.62),(.63,.18),(.72,.17))
        pts+=curve((.72,.17),(.85,.17),(.85,.30),(.78,.36))[1:]
        pts+=[(.31,.78),(.18,.82)]
        p.shape(pts);p.line([(.59,.28),(.72,.41)],.023)
    elif glyph=='no':
        p.ring(.5,.5,.35,width=.049)
        p.line([(.34,.34),(.66,.66)],.049);p.line([(.66,.34),(.34,.66)],.049)
    elif glyph.startswith('resize_'):
        a=direction(glyph)
        p.line(turn([(.25,.5),(.75,.5)],a),.026)
        p.shape(turn([(.10,.5),(.30,.35),(.30,.65)],a))
        p.shape(turn([(.90,.5),(.70,.35),(.70,.65)],a))
    elif glyph=='move':
        p.shape([(.5,.08),(.62,.27),(.54,.27),(.54,.46),(.73,.46),(.73,.38),(.92,.5),(.73,.62),(.73,.54),(.54,.54),(.54,.73),(.62,.73),(.5,.92),(.38,.73),(.46,.73),(.46,.54),(.27,.54),(.27,.62),(.08,.5),(.27,.38),(.27,.46),(.46,.46),(.46,.27),(.38,.27)])
    elif glyph=='up':
        p.line([(.20,.40),(.5,.12),(.80,.40)],.045)
        p.capsule((.44,.42,.56,.88),.05)
    elif glyph=='hand':
        # Open grasp with a broad thumb and four staggered fingers.
        pts=[(.16,.49),(.28,.53),(.24,.29)]
        pts+=curve((.24,.29),(.20,.17),(.33,.14),(.36,.28))[1:]
        pts+=[(.40,.45),(.39,.16)]
        pts+=curve((.39,.16),(.39,.04),(.53,.04),(.53,.16))[1:]
        pts+=[(.54,.43),(.57,.21)]
        pts+=curve((.57,.21),(.58,.10),(.71,.13),(.70,.25))[1:]
        pts+=[(.68,.46),(.73,.32)]
        pts+=curve((.73,.32),(.78,.21),(.89,.27),(.83,.40))[1:]
        pts+=curve((.83,.40),(.81,.64),(.73,.85),(.51,.86))[1:]
        pts+=curve((.51,.86),(.31,.89),(.18,.69),(.12,.57))[1:]
        pts+=curve((.12,.57),(.08,.51),(.11,.46),(.16,.49))[1:]
        p.shape(pts)
    elif glyph=='pin':
        p.disk(.5,.31,.22)
        p.shape([(.34,.58),(.66,.58),(.5,.91)])
        p.disk(.5,.31,.047)
    elif glyph=='person':
        ellipse(p,.5,.27,.16,.13)
        pts=curve((.18,.87),(.19,.45),(.81,.45),(.82,.87))
        pts+=[(.18,.87)];p.shape(pts)
        p.line([(.32,.79),(.68,.79)],.023)


def draw_beam(p, glyph, frame):
    from .designs import curve
    if glyph=='arrow':
        # A text-selection pointer used as Normal Select.
        p.line([(.5,.12),(.5,.88)],.042)
        p.line(curve((.25,.10),(.44,.10),(.5,.20),(.5,.25)),.030)
        p.line(curve((.75,.10),(.56,.10),(.5,.20),(.5,.25)),.030)
        p.line(curve((.25,.90),(.44,.90),(.5,.80),(.5,.75)),.030)
        p.line(curve((.75,.90),(.56,.90),(.5,.80),(.5,.75)),.030)
    elif glyph=='help':
        p.line([(.28,.12),(.14,.12),(.14,.88),(.28,.88)],.026)
        p.line([(.72,.12),(.86,.12),(.86,.88),(.72,.88)],.026)
        question(p,scale=.85)
    elif glyph=='appstarting':
        p.line([(.14,.29),(.14,.71)],.030);p.line([(.86,.29),(.86,.71)],.030)
        x=.29+.06*frame
        p.line([(.25,.5),(.75,.5)],.021)
        p.shape([(x-.055,.38),(x+.055,.38),(x+.055,.62),(x-.055,.62)])
    elif glyph=='wait':
        # Animated three-sided orbit around a central square.
        a=frame*math.pi/4
        p.line(turn([(.18,.30),(.18,.70),(.82,.70),(.82,.30)],a),.033)
        p.shape([(.43,.43),(.57,.43),(.57,.57),(.43,.57)])
    elif glyph=='crosshair':
        p.line([(.12,.12),(.88,.88)],.025);p.line([(.88,.12),(.12,.88)],.025)
        p.ring(.5,.5,.12,width=.027)
    elif glyph=='ibeam':
        # Separate insertion caret, rather than repeating Normal Select.
        p.line([(.5,.12),(.5,.88)],.031)
        p.shape([(.32,.10),(.68,.10),(.5,.29)])
        p.shape([(.32,.90),(.68,.90),(.5,.71)])
    elif glyph=='pen':
        p.line([(.19,.81),(.73,.19)],.071)
        p.shape([(.12,.9),(.19,.68),(.34,.81)])
        p.line([(.65,.16),(.84,.32)],.023)
    elif glyph=='no':
        p.line([(.27,.13),(.13,.13),(.13,.87),(.27,.87)],.032)
        p.line([(.73,.13),(.87,.13),(.87,.87),(.73,.87)],.032)
        p.line([(.32,.67),(.68,.33)],.054)
    elif glyph.startswith('resize_'):
        a=direction(glyph)
        p.line(turn([(.12,.31),(.12,.69)],a),.026)
        p.line(turn([(.88,.31),(.88,.69)],a),.026)
        p.line(turn([(.25,.5),(.75,.5)],a),.023)
        p.line(turn([(.37,.38),(.25,.5),(.37,.62)],a),.023)
        p.line(turn([(.63,.38),(.75,.5),(.63,.62)],a),.023)
    elif glyph=='move':
        for a in (0,math.pi/2,math.pi,3*math.pi/2):
            p.line(turn([(.13,.37),(.13,.63)],a),.026)
            p.line(turn([(.23,.5),(.40,.5)],a),.032)
        p.shape([(.5,.38),(.62,.5),(.5,.62),(.38,.5)])
    elif glyph=='up':
        p.line([(.22,.86),(.78,.86)],.028)
        p.line([(.5,.75),(.5,.15)],.028)
        p.shape([(.5,.10),(.72,.34),(.28,.34)])
    elif glyph=='hand':
        # Underlined link badge.
        p.capsule((.14,.20,.86,.68),.18)
        p.line([(.34,.36),(.28,.44),(.34,.52)],.027)
        p.line([(.66,.36),(.72,.44),(.66,.52)],.027)
        p.line([(.25,.84),(.75,.84)],.031)
    elif glyph=='pin':
        p.shape([(.5,.09),(.77,.36),(.5,.63),(.23,.36)])
        p.line([(.5,.63),(.5,.9)],.027);p.line([(.37,.9),(.63,.9)],.024)
        p.ring(.5,.36,.07,width=.020)
    elif glyph=='person':
        p.line([(.20,.14),(.10,.14),(.10,.86),(.20,.86)],.024)
        p.line([(.80,.14),(.90,.14),(.90,.86),(.80,.86)],.024)
        p.disk(.5,.31,.13)
        p.line(curve((.30,.78),(.30,.53),(.70,.53),(.70,.78)),.045)


DRAW_STYLES={'hand':draw_hand,'macos':draw_macos,'beam':draw_beam}
NORMAL_HOTSPOTS={'hand':(.42,.09),'macos':(.17,.08),'beam':(.5,.5)}
