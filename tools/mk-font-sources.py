# SPDX-License-Identifier: GPL-3.0-or-later
# Builds data/font-sources.json: pinned google/fonts commit, exact files, sha256.
# Run inside data/ with a google/fonts clone at ./gf (git clone https://github.com/google/fonts gf).
import json, subprocess, hashlib, os, re, concurrent.futures as cf, urllib.request
m=json.load(open('office-font-map.json'))['fonts']
commit=subprocess.check_output(['git','-C','gf','rev-parse','HEAD'],text=True).strip()
tree=subprocess.check_output(['git','-C','gf','ls-tree','-r','--name-only','HEAD','ofl','apache','ufl'],text=True).split('\n')
bydir={}
for p in tree:
    d,_,n=p.rpartition('/'); bydir.setdefault(d,[]).append(n)
firsts={}
for v in m.values():
    for o in v['o']:   # every option: when the best has no download, the next one can stand in
        if o.get('gf'): firsts[o['f']]=o['gf']
CAP=8*1024*1024
want=re.compile(r'-(Regular|Bold|Italic|BoldItalic)\.(ttf|otf)$')
def pick(d):
    names=[n for n in bydir.get(d,[]) if n.lower().endswith(('.ttf','.otf'))]
    statics=[n for n in names if '[' not in n]
    if len(statics)>4: names=[n for n in statics if want.search(n)] or names
    lic=[n for n in bydir.get(d,[]) if n in ('OFL.txt','LICENSE.txt','UFL.txt')]
    return names, lic
base=f'https://raw.githubusercontent.com/google/fonts/{commit}/'
os.makedirs('cache',exist_ok=True)
def get(path):
    f='cache/'+path.replace('/','__')
    if not os.path.exists(f):
        urllib.request.urlretrieve(base+urllib.request.quote(path),f)
    b=open(f,'rb').read(); return {'p':path,'sha256':hashlib.sha256(b).hexdigest(),'size':len(b)}
out={}
jobs={}
with cf.ThreadPoolExecutor(12) as ex:
    for fam,d in firsts.items():
        names,lic=pick(d)
        jobs[fam]=([ex.submit(get,f'{d}/{n}') for n in names],[ex.submit(get,f'{d}/{n}') for n in lic])
    for fam,(fs,ls) in jobs.items():
        files=[]; bad=False
        for f in fs:
            try: r=f.result()
            except Exception as e: print('fail',fam,e); bad=True; continue
            if r['size']<=CAP: files.append(r)
            else: print('too big',fam,r['p'],r['size']); bad=True
        # A family is all its files or none (no half-installed families).
        if bad or not files: print('dropped',fam,firsts[fam]); continue
        e={'files':files}
        for l in ls:
            try: e['license']=l.result()
            except Exception: pass
        out[fam]=e
json.dump({'v':1,'about':'Exact font files for the free matches in office-font-map.json, from google/fonts at a pinned commit; each with its size and sha256: check every file before parsing it. Made by tools/mk-font-sources.py.',
           'base':base,'commit':commit,'families':out},open('font-sources.json','w'),separators=(',',':'),sort_keys=True)
print(len(out),'families', sum(len(e['files']) for e in out.values()),'files', sum(f['size'] for e in out.values() for f in e['files'])//1048576,'MB')
