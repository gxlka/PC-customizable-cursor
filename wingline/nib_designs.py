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
        # Tall filled help ticket with soft shoulders and a small lower tab.
        rounded(p,[(.27,.10),(.74,.10),(.84,.23),(.84,.73),(.63,.73),
                   (.54,.90),(.44,.73),(.17,.73),(.17,.23)],.28)
        q=curve((.39,.34),(.38,.19),(.68,.22),(.60,.39))
        q+=curve((.60,.39),(.56,.44),(.49,.41),(.49,.52))[1:]
        p.rawline(q,p.theme.edge,.035)
        p.rawline([(.49,.62),(.49,.62)],p.theme.edge,.048)
    elif glyph=='wait':
        # Three rounded squares travel a smooth vertical wave, never rotate.
        for i in range(3):
            y=.5+.13*math.sin(phase-i*math.tau/3)
            p.capsule((.10+i*.28,y-.115,.31+i*.28,y+.115),.07)
    elif glyph=='appstarting':
        # Two broad parallel bars slide gently in opposite directions.
        for i in range(2):
            x=.5+(.075 if i==0 else -.075)*math.sin(phase)
            p.capsule((x-.30,.20+i*.35,x+.30,.43+i*.35),.115)
    elif glyph=='crosshair':
        # Four blunt filled corner pads and a solid center dot.
        for x,y in ((.14,.14),(.61,.14),(.14,.61),(.61,.61)):
            p.capsule((x,y,x+.25,y+.25),.085)
        p.disk(.5,.5,.105)
    elif glyph=='ibeam':
        # One filled slim spindle with broad rounded rectangular serif blocks.
        rounded(p,[(.27,.11),(.73,.11),(.77,.20),(.73,.30),(.59,.30),
                   (.59,.70),(.73,.70),(.77,.80),(.73,.89),(.27,.89),
                   (.23,.80),(.27,.70),(.41,.70),(.41,.30),(.27,.30),(.23,.20)],.25)
    elif glyph=='pen':
        # A flat marker silhouette with a blunt chisel and rounded cap.
        rounded(p,[(.26,.13),(.60,.13),(.68,.23),(.68,.69),(.50,.86),
                   (.26,.86),(.20,.76),(.20,.23)],.22)
        p.rawline([(.24,.65),(.63,.65)],p.theme.edge,.023)
    elif glyph=='no':
        # Rounded stop octagon with a bold centered cancellation cross.
        rounded(p,[(.32,.12),(.68,.12),(.88,.32),(.88,.68),(.68,.88),
                   (.32,.88),(.12,.68),(.12,.32)],.30)
        p.rawline([(.36,.36),(.64,.64)],p.theme.edge,.048)
        p.rawline([(.36,.64),(.64,.36)],p.theme.edge,.048)
    elif glyph.startswith('resize_'):
        # Square-ended grips connect with a filled bridge. No nibs or arrows.
        angle={'resize_horizontal':0,'resize_vertical':math.pi/2,
               'resize_nwse':math.pi/4,'resize_nesw':-math.pi/4}[glyph]
        points=[(.10,.25),(.29,.25),(.29,.42),(.71,.42),(.71,.25),(.90,.25),
                (.90,.75),(.71,.75),(.71,.58),(.29,.58),(.29,.75),(.10,.75)]
        rounded(p,rotate(points,angle),.16)
        # Direction remains a static Windows resize indicator, never animates.
    elif glyph=='move':
        # Filled five-pad control with short, square shoulders.
        rounded(p,[(.37,.12),(.63,.12),(.63,.37),(.88,.37),(.88,.63),
                   (.63,.63),(.63,.88),(.37,.88),(.37,.63),(.12,.63),
                   (.12,.37),(.37,.37)],.25)
        p.rawline([(.50,.50),(.50,.50)],p.theme.edge,.068)
    elif glyph=='up':
        # Solid stepped lifting handle, with no pointed arrow component.
        rounded(p,[(.32,.12),(.68,.12),(.68,.32),(.85,.32),(.85,.51),
                   (.61,.51),(.61,.85),(.39,.85),(.39,.51),(.15,.51),(.15,.32),(.32,.32)],.24)
    elif glyph=='hand':
        # A tap control: filled circular thumb pad and a rounded vertical finger.
        path=curve((.28,.76),(.13,.69),(.16,.50),(.34,.48))
        path+=[(.34,.22)]
        path+=curve((.34,.22),(.34,.07),(.55,.07),(.55,.22))[1:]
        path+=[(.55,.45)]
        path+=curve((.55,.45),(.83,.39),(.91,.73),(.72,.86))[1:]
        path+=curve((.72,.86),(.56,.96),(.39,.85),(.28,.76))[1:]
        p.shape(path)
        p.rawline([(.63,.57),(.65,.72)],p.theme.edge,.020)
    elif glyph=='pin':
        # A location beacon on a broad rounded pedestal; no droplet pin.
        p.capsule((.25,.14,.75,.61),.15)
        p.capsule((.41,.57,.59,.77),.07)
        p.capsule((.13,.74,.87,.88),.06)
        p.rawline([(.50,.36),(.50,.36)],p.theme.edge,.105)
    elif glyph=='person':
        # A rounded bust with an offset head and asymmetrical shoulder.
        path=curve((.17,.86),(.17,.62),(.30,.56),(.39,.55))
        path+=curve((.39,.55),(.22,.46),(.22,.13),(.47,.12))[1:]
        path+=curve((.47,.12),(.75,.10),(.79,.45),(.61,.55))[1:]
        path+=curve((.61,.55),(.83,.59),(.90,.72),(.83,.86))[1:]
        path+=curve((.83,.86),(.68,.91),(.32,.91),(.17,.86))[1:]
        p.shape(path)
    else:
        raise ValueError(f'Unknown Nib role: {glyph}')
