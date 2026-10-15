# office-font-map

Open a document made on Windows (PowerPoint, Word, Excel, …) on a computer that doesn't have Microsoft's
fonts, and have it look the same.

Documents from Windows name fonts like Calibri, Cambria, Aptos and Segoe UI. Most other systems don't have
them, and can't legally ship them. Swapping in any free font changes how big the text looks, so lines break
in other places, text spills out of its box and pages reflow.

This project is the data and the method to fix that:

- **396 Office font families**, each with up to three free, openly licensed look-alikes, best first.
  Metric-compatible matches come first (Carlito for Calibri, Caladea for Cambria, Liberation for Arial,
  Times New Roman and Courier New): same width at the same size, so nothing moves.
- **Measured size factors** for the others: draw the free font at the Office size × `s` and it sets text
  about as wide as the Office font did, so lines break in the same places.
- **The way back**: the document keeps the Office font name and its original size. Saving writes those back,
  so the file still looks right in Office. A size the user changed is converted back and rounded to half a
  point.
- **When no match is installed**: per-character widths of the Office fonts (measured with DirectWrite, the
  way Windows draws them), so any installed font can be measured at runtime and sized to match.
- **Line metrics** (ascent, descent and gap as Windows lays the font out), so lines can sit where Office puts
  them.
- **Where to get the free fonts**: for 512 families, the exact files in google/fonts at one pinned commit,
  each with its size and SHA-256 hash, plus the Arch Linux package where there is one.

No font files are included: only names, measurements and where to download them.

## Using it

- `data/office-font-map.json`: the table. Format: [docs/format.md](docs/format.md).
- `data/font-sources.json`: pinned, hashed downloads for the free fonts.
- [docs/using-it.md](docs/using-it.md): the method step by step, for any program (opening, drawing, editing,
  saving).
- `python/office_font_map.py`: a reference implementation of that method, standard library only. Copy it
  into your project, or read it as a worked example. Run its tests with
  `cd python && python3 -m unittest`.

Copy the data into your program rather than downloading it at run time: it's small (about 130 KB, and
190 KB with download sources) and changes rarely.

## Used by

- [OmaShow](https://github.com/28allday/omashow), a presentation app for Omarchy, which carries its own copy
  of this data and implements the method in C++ (`src/core/fontswap.cpp`).

## How it was made

See [docs/how-it-was-measured.md](docs/how-it-was-measured.md). `tools/` holds the scripts that build and
update the data.

## Licence

Open, and it stays open: anything built from it must be shared under the same terms.

- Data (`data/`): [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). Credit "office-font-map by
  JesusLovesYou1013". CC BY-SA 4.0 is one-way compatible with GPL 3, so GPL programs can include it.
- Code (`python/`, `tools/`): GPL-3.0-or-later, see [LICENSE](LICENSE).
- The free fonts themselves are under their own licences, almost all the SIL Open Font License. Each
  download source names its licence file.
- Microsoft, Office, Calibri, Cambria, Aptos, Segoe and the other font names are trademarks of their owners
  and are used here only to say which font a document asks for. This project contains none of their fonts.
