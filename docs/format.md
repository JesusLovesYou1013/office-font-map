# Data format

## data/office-font-map.json

```json
{"v": 1, "about": "…", "fonts": {"Calibri": {"o": [ … ], "va": [ … ], "xm": [ … ], "c": "s", "aw": [ … ]}, …}}
```

`fonts` is keyed by the Office family name as documents write it. Compare names without regard to case.

### Per Office family

| Key  | Meaning |
|------|---------|
| `o`  | The free matches, best first: metric-compatible ones, then by measured likeness. One to three. |
| `wt` | The weight the family carries in its name, e.g. 600 for "Segoe UI Semibold". Absent when none. Draw the match at this weight. |
| `va` | `[ascent, descent, gap]` in em, as Windows (GDI+) lays the font out. Line height = sum × size. |
| `xm` | `[x-height, cap height, sentence width]` in em. The sentence is `SENTENCE` below, at 100 px. |
| `c`  | Generic class from the font's PANOSE: `s` sans, `r` serif, `m` mono, `h` script, `d` decorative or symbol. Use it to ask the system for a fallback of the right kind. |
| `aw` | `[regular, bold, italic]` kerned advance width per character, in em, over `CORPUS` below, measured with DirectWrite. Present for 207 of the 396 families; the others have `xm` only. |

### Per match (`o` entries)

| Key   | Meaning |
|-------|---------|
| `f`   | Free family name. |
| `m`   | 1 if metric-compatible (same advance widths at the same size): draw at the Office size. 0 otherwise. |
| `s`   | Size factor: draw at Office size × `s`. Only for `m: 0`. |
| `w`   | The match's width at the same size, relative to the Office font (information; `s` already accounts for it). |
| `l`   | Line height relative to the Office font's. |
| `pkg` | Arch Linux package that provides it. |
| `gf`  | google/fonts directory (`ofl/carlito`); see font-sources.json for the exact files. |
| `gh`  | GitHub `owner/repo/dir` for fonts not in google/fonts. |

### Measuring texts

`SENTENCE` (for `xm[2]`):

    Sphinx of black quartz, judge my vow. The quick brown fox jumps over the lazy dog 0123456789

`CORPUS` (for `aw`; 719 characters, ordinary English prose so letters come at their usual frequencies; one
line, no line breaks): see `CORPUS` in `python/office_font_map.py`, which is the exact text.

## data/font-sources.json

```json
{"v": 1, "about": "…", "base": "https://raw.githubusercontent.com/google/fonts/<commit>/", "commit": "<40 hex>",
 "families": {"Carlito": {"files": [{"p": "ofl/carlito/Carlito-Regular.ttf", "sha256": "…", "size": 123}],
                          "license": {"p": "ofl/carlito/OFL.txt", "sha256": "…", "size": 4567}}}}
```

- Download `base + p`. Check the size and SHA-256 before anything parses the file.
- A family is all its files or none: install it only when every file checked out.
- Keep the licence file beside the fonts.
- Where a family has more than four static files, only Regular, Bold, Italic and BoldItalic are listed.
  Otherwise all of them are listed, variable fonts included.
