from pathlib import Path
import ast,re

p=Path('/app/GamingShortsFactory_V101_SUBTITLE_REFINEMENT.py')
s=p.read_text(encoding='utf-8')
tree=ast.parse(s)

print('=== V102 DIAGNOSTIC FUNCTIONS ===')
for n in tree.body:
    if isinstance(n,(ast.FunctionDef,ast.AsyncFunctionDef)) and 'hook' in n.name.lower():
        print(f'--- FUNCTION {n.name} lines {n.lineno}-{n.end_lineno} ---')
        print(ast.get_source_segment(s,n) or '')

print('=== V102 DIAGNOSTIC HOOK CONTEXT ===')
lines=s.splitlines()
hits=[]
for i,line in enumerate(lines):
    if re.search(r'hook',line,re.I):
        hits.append(i)
shown=0
last_end=-1
for i in hits:
    a=max(0,i-8); b=min(len(lines),i+14)
    if a<=last_end: continue
    print(f'--- lines {a+1}-{b} ---')
    print('\n'.join(lines[a:b]))
    last_end=b
    shown+=1
    if shown>=70: break

print('=== V102 EXACT UI 11980-12150 ===')
lines=s.splitlines()
print('\n'.join(lines[11979:12150]))
print('=== V102 EXACT UI 12450-12550 ===')
print('\n'.join(lines[12449:12550]))

print('=== V102 EXACT UI 11820-11985 ===')
lines=s.splitlines()
print('\n'.join(lines[11819:11985]))
