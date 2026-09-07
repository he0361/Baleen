# 来源：公众号@小林coding
# 后端八股网站：xiaolincoding.com
# Agent网站：xiaolinnote.com
# 简历模版：jianli.xiaolinnote.com
from __future__ import annotations

import os
import sys

if sys.platform == "win32":
    from textual.drivers.windows_driver import WindowsDriver as _BaseDriver
else:
    from textual.drivers.linux_driver import LinuxDriver as _BaseDriver


class NoAltScreenDriver(_BaseDriver):
    """Windows 使用与视区等大的备用屏；其他平台保留原有滚动回看行为。

    保留历史类名供调用方使用。Windows 主缓冲区通常有 9001 行，不能
    把这个高度作为 Textual 的界面高度，否则标题会被绘制到视区之外。
    """

    def start_application_mode(self):
        if sys.platform != 'win32':
            try:
                rows = os.get_terminal_size().lines
            except OSError:
                rows = 24
            sys.stdout.write("\n" * rows)
            sys.stdout.flush()
            super().start_application_mode()
            return
        import asyncio
        from textual.drivers import win32
        from textual.drivers._writer_thread import WriterThread
        from Baleen.windows_input import UnicodeEventMonitor
        from Baleen.console_setup import unicode_console

        self._restore_console = win32.enable_application_mode()
        # Enter synchronously before configuring the new buffer's font. The
        # writer thread is asynchronous; enqueueing this would race font setup.
        self._file.write('\x1b[?1049h')
        self._file.flush()
        self._unicode_context = unicode_console()
        self._app._compact_banner = self._unicode_context.__enter__()
        self._writer_thread = WriterThread(self._file)
        self._writer_thread.start()
        self._enable_mouse_support()
        self.write('\x1b[?25l\x1b[?1004h')
        self._enable_bracketed_paste()
        self.flush()
        self._event_thread = UnicodeEventMonitor(
            asyncio.get_running_loop(), self._app, self.exit_event, self.process_message
        )
        self._event_thread.start()

    def write(self, data: str) -> None:
        if sys.platform != 'win32':
            data = data.replace("\x1b[?1049h", "").replace("\x1b[?1049l", "")
        if data:
            super().write(data)

    def close(self) -> None:
        try:
            super().close()
        finally:
            context = getattr(self, '_unicode_context', None)
            if context is not None:
                self._unicode_context = None
                context.__exit__(None, None, None)
