from pathlib import Path

src=Path('/app/GamingShortsFactory_V98_10_SPEED_PASS1.py')
out=Path('/app/GamingShortsFactory_V98_11_SPEED_ALL.py')
s=src.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise RuntimeError(f'V98.11 target not found: {label}')
    s=s.replace(old,new,1)

# ------------------------------------------------------------
# FAST FULL-SCAN PROFILES
# <=3 min keeps the original dense scan.
# 3-20 min: 1.25 fps / 160 px is plenty for coarse ranking and cuts decode work.
# Long gameplay becomes slightly sparser, then dense shortlist refinement restores detail.
# ------------------------------------------------------------
replace_once(
'''    if total<=20*60:
        return {
            "tier":"standard",
            "video_fps":2.0,
            "analysis_width":192,
            "adaptive":False,
        }
''',
'''    if total<=3*60:
        return {
            "tier":"standard",
            "video_fps":2.0,
            "analysis_width":192,
            "adaptive":False,
        }
    if total<=20*60:
        return {
            "tier":"medium",
            "video_fps":1.25,
            "analysis_width":160,
            "adaptive":False,
        }
''',
'medium scan profile')

replace_once(
'''            "video_fps":1.0,
            "analysis_width":160,
            "adaptive":True,
''',
'''            "video_fps":0.75,
            "analysis_width":144,
            "adaptive":True,
''',
'long scan profile')

# Let the two concurrent FFmpeg full-scan passes share the 2-vCPU Railway box cleanly.
replace_once(
'''        FFMPEG_PATH,"-hide_banner","-i",str(input_file),"-vn",
''',
'''        FFMPEG_PATH,"-hide_banner","-threads","1","-i",str(input_file),"-vn",
''',
'audio scan thread budget')
replace_once(
'''        FFMPEG_PATH,"-hide_banner","-i",str(input_file),"-an",
''',
'''        FFMPEG_PATH,"-hide_banner","-threads","1","-i",str(input_file),"-an",
''',
'video scan thread budget')

# Dense refinement: still detailed, but cheaper on long gameplay.
replace_once(
'''    Uses 4 fps / 192 px and returns a small visual-support signal.
''',
'''    Uses 3 fps / 160 px and returns a small visual-support signal.
''',
'refine doc')
replace_once(
'''        FFMPEG_PATH,"-hide_banner",
        "-ss",str(max(0.0,float(start))),
''',
'''        FFMPEG_PATH,"-hide_banner","-threads","1",
        "-ss",str(max(0.0,float(start))),
''',
'refine thread budget')
replace_once(
'''"fps=4,scale=192:-2,select='gte(scene,0)',metadata=print",
''',
'''"fps=3,scale=160:-2,select='gte(scene,0)',metadata=print",
''',
'refine visual density')

# Smaller shortlist is still ample for 3 final clips, but cuts expensive second-pass work.
replace_once(
'''    shortlist_target=10 if profile in ("auto","director","reaction") else 8
    coarse_target=shortlist_target+(4 if adaptive_scan else 0)
''',
'''    shortlist_target=8 if profile in ("auto","director","reaction") else 7
    coarse_target=shortlist_target+(3 if adaptive_scan else 0)
''',
'shortlist size')

# On a 2-vCPU container, two refine workers avoid FFmpeg oversubscription.
replace_once(
'''        workers=min(3,len(shortlist))
''',
'''        workers=min(2,len(shortlist))
''',
'refine workers')

# Reactions: analyze only the best 4 candidates semantically instead of 6.
replace_once(
'''            profile=="reaction" and len(enriched)<6
''',
'''            profile=="reaction" and len(enriched)<4
''',
'reaction voice shortlist')

# Voice extraction: remove expensive loudnorm; Whisper Tiny does not require mastering.
replace_once(
'''            "-af","highpass=f=70,lowpass=f=7800,loudnorm=I=-16:LRA=11:TP=-1.5",
''',
'''            "-af","highpass=f=70,lowpass=f=7800",
''',
'voice analysis audio filter')

# Web low-memory inference: greedy Tiny is much faster and sufficient for event cues.
replace_once(
'''            beam_size=2,best_of=2,condition_on_previous_text=False,
''',
'''            beam_size=(1 if GSF_LOW_MEMORY_WEB else 2),
            best_of=(1 if GSF_LOW_MEMORY_WEB else 2),
            condition_on_previous_text=False,
''',
'Whisper web beam size')

# Bump cache version so the new scan profile never reuses old-density results.
replace_once(
'''GSF_AI_ENGINE_VERSION = "v50-performance-final"
''',
'''GSF_AI_ENGINE_VERSION = "v51-speed-adaptive"
''',
'AI cache version')

s=s.replace(
    'Gaming Shorts Factory · V98.10 Speed Pass 1',
    'Gaming Shorts Factory · V98.11 Speed All'
)

out.write_text(s,encoding='utf-8')
print(f'V98.11 speed-all patch applied: {out}')
