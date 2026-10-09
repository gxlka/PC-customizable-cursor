"""Build the approved Windows Flow family and append it to the full pack."""
import argparse
import ctypes
import os
from pathlib import Path
import shutil
import struct
import zipfile
from functools import lru_cache
from PIL import Image, ImageDraw
from wingline.fluent_prototype import render, FRAMES
from wingline.roles import ROLE_ORDER, Theme
from wingline.artwork import SUPPORTED_SIZES
from wingline.cur import encode_cur
from wingline.ani import _chunk, _validate_cursor_frame
from wingline.package import _installer_text, _read_riff_chunks, _check_cur

ROOT=Path(__file__).resolve().parent
RATES=[2+(i%5 in (2,4)) for i in range(FRAMES)]

@lru_cache(maxsize=40)
def bounds(glyph):
    frames=range(FRAMES) if glyph=='wait' else (0,)
    boxes=[render(glyph,256,f).getchannel('A').getbbox() for f in frames]
    return (min(b[0] for b in boxes),min(b[1] for b in boxes),max(b[2] for b in boxes),max(b[3] for b in boxes))

def cursor(role,size,frame=0,dark=False):
    # Fixed bounds over the cycle prevent size pumping or click-point drift.
    b=bounds(role.glyph);scale=size/256
    crop=tuple(round(v*scale) for v in b)
    raw=render(role.glyph,size,frame,dark).crop(crop)
    extent=round(size*.875);ratio=extent/max(raw.size)
    fitted=raw.resize((round(raw.width*ratio),round(raw.height*ratio)),Image.Resampling.LANCZOS)
    x=(size-fitted.width)//2;y=(size-fitted.height)//2
    image=Image.new('RGBA',(size,size));image.alpha_composite(fitted,(x,y))
    h={'arrow':(.12,.08),'hand':(.49,.12),'pen':(.5,.89),'up':(.5,.10)}.get(role.glyph,(.5,.5))
    hotspot=(round(x+(h[0]*size-crop[0])*ratio),round(y+(h[1]*size-crop[1])*ratio))
    hotspot=tuple(max(0,min(size-1,v)) for v in hotspot)
    return image,hotspot

def animated(role,size,dark):
    frames=[encode_cur([cursor(role,size,f,dark)]) for f in range(FRAMES)]
    for f in frames:_validate_cursor_frame(f)
    header=struct.pack('<9I',36,FRAMES,FRAMES,size,size,32,1,2,1)
    data=b'ACON'+_chunk(b'anih',header)+_chunk(b'rate',struct.pack('<'+str(FRAMES)+'I',*RATES))+_chunk(b'LIST',b'fram'+b''.join(_chunk(b'icon',f) for f in frames))
    return b'RIFF'+struct.pack('<I',len(data))+data

def verify_ani(data,size):
    assert data[:4]==b'RIFF' and data[8:12]==b'ACON'
    assert struct.unpack_from('<I',data,4)[0]==len(data)-8
    chunks=dict(_read_riff_chunks(data,12,len(data)))
    assert struct.unpack('<9I',chunks[b'anih'])==(36,FRAMES,FRAMES,size,size,32,1,2,1)
    assert list(struct.unpack('<'+str(FRAMES)+'I',chunks[b'rate']))==RATES
    listing=chunks[b'LIST'];assert listing[:4]==b'fram'
    icons=_read_riff_chunks(listing,4,len(listing));assert len(icons)==FRAMES
    hotspots=set()
    for kind,f in icons:
        assert kind==b'icon';_validate_cursor_frame(f)
        hotspots.add(struct.unpack_from('<HH',f,10))
    assert len(hotspots)==1

def verify_native(directory):
    if os.name!='nt':return
    user=ctypes.WinDLL('user32',use_last_error=True)
    user.LoadImageW.argtypes=[ctypes.c_void_p,ctypes.c_wchar_p,ctypes.c_uint,ctypes.c_int,ctypes.c_int,ctypes.c_uint]
    user.LoadImageW.restype=ctypes.c_void_p
    user.DestroyCursor.argtypes=[ctypes.c_void_p]
    for f in directory.rglob('*'):
        if f.suffix not in ('.ani','.cur'):continue
        handle=user.LoadImageW(None,str(f.resolve()),2,0,0,0x10)
        if not handle:raise ctypes.WinError(ctypes.get_last_error())
        user.DestroyCursor(handle)

def build(output):
    output=Path(output);output.mkdir(parents=True,exist_ok=True)
    for dark,variant in [(False,'White'),(True,'Black')]:
        key='Windows-Flow-'+variant;theme=Theme(key,'Windows Flow '+variant,'#20242a' if dark else '#ffffff','#ffffff' if dark else '#20242a','flow')
        folder=output/key;folder.mkdir(parents=True,exist_ok=True)
        names=[]
        for role in ROLE_ORDER:
            name=f'{key}-{role.key}.ani';names.append(name)
            for size,suffix in [(64,'.ani'),(256,'-large.ani')]:
                data=animated(role,size,dark);verify_ani(data,size)
                (folder/f'{key}-{role.key}{suffix}').write_bytes(data)
            data=encode_cur([cursor(role,s,0,dark) for s in SUPPORTED_SIZES]);_check_cur(data,set(SUPPORTED_SIZES))
            (folder/f'{key}-{role.key}.cur').write_bytes(data)
        (folder/f'{key}.inf').write_text(_installer_text(theme,names),encoding='utf-8')
        for file in ['Install-Wingline.ps1','Install-Wingline.cmd']:shutil.copy2(ROOT/'installer'/file,folder/file)
        (folder/'INSTALL.txt').write_text('Windows Flow\n\nExtract the ZIP, open the White or Black folder, and double-click Install-Wingline.cmd.\nNo administrator rights or background app needed.\n\n17 independently drawn roles, slow 1.92-second loops, steady click hotspots.\nNormal and 256px high-DPI ANI versions are selected by the installer.\nStatic CUR alternatives are included for manual selection.\n',encoding='utf-8')
        preview=Image.new('RGB',(720,610),'#2e333b' if dark else '#eef0f4');draw=ImageDraw.Draw(preview)
        draw.text((20,12),'Windows Flow '+variant,fill='#fff' if dark else '#222')
        for i,role in enumerate(ROLE_ORDER):
            x=18+(i%6)*117;y=50+(i//6)*180
            asset=cursor(role,96,0,dark)[0];preview.paste(asset,(x,y),asset)
            draw.text((x,y+111),role.key,fill='#fff' if dark else '#222')
        preview.save(folder/'preview.png')
    verify_native(output)
    archive=output/'Windows-Flow.zip'
    with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
        for folder in sorted(output.glob('Windows-Flow-*')):
            for file in sorted(folder.iterdir()):z.write(file,file.relative_to(output))
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None;assert len(z.namelist())==112
    return archive

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,default=Path('dist-flow'));p.add_argument('--append-pack',type=Path);args=p.parse_args()
    archive=build(args.output)
    if args.append_pack:
        with zipfile.ZipFile(archive) as source,zipfile.ZipFile(args.append_pack,'a',zipfile.ZIP_DEFLATED) as target:
            for name in source.namelist():
                if name in target.namelist():raise ValueError('Windows Flow already exists in this pack')
                target.writestr(name,source.read(name))
    print('Windows Flow: 34 roles, 68 ANI files, 34 static alternatives, all exports validated.')
    print(archive)
