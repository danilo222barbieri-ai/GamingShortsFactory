from pathlib import Path
import ast,re
p=Path('/app/GamingShortsFactory_V103_1_CLEAN_HOOK_PIXFMT.py')
s=p.read_text(encoding='utf-8')
tree=ast.parse(s)

print('=== V103.2 DIAG RENDER FUNCTIONS ===')
for name in ('_gsf_render_core','_gsf_render_final_recipe','_gsf_render_editor_output','_gsf_apply_editor_changes'):
    n=next((x for x in tree.body if isinstance(x,ast.FunctionDef) and x.name==name),None)
    if n:
        print(f'--- {name} {n.lineno}-{n.end_lineno} ---')
        print(ast.get_source_segment(s,n) or '')

print('=== V103.2 DIAG FORMAT/SCALE CONTEXT ===')
lines=s.splitlines()
hits=[]
for i,line in enumerate(lines):
    if re.search(r'608|scale=.*1080|1080.*scale|1920|fmt=|fmt\)|render_kwargs|main_editor|inline_editor',line,re.I):
        hits.append(i)
last=-1
for i in hits:
    a=max(0,i-5); b=min(len(lines),i+10)
    if a<=last: continue
    print(f'--- lines {a+1}-{b} ---')
    print('\n'.join(lines[a:b]))
    last=b
