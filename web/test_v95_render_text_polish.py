from pathlib import Path
import ast,sys,re

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')
tree=ast.parse(s)

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_clean_burnin_text')
mod=ast.Module(body=[node],type_ignores=[])
ast.fix_missing_locations(mod)
ns={'re':re}
exec(compile(mod,str(p),'exec'),ns,ns)
clean=ns['_gsf_clean_burnin_text']

need(clean('ELIMINATO! 🎯')=='ELIMINATO!','target emoji removed from hook')
need(clean('CHE GOL! ⚽🔥')=='CHE GOL!','multiple emoji removed cleanly')
need(clean('Caffè già!')=='Caffè già!','accented Italian text preserved')
need('_gsf_clean_burnin_text(hook_text)' in s,'hook renderer uses sanitizer')
need('ELIMINATO! 🎯' not in s and 'CHE GOL! ⚽🔥' not in s and 'CHE REAZIONE! 😱' not in s,'built-in hook templates are typography-safe')
need('numero_clip=3' in s,'three-clip AI contract unchanged')
need('key="upload_v73"' in s,'stable uploader key unchanged')
need('gsf-v89-upload-visual' in s,'approved upload circle unchanged')
need('"-crf","21"' in s,'V94 final encode quality preserved')
need('def _gsf_subtitle_groups' in s,'V94 phrase-aware subtitles preserved')
need('def _gsf_smooth_reframe_track' in s,'V94 smooth reframe preserved')
need('Gaming Shorts Factory · V95 Render Text Polish' in s,'V95 marker')
print('V95 render text polish regression: PASS')
