from pathlib import Path
import ast,sys,tempfile,subprocess,json,re,os

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')
tree=ast.parse(s)

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

core_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_render_core')
core=ast.get_source_segment(s,core_node) or ''
audio_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_render_audio_filter')
audio_src=ast.get_source_segment(s,audio_node) or ''

need('Gaming Shorts Factory · V103 Final Quality' in s,'V103 marker')
need('"-crf","14"' in core,'CRF14 master quality preserved')
need('"-preset","medium"' in core,'medium preset preserved')
need('"-threads","2"' in core,'two-thread render preserved')
need('rc-lookahead=16:ref=2:bframes=2' in core,'memory bounds preserved')
need('"-profile:v","high"' in core and '"-level:v","4.2"' in core,'H.264 High 4.2 preserved')
need('"-tag:v","avc1"' in core,'avc1 compatibility tag enforced')
need('"-pix_fmt","yuv420p"' in core,'social pixel format enforced')
need('"-fpsmax","60"' in core,'social frame-rate ceiling enforced')
need('"-c:a","aac","-b:a","192k"' in core,'AAC 192k preserved')
need('"-ar","48000"' in core and '"-ac","2"' in core,'48kHz stereo standardized')
need('"-movflags","+faststart"' in core,'faststart preserved')
need('"rotate=0"' in core,'rotation metadata normalized')
need('loudnorm=I=-14:LRA=9:TP=-1.5' in audio_src,'-14 LUFS loudness normalization preserved')
need('alimiter=limit=0.95:attack=5:release=50' in audio_src,'true-peak safety limiter preserved')
need('_gsf_validate_social_master(output_path,fmt=fmt)' in core,'post-render social compatibility gate installed')

# Regression guards from V100/V101/V102.
need('GSF_SMART_REFRAME_VERSION = "v100-gameplay-safe"' in s,'Smart Reframe preserved')
need('_gsf_refine_subtitle_words' in s,'V101 subtitle timing preserved')
need('_GSF_HOOK_OFF_V102' in s and '_gsf_v102_hook_preview_bytes' in s,'V102 Smart Hook preserved')
need('Math.min(10,requestedConcurrency)' in s,'MAX Upload preserved')
need('numero_clip=3' in s,'three AI clips preserved')

# Load validator helpers directly.
names={'_gsf_probe_social_master','_gsf_ratio_float','_gsf_validate_social_master'}
nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in names]
ns={'subprocess':subprocess,'shutil':__import__('shutil')}
mod=ast.Module(body=nodes,type_ignores=[])
ast.fix_missing_locations(mod)
exec(compile(mod,str(p),'exec'),ns,ns)
validate=ns['_gsf_validate_social_master']

with tempfile.TemporaryDirectory() as td:
    td=Path(td)
    master=td/'master.mp4'
    audio_filter='loudnorm=I=-14:LRA=9:TP=-1.5,volume=1.0000,alimiter=limit=0.95:attack=5:release=50,afade=t=in:st=0:d=0.0450,afade=t=out:st=0.9150:d=0.0850'
    cmd=[
        'ffmpeg','-hide_banner','-loglevel','error','-y',
        '-f','lavfi','-i','testsrc2=size=1080x1920:rate=60',
        '-f','lavfi','-i','sine=frequency=880:sample_rate=44100',
        '-t','1',
        '-vf','format=yuv420p',
        '-af',audio_filter,
        '-c:v','libx264','-preset','medium','-crf','14','-threads','2',
        '-x264-params','rc-lookahead=16:ref=2:bframes=2',
        '-profile:v','high','-level:v','4.2','-tag:v','avc1',
        '-pix_fmt','yuv420p','-fpsmax','60',
        '-c:a','aac','-b:a','192k','-ar','48000','-ac','2',
        '-metadata:s:v:0','rotate=0','-movflags','+faststart',str(master)
    ]
    r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=120)
    need(r.returncode==0 and master.exists() and master.stat().st_size>0,'real V103 1080x1920 H.264/AAC master renders')

    report=validate(str(master),'9:16 Short')
    need(report.get('ok'),f'social compatibility validator passes: {report.get("errors")}')
    v=report.get('video') or {}
    a=report.get('audio') or {}
    need((v.get('width'),v.get('height'))==(1080,1920),'master is exactly 1080x1920')
    need(v.get('codec')=='h264' and v.get('tag')=='avc1' and v.get('pix_fmt')=='yuv420p','master video is H.264 avc1 yuv420p')
    need(float(v.get('fps') or 0)<=60.05,'master fps is social-safe')
    need(a.get('codec')=='aac' and str(a.get('sample_rate'))=='48000' and int(a.get('channels') or 0)==2,'master audio is AAC 48kHz stereo')

    # Verify output loudness is near the intended social target.
    lr=subprocess.run([
        'ffmpeg','-hide_banner','-nostats','-i',str(master),
        '-vn','-af','loudnorm=I=-14:LRA=9:TP=-1.5:print_format=json',
        '-f','null','-'
    ],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=30)
    m=re.findall(r'"input_i"\s*:\s*"(-?[0-9.]+)"',lr.stderr or '')
    need(bool(m),'loudness analysis returns integrated LUFS')
    measured=float(m[-1])
    need(-16.5<=measured<=-11.5,f'normalized audio is near -14 LUFS ({measured:.1f})')

    # Quality-vs-size benchmark: CRF14 is intentionally retained over a smaller CRF18 master.
    source=td/'quality_source.mkv'
    r=subprocess.run([
        'ffmpeg','-hide_banner','-loglevel','error','-y',
        '-f','lavfi','-i','testsrc2=size=540x960:rate=30',
        '-t','0.8','-c:v','ffv1','-threads','2',str(source)
    ],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=45)
    need(r.returncode==0,'lossless benchmark source created')

    scores={}
    sizes={}
    for crf in (14,18):
        out=td/f'crf{crf}.mp4'
        r=subprocess.run([
            'ffmpeg','-hide_banner','-loglevel','error','-y','-i',str(source),
            '-c:v','libx264','-preset','medium','-crf',str(crf),'-threads','2',
            '-x264-params','rc-lookahead=16:ref=2:bframes=2',
            '-pix_fmt','yuv420p','-an',str(out)
        ],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=60)
        need(r.returncode==0 and out.exists(),'CRF%d benchmark encode created'%crf)
        sizes[crf]=out.stat().st_size
        q=subprocess.run([
            'ffmpeg','-hide_banner','-i',str(out),'-i',str(source),
            '-lavfi','[0:v][1:v]ssim','-f','null','-'
        ],stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=30)
        mm=re.findall(r'All:([0-9.]+)',q.stderr or '')
        need(bool(mm),'CRF%d SSIM measured'%crf)
        scores[crf]=float(mm[-1])

    need(sizes[14]>=sizes[18],'CRF14 correctly spends more bytes than CRF18')
    need(scores[14]>=scores[18]-0.0005,'CRF14 preserves at least as much visual detail as CRF18')
    print(f'BENCHMARK: CRF14={sizes[14]} bytes SSIM={scores[14]:.6f} | CRF18={sizes[18]} bytes SSIM={scores[18]:.6f}')

print('V103 Final Quality regression: PASS')
