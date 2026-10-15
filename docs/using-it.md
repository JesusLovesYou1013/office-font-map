# Using it in a program

This is the method OmaShow uses. The Python file in `python/` does each step.

## 1. Opening a document

For every font family the document names:

1. If the family is installed, use it. Nothing else to do.
2. If it's in the table (`fonts`, any case), take the first match in `o` that is installed.
3. Keep, with the text that uses it:
   - the Office family name,
   - its original size,
   - the factor you applied (1 for metric-compatible matches),
   - the weight in its name (`wt`) if any.

   This is what lets you save it back unchanged. Theme fonts need the same.
4. Swap the family for the match, and the size:
   - metric-compatible (`m: 1`): keep the size;
   - otherwise: size × `s`.
5. If `wt` is set, draw at that weight ("Segoe UI Semibold" becomes the match at 600).

If none of the matches is installed, you can either:

- offer to download them (see font-sources.json: check sizes and hashes; a family installs whole or not at
  all), or
- use a **fallback**: an installed font of the same class `c` (ask the system for "sans-serif", "serif" and so
  on) sized to match. Measure its kerned advance per character over `CORPUS` at the style you need, then:
  - size factor = Office `aw` ÷ the fallback's (clamped to 0.6 to 1.6; treat it as 1 when within 0.3%).
  - For families without `aw`, use the advance over `SENTENCE` against `xm[2]`.

Do this before showing the document, so it never appears in the wrong font first and then jumps.

## 2. Showing sizes

Show the user the size actually drawn (the swapped size). If Calibri 11 is drawn as a scaled match at 10.5,
the size field says 10.5. What's on screen and what the field says always agree.

## 3. Lines that sit where Office puts them (optional)

For metric-compatible matches and fallbacks, the free font's ascent and descent differ a little from the
Office font's, so lines drift up or down. With `va` (the Office font's ascent, descent and gap in em) and the
free font's own metrics:

- line-height multiplier = (Office ascent + descent + gap) × Office size ÷ (free ascent + descent + leading) × drawn size
- shift up = free ascent × drawn size − Office ascent × Office size

Ignore a multiplier within 0.5% of 1 and a shift under 0.25 px. This is for drawing only, so there's nothing
to undo on save. In OmaShow, scaled table matches looked worse with it, so it's left off for them.

## 4. Saving back to the Office format

For each piece of text that was swapped:

- Write the Office family name back, not the free one.
- Size untouched since opening: write exactly the original size. Don't divide and round, or sizes creep.
- Size changed by the user: divide by the factor and round to half a point (Office's own step), never below
  1 pt.
- Don't embed the Office font (you don't have it) or the free stand-in.

A free family the user picked themselves that is metric-compatible with an Office family (Carlito, say) can be
saved under the Office name (Calibri). The document then looks right on Windows with no font embedded.

## 5. Where it falls short

- Some text still breaks one word differently at a box edge, because kerning and shaping differ even when
  overall widths match.
- 189 of the 396 families have no per-character widths yet (`aw`), only the older sentence width.
- Scripts other than Latin were measured more thinly.
