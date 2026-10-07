"""Load every exported cursor through Windows and verify its native dimensions."""
import ctypes
from ctypes import wintypes
from pathlib import Path
import sys
import tempfile

from wingline.artwork import SUPPORTED_SIZES
from wingline.roles import THEMES, ROLE_ORDER
from wingline.package import _read_riff_chunks


def verify(root):
    if sys.platform != 'win32':
        raise RuntimeError('The native cursor loader check requires Windows.')
    user32=ctypes.WinDLL('user32',use_last_error=True)
    gdi32=ctypes.WinDLL('gdi32',use_last_error=True)
    class ICONINFO(ctypes.Structure):
        _fields_=[('fIcon',wintypes.BOOL),('xHotspot',wintypes.DWORD),('yHotspot',wintypes.DWORD),
                  ('hbmMask',wintypes.HBITMAP),('hbmColor',wintypes.HBITMAP)]
    class BITMAP(ctypes.Structure):
        _fields_=[('bmType',wintypes.LONG),('bmWidth',wintypes.LONG),('bmHeight',wintypes.LONG),
                  ('bmWidthBytes',wintypes.LONG),('bmPlanes',wintypes.WORD),
                  ('bmBitsPixel',wintypes.WORD),('bmBits',ctypes.c_void_p)]
    user32.LoadImageW.argtypes=[wintypes.HINSTANCE,wintypes.LPCWSTR,wintypes.UINT,ctypes.c_int,ctypes.c_int,wintypes.UINT]
    user32.LoadImageW.restype=wintypes.HANDLE
    user32.GetIconInfo.argtypes=[wintypes.HANDLE,ctypes.POINTER(ICONINFO)]
    user32.GetIconInfo.restype=wintypes.BOOL
    user32.DestroyCursor.argtypes=[wintypes.HANDLE]
    user32.DestroyCursor.restype=wintypes.BOOL
    gdi32.GetObjectW.argtypes=[wintypes.HANDLE,ctypes.c_int,ctypes.c_void_p]
    gdi32.GetObjectW.restype=ctypes.c_int
    gdi32.DeleteObject.argtypes=[wintypes.HANDLE]
    gdi32.DeleteObject.restype=wintypes.BOOL
    files=sorted(list(root.glob('*/*.cur'))+list(root.glob('*/*.ani')))
    expected = len(THEMES)*(len(ROLE_ORDER)+2)
    if len(files)!=expected:
        raise ValueError(f'Expected {expected} cursor assets across {len(THEMES)} schemes; found {len(files)}.')
    checks=0
    def check(path):
        nonlocal checks
        for size in SUPPORTED_SIZES:
            cursor=user32.LoadImageW(None,str(path.resolve()),2,size,size,0x10)
            if not cursor:
                raise OSError(ctypes.get_last_error(),f'Windows could not load {path.name} at {size}px')
            info=ICONINFO()
            try:
                if not user32.GetIconInfo(cursor,ctypes.byref(info)):
                    raise ctypes.WinError(ctypes.get_last_error())
                bitmap=BITMAP()
                handle=info.hbmColor or info.hbmMask
                if not gdi32.GetObjectW(handle,ctypes.sizeof(bitmap),ctypes.byref(bitmap)):
                    raise ctypes.WinError(ctypes.get_last_error())
                height=bitmap.bmHeight if info.hbmColor else bitmap.bmHeight//2
                if (bitmap.bmWidth,height)!=(size,size):
                    raise ValueError(f'{path.name}: requested {size}px; Windows loaded {bitmap.bmWidth}x{height}.')
                if info.fIcon or info.xHotspot>=size or info.yHotspot>=size:
                    raise ValueError(f'{path.name}: invalid native cursor hotspot.')
                checks+=1
            finally:
                if info.hbmColor:gdi32.DeleteObject(info.hbmColor)
                if info.hbmMask:gdi32.DeleteObject(info.hbmMask)
                user32.DestroyCursor(cursor)
    with tempfile.TemporaryDirectory() as temporary:
        for path in files:
            check(path)
            if path.suffix == '.ani':
                data = path.read_bytes()
                for chunk_id, payload in _read_riff_chunks(data, 12, len(data)):
                    if chunk_id == b'LIST' and payload[:4] == b'fram':
                        for index, (_, frame) in enumerate(_read_riff_chunks(payload, 4, len(payload))):
                            frame_path = Path(temporary) / f'{path.stem}-frame-{index}.cur'
                            frame_path.write_bytes(frame)
                            check(frame_path)
    print(f'Windows loaded all {len(files)} cursor assets and every animation frame successfully: {checks} native size checks.')


if __name__=='__main__':
    verify(Path(sys.argv[1] if len(sys.argv)>1 else 'dist'))
