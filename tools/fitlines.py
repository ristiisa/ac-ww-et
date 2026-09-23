"""Shorten over-wide translated lines without changing the line count.

Usage: fitlines.py file.json [file.json ...]

For each line wider than the limit, first try meaning-preserving word
shortenings, then move the trailing word onto the next line (never across a
page break, never a word that carries a control code).
"""
import json
import re
import sys

import check

SHORT = [
    ("kohutavalt kahju", "väga kahju"),
    ("kohutavalt ", "väga "),
    ("absoluutselt ", "täiesti "),
    ("tegelikult ", "tõesti "),
    ("lihtsalt ", ""),
    ("muljetavaldav", "muljetav"),
    ("üsna ", ""),
    ("väga ", ""),
    ("eks-eks?", "eks?"),
    ("Tõepoolest", "Tõesti"),
    ("tõepoolest", "tõesti"),
    ("Kujutan ette", "Arvan"),
    ("kujutan ette", "arvan"),
    ("sellepärast", "seepärast"),
    ("Sellepärast", "Seepärast"),
    ("ja ometi", "ent"),
    ("Ja ometi", "Ent"),
    ("praegu ", ""),
    ("Muidugi ", ""),
    ("muidugi ", ""),
    ("Aga ma kaldun kõrvale", "Aga see selleks"),
    ("kindlasti ", ""),
    ("ilmselt ", ""),
    ("tõesti ", ""),
    ("Seetõttu", "Seega"),
    ("seetõttu", "seega"),
    ("hämmastav", "imeline"),
    ("Hämmastav", "Imeline"),
    ("suurepärane", "imeline"),
    ("Suurepärane", "Imeline"),
    ("täpselt ", ""),
    ("Ausalt öeldes", "Ausalt"),
    ("ausalt öeldes", "ausalt"),
    ("Pean ütlema, et ", ""),
    ("Pean tunnistama, et ", ""),
    ("vastikumat", "alatumat"),
    ("eemaletõukav", "alatu"),
    ("väljapanek", "eksponaat"),
    ("Ja ometi ", ""),
    ("ja ometi ", ""),
    ("sugugi ", ""),
    ("üldse ", ""),
    ("ikka ", ""),
    ("küll ", ""),
    ("juba ", ""),
    ("siis ", ""),
    ("ehk ", ""),
    ("tead küll", "tead"),
    (" küll.", "."),
    (" küll,", ","),
    ("Milline ", "Kui "),
    ("milline ", "kui "),
    ("selline ", "nii "),
    ("Selline ", "Nii "),
    ("sellised ", "need "),
    ("tavaliselt ", ""),
    ("veidi ", ""),
    ("pisut ", ""),
    ("võib-olla ", "ehk "),
    ("Võib-olla ", "Ehk "),
    ("nii et ", "nii "),
    (", aga ", ", "),
    ("Tõesti, ", ""),
    ("tõesti, ", ""),
    ("Jah, ", ""),
    ("Noh, ", ""),
]
_TOK = re.compile(r'\{[^}]*\}|[^\s{]+|\s+')


def has_code(tok):
    return tok.startswith('{')


def try_shorten(line, maxw):
    """Best meaning-preserving shortening, or None if nothing applies."""
    best, bestw = None, check.width(line)
    for old, new in SHORT:
        if old in line:
            cand = line.replace(old, new, 1)
            w = check.width(cand)
            if w < bestw:
                best, bestw = cand, w
    return best


def move_down(lines, i, maxw, blank_ok=False):
    """Move the trailing word of lines[i] to the front of lines[i+1]."""
    if i + 1 >= len(lines):
        return False
    if not blank_ok and not lines[i + 1].strip():
        return False
    toks = _TOK.findall(lines[i])
    tail = []
    while toks and (toks[-1].isspace() or has_code(toks[-1])):
        t = toks.pop()
        if not t.isspace():
            tail.insert(0, t)
    if not toks:
        return False
    word = toks.pop()
    while toks and toks[-1].isspace():
        toks.pop()
    moved = word + ''.join(tail) + ' ' + lines[i + 1]
    if i + 1 == len(lines) - 1 and check.width(moved) > maxw:
        return False
    lines[i] = ''.join(toks)
    lines[i + 1] = moved
    return True


def move_up(lines, i, maxw):
    """Move the leading word of lines[i] onto the end of lines[i-1]."""
    if i == 0 or not lines[i - 1].strip():
        return False
    toks = _TOK.findall(lines[i])
    head = []
    while toks and (toks[0].isspace() or has_code(toks[0])):
        t = toks.pop(0)
        if not t.isspace():
            head.append(t)
    if not toks:
        return False
    word = ''.join(head) + toks.pop(0)
    while toks and toks[0].isspace():
        toks.pop(0)
    if check.width(lines[i - 1] + ' ' + word) > maxw:
        return False
    lines[i - 1] = lines[i - 1] + ' ' + word
    lines[i] = ''.join(toks)
    return True


def move_word(lines, i, maxw, blank_ok=False):
    """Free space on lines[i], making room further down if need be."""
    if move_down(lines, i, maxw, blank_ok):
        return True
    return move_up(lines, i, maxw)


def fit(text, maxw, pages):
    m = re.search(r'\{02[0-9a-f ]*\}', text)
    body, tail = (text[:m.start()], text[m.start():]) if m else (text, '')
    lines = body.split('\n')
    for blank_ok in (False, True):
        stuck = set()
        for _ in range(200):
            bad = [i for i, l in enumerate(lines)
                   if i not in stuck and check.width(l) > maxw]
            if not bad:
                break
            i = bad[0]
            cand = try_shorten(lines[i], maxw)
            if cand is not None:
                lines[i] = cand
                continue
            if not move_word(lines, i, maxw, blank_ok):
                stuck.add(i)
    return '\n'.join(lines) + tail


def main(paths):
    for p in paths:
        maxw, pages = check.profile(p)
        if maxw is None:
            continue
        d = json.load(open(p, encoding='utf-8'))
        for e in d['messages']:
            if not e['et']:
                continue
            before = [check.width(l) for l in check.body_lines(e['et'])]
            if max(before, default=0) <= maxw:
                continue
            cand = fit(e['et'], maxw, pages)
            after = [check.width(l) for l in check.body_lines(cand)]
            bad = lambda ws: sum(1 for w in ws if w > maxw)
            # never accept a rewrap that makes some line even wider
            if bad(after) < bad(before) and max(after) <= max(before):
                e['et'] = cand
        json.dump(d, open(p, 'w', encoding='utf-8', newline='\n'), ensure_ascii=False, indent=1)
        open(p, 'a', encoding='utf-8', newline='\n').write('\n')


if __name__ == '__main__':
    main(sys.argv[1:])
