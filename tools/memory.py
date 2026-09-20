"""Translation memory: fill untranslated messages whose English text has
already been translated somewhere else, and report progress.

    memory.py            fill exact repeats
    memory.py --report   progress per folder, no changes
"""
import collections
import glob
import json
import sys

FILES = sorted(p for p in glob.glob('translation/**/*.json', recursive=True))


def load():
    return [(p, json.load(open(p, encoding='utf-8'))) for p in FILES]


def entries(doc):
    return doc.get('messages', []) + doc.get('names', [])


def fill():
    docs = load()
    known = {}
    for _, doc in docs:
        for e in entries(doc):
            if e['et']:
                known.setdefault(e['en'], e['et'])
    filled = 0
    for p, doc in docs:
        changed = False
        for e in entries(doc):
            if not e['et'] and e['en'] in known:
                e['et'] = known[e['en']]
                filled += 1
                changed = True
        if changed:
            with open(p, 'w', encoding='utf-8') as f:
                json.dump(doc, f, ensure_ascii=False, indent=1)
                f.write('\n')
    print(f'filled {filled} repeated lines from {len(known)} known translations')


def report():
    tot = collections.Counter()
    done = collections.Counter()
    for p, doc in load():
        area = '/'.join(p.split('/')[1:3]) if p.count('/') > 2 else p.split('/')[1]
        for e in entries(doc):
            tot[area] += 1
            done[area] += bool(e['et'])
    width = max(len(a) for a in tot)
    for area in sorted(tot, key=lambda a: -(tot[a] - done[a])):
        pct = 100 * done[area] / tot[area]
        print(f'{area:{width}}  {done[area]:6}/{tot[area]:6}  {pct:5.1f}%')
    print(f'{"TOTAL":{width}}  {sum(done.values()):6}/{sum(tot.values()):6}'
          f'  {100 * sum(done.values()) / sum(tot.values()):5.1f}%')


if __name__ == '__main__':
    report() if '--report' in sys.argv else fill()
