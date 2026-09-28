from pathlib import Path
import ast,sys,tempfile,subprocess

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')
tree=ast.parse(s)

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

def load_functions(names):
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in set(names)]
    import re
    ns={"re":re}
    mod=ast.Module(body=nodes,type_ignores=[])
    ast.fix_missing_locations(mod)
    exec(compile(mod,str(p),'exec'),ns,ns)
    return ns

names=[
    '_gsf_hex_to_ass','_gsf_ass_time','_gsf_ass_escape',
    '_gsf_clean_burnin_text','_gsf_wrap_hook','_gsf_subtitle_groups',
    '_gsf_refine_subtitle_words','_gsf_subtitle_visual_units',
    '_gsf_subtitle_auto_size','_gsf_subtitle_safe_xy','_gsf_write_render_ass'
]
ns=load_functions(names)

need('Gaming Shorts Factory · V101 Subtitle Refinement' in s,'V101 marker')
need('Gaming Shorts Factory · V100.8 Fast Render' not in s,'V101 becomes production marker')
need('"-crf","14"' in s,'V100.8 render quality preserved')
need('"-preset","medium"' in s,'V100.8 medium preset preserved')
need('"-threads","2"' in s,'V100.8 render speed preserved')
need('Math.min(10,requestedConcurrency)' in s,'MAX Upload preserved')
need('GSF_SMART_REFRAME_VERSION = "v100-gameplay-safe"' in s,'Smart Reframe preserved')
need('numero_clip=3' in s,'three AI clips preserved')
need('editor_sub_font_v18' in s and 'subtitle_text_color_v18' in s,'existing manual subtitle personalization preserved')
need('subtitle_preset_v101' not in s,'no new subtitle style/preset control added')

refine=ns['_gsf_refine_subtitle_words']
words=refine([
    {'text':'prima','start':0.20,'end':0.46},
    {'text':'seconda','start':0.41,'end':0.72},
    {'text':'terza','start':0.70,'end':0.71},
])
need(all(words[i]['start']<=words[i+1]['start'] for i in range(len(words)-1)),'word starts normalized monotonically')
need(all(w['end']>=w['start']+.054 for w in words),'minimum readable word duration preserved')
need(words[0]['end']<=words[1]['start']+.001,'overlap handoff normalized for precise highlight')

autosize=ns['_gsf_subtitle_auto_size']
need(autosize(92,'wow','9:16 Short')==92,'short phrase keeps manual font size')
long_size=autosize(92,'questa è una frase molto lunga per uno short','9:16 Short')
need(24<=long_size<92,'long phrase shrinks automatically instead of overflowing')

safe=ns['_gsf_subtitle_safe_xy']
x,y=safe('9:16 Short',50,50,'test breve',92,1080,1920)
need(abs(x-540)<=2 and abs(y-960)<=2,'safe manual placement remains unchanged')
x2,y2=safe('9:16 Short',95,92,'test molto lungo sul lato destro',72,1080,1920)
need(x2<950 and y2<1500,'unsafe social-edge placement is clamped inward')

with tempfile.TemporaryDirectory() as td:
    ass=Path(td)/'subs.ass'
    ok=ns['_gsf_write_render_ass'](
        str(ass),
        [
            {'text':'ciao','start':0.00,'end':0.18},
            {'text':'mondo','start':0.34,'end':0.58},
            {'text':'gaming','start':0.60,'end':0.82},
        ],
        font='DejaVu Sans',size=92,x_pct=50,y_pct=78,
        text_color='#FFFFFF',active_color='#FFD400',outline_color='#000000',
        fmt='9:16 Short'
    )
    need(ok and ass.exists(),'V101 ASS renderer writes subtitle file')
    txt=ass.read_text(encoding='utf-8')
    need('Style: Default,DejaVu Sans,92' in txt,'manual font and base size remain authoritative')
    need('\\c' in txt,'current-word color highlight remains present')
    need(txt.count('Dialogue: 0')>=4,'precise word timing includes neutral inter-word gap')
    need('\\fs' in txt,'automatic fitted size emitted as ASS override')

    out=Path(td)/'subtitle_smoke.mp4'
    cmd=[
        'ffmpeg','-hide_banner','-loglevel','error','-y',
        '-f','lavfi','-i','color=c=black:s=1080x1920:r=30',
        '-t','0.9','-vf',f'ass={ass}',
        '-c:v','libx264','-preset','ultrafast','-crf','28','-an',str(out)
    ]
    r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=45)
    need(r.returncode==0 and out.exists() and out.stat().st_size>0,'real FFmpeg/libass V101 subtitle smoke render executes')

need('_preview_fs=_gsf_subtitle_auto_size' in s,'live preview uses the same automatic sizing logic')
need('_px,_py=_gsf_subtitle_safe_xy' in s,'live preview uses the same social safe-zone logic')

print('V101 Subtitle Refinement regression: PASS')
