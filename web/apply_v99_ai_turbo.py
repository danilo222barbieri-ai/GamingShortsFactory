from pathlib import Path

src=Path('/app/GamingShortsFactory_V98_FINAL_6LANES.py')
out=Path('/app/GamingShortsFactory_V99_AI_TURBO.py')
s=src.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise RuntimeError(f'V99 target not found: {label}')
    s=s.replace(old,new,1)

# ------------------------------------------------------------
# V99 TURBO SCAN
# <=3 minutes keeps the proven dense profile.
# Longer gameplay scans only decoder keyframes globally, then restores
# local detail on a small shortlist. This avoids decoding every P/B frame
# of a long gameplay just to throw almost all of them away.
# ------------------------------------------------------------
replace_once(
'''    if total<=20*60:
        return {
            "tier":"medium",
            "video_fps":1.25,
            "analysis_width":160,
            "adaptive":False,
        }
    if total<=60*60:
        return {
            "tier":"long",
            "video_fps":0.75,
            "analysis_width":144,
            "adaptive":True,
        }
    return {
        "tier":"very_long",
        "video_fps":0.5,
        "analysis_width":144,
        "adaptive":True,
    }
''',
'''    if total<=20*60:
        return {
            "tier":"medium_turbo",
            "video_fps":0.5,
            "analysis_width":128,
            "adaptive":True,
            "keyframes_only":True,
        }
    if total<=60*60:
        return {
            "tier":"long_turbo",
            "video_fps":0.35,
            "analysis_width":112,
            "adaptive":True,
            "keyframes_only":True,
        }
    return {
        "tier":"very_long_turbo",
        "video_fps":0.25,
        "analysis_width":112,
        "adaptive":True,
        "keyframes_only":True,
    }
''',
'turbo scan profiles')

# Standard <=3min profile explicitly declares normal decode for diagnostics.
replace_once(
'''            "analysis_width":192,
            "adaptive":False,
        }
''',
'''            "analysis_width":192,
            "adaptive":False,
            "keyframes_only":False,
        }
''',
'standard decode flag')

# Same 0.5s audio windows, half the sample workload.
replace_once(
'''            "aresample=16000,asetnsamples=n=8000:p=0,"
''',
'''            "aresample=8000,asetnsamples=n=4000:p=0,"
''',
'light audio scan')

# Build the coarse video command dynamically. On gameplay >3 min the decoder
# discards non-keyframes BEFORE filtering, which is the big speed win.
replace_once(
'''    cmd_video=[
        FFMPEG_PATH,"-hide_banner","-threads","1","-i",str(input_file),"-an",
        "-vf",
        (
            f"fps={video_fps:g},scale={analysis_width}:-2,"
            "select='gte(scene,0)',metadata=print"
        ),
        "-f","null","-"
    ]
''',
'''    keyframes_only=bool(profile.get("keyframes_only",False))
    cmd_video=[FFMPEG_PATH,"-hide_banner","-threads","2"]
    if keyframes_only:
        cmd_video += ["-skip_frame","nokey"]
    cmd_video += ["-i",str(input_file),"-an","-vf"]
    if keyframes_only:
        cmd_video += [
            f"scale={analysis_width}:-2,"
            "select='gte(scene,0)',metadata=print"
        ]
    else:
        cmd_video += [
            f"fps={video_fps:g},scale={analysis_width}:-2,"
            "select='gte(scene,0)',metadata=print"
        ]
    cmd_video += ["-f","null","-"]
''',
'keyframe coarse video command')

replace_once(
'''        "analysis_width":analysis_width,
        "duration_seconds":round(total_seconds,2),
''',
'''        "analysis_width":analysis_width,
        "keyframes_only":keyframes_only,
        "duration_seconds":round(total_seconds,2),
''',
'keyframe diagnostics')

# Dense local refinement is still much richer than the keyframe scan, but lighter.
replace_once(
'''    Uses 3 fps / 160 px and returns a small visual-support signal.
''',
'''    Uses 2 fps / 144 px and returns a focused visual-support signal.
''',
'refine documentation')
replace_once(
'''"fps=3,scale=160:-2,select='gte(scene,0)',metadata=print",
''',
'''"fps=2,scale=144:-2,select='gte(scene,0)',metadata=print",
''',
'refine density')

# Adaptive scans do not need to score every possible starting second.
replace_once(
'''    for start in range(0,last_start+1):
''',
'''    candidate_stride=2 if adaptive_scan else 1
    for start in range(0,last_start+1,candidate_stride):
''',
'candidate stride')

# Six good windows are enough to choose three diverse clips.
replace_once(
'''    shortlist_target=8 if profile in ("auto","director","reaction") else 7
    coarse_target=shortlist_target+(3 if adaptive_scan else 0)
''',
'''    shortlist_target=6
    coarse_target=7 if adaptive_scan else shortlist_target
''',
'shortlist turbo size')

# New scan representation must never reuse V98 scan cache entries.
replace_once(
'''GSF_AI_ENGINE_VERSION = "v51-speed-adaptive"
''',
'''GSF_AI_ENGINE_VERSION = "v52-keyframe-turbo"
''',
'V99 engine cache version')

s=s.replace(
    'Gaming Shorts Factory · V98 FINAL 6LANES',
    'Gaming Shorts Factory · V99 AI Turbo'
)

out.write_text(s,encoding='utf-8')
print(f'V99 AI Turbo patch applied: {out}')
