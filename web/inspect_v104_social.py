from pathlib import Path
import re,ast
p=Path('/app/GamingShortsFactory_V103_2_CANONICAL_FORMAT.py')
s=p.read_text(encoding='utf-8')
print('=== V104 SOCIAL FUNCTIONS ===')
tree=ast.parse(s)
for n in tree.body:
    if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and re.search(r'youtube|tiktok|instagram|social|publish|upload',n.name,re.I):
        print(f'--- {n.name} {n.lineno}-{n.end_lineno} ---')
        print(ast.get_source_segment(s,n) or '')
print('=== V104 SOCIAL UI CONTEXT ===')
lines=s.splitlines()
hits=[]
for i,line in enumerate(lines):
    if re.search(r'YouTube|TikTok|Instagram|social|pubblic|shorts|reels',line,re.I):
        hits.append(i)
last=-1
for i in hits:
    a=max(0,i-8); b=min(len(lines),i+18)
    if a<=last: continue
    print(f'--- lines {a+1}-{b} ---')
    print('\n'.join(lines[a:b]))
    last=b
