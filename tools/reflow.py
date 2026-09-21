"""Move trailing words off over-wide lines onto the next line.

Usage: reflow.py translation/.../file.json [...]

Only rearranges whitespace inside an entry: the line count, the control
codes and their order stay exactly the same, so a reflowed entry still
matches the English layout. A word is moved only when the split point is
plain text (never inside a control code), the following line does not
start with a code, and that line still fits afterwards.
"""
import glob
import json
import re
import sys

import check

_CODE = re.compile(r'\{\{|\}\}|\{[0-9a-fA-F ]*\}')


def _plain_spaces(line):
    """Indices of spaces that are not inside a control code."""
    masked = list(line)
    for m in _CODE.finditer(line):
        for i in range(m.start(), m.end()):
            masked[i] = '\0'
    return [i for i, c in enumerate(masked) if c == ' ']


_CHOICE = re.compile(r'\{0[256] ')


_LEAD = re.compile(r'^(?:\{0[17][0-9a-fA-F ]*\})+')


def _insert_point(line):
    """Where text may be inserted: after leading pause/expression codes."""
    if not line.startswith('{'):
        return 0
    m = _LEAD.match(line)
    return m.end() if m else -1


def reflow_lines(lines):
    lines = list(lines)
    changed = False
    if any(_CHOICE.search(l) for l in lines):
        return lines, False  # menus: choice lines must stay put
    for i in range(len(lines) - 1):
        while check.width(lines[i]) > check.MAX_WIDTH:
            nxt = lines[i + 1]
            at = _insert_point(nxt)
            if at < 0 or not lines[i].strip():
                break
            spaces = _plain_spaces(lines[i].rstrip())
            if not spaces:
                break
            cut = spaces[-1]
            word = lines[i][cut + 1:]
            if not word.strip():
                break
            tail = nxt[at:]
            cand_nxt = nxt[:at] + word + (' ' if tail else '') + tail
            if check.width(cand_nxt) > check.MAX_WIDTH:
                break
            lines[i], lines[i + 1] = lines[i][:cut], cand_nxt
            changed = True
    return lines, changed


def main(paths):
    total = 0
    for p in paths:
        doc = json.load(open(p, encoding='utf-8'))
        hit = False
        for e in doc.get('messages', []):
            if not e['et']:
                continue
            lines, changed = reflow_lines(e['et'].split('\n'))
            if changed:
                e['et'] = '\n'.join(lines)
                hit = True
                total += 1
        if hit:
            with open(p, 'w', encoding='utf-8') as f:
                json.dump(doc, f, ensure_ascii=False, indent=1)
                f.write('\n')
    print(f'reflowed {total} messages')


if __name__ == '__main__':
    main(sys.argv[1:] or sorted(glob.glob('translation/**/*.json', recursive=True)))
