# How it was measured

## The Office side (Windows)

The Office fonts were measured on a Windows machine with Office installed, from each font's own files as
Windows draws them:

- **Line metrics (`va`)**: GDI+ cell ascent, cell descent, and line spacing minus both, divided by the em
  size. Latin script where it was measured.
- **Shape (`xm`)**: x-height and cap height from 400 px renders, and the advance width of `SENTENCE` from a
  100 px render, all in em (GDI+).
- **Class (`c`)**: from the font's PANOSE numbers (family kind, serif style, proportion), and from its name
  when PANOSE is empty.
- **Per-character widths (`aw`)**: WPF `FormattedText` (DirectWrite, kerning on) at 100 px over `CORPUS`,
  divided by its length, for regular, bold and italic. 207 families were measured. The other 189 weren't on
  the measuring machine and keep only the sentence width.

## The free side

The candidate free families (google/fonts and Linux distribution packages) were measured the same way and
ranked by likeness to each Office font. Each candidate's size factor `s` makes it set text as wide as the
Office font at the Office size. `w` and `l` are its width and line height at the same size.

The best three per Office family were kept. Designed metric clones (Liberation, Arimo, Tinos, Cousine,
Caladea, Carlito), whose widths are built to match, were put first and marked `m: 1`
(`tools/curate-clones.py`).

## Checking

In OmaShow, against PowerPoint's own output for the same decks:

- **Per-character sizes**: 11,397 characters, 0 size mismatches.
- **Line breaks**: compared box by box against PowerPoint's PDF. 15 of 19 boxes broke identically before
  per-character widths were added; the rest differ by one word.
- **Baselines**: within 1–3 px of PowerPoint's after the `va` line fix (from 4–5 px).
- **Round trips**: PowerPoint → OmaShow → PowerPoint keeps every font name and size.

## The scripts (`tools/`)

- `curate-clones.py map.json`: puts the metric clones first.
- `curate-vmetrics.py map.json final.json:families.json …`: adds `va`, `xm` and `c` from the Windows
  measurement files.
- `mk-font-sources.py`: builds `font-sources.json` from a google/fonts clone at a pinned commit (run in
  `data/`, with the clone at `./gf`).

Not here yet: the Windows measuring scripts (PowerShell) and the raw measurement files (`final.json`,
`families.json`, `office-widths.json`). They'll be added from the original measuring machine.
