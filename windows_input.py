"""Windows Unicode input support, isolated from third-party installation files."""
import ctypes
from textual.drivers import win32
from textual._xterm_parser import XTermParser
from textual import constants

def committed_text(event):
    """Keep IME Unicode commits even when Windows reports a key-up event.

    Ordinary physical key-up events must not duplicate text. IME synthetic
    events use virtual key 0 or VK_PACKET; VK_PROCESSKEY is composition only.
    """
    char = event.uChar.UnicodeChar
    if not char or char == '\x00' or event.wVirtualKeyCode == 0xE5:
        return ''
    synthetic = event.wVirtualKeyCode in (0, 0xE7)
    if not event.bKeyDown and not (synthetic and ord(char) >= 128):
        return ''
    if event.dwControlKeyState and event.wVirtualKeyCode == 0 and ord(char) < 128:
        return ''
    return char * max(1, event.wRepeatCount)

class UnicodeEventMonitor(win32.EventMonitor):
    def run(self):
        parser = XTermParser(debug=constants.DEBUG)
        count = win32.wintypes.DWORD()
        handle = win32.GetStdHandle(win32.STD_INPUT_HANDLE)
        records = (win32.INPUT_RECORD * 1024)()
        try:
            while not self.exit_event.is_set():
                for event in parser.tick():
                    self.process_event(event)
                if win32.wait_for_handles([handle], 100) is None:
                    continue
                if not win32.KERNEL32.ReadConsoleInputW(handle, ctypes.byref(records), 1024, ctypes.byref(count)):
                    raise ctypes.WinError()
                chars = []
                for record in records[:count.value]:
                    if record.EventType == 1:
                        chars.append(committed_text(record.Event.KeyEvent))
                    elif record.EventType == 4:
                        size = record.Event.WindowBufferSizeEvent.dwSize
                        self.on_size_change(size.X, size.Y)
                text = ''.join(chars)
                if text:
                    text = text.encode('utf-16', 'surrogatepass').decode('utf-16', 'replace')
                    for event in parser.feed(text):
                        self.process_event(event)
        except Exception as error:
            self.app.log.error('Windows input error', error)
