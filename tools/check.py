"""Check translated lines against the dialogue box limits.

Usage: check.py [translation/*.json ...]   (default: all files)

Line width is measured in pixels with fontA's glyph widths (+1px spacing).
Variables ({04 ..}) are counted as VAR_WIDTH pixels. A page is 3 lines;
choice lines after a {02 ..} code are not part of a page.
"""
import glob
import json
import re
import struct
import sys

import ndspy.lz10

FONT = 'extracted/font/fontA_attr.bin'
MAX_WIDTH = 160  # English dialogue: max 164, 99th percentile 160 (see --calibrate)
VAR_WIDTH = 48   # e.g. an 8-letter player or town name
PAGE_LINES = 3

_attr = open(FONT, 'rb').read()
_attr = ndspy.lz10.decompress(_attr[4:])
WIDTHS = {struct.unpack_from('<H', _attr, i)[0]: struct.unpack_from('<H', _attr, i + 2)[0]
          for i in range(0, len(_attr), 4)}

_CODE = re.compile(r'\{\{|\}\}|\{([0-9a-fA-F ]*)\}')


def width(line):
    w = 0
    pos = 0
    for m in _CODE.finditer(line):
        w += _text_width(line[pos:m.start()])
        if m.group(0) in ('{{', '}}'):
            w += _text_width(m.group(0)[0])
        elif m.group(1).startswith('04'):
            w += VAR_WIDTH
        pos = m.end()
    return w + _text_width(line[pos:])


def _text_width(s):
    return sum(WIDTHS.get(c.encode('cp1252', errors='replace')[0], 5) + 1 for c in s)


def body_lines(text):
    """Lines that are shown in the dialogue box (choice lines stripped)."""
    m = re.search(r'\{02[0-9a-f ]*\}', text)
    return (text[:m.start()] if m else text).split('\n')


def main(paths):
    problems = 0
    for p in paths:
        for e in json.load(open(p, encoding='utf-8'))['messages']:
            if not e['et']:
                continue
            en, et = body_lines(e['en']), body_lines(e['et'])
            if len(et) % PAGE_LINES != len(en) % PAGE_LINES:
                print(f'{p} #{e["id"]}: {len(et)} lines vs English {len(en)}')
                problems += 1
            for n, line in enumerate(et):
                if (w := width(line)) > MAX_WIDTH:
                    print(f'{p} #{e["id"]} line {n + 1}: {w}px > {MAX_WIDTH}: {line!r}')
                    problems += 1
            n_en = len(e['en'].split('\n')) - len(en)
            n_et = len(e['et'].split('\n')) - len(et)
            if n_en != n_et:
                print(f'{p} #{e["id"]}: {n_et} choices vs English {n_en}')
                problems += 1
    print(f'{problems} problem(s)')
    return problems


def calibrate():
    ws = []
    for p in glob.glob('translation/message/**/*.json', recursive=True):
        for e in json.load(open(p, encoding='utf-8'))['messages']:
            for line in body_lines(e['en']):
                if '{04' not in line:
                    ws.append(width(line))
    ws.sort()
    print('max', ws[-1], 'p99.9', ws[int(len(ws) * .999)], 'p99', ws[int(len(ws) * .99)])


if __name__ == '__main__':
    if sys.argv[1:] == ['--calibrate']:
        calibrate()
    else:
        sys.exit(1 if main(sys.argv[1:] or glob.glob('translation/**/*.json', recursive=True)) else 0)
