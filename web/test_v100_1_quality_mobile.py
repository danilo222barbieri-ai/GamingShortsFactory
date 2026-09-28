from pathlib import Path
import ast,sys,subprocess,tempfile

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')
tree=ast.parse(s)

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

def load_funcs(names):
    nodes=[]
    by={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
    for name in names:
        if name not in by:
            raise AssertionError('missing function '+name)
        nodes.append(by[name])
    mod=ast.Module(body=nodes,type_ignores=[])
    ast.fix_missing_locations(mod)
    ns={}
    exec(compile(mod,str(p),'exec'),ns,ns)
    return ns

need('Gaming Shorts Factory · V100.1 Quality + Mobile Preview' in s,'V100.1 marker')
need('flags=lanczos+accurate_rnd+full_chroma_int' in s,'Lanczos HQ scaling installed')
need('unsharp=5:5:0.22:3:3:0.08' in s,'subtle post-scale sharpening installed')
need('"-crf","18"' in s,'x264 final quality raised to CRF18')
need('"-global_quality","18"' in s,'QSV final quality raised to 18')
need('gsf-mobile-preview-gap' in s,'mobile Anteprima spacer installed')
need('@media (max-width:768px)' in s and 'height:12px' in s,'mobile spacer is 12px')
need(s.count('gsf-mobile-preview-gap')>=2,'preview spacer style and marker both present')

# V100 intelligence remains frozen.
for marker in (
    'GSF_SMART_REFRAME_VERSION = "v100-gameplay-safe"',
    'V100 gameplay-aware tracking',
    '"hud_suppression"',
    '"hook_top":0.17',
    '"subtitle_bottom":0.24',
    'dead_zone',
    'pending_count',
    'accel_limit',
    'cluster_share',
):
    need(marker in s,f'V100 tracking preserved: {marker}')

# V98/V99 UI/architecture contracts remain untouched.
need('gsfUploadCapabilities' in s,'V99 bucket architecture preserved')
need("'/direct-upload/bucket/init'" in s,'direct bucket upload preserved')
need('GSF_AI_ENGINE_VERSION = "v52-keyframe-turbo"' in s,'V99 AI engine frozen')
need('numero_clip=3' in s,'three AI clips preserved')
need('((220,391,424) if vertical else (520,293,332))' in s,'editor dimensions frozen')
need('_profile="PLAYER 16:9"; _target_width=640; _max_vw="640px"; _cap=430' in s,'main player dimensions frozen')
need('def _gsf_subtitle_groups' in s,'subtitle grouping preserved')

# Exercise the actual V100.1 FFmpeg filter on a synthetic 1080p gameplay frame.
ns=load_funcs([
    '_gsf_smooth_reframe_track',
    '_gsf_smart_reframe_cx_expression',
    '_gsf_smart_reframe_filter',
])
vf=ns['_gsf_smart_reframe_filter'](
    [
        {'t':0.0,'cx':0.50,'confidence':0.8},
        {'t':0.5,'cx':0.60,'confidence':0.8},
        {'t':1.0,'cx':0.68,'confidence':0.8},
    ],
    1.0,0
)
cmd=[
    'ffmpeg','-hide_banner','-loglevel','error',
    '-f','lavfi','-i','testsrc2=size=1920x1080:rate=10',
    '-t','0.5','-vf',vf,'-f','null','-'
]
r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=45)
need(r.returncode==0,'V100.1 HQ Smart Reframe filter executes in FFmpeg')
if r.returncode!=0:
    print(r.stderr)

print('V100.1 quality/mobile regression: PASS')
