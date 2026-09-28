from pathlib import Path
import ast,sys,subprocess,shutil,tempfile

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')
tree=ast.parse(s)

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

need('Gaming Shorts Factory · V103.2 Canonical Final Format' in s,'V103.2 marker')
need('ANTEPRIMA HOOK' not in s,'hook preview remains removed')
need('st.session_state["hook_enabled_v102"]=False' in s,'hook remains disabled')

core_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_render_core')
core=ast.get_source_segment(s,core_node) or ''
need('fmt=_gsf_normalize_final_fmt(fmt)' in core,'final renderer canonicalizes format before rendering')
need(core.find('fmt=_gsf_normalize_final_fmt(fmt)') < max(core.find('if fmt'),999999),'canonicalization precedes format branches')
need('scale=1080:1920:flags=lanczos' in s,'vertical full-HD Smart Reframe target preserved')
need('"-crf","14"' in core,'CRF14 preserved')
need('"-preset","medium"' in core,'medium preset preserved')
need('"-threads","2"' in core,'two-thread render preserved')
need('"-pix_fmt","yuv420p"' in core,'yuv420p render target preserved')
need('"-tag:v","avc1"' in core,'avc1 preserved')

# Load canonicalizer + validator helpers.
names={'_gsf_normalize_final_fmt','_gsf_probe_social_master','_gsf_ratio_float','_gsf_validate_social_master'}
nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
ns={'subprocess':subprocess,'shutil':shutil}
mod=ast.Module(body=nodes,type_ignores=[])
ast.fix_missing_locations(mod)
exec(compile(mod,str(p),'exec'),ns,ns)
norm=ns['_gsf_normalize_final_fmt']
need(norm('9:16')=='9:16 Short','9:16 alias canonicalized')
need(norm('9:16 Short')=='9:16 Short','9:16 Short preserved')
need(norm('Verticale 9:16')=='9:16 Short','descriptive vertical alias canonicalized')
need(norm('9x16')=='9:16 Short','9x16 alias canonicalized')
need(norm('16:9')=='16:9','16:9 preserved')

fake={
 'ok':True,
 'data':{
   'streams':[
     {'codec_type':'video','codec_name':'h264','codec_tag_string':'avc1','profile':'High','level':42,
      'pix_fmt':'yuv420p','width':1080,'height':1920,'avg_frame_rate':'30/1','r_frame_rate':'30/1'},
     {'codec_type':'audio','codec_name':'aac','sample_rate':'48000','channels':2}
   ],
   'format':{'format_name':'mov,mp4,m4a,3gp,3g2,mj2','duration':'1','size':'1','bit_rate':'1'}
 }
}
ns['_gsf_probe_social_master']=lambda path: fake
for alias in ('9:16','9:16 Short','Verticale 9:16','9x16'):
    rep=ns['_gsf_validate_social_master']('dummy.mp4',alias)
    need(rep.get('ok'),f'validator treats {alias!r} as 1080x1920 vertical: {rep.get("errors")}')

# A 608x1080 vertical file must NOT be silently accepted as final master.
fake['data']['streams'][0]['width']=608
fake['data']['streams'][0]['height']=1080
rep=ns['_gsf_validate_social_master']('dummy.mp4','9:16')
need(not rep.get('ok'),'608x1080 is still rejected as sub-HD final output')
need(any('1080x1920' in e for e in rep.get('errors',[])),'sub-HD error now reports correct vertical target')

print('V103.2 Canonical Final Format regression: PASS')
