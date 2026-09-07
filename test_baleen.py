import unittest
import os
import tempfile
from unittest.mock import AsyncMock, MagicMock, patch
from textual.app import App, ComposeResult
from textual import events
from Baleen.app import ChatInput, BaleenApp
from Baleen.config import ProviderConfig
from Baleen.branding import make_banner, PIXELS, PALETTE, TITLE_COLOR
from Baleen.windows_input import committed_text
from textual.drivers.win32 import KEY_EVENT_RECORD

class InputHost(App):
    def compose(self) -> ComposeResult:
        yield ChatInput()

    def on_chat_input_submitted(self, event):
        self.submitted = event.text

class InputTests(unittest.TestCase):
    def test_windows_switches_screen_before_configuring_font(self):
        from Baleen.driver import NoAltScreenDriver
        driver = object.__new__(NoAltScreenDriver)
        driver._file = MagicMock()
        driver._app = MagicMock()
        driver.exit_event = MagicMock()
        driver.process_message = MagicMock()
        driver._enable_mouse_support = MagicMock()
        driver._enable_bracketed_paste = MagicMock()
        driver.flush = MagicMock()
        order = []
        driver._file.write.side_effect = lambda value: order.append(('write', value))
        driver._file.flush.side_effect = lambda: order.append(('flush', None))
        context = MagicMock()
        context.__enter__.side_effect = lambda: order.append(('font', None)) or True
        with patch('asyncio.get_running_loop'), patch('textual.drivers.win32.enable_application_mode'), patch('textual.drivers._writer_thread.WriterThread'), patch('Baleen.windows_input.UnicodeEventMonitor'), patch('Baleen.console_setup.unicode_console', return_value=context):
            driver.start_application_mode()
        self.assertEqual(order[:3], [('write', '\x1b[?1049h'), ('flush', None), ('font', None)])
        self.assertTrue(driver._app._compact_banner)

    def test_windows_driver_keeps_alternate_screen_sequences(self):
        from Baleen.driver import NoAltScreenDriver
        from textual.drivers.windows_driver import WindowsDriver
        driver = object.__new__(NoAltScreenDriver)
        with patch.object(WindowsDriver, 'write') as write:
            driver.write('\x1b[?1049h')
            driver.write('\x1b[?1049l')
            self.assertEqual([call.args[0] for call in write.call_args_list], ['\x1b[?1049h', '\x1b[?1049l'])

    def record(self, text, down=True, vk=0, flags=0, repeats=1):
        record = KEY_EVENT_RECORD()
        record.uChar.UnicodeChar = text
        record.bKeyDown = down
        record.wVirtualKeyCode = vk
        record.dwControlKeyState = flags
        record.wRepeatCount = repeats
        return record

    def test_unicode_with_modifier_flags(self):
        self.assertEqual(committed_text(self.record('中', flags=8)), '中')

    def test_synthetic_unicode_key_up(self):
        self.assertEqual(committed_text(self.record('文', down=False)), '文')

    def test_physical_key_up_not_duplicated(self):
        self.assertEqual(committed_text(self.record('a', down=False, vk=65)), '')

    def test_composition_not_submitted(self):
        self.assertEqual(committed_text(self.record('\r', vk=0xE5)), '')

    def test_repeat_and_null(self):
        self.assertEqual(committed_text(self.record('a', vk=65, repeats=3)), 'aaa')
        self.assertEqual(committed_text(self.record('\0')), '')

    def test_banner(self):
        text = make_banner('test-model', 'E:/Baleen')
        self.assertEqual(len(text.plain.splitlines()), 8)
        self.assertIn('Your coding companion', text.plain)
        self.assertIn('▀', text.plain)
        self.assertTrue(any(span.style == f'on {TITLE_COLOR}' for span in text.spans))

    def test_full_size_fallback(self):
        text = make_banner(compact=False)
        self.assertEqual(len(text.plain.splitlines()), 13)
        self.assertTrue(text.plain.isascii())

    def test_half_size_preserves_every_pixel(self):
        from rich.console import Console
        from Baleen.branding import BACKGROUND
        console = Console(color_system='truecolor')
        text = make_banner()
        lines = text.plain.splitlines(keepends=True)
        for row_index, row in enumerate(PIXELS):
            offset = sum(map(len, lines[:row_index // 2]))
            for column, pixel in enumerate(row):
                style = text.get_style_at_offset(console, offset + column)
                color = style.color if row_index % 2 == 0 else style.bgcolor
                self.assertEqual(color.get_truecolor().hex.lower(), PALETTE.get(pixel, BACKGROUND).lower())

class WidgetTests(unittest.IsolatedAsyncioTestCase):
    async def test_missing_key_still_displays_header(self):
        provider = ProviderConfig('test', 'anthropic', 'https://example.invalid', 'test', api_key='')
        with patch.dict(os.environ, {'ANTHROPIC_API_KEY': ''}):
            app = BaleenApp([provider])
            async with app.run_test(size=(120, 30)) as pilot:
                await pilot.pause()
                title = app.query_one('#title-bar')
                self.assertTrue(title.visible)
                self.assertEqual(title.region.height, 8)
                self.assertIn('Your coding companion', str(title.render()))
                self.assertIn('[!] Anthropic API key not found', str(app.query_one('.error-message').render()))

    async def test_full_app_layout(self):
        previous = os.getcwd()
        with tempfile.TemporaryDirectory() as directory:
            os.chdir(directory)
            try:
                provider = ProviderConfig(name='test', protocol='anthropic', base_url='https://example.invalid', model='test', api_key='test-only')
                with patch.object(BaleenApp, '_resolve_context_window', new=AsyncMock()):
                    app = BaleenApp([provider])
                    async with app.run_test(size=(100, 30)) as pilot:
                        await pilot.pause()
                        widget = app.query_one(ChatInput)
                        self.assertGreater(widget.region.height, 0)
                        self.assertLessEqual(widget.region.bottom, 30)
                        widget.insert('你好，Baleen')
                        await pilot.pause()
                        self.assertEqual(widget.text, '你好，Baleen')
            finally:
                if 'app' in locals() and app.session:
                    app.session.close()
                os.chdir(previous)

    async def test_chinese_edit_paste_submit(self):
        app = InputHost()
        async with app.run_test() as pilot:
            widget = app.query_one(ChatInput)
            widget.focus()
            await pilot.press('中', '文')
            self.assertEqual(widget.text, '中文')
            await pilot.press('backspace')
            self.assertEqual(widget.text, '中')
            app.post_message(events.Paste('文输入'))
            await pilot.pause()
            self.assertEqual(widget.text, '中文输入')
            await pilot.press('enter')
            self.assertEqual(app.submitted, '中文输入')
            self.assertEqual(widget.text, '')

if __name__ == '__main__':
    unittest.main()
