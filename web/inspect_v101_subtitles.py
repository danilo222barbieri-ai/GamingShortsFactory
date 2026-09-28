from pathlib import Path
import ast,re

p=Path('/app/GamingShortsFactory_V100_8_FAST_RENDER.py')
s=p.read_text(encoding='utf-8')
tree=ast.parse(s)

print('=== V101 DIAGNOSTIC: _gsf_write_render_ass ===')
node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_write_render_ass')
seg=ast.get_source_segment(s,node) or ''
print(seg[:16000])

print('=== V101 DIAGNOSTIC: subtitle UI/context lines ===')
lines=s.splitlines()
hits=[]
for i,line in enumerate(lines):
    if re.search(r'editor_sub|project_subtitles|subtitle.*font|subtitle.*color|sub_.*font|sub_.*color|font.*subtitle|color.*subtitle',line,re.I):
        hits.append(i)
seen=set()
for i in hits[:80]:
    a=max(0,i-4); b=min(len(lines),i+7)
    key=(a,b)
    if key in seen: continue
    seen.add(key)
    print(f'--- lines {a+1}-{b} ---')
    print('\n'.join(lines[a:b]))
