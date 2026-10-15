"""office_font_map: draw Office documents in free fonts at the size that makes them look the same.

Reference implementation of docs/using-it.md. Standard library only; copy this file into any project.
SPDX-License-Identifier: GPL-3.0-or-later

    from office_font_map import FontMap
    fm = FontMap.load()                                   # data/office-font-map.json beside this repo
    choice = fm.choose("Calibri", installed={"Carlito", "Open Sans"})
    shown = fm.shown_size(11, choice)                     # what to draw / show in the size field
    back = fm.office_size(shown, choice, original=11)     # what to write back to the Office file
"""
from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass, field

HERE = os.path.dirname(os.path.abspath(__file__))
DEFAULT_MAP = os.path.join(HERE, os.pardir, "data", "office-font-map.json")

# The text the map's "aw" widths were measured over (kerned, at 100 px, per character).
# Measure a fallback font over exactly this string to compare it with an Office font.
CORPUS = (
    "When the quarterly review began, the team looked first at what had changed since the last meeting. S"
    "ales in the northern region grew by about twelve percent, while costs in shipping and support fell s"
    "lightly. Several customers asked for clearer pricing, and the product group agreed to publish a simp"
    "le guide before the end of the month. We also hired four people across two offices, which should hel"
    "p with the backlog of requests that built up during the summer. Next, we will focus on three goals: "
    "keep response times under a day, finish the new reporting tools, and plan the training program for s"
    "pring. If you have questions about any of these points, please write to your manager or bring them t"
    "o the next session.")
# Older measure (map "xm"[2]): the advance width of this sentence in em, for families without "aw".
SENTENCE = "Sphinx of black quartz, judge my vow. The quick brown fox jumps over the lazy dog 0123456789"

# Within this much, a fallback is drawn at the Office size rather than scaled.
SAME_WIDTH = 0.003
# A fallback is never scaled outside this range.
SIZE_RANGE = (0.6, 1.6)


@dataclass(frozen=True)
class Option:
    """One free family that can stand in for an Office family."""
    family: str
    metric: bool          # same advance widths at the same size: no scaling, lines break the same
    size: float = 1.0     # draw at office size x this (only when not metric)
    width: float = 1.0    # its width at the same size, relative to the Office font
    line: float = 1.0     # its line height relative to the Office font's
    package: str = ""     # Arch Linux package
    google_fonts: str = ""  # google/fonts directory, e.g. "ofl/carlito"
    github: str = ""      # owner/repo/dir
    fallback: bool = False  # not from the table: a font measured at runtime

    @property
    def scales(self) -> bool:
        return not self.metric and not math.isclose(self.size, 1.0)


@dataclass
class Entry:
    office: str
    options: list[Option] = field(default_factory=list)
    weight: int = 0                  # weight carried in the family name ("Segoe UI Semibold" -> 600)
    vertical: tuple = ()             # (ascent, descent, gap) in em, as Windows lays it out
    shape: tuple = ()                # (x-height, cap height, sentence width) in em
    kind: str = "s"                  # s sans, r serif, m mono, h script, d decorative
    advance: tuple = ()              # kerned advance per character over CORPUS: (regular, bold, italic)


class FontMap:
    def __init__(self, data: dict):
        self.entries: dict[str, Entry] = {}
        for office, raw in data["fonts"].items():
            options = [Option(family=o["f"], metric=bool(o.get("m")), size=o.get("s", 1.0), width=o.get("w", 1.0),
                              line=o.get("l", 1.0), package=o.get("pkg", ""), google_fonts=o.get("gf", ""),
                              github=o.get("gh", "")) for o in raw.get("o", [])]
            self.entries[office.lower()] = Entry(office, options, raw.get("wt", 0), tuple(raw.get("va", ())),
                                                 tuple(raw.get("xm", ())), raw.get("c", "s"), tuple(raw.get("aw", ())))

    @classmethod
    def load(cls, path: str = DEFAULT_MAP) -> "FontMap":
        with open(path, encoding="utf-8") as f:
            return cls(json.load(f))

    # --- looking things up ------------------------------------------------------------------------

    def entry(self, office: str) -> Entry | None:
        return self.entries.get(office.lower())

    def is_office(self, family: str) -> bool:
        return family.lower() in self.entries

    def options(self, office: str) -> list[Option]:
        """The free matches of an Office family, best first."""
        e = self.entry(office)
        return list(e.options) if e else []

    def choose(self, office: str, installed) -> Option | None:
        """The first free match that is installed (``installed``: a set of family names, any case)."""
        have = {f.lower() for f in installed}
        return next((o for o in self.options(office) if o.family.lower() in have), None)

    def office_for(self, free: str) -> str:
        """The Office family a free family is metric-compatible with ("Carlito" -> "Calibri"), or "".
        Use it when saving a font the user picked: it can be written under the Office name."""
        for e in self.entries.values():
            if any(o.metric and o.family.lower() == free.lower() for o in e.options):
                return e.office
        return ""

    # --- sizes ------------------------------------------------------------------------------------

    @staticmethod
    def shown_size(office_pt: float, option: Option | None) -> float:
        """The size to draw and to show the user. Metric-compatible matches keep the Office size."""
        return office_pt * option.size if option and option.scales else office_pt

    @staticmethod
    def office_size(shown_pt: float, option: Option | None, original: float | None = None) -> float:
        """The size to write back to the Office file.
        Unchanged since opening -> exactly the original. Changed -> divided back, rounded to half a point
        (Office's own step), never below 1 pt."""
        if not option or not option.scales:
            return shown_pt
        if original and math.isclose(shown_pt, original * option.size, rel_tol=1e-6):
            return original
        return max(1.0, round(shown_pt / option.size * 2) / 2)

    # --- when no free match is installed ----------------------------------------------------------

    def fallback(self, office: str, family: str, measured_advance: float, style: int = 0,
                 ascent: float = 0, descent: float = 0, leading: float = 0) -> Option | None:
        """Size an installed font that is not in the table (e.g. the system's default sans).

        measured_advance: that font's kerned advance per character over CORPUS, in em
                          (or, for a family whose entry has no "aw", its advance over SENTENCE in em).
        style: 0 regular, 1 bold, 2 italic.  ascent/descent/leading: its vertical metrics in em, for the
        line factor. Returns None when the table has no width for this family."""
        e = self.entry(office)
        if not e or measured_advance <= 0:
            return None
        if e.advance and len(e.advance) > style and e.advance[style] > 0:
            target = e.advance[style]
        elif e.advance and e.advance[0] > 0:
            target = e.advance[0]
        elif len(e.shape) > 2 and e.shape[2] > 0:
            target = e.shape[2]
        else:
            return None
        same = measured_advance / target
        size = 1.0 if abs(same - 1) <= SAME_WIDTH else round(min(max(target / measured_advance, SIZE_RANGE[0]), SIZE_RANGE[1]), 3)
        line = 1.0
        free = ascent + descent + max(0.0, leading)
        if len(e.vertical) == 3 and free > 0:
            line = sum(e.vertical) / (size * free)
        return Option(family=family, metric=False, size=size, width=same * size, line=line, fallback=True)

    def vertical_fix(self, office: str, option: Option, drawn_pt: float,
                     ascent: float, descent: float, leading: float) -> tuple[float, float]:
        """(line-height multiplier, shift in the unit of drawn_pt) that puts a metric-compatible match's or a
        fallback's lines where the Office font's land. ascent/descent/leading: the free font's, in em.
        Drawing only: nothing to reverse on save. (1, 0) when no fix applies."""
        e = self.entry(office)
        if not e or len(e.vertical) != 3 or not (option.metric or option.fallback):
            return 1.0, 0.0
        free = ascent + descent + max(0.0, leading)
        if free <= 0:
            return 1.0, 0.0
        office_pt = drawn_pt / (option.size if option.scales else 1.0)
        line = sum(e.vertical) * office_pt / (free * drawn_pt)
        shift = ascent * drawn_pt - e.vertical[0] * office_pt
        return (1.0 if abs(line - 1) < 0.005 else line), (0.0 if abs(shift) < 0.25 else shift)
