from pathlib import Path
import ast,sys,tempfile,subprocess,shutil

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')
tree=ast.parse(s)

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

need('Gaming Shorts Factory · V103.1 Clean Final' in s,'V103.1 marker')
need('ANTEPRIMA HOOK' not in s,'hook preview caption removed')
need('_gsf_v71_render_mini_player(\n                    _v102_pp' not in s,'hook preview player removed')
need('st.text_input(\n                "Testo hook"' not in s,'hook text field removed from final flow')
need('st.toggle(\n                "Hook"' not in s,'hook toggle removed from final flow')
need('st.session_state["hook_enabled_v102"]=False' in s,'hook disabled in project state')
need('_final_recipe["manual_hook"]=_GSF_HOOK_OFF_V102' in s,'AI final recipe forces hook OFF')
need('_v103_kw["hook_text"]=""' in s,'Editor final recipe clears hook')
need('_gsf_hook_from_diag' in s,'hook engine code remains available for future editor use')

# Quality/render guards preserved.
core=ast.get_source_segment(s,next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_render_core')) or ''
need('"-crf","14"' in core,'CRF14 preserved')
need('"-preset","medium"' in core,'medium preset preserved')
need('"-threads","2"' in core,'two-thread render preserved')
need('"-pix_fmt","yuv420p"' in core,'render still requests yuv420p')
need('"-tag:v","avc1"' in core,'avc1 tag preserved')
need('"-c:a","aac","-b:a","192k"' in core,'AAC 192k preserved')
need('"-ar","48000"' in core and '"-ac","2"' in core,'48k stereo preserved')
need('GSF_SMART_REFRAME_VERSION = "v100-gameplay-safe"' in s,'Smart Reframe preserved')
need('_gsf_refine_subtitle_words' in s,'V101 subtitles preserved')
need('numero_clip=3' in s,'three AI clips preserved')

# Load validator helpers and verify yuv420p + yuvj420p behavior.
names={'_gsf_probe_social_master','_gsf_ratio_float','_gsf_validate_social_master'}
nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
ns={'subprocess':subprocess,'shutil':shutil}
mod=ast.Module(body=nodes,type_ignores=[])
ast.fix_missing_locations(mod)
exec(compile(mod,str(p),'exec'),ns,ns)
validate=ns['_gsf_validate_social_master']

with tempfile.TemporaryDirectory() as td:
    td=Path(td)
    normal=td/'normal.mp4'
    cmd=[
        'ffmpeg','-hide_banner','-loglevel','error','-y',
        '-f','lavfi','-i','testsrc2=size=1080x1920:rate=30',
        '-f','lavfi','-i','sine=frequency=440:sample_rate=48000',
        '-t','0.6',
        '-c:v','libx264','-preset','ultrafast','-crf','20','-threads','2',
        '-profile:v','high','-level:v','4.2','-tag:v','avc1',
        '-pix_fmt','yuv420p',
        '-c:a','aac','-b:a','192k','-ar','48000','-ac','2',
        '-movflags','+faststart',str(normal)
    ]
    r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=60)
    need(r.returncode==0 and normal.exists(),'reference social MP4 renders')
    rep=validate(str(normal),'9:16 Short')
    need(rep.get('ok'),f'yuv420p validator passes: {rep.get("errors")}')

    # Unit-level alias check by replacing ffprobe response inside validator namespace.
    original_probe=ns['_gsf_probe_social_master']
    fake={
        'ok':True,
        'data':{
            'streams':[
                {'codec_type':'video','codec_name':'h264','codec_tag_string':'avc1',
                 'profile':'High','level':42,'pix_fmt':'yuvj420p',
                 'width':1080,'height':1920,'avg_frame_rate':'30/1','r_frame_rate':'30/1'},
                {'codec_type':'audio','codec_name':'aac','sample_rate':'48000','channels':2}
            ],
            'format':{'format_name':'mov,mp4,m4a,3gp,3g2,mj2','duration':'1.0','size':'1','bit_rate':'1'}
        }
    }
    ns['_gsf_probe_social_master']=lambda path: fake
    rep2=ns['_gsf_validate_social_master']('dummy.mp4','9:16 Short')
    need(rep2.get('ok'),f'yuvj420p compatibility alias passes: {rep2.get("errors")}')
    ns['_gsf_probe_social_master']=original_probe

print('V103.1 Clean Final regression: PASS')
