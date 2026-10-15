#!/usr/bin/env python3
"""Add each Office family's vertical metrics to office-font-map.json as "va": [ascent, descent, gap]
in em, as Windows/PowerPoint lays the font out (GDI+ cell ascent, cell descent, and line spacing
minus both), measured on the Office machine (final.json targets, Latin script where measured).
Each measurement set is final.json paired with the families.json that numbers its families;
earlier sets win. usage: curate-vmetrics.py map.json final.json:families.json [...]"""
import json, sys
p = sys.argv[1]; m = json.load(open(p)); by = {}
for pair in sys.argv[2:]:
    final, fams = pair.split(':')
    name = {f['id']: f['family'] for f in json.load(open(fams, encoding='utf-8-sig'))}
    got = {}
    for key, t in json.load(open(final, encoding='utf-8-sig'))['targets'].items():
        fid, script = key.split('|'); fam = name.get(fid)
        if fam and t.get('em') and (script == 'latin' or fam not in got): got[fam] = t
    for fam, t in got.items(): by.setdefault(fam, t)
n = 0
for fam, e in m['fonts'].items():
    t = by.get(fam)
    if not t: e.pop('va', None); continue
    em = t['em']; a, d = t['cellAsc'] / em, t['cellDesc'] / em
    e['va'] = [round(a, 4), round(d, 4), round(max(0, t['lineSpacing'] / em - a - d), 4)]; n += 1
json.dump(m, open(p, 'w'), separators=(',', ':'), ensure_ascii=False)
print('va for', n, 'of', len(m['fonts']))

# Shape metrics for sizing a fallback measured at runtime: "xm": [x-height, cap height, width of the
# measuring sentence] in em (GDI+, 400 px / 100 px renders), and "c": the generic class from PANOSE
# (s sans, r serif, m mono, h script, d decorative/symbol) for fontconfig's fallback.
fam_rec = {}
for pair in sys.argv[2:]:
    final, fams = pair.split(':')
    for f in json.load(open(fams, encoding='utf-8-sig')): fam_rec.setdefault(f['family'], f)
def klass(f):
    p = [int(x) for x in (f.get('panose') or '0 0 0 0 0 0 0 0 0 0').split()]
    if p[3] == 9: return 'm'
    if p[0] == 3: return 'h'
    if p[0] in (4, 5): return 'd'
    if p[0] == 2 and p[1] in (11, 12, 13, 14, 15): return 's'
    if p[0] == 2 and p[1] >= 2: return 'r'
    n = f['family'].lower()
    return 'm' if 'mono' in n or 'console' in n or 'courier' in n else 'r' if any(k in n for k in ('serif', 'roman', 'book', 'times', 'garamond')) else 's'
k = 0
for fam, e in m['fonts'].items():
    t = by.get(fam)
    if t and t.get('xhPx400') and t.get('sentencePx100'):
        e['xm'] = [round(t['xhPx400'] / 400, 4), round((t.get('capPx400') or 0) / 400, 4), round(t['sentencePx100'] / 100, 3)]; k += 1
    if fam in fam_rec: e['c'] = klass(fam_rec[fam])
json.dump(m, open(p, 'w'), separators=(',', ':'), ensure_ascii=False)
print('xm for', k)
