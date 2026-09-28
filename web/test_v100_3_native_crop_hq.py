from pathlib import Path
import ast,subprocess,sys,tempfile,time

p=Path(sys.argv[1]); s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')
tree=ast.parse(s)

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

def load_funcs(names):
    by={n.name:n for n in tree.body if isinstance(n,ast.FunctionDef)}
    nodes=[by[n] for n in names]
    mod=ast.Module(body=nodes,type_ignores=[])
    ast.fix_missing_locations(mod)
    ns={}
    exec(compile(mod,str(p),'exec'),ns,ns)
    return ns

need('Gaming Shorts Factory · V100.3 Native Crop HQ' in s,'V100.3 marker')
need("crop=w='" in s and "scale=1080:1920:flags=lanczos" in s,'native crop then final upscale installed')
need('scale=-2:1920:flags=lanczos' not in ast.get_source_segment(
    s,next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_smart_reframe_filter')
),'old full-frame pre-scale removed')
need('unsharp=5:5:0.08:3:3:0.02' in s,'very light sharpening retained')

# Master encode and frozen contracts remain.
for marker in (
    '"libx264 Master"',
    '"-preset","slow"',
    '"-crf","13"',
    'GSF_SMART_REFRAME_VERSION = "v100-gameplay-safe"',
    'V100 gameplay-aware tracking',
    '"hud_suppression"',
    '"hook_top":0.17',
    '"subtitle_bottom":0.24',
    'gsf-mobile-preview-gap',
    'gsfUploadCapabilities',
    'GSF_AI_ENGINE_VERSION = "v52-keyframe-turbo"',
    'numero_clip=3',
    '((220,391,424) if vertical else (520,293,332))',
    '_profile="PLAYER 16:9"; _target_width=640; _max_vw="640px"; _cap=430',
):
    need(marker in s,f'preserved: {marker}')

ns=load_funcs([
    '_gsf_smooth_reframe_track',
    '_gsf_smart_reframe_cx_expression',
    '_gsf_smart_reframe_filter',
])
vf=ns['_gsf_smart_reframe_filter'](
    [
        {'t':0.0,'cx':0.50,'confidence':0.8},
        {'t':0.5,'cx':0.62,'confidence':0.8},
        {'t':1.0,'cx':0.70,'confidence':0.8},
    ],1.0,0
)

# Real filter test from 1920x1080.
cmd=[
    'ffmpeg','-hide_banner','-loglevel','error',
    '-f','lavfi','-i','testsrc2=size=1920x1080:rate=30',
    '-t','0.6','-vf',vf,'-f','null','-'
]
t0=time.perf_counter()
r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=45)
elapsed=time.perf_counter()-t0
need(r.returncode==0,'native-crop Smart Reframe executes in FFmpeg')
print(f'V100.3 native-crop filter smoke time: {elapsed:.3f}s')

# Verify zoom path also produces valid frames.
vf_zoom=ns['_gsf_smart_reframe_filter'](
    [{'t':0.0,'cx':0.5,'confidence':0.8},{'t':1.0,'cx':0.6,'confidence':0.8}],
    1.18,20
)
cmd2=[
    'ffmpeg','-hide_banner','-loglevel','error',
    '-f','lavfi','-i','testsrc2=size=1920x1080:rate=30',
    '-t','0.4','-vf',vf_zoom,'-f','null','-'
]
r2=subprocess.run(cmd2,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=45)
need(r2.returncode==0,'native-crop zoom/y-position path executes')

print('V100.3 Native Crop HQ regression: PASS')
