#!/usr/bin/env python3
"""Put the designed metric clones first in office-font-map.json. They were not in the
measured candidate set; their metrics are documented as matching the Office face."""
import json, sys
p = sys.argv[1]; m = json.load(open(p)); F = m['fonts']
C = {
 'Arial': [('Liberation Sans','ttf-liberation',None), ('Arimo',None,'apache/arimo')],
 'Arial Narrow': [('Liberation Sans Narrow','ttf-liberation',None)],
 'Times New Roman': [('Liberation Serif','ttf-liberation',None), ('Tinos',None,'apache/tinos')],
 'Courier New': [('Liberation Mono','ttf-liberation',None), ('Cousine',None,'apache/cousine')],
 'Cambria': [('Caladea','ttf-caladea','ofl/caladea')],
}
for office, clones in C.items():
    e = F.setdefault(office, {'o': []})
    names = {c[0] for c in clones}
    rest = [o for o in e['o'] if o['f'] not in names]
    new = []
    for f, pkg, gf in clones:
        o = {'f': f, 'm': 1, 's': 1.0, 'w': 1.0, 'l': 1.0}
        if pkg: o['pkg'] = pkg
        if gf: o['gf'] = gf
        new.append(o)
    e['o'] = new + rest
json.dump(m, open(p, 'w'), separators=(',', ':'), ensure_ascii=False)
