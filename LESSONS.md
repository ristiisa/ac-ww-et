# Lessons from translating Animal Crossing: Wild World into Estonian

Notes for the next agent who translates a Nintendo DS game. Written after
finishing all 21461 text entries of AC:WW (USA Rev 1). Some of it is
AC:WW-specific, most of it generalises to any DS title with a lot of text.

---

## 1. Build the tooling before you translate a single line

The temptation is to open a file, start translating, and figure out the rest
later. Don't. The first day should produce a pipeline, not a translation:

```
extract.py   ROM -> extracted/        (raw files, fonts, archives)
export.py    extracted/ -> translation/**.json   ({"en": ..., "et": ...})
build.py     translation/ + ROM -> out/GAME.nds
check.py     layout validation
memory.py    progress report + auto-fill of exact repeats
```

The JSON shape that worked: one file per original text file, each entry
`{"id": n, "en": "...", "et": "..."}`. An empty `et` falls back to English,
so the ROM builds and boots from day one and stays playable through the whole
project. This is what makes incremental work possible.

Invest in the round trip early: extract → build → boot in an emulator, with
zero translated strings. If that loop is broken you will discover it after
2000 entries instead of after 5.

## 2. Find the text format before guessing

AC:WW uses **BMG** (`MESGbmg1` magic: an `INF1` index section plus a `DAT1`
string blob). Encoding byte `1` in the header means **Windows-1252**. Knowing
this answered three questions at once: which characters are legal, how long a
string may be, and where the control codes live.

Ways in, roughly in order of payoff:

1. Look for a decompilation or format doc for *any* game by the same
   developer, not just this one. There is no Wild World disassembly, but the
   GameCube and N64 Animal Crossing decomps describe the same BMG-ish text
   format. You don't need a disassembly at all if the text is pure data.
2. Search the ROM for known magic strings (`MESG`, `BMG`, `SCEL`, `NARC`,
   `LZ77`) before writing a parser.
3. Use `ndspy` for everything ROM-level: filesystem, LZ10/LZ11, NARC. Don't
   hand-roll decompression.

## 3. Check the font before promising diacritics

The very first question for any non-English target language: **does the font
already contain the glyphs?** For AC:WW the answer was yes — `fontA` already
had cp1252 glyphs including `õ ä ö ü š ž Õ Ä Ö Ü Š Ž`, so no font hacking was
needed at all. That single check saved what would have been the hardest part
of the project.

If the glyphs are missing you are looking at font editing plus possibly a
new encoding table, and you should scope the project accordingly *before*
starting.

Corollary: any character outside the ROM's encoding breaks the build. One
stray Cyrillic character or a typographic `—` pasted from a web page will
fail the build with an encoding error. Estonian quotes had to be the cp1252
ones (`„` 0x84, `"` 0x94), not Unicode curly quotes.

## 4. Control codes are the real constraint, not the words

AC:WW text is full of inline codes, rendered in the JSON as `{07 0b 00}` style
hex groups:

| Code | Meaning |
|---|---|
| `{01 00 00 0X 00}` | pause of X frames |
| `{01 01 00}` / `{01 02 00}` `{01 03 00}` | line/page break variants |
| `{02 ...}` / `{05 ...}` | choice menus (following lines are the options) |
| `{04 xx 00}` | variable: player name, town, villager, item, catchphrase |
| `{06 ...}` | jump table — **copy verbatim, never translate** |
| `{07 xx 00}` | speaker facial expression |
| `{09 xx 00}` | camera / speaker switch |
| `{0b 0X 00}` | grammar hint for the following variable |
| `{ff 00 00 0X}` | highlight colour on / `{ff 00 00 00}` off |

Three rules, learned the hard way:

- **The multiset of control codes must match the English exactly.**
- **So must their order.** This is the one that bites. Estonian word order
  differs from English, so a natural translation happily moves a pause or a
  highlight to the other side of a word — and the sequence no longer matches.
  Eight such bugs survived into the finished translation and had to be swept
  up at the end.
- **A code's position relative to a line break matters** when a highlight
  opens on one line and closes on the next: keep the break inside the pair,
  exactly where English has it.

Write a verifier for this on day one:

```python
def codes(t):
    return [m.group(0) for m in TOKEN.finditer(t)
            if m.group(0).startswith('{') and len(m.group(0)) > 2]
# flag every entry where codes(en) != codes(et)
```

Twenty lines of code. Run it after **every** batch. The layout checker will
not catch this class of bug, and the build may silently accept it.

## 5. Text box geometry: measure, don't eyeball

`check.py` measures line width **in pixels using the game's own font width
table**, not in characters. This matters more than it sounds: `i` and `W` are
not the same width, and a variable like the player's name is invisible in the
source but occupies real space.

The numbers that ended up mattering for AC:WW:

- `MAX_WIDTH = 160` px per dialogue line (derived by measuring every English
  line and taking the 99th percentile — the absolute max was 164).
- `VAR_WIDTH = 48` px charged for each `{04 xx 00}` variable — roughly an
  8-letter name. A line with a variable has room for very little else.
- `{ff ...}` highlight codes cost **0** px.
- `PAGE_LINES = 3` — the dialogue box shows 3 lines at a time.
- Info boxes (the encyclopedia) are a different, narrower box: `BOX_WIDTH = 100`,
  and they are not paged.

Two refinements that removed a lot of false positives, worth copying:

- A line is only a problem if it is over the limit **and** wider than the
  widest English line in the same entry. English sometimes exceeds the nominal
  limit itself; matching it is fine.
- Line count does not have to be *equal* to English, it has to be **congruent
  modulo the page height**. `len(et) % 3 == len(en) % 3` keeps every
  subsequent page break aligned, which is what actually matters, while giving
  you three extra lines of room when a language needs them.

Choice lines (everything after a `{02 ...}`) live outside the page and are
counted separately — the number of choices must match exactly, or the menu
indices break.

## 6. Expect the target language to be longer, and plan for it

Estonian runs longer than English for most phrasings, and the box does not
grow. Practical tactics, in the order to try them:

1. Drop pronouns — Estonian marks person on the verb, so `Ma lähen` → `Lähen`.
2. Prefer the shorter synonym (`putukavõistlus` → `võistlus` on a tight line).
3. Redistribute words across lines within the entry (never across a page
   break, never splitting a word that carries a control code).
4. Only then rewrite the sentence.

Steps 1–3 are mechanical enough to automate: `reflow.py` moves trailing words
onto the next line while guaranteeing the line count and code order are
untouched, and `fitlines.py` applies a table of meaning-preserving
shortenings. Automating this removed most of the tedium — expect roughly
1–24 over-wide lines per 100-entry batch, and most of them are one word too
long.

## 7. Work in batches with a fixed loop

The loop that carried the project, per batch of ~20–100 entries:

```
dump untranslated English for the batch
write a scratchpad script: {id: "translation", ...}
apply it
check.py      # widths, line counts, choice counts
(fix widths)
vcheck.py     # control-code sequence
git add -A    # staging only; the user commits
memory.py --report   # progress
```

Keeping the translations in a throwaway Python dict rather than editing JSON
by hand is what made this fast: one file to write, one command to apply,
trivially re-runnable after a fix.

A batch is done when `check.py` prints `0 problem(s)` and the code verifier
prints `0 mismatches`. Do not start the next batch before that — unverified
batches accumulate into an end-of-project sweep, which is exactly what
happened with the eight code-order bugs above.

## 8. Glob for what you missed

Batching by folder silently skips files. One 43-entry file (`ha/3p/ko_.json`)
was missed for a long time because the folder-level loop that should have
covered it didn't. Periodically re-glob the whole tree and list every file
that still has empty `et` fields, instead of trusting your own batch
bookkeeping. `memory.py --report` doing per-folder percentages made this
visible.

## 9. Keep a glossary, and unify at the end anyway

A `GLOSSARY.md` with every proper noun, event name and recurring game term was
essential — but it was written *while* translating, so the first few thousand
entries predate half of it. The result was five different names for the same
festival.

Two things to do:

- Start the glossary before the first entry, and put the *inflected* forms in
  it too if the language inflects. "Bright Nights = valgusööd" doesn't tell
  you what the genitive is, so people invent one.
- Budget a **consistency pass at the end** regardless. Grep each English term,
  list the distinct Estonian renderings with counts, and unify. This found
  seven inconsistent terms across 77 entries in 23 files.

One trap in that pass: replace only inside entries whose **English** contains
the term. A blind text replacement turned "expert bug catchers" into "expert
bug-contests" and "a bug-catching contest" into "a bug-contest contest",
because the same Estonian stem was used for both the event name and the
ordinary activity. Context-restrict the replacement, then re-read the diffs.

And remember that the longer canonical term can overflow lines that used to
fit — re-run the layout check after unifying, not before.

## 10. Match the register per speaker, not per game

AC:WW has six villager personalities (`bo`, `ge`, `ta`, `ko`, `fu`, `ha`) and
each has its own folder of the *same* dialogue. Translating them identically
wastes the game's best feature. Before starting a personality, read twenty of
its lines and write down its register: for the jock (`ha`) that meant "Jou",
"mees", "vend", "vinge", "trenn", "lihased", and a laugh spelled
"Vaar haar haar".

Keep a list of those markers next to the glossary and reuse them; consistency
of voice across 1800 entries is impossible to hold in your head.

Also: pick the profanity level early and stick to it. Estonian "kurat" was too
strong for a game rated for children, so everything became "pagan" — but only
after some had already been written the other way.

## 11. Destructive-operation hygiene

`git checkout` on a translation file once destroyed 220 finished
translations. In a project where the working tree *is* the deliverable and
nothing is committed yet, any command that restores files from the index is
a data-loss event.

- Stage constantly (`git add -A` after every batch). Staging is free and it is
  the only safety net when the user prefers to commit themselves.
- Never `git checkout` / `git restore` a translation file.
- Guard every scripted repair with a check that the text it expects is
  actually there, and print a `MISS` instead of silently doing nothing or
  crashing halfway through a file:

```python
if old not in e['et']:
    print('MISS', name, mid, old[:35]); continue
```

## 12. Know what the final ROM looks like

The rebuilt ROM is ~33.9 MiB against the original's exactly 32.00 MiB, because
`ndspy` relays out the filesystem and loses the original's tight packing. It
makes no difference in an emulator; it can matter on a flashcart or if anyone
cares about matching the original size. Check this early if it matters, since
fixing it means writing files back in place rather than rebuilding.

Test on the real target. An emulator on a phone (Delta, DraStic, melonDS) is
where layout bugs actually show up, and it costs nothing to hand the user a
build mid-project rather than at the end.

---

## Summary checklist

1. Pipeline and round-trip build first, translation second.
2. Identify the text format and its encoding before writing a parser.
3. Verify the font has your glyphs before promising the language.
4. Write a control-code sequence verifier on day one and run it every batch.
5. Measure line width in pixels with the game's own font table.
6. Line count modulo page height; choice count exactly.
7. Glossary from entry one, including inflected forms.
8. Batch, verify, stage, report — in that order, every time.
9. Re-glob the tree for missed files; don't trust your own bookkeeping.
10. Consistency pass at the end, context-restricted, then re-check layout.
