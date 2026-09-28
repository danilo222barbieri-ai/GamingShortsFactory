from pathlib import Path
import ast,subprocess,sys,tempfile

p=Path(sys.argv[1]); s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')
tree=ast.parse(s)

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_render_core')
core=ast.get_source_segment(s,node) or ''

need('Gaming Shorts Factory · V100.2 Master Quality' in s,'V100.2 marker')
need('"libx264 Master"' in core,'software master encoder is first choice')
need(core.index('"libx264 Master"') < core.index('"Intel QSV HQ fallback"'),'QSV moved to fallback')
need('"-preset","slow"' in core,'slow preset enabled')
need('"-crf","13"' in core,'near-master CRF13 enabled')
need('"-profile:v","high"' in core,'H.264 High profile enabled')
need('"-level:v","4.2"' in core,'H.264 level 4.2 enabled')
need('"-pix_fmt","yuv420p"' in core,'iPhone/social compatible pixel format')
need('"-b:a","192k"' in core,'AAC quality raised to 192k')
need('"-global_quality","14"' in core,'QSV fallback also raised to HQ')
need('"veryfast"' not in core,'veryfast final encode removed')
need('unsharp=5:5:0.10:3:3:0.03' in s,'sharpen reduced to avoid moving artifacts')

# Frozen architecture/intelligence/UI contracts.
for marker in (
    'GSF_SMART_REFRAME_VERSION = "v100-gameplay-safe"',
    'V100 gameplay-aware tracking',
    '"hud_suppression"',
    '"hook_top":0.17',
    '"subtitle_bottom":0.24',
    'gsf-mobile-preview-gap',
    'gsfUploadCapabilities',
    "GSF_AI_ENGINE_VERSION = \"v52-keyframe-turbo\"",
    'numero_clip=3',
    '((220,391,424) if vertical else (520,293,332))',
    '_profile="PLAYER 16:9"; _target_width=640; _max_vw="640px"; _cap=430',
):
    need(marker in s,f'preserved: {marker}')

# Real encoder smoke test with the exact master codec settings.
with tempfile.TemporaryDirectory() as td:
    out=Path(td)/'master.mp4'
    cmd=[
        'ffmpeg','-hide_banner','-loglevel','error','-y',
        '-f','lavfi','-i','testsrc2=size=1080x1920:rate=30',
        '-t','0.4',
        '-c:v','libx264','-preset','slow','-crf','13',
        '-profile:v','high','-level:v','4.2','-pix_fmt','yuv420p',
        '-an','-movflags','+faststart',str(out)
    ]
    r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=60)
    need(r.returncode==0 and out.exists() and out.stat().st_size>0,'real CRF13 slow master encode executes')

print('V100.2 Master Quality regression: PASS')
