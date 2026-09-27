from pathlib import Path
import ast,sys

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')

for bad in ('{{_loaded_class}}','{{_icon}}','{{_label}}'):
    assert bad not in s, f'escaped placeholder still present: {bad}'

tree=ast.parse(s)
fn=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_v89_upload_visual_html')
module=ast.Module(body=[fn],type_ignores=[])
ns={}
exec(compile(module,'<v90-test>','exec'),ns)
render=ns['_gsf_v89_upload_visual_html']

empty=render(False)
loaded=render(True)
assert 'class="gsf-v89-upload-visual"' in empty
assert 'Carica il tuo video' in empty
assert '>⇧<' in empty
assert 'class="gsf-v89-upload-visual is-loaded"' in loaded
assert 'Video caricato' in loaded
assert '>✓<' in loaded
assert '{_loaded_class}' not in empty+loaded
assert '{_icon}' not in empty+loaded
assert '{_label}' not in empty+loaded
print('V90 upload visual runtime interpolation: PASS')
