"""Nib's solid, rounded artwork. Each state has its own silhouette."""
import math
from .pen_designs import rounded, rotate


def draw_nib(p, glyph, frame):
    from .designs import curve
    phase=frame*math.tau/8
    if glyph=='arrow':
        path=curve((.12,.10),(.30,.17),(.69,.28),(.80,.47))
        path+=curve((.80,.47),(.98,.78),(.61,.99),(.39,.78))[1:]
        path+=curve((.39,.78),(.26,.64),(.20,.32),(.12,.10))[1:]
        p.shape(path)
    elif glyph=='help':
        rounded(p,[(.22,.10),(.75,.16),(.89,.55),(.66,.85),(.16,.77),(.10,.35)],.35)
        q=curve((.39,.37),(.37,.20),(.71,.26),(.60,.43))
        q+=curve((.60,.43),(.56,.48),(.49,.45),(.48,.57))[1:]
        p.rawline(q,p.theme.edge,.035)
        p.rawline([(.48,.67),(.48,.67)],p.theme.edge,.045)
    elif glyph=='wait':
        # Two solid pebbles orbit continuously, without a visible guide ring.
        for offset in (0,math.pi):
            a=phase+offset
            x,y=.5+.24*math.cos(a),.5+.24*math.sin(a)
            p.capsule((x-.12,y-.14,x+.12,y+.14),.12)
    elif glyph=='appstarting':
        # Unequal rounded pillars breathe in a smooth repeating wave.
        for i,h in enumerate((.24,.43,.30)):
            y=.55+.04*math.sin(phase-i*math.tau/3)
            p.capsule((.14+i*.25,y-h,.32+i*.25,y+.20),.09)
    elif glyph=='crosshair':
        # A solid rounded precision tile with four shallow corner scallops.
        rounded(p,[(.25,.11),(.75,.11),(.79,.29),(.89,.35),(.89,.65),
                   (.79,.71),(.75,.89),(.25,.89),(.21,.71),(.11,.65),
                   (.11,.35),(.21,.29)],.30)
        p.rawline([(.37,.50),(.63,.50)],p.theme.edge,.026)
        p.rawline([(.50,.37),(.50,.63)],p.theme.edge,.026)
    elif glyph=='ibeam':
        # Curved serif lips join one broad filled spine.
        path=curve((.20,.14),(.35,.23),(.65,.23),(.80,.14))
        path+=curve((.80,.14),(.86,.20),(.75,.32),(.60,.32))[1:]
        path+=[(.60,.68)]
        path+=curve((.60,.68),(.75,.68),(.86,.80),(.80,.86))[1:]
        path+=curve((.80,.86),(.65,.77),(.35,.77),(.20,.86))[1:]
        path+=curve((.20,.86),(.14,.80),(.25,.68),(.40,.68))[1:]
        path+=[(.40,.32)]
        path+=curve((.40,.32),(.25,.32),(.14,.20),(.20,.14))[1:]
        p.shape(path)
    elif glyph=='pen':
        # A rounded paintbrush, independently drawn from the main Nib.
        rounded(p,[(.19,.85),(.13,.62),(.33,.41),(.45,.44),(.70,.12),
                   (.85,.23),(.59,.57),(.59,.70),(.38,.88)],.25)
        p.rawline([(.31,.48),(.54,.65)],p.theme.edge,.022)
    elif glyph=='no':
        rounded(p,[(.33,.10),(.76,.20),(.87,.62),(.54,.90),(.16,.72),(.11,.31)],.32)
        p.rawline([(.32,.49),(.70,.49)],p.theme.edge,.064)
    elif glyph.startswith('resize_'):
        angle={'resize_horizontal':0,'resize_vertical':math.pi/2,
               'resize_nwse':math.pi/4,'resize_nesw':-math.pi/4}[glyph]
        # Smooth bulb ends, a generous filled waist, no conventional arrowheads.
        path=curve((.32,.32),(.03,.10),(.02,.90),(.32,.68))
        path+=curve((.32,.68),(.41,.59),(.59,.59),(.68,.68))[1:]
        path+=curve((.68,.68),(.97,.90),(.98,.10),(.68,.32))[1:]
        path+=curve((.68,.32),(.59,.41),(.41,.41),(.32,.32))[1:]
        p.shape(rotate(path,angle))
        p.rawline(rotate([(.50,.41),(.50,.59)],angle),p.theme.edge,.018)
    elif glyph=='move':
        # A soft four-petal pad with a broad solid center.
        path=[]
        for angle in (0,math.pi/2,math.pi,3*math.pi/2):
            petal=curve((.34,.34),(.29,-.01),(.71,-.01),(.66,.34))
            path+=rotate(petal,angle)
        p.shape(path)
        p.rawline([(.40,.50),(.60,.50)],p.theme.edge,.026)
        p.rawline([(.50,.40),(.50,.60)],p.theme.edge,.026)
    elif glyph=='up':
        rounded(p,[(.32,.10),(.70,.10),(.87,.33),(.76,.89),(.24,.89),(.13,.33)],.30)
        p.rawline([(.32,.46),(.50,.27),(.68,.46)],p.theme.edge,.038)
        p.rawline([(.50,.27),(.50,.71)],p.theme.edge,.038)
    elif glyph=='hand':
        # Side-on horizontal index finger; every edge belongs to a filled palm.
        path=curve((.13,.43),(.15,.34),(.24,.31),(.31,.34))
        path+=curve((.31,.34),(.39,.24),(.44,.17),(.51,.18))[1:]
        path+=curve((.51,.18),(.62,.22),(.54,.30),(.49,.35))[1:]
        path+=[(.82,.35)]
        path+=curve((.82,.35),(.98,.35),(.97,.51),(.82,.51))[1:]
        path+=[(.64,.51)]
        path+=curve((.64,.51),(.85,.55),(.83,.69),(.71,.70))[1:]
        path+=curve((.71,.70),(.81,.82),(.65,.90),(.52,.84))[1:]
        path+=curve((.52,.84),(.31,.85),(.20,.80),(.13,.71))[1:]
        path+=[(.13,.43)]
        p.shape(path)
    elif glyph=='pin':
        # A folded location map, with a solid pin dot as its visual center.
        rounded(p,[(.12,.25),(.36,.14),(.62,.25),(.87,.13),(.87,.75),
                   (.62,.87),(.36,.76),(.12,.88)],.16)
        p.rawline([(.36,.24),(.36,.66)],p.theme.edge,.019)
        p.rawline([(.62,.35),(.62,.77)],p.theme.edge,.019)
        p.rawline([(.50,.48),(.50,.48)],p.theme.edge,.11)
    elif glyph=='person':
        # A filled portrait badge, distinct from every existing avatar bust.
        p.capsule((.23,.09,.77,.91),.20)
        p.rawline([(.50,.33),(.50,.33)],p.theme.edge,.13)
        p.rawline(curve((.35,.65),(.35,.49),(.65,.49),(.65,.65)),p.theme.edge,.038)
    else:
        raise ValueError(f'Unknown Nib role: {glyph}')
