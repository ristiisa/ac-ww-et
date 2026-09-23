# Animal Crossing: Wild World — Estonian translation

A complete Estonian translation of *Animal Crossing: Wild World* (Nintendo DS,
USA Rev 1). All 21461 text entries are translated.

The repository contains **no game data**. You supply your own ROM dump; the
tools extract its text, apply the translation from `translation/`, and write a
patched ROM to `out/`.

## Requirements

- Python 3.10 or newer (developed on 3.12)
- `ndspy` and `pillow`
- Your own dump of *Animal Crossing: Wild World (USA) (Rev 1)*, placed at
  `rom/Animal Crossing - Wild World (USA) (Rev 1).nds`

No compiler, no devkitARM, no disassembly — the text is pure data.

## Setup

**Linux / macOS**

```sh
python3 -m venv .venv
.venv/bin/pip install ndspy pillow
```

**Windows (PowerShell)**

```powershell
py -m venv .venv
.venv\Scripts\pip install ndspy pillow
```

Everything below uses `.venv/bin/python`; on Windows that is
`.venv\Scripts\python`. Run every command from the repository root — the tools
use paths relative to the working directory.

## Building the ROM

```sh
.venv/bin/python tools/build.py
```

Writes `out/AC_WW_EST.nds`. That is the whole build; `translation/` is already
populated and committed.

The result is ~33.9 MiB against the original's 32.00 MiB, because ndspy relays
out the filesystem. Emulators do not care. Tested on melonDS, and on Android
and iOS via Delta / DraStic / melonDS.

## Working on the translation

```sh
# Re-extract text from the ROM (only needed after changing the export code;
# existing "et" translations are preserved).
.venv/bin/python tools/extract.py      # script/ and font/ -> extracted/
.venv/bin/python tools/export.py       # BMG text -> translation/**/*.json

# Validate
.venv/bin/python tools/check.py        # line widths, line counts, choice counts
.venv/bin/python tools/memory.py --report   # progress per folder

# Automatic repairs
.venv/bin/python tools/reflow.py  translation/message/bo/ev/acorn_.json
.venv/bin/python tools/fitlines.py translation/message/bo/ev/acorn_.json
.venv/bin/python tools/memory.py       # fill entries whose English repeats elsewhere
```

### Layout rules

`check.py` measures line width **in pixels using the game's own font table**,
not in characters:

- 160 px per dialogue line; the box shows 3 lines per page
- a `{04 xx 00}` variable (player name, town, item) costs 48 px
- `{ff ...}` highlight codes cost 0 px
- line count must match English **modulo 3**, choice count **exactly**
- encyclopedia entries use a narrower 100 px box

`check.py` does **not** verify control codes. Their multiset *and order* must
match the English exactly, or dialogue breaks at runtime — `build.py` is what
catches that.

### Reference documents

| File | Contents |
|---|---|
| `translation/GLOSSARY.md` | proper nouns, event names, recurring terms |
| `translation/CHARACTERS.md` | every NPC's speech style and its Estonian register |
| `LESSONS.md` | notes for anyone translating another DS game |

## Layout

```
rom/            your ROM dump (not in git)
extracted/      script/ and font/ pulled out of the ROM
translation/    the translation itself — JSON with "en"/"et" per entry
  message/      dialogue, by speaker personality and context
  string/       item and furniture name tables
  mail/ bbs/    letters and bulletin board
tools/          extract, export, build, check, and repair scripts
out/            the built ROM
```

An empty `"et"` falls back to the English text, so the ROM builds and boots at
any point.

## Legal

This is a fan translation. It distributes no Nintendo code or assets — only
Estonian text and the scripts that apply it to a ROM you dumped yourself.
Under the Estonian Copyright Act (§18, §24) a lawful owner may adapt a work
for personal use. Do not distribute the patched ROM.
