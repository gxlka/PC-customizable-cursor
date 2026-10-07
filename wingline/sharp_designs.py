"""Sharp Head: a swept sail pointer and independently drawn angular role icons."""
import math


def rotate(points, angle):
    c, s = math.cos(angle), math.sin(angle)
    return [(.5+(x-.5)*c-(y-.5)*s, .5+(x-.5)*s+(y-.5)*c) for x,y in points]


def draw_sharp(p, glyph, frame):
    from .designs import curve
    if glyph == 'arrow':
        # Sketch's swept head, concave left edge, shorter stem and curved foot.
        head = curve((.18,.08),(.35,.27),(.60,.45),(.80,.55))
        head += curve((.80,.55),(.62,.39),(.35,.46),(.18,.66))[1:]
        head += curve((.18,.66),(.26,.43),(.25,.23),(.18,.08))[1:]
        p.shape(head)
        p.line([(.43,.48),(.57,.79)],.048)
        p.line(curve((.40,.85),(.51,.85),(.66,.82),(.73,.77)),.040)
    elif glyph == 'help':
        # Open folded information ribbon, never a pointer with a badge.
        p.shape([(.16,.18),(.72,.18),(.87,.33),(.73,.47),(.87,.63),(.72,.82),(.16,.82),(.28,.50)])
        p.line([(.51,.39),(.51,.64)],.042)
        p.disk(.51,.29,.030)
    elif glyph == 'wait':
        # Three revolving, tapered turbine vanes and a stationary hub.
        for i in range(3):
            angle = frame*math.tau/8 + i*math.tau/3
            p.shape(rotate([(.55,.35),(.62,.12),(.79,.21),(.74,.40),(.61,.47)],angle))
        p.shape([(.50,.43),(.57,.50),(.50,.57),(.43,.50)])
    elif glyph == 'appstarting':
        # A scanning, stepped equalizer with a detached baseline.
        for i in range(5):
            x = .16+i*.14
            h = .20+.23*(.5+.5*math.cos(frame*math.tau/8-i*.8))
            p.shape([(x,.66),(x,.66-h),(x+.075,.61-h),(x+.075,.66)])
        p.line([(.12,.79),(.88,.79)],.034)
    elif glyph == 'crosshair':
        for angle in (0,math.pi/2,math.pi,3*math.pi/2):
            p.line(rotate([(.34,.12),(.12,.12),(.12,.34)],angle),.045)
        p.line([(.50,.38),(.50,.62)],.034)
        p.line([(.38,.50),(.62,.50)],.034)
    elif glyph == 'ibeam':
        p.shape([(.45,.14),(.55,.14),(.55,.86),(.45,.86)])
        for angle in (0,math.pi):
            p.line(rotate([(.23,.24),(.23,.13),(.77,.13),(.77,.24)],angle),.040)
    elif glyph == 'pen':
        p.shape([(.16,.86),(.24,.62),(.69,.13),(.85,.28),(.40,.76)])
        p.line([(.31,.65),(.65,.29)],.018)
        p.shape([(.70,.09),(.80,.09),(.91,.20),(.91,.29)])
    elif glyph == 'no':
        p.shape([(.29,.12),(.71,.12),(.88,.50),(.71,.88),(.29,.88),(.12,.50)])
        p.line([(.30,.50),(.70,.50)],.068)
    elif glyph.startswith('resize_'):
        angle={'resize_horizontal':0,'resize_vertical':math.pi/2,'resize_nwse':math.pi/4,'resize_nesw':-math.pi/4}[glyph]
        for mirror in (False,True):
            blade=[(.09,.50),(.32,.26),(.29,.44),(.40,.44),(.40,.56),(.29,.56),(.32,.74)]
            if mirror: blade=[(1-x,y) for x,y in blade]
            p.shape(rotate(blade,angle))
        p.shape(rotate([(.46,.46),(.54,.46),(.54,.54),(.46,.54)],angle))
    elif glyph == 'move':
        for angle in (0,math.pi/2,math.pi,3*math.pi/2):
            p.shape(rotate([(.50,.07),(.65,.27),(.50,.36),(.35,.27)],angle))
        p.shape([(.43,.43),(.57,.43),(.57,.57),(.43,.57)])
    elif glyph == 'up':
        p.shape([(.50,.10),(.78,.37),(.62,.34),(.62,.72),(.79,.89),(.21,.89),(.38,.72),(.38,.34),(.22,.37)])
    elif glyph == 'hand':
        # Link selection: interlocking folded ribbons, not another family's hand.
        p.shape([(.12,.29),(.49,.13),(.67,.29),(.54,.42),(.43,.31),(.25,.40),(.25,.60),(.40,.66),(.30,.80),(.12,.69)])
        p.shape([(.88,.71),(.51,.87),(.33,.71),(.46,.58),(.57,.69),(.75,.60),(.75,.40),(.60,.34),(.70,.20),(.88,.31)])
        p.line([(.38,.60),(.62,.40)],.045)
    elif glyph == 'pin':
        p.shape([(.50,.08),(.79,.27),(.76,.53),(.50,.91),(.24,.53),(.21,.27)])
        p.shape([(.50,.22),(.62,.35),(.50,.48),(.38,.35)])
    elif glyph == 'person':
        p.shape([(.36,.13),(.64,.13),(.71,.30),(.62,.48),(.38,.48),(.29,.30)])
        p.shape([(.30,.56),(.70,.56),(.86,.86),(.14,.86)])
        p.line([(.50,.60),(.50,.77)],.032)
    else:
        raise ValueError(f'Unknown Sharp Head role: {glyph}')
