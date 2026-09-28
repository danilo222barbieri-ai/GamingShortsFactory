from pathlib import Path
import ast,sys

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')
tree=ast.parse(s)

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

def load_func(name):
    node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name==name)
    mod=ast.Module(body=[node],type_ignores=[])
    ast.fix_missing_locations(mod)
    ns={}
    exec(compile(mod,str(p),'exec'),ns,ns)
    return ns[name]

need('Gaming Shorts Factory · V100 Smart Reframe' in s,'V100 marker')
need('GSF_SMART_REFRAME_VERSION = "v100-gameplay-safe"' in s,'V100 cache version')
need('gsf_smart_reframe_cache_v100' in s,'V100 dedicated reframe cache')
need('V100 gameplay-aware tracking' in s,'gameplay-aware analyzer installed')
need('"hud_suppression"' in s and '"hud_guard"' in s,'HUD suppression installed')
need('"hook_top":0.17' in s and '"subtitle_bottom":0.24' in s,'hook/subtitle safe zones installed')
need('dead_zone' in s and 'pending_count' in s,'dead-zone and hysteresis installed')
need('accel_limit' in s and 'velocity' in s,'velocity/acceleration damping installed')
need('cluster_share' in s and 'np.convolve' in s,'coherent subject cluster tracking installed')
need('target_aspect=9.0/16.0' in s and 'portrait_pressure' in s,'9:16-specific control installed')

smooth=load_func('_gsf_smooth_reframe_track')

# Nervous micro-jitter should barely move the camera.
jitter=[
 {'t':0.0,'cx':0.50,'confidence':0.55,'hud_guard':0.0},
 {'t':0.5,'cx':0.515,'confidence':0.50,'hud_guard':0.0},
 {'t':1.0,'cx':0.492,'confidence':0.52,'hud_guard':0.0},
 {'t':1.5,'cx':0.518,'confidence':0.48,'hud_guard':0.0},
 {'t':2.0,'cx':0.501,'confidence':0.55,'hud_guard':0.0},
]
sj=smooth(jitter)
need(max(abs(x['cx']-0.5) for x in sj)<0.035,'micro-jitter stays inside stable camera zone')

# One low-confidence HUD spike must not yank the crop.
hud=[
 {'t':0.0,'cx':0.50,'confidence':0.60,'hud_guard':0.0},
 {'t':0.5,'cx':0.50,'confidence':0.58,'hud_guard':0.0},
 {'t':1.0,'cx':0.86,'confidence':0.20,'hud_guard':0.65},
 {'t':1.5,'cx':0.51,'confidence':0.55,'hud_guard':0.0},
 {'t':2.0,'cx':0.50,'confidence':0.60,'hud_guard':0.0},
]
sh=smooth(hud)
need(max(abs(x['cx']-0.5) for x in sh)<0.09,'isolated HUD spike is rejected')

# Sustained confident motion must still be followed.
move=[
 {'t':0.0,'cx':0.50,'confidence':0.75,'hud_guard':0.0},
 {'t':0.5,'cx':0.58,'confidence':0.78,'hud_guard':0.0},
 {'t':1.0,'cx':0.66,'confidence':0.80,'hud_guard':0.0},
 {'t':1.5,'cx':0.74,'confidence':0.82,'hud_guard':0.0},
 {'t':2.0,'cx':0.78,'confidence':0.84,'hud_guard':0.0},
 {'t':2.5,'cx':0.79,'confidence':0.82,'hud_guard':0.0},
]
sm=smooth(move)
need(sm[-1]['cx']>0.64,'sustained subject motion is followed')
steps=[abs(sm[i]['cx']-sm[i-1]['cx']) for i in range(1,len(sm))]
need(max(steps)<0.15,'camera never makes a nervous crop jump')

# Frozen V98/V99 contracts.
need('gsfUploadCapabilities' in s,'V99 bucket architecture preserved')
need("'/direct-upload/bucket/init'" in s,'direct bucket upload preserved')
need('GSF_AI_ENGINE_VERSION = "v52-keyframe-turbo"' in s,'V99 AI engine frozen')
need('numero_clip=3' in s,'three AI clips preserved')
need('((220,391,424) if vertical else (520,293,332))' in s,'editor dimensions frozen')
need('_profile="PLAYER 16:9"; _target_width=640; _max_vw="640px"; _cap=430' in s,'main player frozen')
need('def _gsf_subtitle_groups' in s,'subtitle grouping preserved')
need('"-crf","21"' in s,'render quality preserved')
need('def _gsf_smart_reframe_filter(track,zoom=1.0,y_pos=0):' in s,'existing final crop renderer preserved')
print('V100 Smart Reframe regression: PASS')
