"""Baleen's terminal-native pixel mascot."""
from rich.text import Text

PIXELS = (
    '       c   c            ',
    '        c c             ',
    '         c              ',
    '                        ',
    '      bbbbbbbbb         ',
    '    bbbbbbbbbbbbb       ',
    '   bbbbbbbbbbbbbbb      ',
    '   bbbwbbbbbbbbbbb   b b',
    '   bbbbbbbbbbbbbbb   bbb',
    '   bbbbbbbbbbbbbbbbbbb  ',
    '    bbbbbbbbbbbbbbbb    ',
    '     dddddddddddd       ',
    '       dddddddd         ',
)
PALETTE = {'b': '#389DFA', 'c': '#7DE3F4', 'd': '#2375C2', 'w': '#EAF7FF'}
BACKGROUND = '#121212'
TITLE_COLOR = '#EEF6FF'
TITLE_PIXELS = {
    'B': ('11110', '11001', '11110', '11001', '11110'),
    'a': ('00000', '01110', '00001', '01111', '01111'),
    'l': ('01100', '00100', '00100', '00100', '01110'),
    'e': ('00000', '01110', '11111', '10000', '01110'),
    'n': ('00000', '11110', '11001', '11001', '11001'),
}

def make_banner(model: str = '', work_dir: str = '', *, compact: bool = True) -> Text:
    if compact:
        return _compact_banner(model, work_dir)
    result = Text(style=f'on {BACKGROUND}', no_wrap=True, overflow='ellipsis')
    labels = {10: 'Your coding companion', 11: model, 12: work_dir}
    # Background-colored spaces do not depend on block-glyph font coverage.
    # Two columns approximate a square pixel in a normal terminal font.
    width = max(map(len, PIXELS))
    for index, row in enumerate(PIXELS):
        for pixel in row.ljust(width):
            result.append('  ', style=f'on {PALETTE.get(pixel, BACKGROUND)}')
        result.append('    ')
        if 4 <= index < 9:
            for letter in 'Baleen':
                for pixel in TITLE_PIXELS[letter][index - 4]:
                    result.append(' ', style=f'on {TITLE_COLOR if pixel == "1" else BACKGROUND}')
                result.append(' ')
        else:
            result.append(labels.get(index, ''), style='#8DA7BA')
        if index < len(PIXELS) - 1:
            result.append('\n')
    return result


def _compact_banner(model: str, work_dir: str) -> Text:
    """Pair the ORIGINAL rows; never resample or remove source pixels."""
    result = Text(style=f'on {BACKGROUND}', no_wrap=True, overflow='ellipsis')
    width = max(map(len, PIXELS))
    rows = [row.ljust(width) for row in PIXELS]
    if len(rows) % 2:
        rows.append(' ' * width)
    for index in range(8):
        if index < len(rows) // 2:
            for top, bottom in zip(rows[index * 2], rows[index * 2 + 1]):
                foreground = PALETTE.get(top, BACKGROUND)
                background = PALETTE.get(bottom, BACKGROUND)
                result.append('▀', style=f'{foreground} on {background}')
        else:
            result.append(' ' * width)
        result.append('    ')
        if index < 5:
            for letter in 'Baleen':
                for pixel in TITLE_PIXELS[letter][index]:
                    result.append(' ', style=f'on {TITLE_COLOR if pixel == "1" else BACKGROUND}')
                result.append(' ')
        else:
            result.append({5: 'Your coding companion', 6: model, 7: work_dir}[index], style='#8DA7BA')
        if index < 7:
            result.append('\n')
    return result
