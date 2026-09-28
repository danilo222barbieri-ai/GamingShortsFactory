from pathlib import Path
import ast,sys,tempfile,subprocess,re,os

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')
tree=ast.parse(s)

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

def load_functions(names,extra=None):
    nodes=[n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name in set(names)]
    ns={"re":re}
    if extra: ns.update(extra)
    mod=ast.Module(body=nodes,type_ignores=[])
    ast.fix_missing_locations(mod)
    exec(compile(mod,str(p),'exec'),ns,ns)
    return ns

need('Gaming Shorts Factory · V102 Smart Hook' in s,'V102 marker')
need('Gaming Shorts Factory · V101 Subtitle Refinement' not in s,'V102 becomes production marker')
need('"-crf","14"' in s and '"-threads","2"' in s,'V100.8 final quality/speed preserved')
need('_gsf_refine_subtitle_words' in s and '_gsf_subtitle_auto_size' in s,'V101 subtitle refinement preserved')
need('Math.min(10,requestedConcurrency)' in s,'MAX Upload preserved')
need('GSF_SMART_REFRAME_VERSION = "v100-gameplay-safe"' in s,'Smart Reframe preserved')
need('numero_clip=3' in s,'three AI clips preserved')

# Hook decision logic: manual, explicit OFF, strong event, spoken content, no generic fallback.
ns=load_functions(
    ['_gsf_clean_burnin_text','_gsf_hook_transcript_excerpt','_gsf_hook_from_diag'],
    {
        '_GSF_HOOK_OFF_V102':'__GSF_HOOK_OFF_V102__',
        '_GSF_HOOK_TEMPLATES':{
            'goal':'CHE GOL!','shooter_elimination':'ELIMINATO!',
            'victory':'VITTORIA!','sports_big_chance':'CHE OCCASIONE!',
            'racing':'MOMENTO GARA!','achievement':'SBLOCCATO!',
            'impact_event':'ECCO IL MOMENTO!'
        }
    }
)
hook=ns['_gsf_hook_from_diag']
need(hook({},manual_hook='Mia frase')=='Mia frase','manual hook always wins')
need(hook({},manual_hook='__GSF_HOOK_OFF_V102__')=='','explicit OFF suppresses automatic hook')
need(hook({'features':{'event_type':'goal','event_score':.78}})=='CHE GOL!','strong detected event selects content hook')
need(hook({'features':{'moment_category':'action','event_score':.1,'hook_score':.6,'payoff_position':1.0}})=='','strong action alone no longer creates generic copy')
spoken=hook({
    'transcript':'Ma hai visto cosa è successo?!',
    'features':{'moment_category':'reaction','reaction':.72,'hook_score':.58,'speech':.70}
})
need('visto' in spoken.lower() and 'successo' in spoken.lower(),'real spoken reaction can become contextual hook')
_hook_src=ast.get_source_segment(s,next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_hook_from_diag')) or ''
need('_GSF_CATEGORY_HOOKS[' not in _hook_src,'generic category fallback removed')

# UI + state contract.
need('st.toggle(\n                "Hook"' in s,'Hook ON/OFF control installed')
need('st.text_input(\n                "Testo hook"' in s,'Hook manual edit installed')
need('max_chars=70' in s,'manual hook length bounded')
need('st.session_state["hook_testo"]=_v102_effective' in s,'single hook text state synchronized')
need('_GSF_HOOK_OFF_V102' in s,'OFF state survives auto-render path')
need('_v102_kw["hook_text"]=_v102_recipe_hook' in s,'Editor recipes receive same hook text')
need('_final_recipe["manual_hook"]=_v102_recipe_hook' in s,'AI recipe receives same hook text')
need('st.session_state.pop(_k,None)' in s and '"publication_final_bytes"' in s,'changing hook invalidates stale final render')

# Preview parity uses the exact ASS renderer rather than a CSS approximation.
preview_node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_v102_hook_preview_bytes')
preview_src=ast.get_source_segment(s,preview_node) or ''
need('_gsf_write_render_ass(' in preview_src,'preview uses same ASS writer as final render')
need('hook_y_pct=15' in preview_src,'preview uses same hook vertical position')
need('min(2.0,max(1.15,float(duration)*0.12))' in preview_src,'preview uses same hook duration formula')
need('"-fpsmax","60"' in preview_src,'preview inherits FPS safety')
need('_gsf_v71_render_mini_player(' in s,'preview reuses existing mini-player system')

# Real libass hook smoke using the production ASS writer.
names=[
    '_gsf_hex_to_ass','_gsf_ass_time','_gsf_ass_escape',
    '_gsf_clean_burnin_text','_gsf_wrap_hook','_gsf_subtitle_groups',
    '_gsf_refine_subtitle_words','_gsf_subtitle_visual_units',
    '_gsf_subtitle_auto_size','_gsf_subtitle_safe_xy','_gsf_write_render_ass'
]
assns=load_functions(names)
with tempfile.TemporaryDirectory() as td:
    ass=Path(td)/'hook.ass'
    ok=assns['_gsf_write_render_ass'](
        str(ass),[],fallback_text='',fmt='9:16 Short',
        hook_text='CHE GOL!',hook_duration=1.8,hook_y_pct=15
    )
    need(ok and ass.exists(),'production ASS writer accepts hook-only preview')
    txt=ass.read_text(encoding='utf-8')
    need('CHE GOL!' in txt and 'Dialogue: 2,0:00:00.00,0:00:01.80' in txt,'hook timing is encoded exactly')
    out=Path(td)/'hook_smoke.mp4'
    cmd=[
        'ffmpeg','-hide_banner','-loglevel','error','-y',
        '-f','lavfi','-i','color=c=black:s=540x960:r=30',
        '-t','2.0','-vf',f'ass={ass}',
        '-c:v','libx264','-preset','ultrafast','-crf','28','-an',str(out)
    ]
    r=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,timeout=45)
    need(r.returncode==0 and out.exists() and out.stat().st_size>0,'real FFmpeg/libass V102 hook render executes')

print('V102 Smart Hook regression: PASS')
