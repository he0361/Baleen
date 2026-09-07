"""Prepare only the active console for Unicode artwork, restoring it on exit."""
from contextlib import contextmanager
import sys


@contextmanager
def unicode_console():
    if sys.platform != 'win32':
        yield True
        return

    import ctypes
    from ctypes import wintypes

    class Coord(ctypes.Structure):
        _fields_ = [('X', ctypes.c_short), ('Y', ctypes.c_short)]

    class Font(ctypes.Structure):
        _fields_ = [
            ('cbSize', wintypes.ULONG), ('nFont', wintypes.DWORD),
            ('dwFontSize', Coord), ('FontFamily', wintypes.UINT),
            ('FontWeight', wintypes.UINT), ('FaceName', wintypes.WCHAR * 32),
        ]

    kernel = ctypes.WinDLL('kernel32', use_last_error=True)
    kernel.GetStdHandle.restype = wintypes.HANDLE
    kernel.GetCurrentConsoleFontEx.argtypes = [wintypes.HANDLE, wintypes.BOOL, ctypes.POINTER(Font)]
    kernel.SetCurrentConsoleFontEx.argtypes = [wintypes.HANDLE, wintypes.BOOL, ctypes.POINTER(Font)]
    handle = kernel.GetStdHandle(-11)
    original = Font()
    original.cbSize = ctypes.sizeof(Font)
    if not kernel.GetCurrentConsoleFontEx(handle, False, ctypes.byref(original)):
        # Redirected output and unsupported console hosts keep the space renderer.
        yield False
        return

    input_cp, output_cp = kernel.GetConsoleCP(), kernel.GetConsoleOutputCP()
    font = Font.from_buffer_copy(original)
    font.FaceName = 'Consolas'
    font.dwFontSize.X = 0
    font.FontFamily = 54
    font.FontWeight = 400
    try:
        # With the original Chinese code page, conhost may silently retain SimSun.
        ready = bool(kernel.SetConsoleCP(65001) and kernel.SetConsoleOutputCP(65001))
        ready = ready and bool(kernel.SetCurrentConsoleFontEx(handle, False, ctypes.byref(font)))
        current = Font()
        current.cbSize = ctypes.sizeof(Font)
        ready = ready and bool(kernel.GetCurrentConsoleFontEx(handle, False, ctypes.byref(current)))
        yield ready and current.FaceName.casefold() == 'consolas'
    finally:
        kernel.SetConsoleCP(input_cp)
        kernel.SetConsoleOutputCP(output_cp)
        kernel.SetCurrentConsoleFontEx(handle, False, ctypes.byref(original))
