from pathlib import Path
import ast,sys,re,math

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')
tree=ast.parse(s)

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

def load_func(name,extra=None):
    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
    mod=ast.Module(body=[node],type_ignores=[])
    ast.fix_missing_locations(mod)
    ns={}
    if extra:
        ns.update(extra)
    exec(compile(mod,str(p),'exec'),ns,ns)
    return ns[name]

need('Gaming Shorts Factory · V94 Short Quality' in s,'V94 marker')
need('numero_clip=3' in s,'three AI clips unchanged')
need('key="upload_v73"' in s,'stable uploader untouched')
need('gsf-v89-upload-visual' in s,'approved upload circle untouched')
need('"-crf","21"' in s,'final x264 quality raised')
need('"-global_quality","21"' in s,'QSV quality raised')

groups=load_func('_gsf_subtitle_groups')
words=[
    {'text':'questa','start':0.0,'end':0.2},
    {'text':'è','start':0.22,'end':0.35},
    {'text':'una','start':0.36,'end':0.5},
    {'text':'frase','start':0.51,'end':0.7},
    {'text':'lunghissima','start':0.71,'end':0.95},
    {'text':'wow!','start':1.0,'end':1.2},
    {'text':'poi','start':2.0,'end':2.2},
]
g=groups(words)
need(len(g)>=3,'subtitle grouping reacts to length/punctuation/gaps')
need(all(len(x)<=4 for x in g),'subtitle groups never exceed four words')
need(any(str(x[-1]['text']).endswith('!') for x in g),'punctuation closes subtitle phrase')

smooth=load_func('_gsf_smooth_reframe_track')
track=[{'t':0,'cx':0.50},{'t':1,'cx':0.82},{'t':2,'cx':0.42},{'t':3,'cx':0.78},{'t':4,'cx':0.55}]
sm=smooth(track)
raw_steps=[abs(track[i]['cx']-track[i-1]['cx']) for i in range(1,len(track))]
sm_steps=[abs(sm[i]['cx']-sm[i-1]['cx']) for i in range(1,len(sm))]
need(max(sm_steps)<max(raw_steps),'smart reframe damps violent crop jumps')
need(all(0.10<=x['cx']<=0.90 for x in sm),'smart reframe stays in safe horizontal bounds')

score=load_func('_gsf_score_ai_window')
base={
 'dead_ratio':0.05,'dead_streak_ratio':0.02,'speech':0.1,'reaction':0.1,
 'hook_score':0.2,'payoff_position':0.2,'reaction_cue':0.1,'event_score':0.2,
 'short_worthiness':0.2,'motion_avg':0.2,'motion_peak':0.2,'motion_burst':0.2,
 'active_ratio':0.3,'audio_avg':0.2,'audio_burst':0.2,'audio_peak':0.2,
 'synergy':0.2,'arc':0.2,'center_peak':0.2,'activity_avg':0.2,'activity_peak':0.2,
}
publishable=dict(base,short_worthiness=0.9,hook_score=0.75,payoff_position=0.8,event_score=0.65,dead_ratio=0.02,dead_streak_ratio=0.0)
dead=dict(base,short_worthiness=0.12,hook_score=0.05,payoff_position=0.05,dead_ratio=0.8,dead_streak_ratio=0.7)
for profile in ('auto','action','reaction','director'):
    need(score(profile,publishable)>score(profile,dead),f'{profile} prefers complete publishable moment over dead window')

reaction_rich=dict(base,reaction=0.95,reaction_cue=0.9,speech=0.8,audio_burst=0.85,short_worthiness=0.7)
motion_only=dict(base,motion_avg=0.95,motion_peak=0.9,motion_burst=0.9,active_ratio=0.9,short_worthiness=0.45)
need(score('reaction',reaction_rich)>score('reaction',motion_only),'Reazioni still favors reaction-rich window')
need(score('action',motion_only)>score('action',reaction_rich),'Più azione still favors motion-rich window')

need('CHE REAZIONE! 😱' in s and 'AZIONE PURA! 🔥' in s,'stronger conservative hooks installed')
print('V94 short quality regression: PASS')
