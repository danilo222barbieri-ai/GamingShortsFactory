from pathlib import Path
import ast,re
p=Path('/app/GamingShortsFactory_V102_SMART_HOOK.py')
s=p.read_text(encoding='utf-8')
tree=ast.parse(s)
print('=== V103 RENDER CORE ===')
for name in ['_gsf_render_core','_gsf_render_final_recipe','_gsf_recipe_selected']:
    n=next((n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name),None)
    if n:
        print(f'--- {name} ---')
        print(ast.get_source_segment(s,n) or '')
print('=== V103 AUDIO HELPERS ===')
for n in tree.body:
    if isinstance(n,ast.FunctionDef) and re.search(r'audio|loud|normal|volume',n.name,re.I):
        print(f'--- {n.name} ---')
        print((ast.get_source_segment(s,n) or '')[:10000])
