"""Benchmark normal-sized native animated cursor drawing without changing a desktop."""
import ctypes
from ctypes import wintypes
from pathlib import Path
import sys
import time

from wingline.timing import ANIMATION_FRAMES, FRAME_JIFFIES
from wingline.roles import THEMES, ROLE_ORDER


def verify(root):
    if sys.platform != "win32":
        raise RuntimeError("Native performance checks require Windows.")
    user32 = ctypes.WinDLL("user32", use_last_error=True)
    gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)
    user32.LoadImageW.argtypes = [wintypes.HINSTANCE,wintypes.LPCWSTR,wintypes.UINT,ctypes.c_int,ctypes.c_int,wintypes.UINT]
    user32.LoadImageW.restype = wintypes.HANDLE
    user32.DestroyCursor.argtypes = [wintypes.HANDLE]
    user32.GetDC.argtypes = [wintypes.HWND]
    user32.GetDC.restype = wintypes.HDC
    user32.ReleaseDC.argtypes = [wintypes.HWND,wintypes.HDC]
    user32.DrawIconEx.argtypes = [wintypes.HDC,ctypes.c_int,ctypes.c_int,wintypes.HANDLE,ctypes.c_int,ctypes.c_int,wintypes.UINT,wintypes.HBRUSH,wintypes.UINT]
    user32.DrawIconEx.restype = wintypes.BOOL
    gdi32.CreateCompatibleDC.argtypes = [wintypes.HDC]
    gdi32.CreateCompatibleDC.restype = wintypes.HDC
    gdi32.CreateCompatibleBitmap.argtypes = [wintypes.HDC,ctypes.c_int,ctypes.c_int]
    gdi32.CreateCompatibleBitmap.restype = wintypes.HBITMAP
    gdi32.SelectObject.argtypes = [wintypes.HDC,wintypes.HANDLE]
    gdi32.SelectObject.restype = wintypes.HANDLE
    gdi32.DeleteObject.argtypes = [wintypes.HANDLE]
    gdi32.DeleteDC.argtypes = [wintypes.HDC]
    paths = [p for p in sorted(root.glob("*/*.ani")) if not p.stem.endswith("-large")]
    if len(paths) != len(THEMES)*len(ROLE_ORDER):
        raise ValueError("Performance check must cover all 17 roles in every theme.")
    worst = 0
    count = 0
    for size in (32,64):
        screen = user32.GetDC(None)
        dc = gdi32.CreateCompatibleDC(screen)
        bitmap = gdi32.CreateCompatibleBitmap(screen,size,size)
        if not screen or not dc or not bitmap:
            raise ctypes.WinError(ctypes.get_last_error())
        previous = gdi32.SelectObject(dc,bitmap)
        try:
            for path in paths:
                cursor = user32.LoadImageW(None,str(path.resolve()),2,size,size,0x10)
                if not cursor:
                    raise ctypes.WinError(ctypes.get_last_error())
                try:
                    for step in range(ANIMATION_FRAMES):
                        if not user32.DrawIconEx(dc,0,0,cursor,size,size,step,None,3):
                            raise ctypes.WinError(ctypes.get_last_error())
                    start = time.perf_counter()
                    for step in range(320):
                        if not user32.DrawIconEx(dc,0,0,cursor,size,size,step%ANIMATION_FRAMES,None,3):
                            raise ctypes.WinError(ctypes.get_last_error())
                    average = (time.perf_counter()-start)/320
                    if average >= FRAME_JIFFIES/60:
                        raise ValueError(f"{path.name}: native rendering exceeds its frame-time budget.")
                    worst = max(worst,average)
                    count += 320
                finally:
                    user32.DestroyCursor(cursor)
        finally:
            gdi32.SelectObject(dc,previous)
            gdi32.DeleteObject(bitmap)
            gdi32.DeleteDC(dc)
            user32.ReleaseDC(None,screen)
    print(f"Performance: {count} offscreen native animation draws passed; worst per-asset mean {worst*1000:.4f} ms, against {FRAME_JIFFIES/60*1000:.2f} ms frame budget.")


if __name__ == "__main__":
    verify(Path(sys.argv[1] if len(sys.argv)>1 else "dist"))
