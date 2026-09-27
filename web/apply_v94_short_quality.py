from pathlib import Path

src=Path('/app/GamingShortsFactory_V93_DEEP_STABILITY.py')
out=Path('/app/GamingShortsFactory_V94_SHORT_QUALITY.py')
s=src.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise RuntimeError(f'V94 patch target not found: {label}')
    s=s.replace(old,new,1)

# ------------------------------------------------------------
# V94 — Hooks: still conservative, but less generic and more useful on Shorts.
# We only name events already recognized by the AI diagnostics.
# ------------------------------------------------------------
replace_once(
'''_GSF_HOOK_TEMPLATES = {
    "goal": "GOOOL! ⚽",
    "shooter_elimination": "ELIMINAZIONE! 🎯",
    "victory": "VITTORIA! 🏆",
    "sports_big_chance": "CHE OCCASIONE! 🥅",
    "racing": "MOMENTO GARA! 🏎️",
    "achievement": "NUOVO TRAGUARDO! ⭐",
    "impact_event": "MOMENTO FORTE! 💥",
}

_GSF_CATEGORY_HOOKS = {
    "reaction": "REAZIONE! 🎙️",
    "action": "AZIONE! 🔥",
    "story": "MOMENTO! 🎬",
}
''',
'''_GSF_HOOK_TEMPLATES = {
    "goal": "CHE GOL! ⚽🔥",
    "shooter_elimination": "ELIMINATO! 🎯",
    "victory": "VITTORIA! 🏆",
    "sports_big_chance": "CHE OCCASIONE! 😱",
    "racing": "MOMENTO GARA! 🏎️🔥",
    "achievement": "SBLOCCATO! ⭐",
    "impact_event": "ECCO IL MOMENTO! 💥",
}

_GSF_CATEGORY_HOOKS = {
    "reaction": "CHE REAZIONE! 😱",
    "action": "AZIONE PURA! 🔥",
    "story": "ECCO IL MOMENTO! 🎬",
}
''',
'hook templates')

replace_once(
'''    category=str(features.get("moment_category","") or "")

    if event_score>=0.56 and event_type in _GSF_HOOK_TEMPLATES:
        return _GSF_HOOK_TEMPLATES[event_type]

    if category in _GSF_CATEGORY_HOOKS:
        return _GSF_CATEGORY_HOOKS[category]
''',
'''    category=str(features.get("moment_category","") or "")
    reaction=max(
        float(features.get("reaction",0.0)),
        float(features.get("reaction_cue",0.0)),
    )
    payoff=float(features.get("payoff_position",0.0))
    hook_score=float(features.get("hook_score",0.0))

    if event_score>=0.56 and event_type in _GSF_HOOK_TEMPLATES:
        return _GSF_HOOK_TEMPLATES[event_type]

    # A category hook is shown only when the underlying moment is strong enough.
    # This avoids stamping generic text over weak clips.
    if category=="reaction" and reaction>=0.34:
        return _GSF_CATEGORY_HOOKS["reaction"]
    if category=="action" and max(event_score,hook_score,payoff)>=0.38:
        return _GSF_CATEGORY_HOOKS["action"]
    if category=="story" and max(hook_score,payoff)>=0.42:
        return _GSF_CATEGORY_HOOKS["story"]
''',
'hook confidence gate')

# ------------------------------------------------------------
# V94 — Subtitles: phrase-aware groups instead of rigid groups of four.
# This reduces long lines, respects punctuation/silence and keeps the line
# continuously visible while the active word changes colour.
# ------------------------------------------------------------
anchor='''def _gsf_write_render_ass(
'''
helper='''def _gsf_subtitle_groups(words,max_words=4,max_chars=25,max_gap=0.58):
    groups=[]
    current=[]
    for item in (words or []):
        tx=str((item or {}).get("text","") or "").strip()
        if not tx:
            continue
        if current:
            joined=" ".join(
                str((w or {}).get("text","") or "").strip()
                for w in current+[item]
            ).strip()
            try:
                gap=float(item.get("start",0.0))-float(current[-1].get("end",0.0))
            except Exception:
                gap=0.0
            if len(current)>=int(max_words) or len(joined)>int(max_chars) or gap>float(max_gap):
                groups.append(current)
                current=[]
        current.append(item)
        if tx.endswith((".", "!", "?", "…")):
            groups.append(current)
            current=[]
    if current:
        groups.append(current)
    return groups


def _gsf_write_render_ass(
'''
replace_once(anchor,helper,'subtitle grouping helper')

start_marker='''    words=list(words or [])
    if words:
'''
end_marker='''    elif str(fallback_text or "").strip():
'''
start=s.find(start_marker)
end=s.find(end_marker,start)
if start<0 or end<0:
    raise RuntimeError('V94 subtitle render block not found')
new_block='''    words=list(words or [])
    if words:
        groups=_gsf_subtitle_groups(words)
        for group in groups:
            for local_idx,word in enumerate(group):
                parts=[]
                for j,item in enumerate(group):
                    tx=_gsf_ass_escape(item.get("text",""))
                    if j==local_idx:
                        parts.append(
                            r"{\\c"+active+r"\\b1}"+tx+
                            r"{\\c"+primary+r"\\b1}"
                        )
                    else:
                        parts.append(tx)
                line=" ".join(parts).strip()
                if not line:
                    continue
                a=float(word.get("start",0.0))
                own_end=max(a+.06,float(word.get("end",a+.16)))
                if local_idx+1<len(group):
                    try:
                        next_start=float(group[local_idx+1].get("start",own_end))
                    except Exception:
                        next_start=own_end
                    b=max(own_end,min(next_start,own_end+.22))
                else:
                    b=own_end+.10
                positioned=r"{\\an5\\pos("+str(x)+","+str(y)+r")}"+line
                ass+=(
                    f"Dialogue: 0,{_gsf_ass_time(a)},{_gsf_ass_time(b)},"
                    f"Default,,0,0,0,,{positioned}\\n"
                )
                wrote=True

'''
s=s[:start]+new_block+s[end:]

# ------------------------------------------------------------
# V94 — Smart Reframe: smooth/limit horizontal crop movement before FFmpeg
# interpolation. This removes nervous micro-pans without freezing real motion.
# ------------------------------------------------------------
old_start=s.find('def _gsf_smart_reframe_cx_expression(track):\n')
old_end=s.find('\ndef _gsf_smart_reframe_filter(',old_start)
if old_start<0 or old_end<0:
    raise RuntimeError('V94 smart reframe function not found')
new_reframe='''def _gsf_smooth_reframe_track(track):
    pts=[]
    for item in (track or []):
        try:
            pts.append({
                "t":float(item["t"]),
                "cx":max(0.10,min(0.90,float(item["cx"]))),
            })
        except Exception:
            continue
    pts=sorted(pts,key=lambda x:x["t"])
    if len(pts)<2:
        return pts

    out=[dict(pts[0])]
    prev=float(pts[0]["cx"])
    for item in pts[1:]:
        raw=float(item["cx"])
        delta=max(-0.22,min(0.22,raw-prev))
        alpha=0.64 if abs(delta)>=0.08 else 0.36
        smooth=prev+delta*alpha
        smooth=max(0.10,min(0.90,smooth))
        out.append({"t":float(item["t"]),"cx":smooth})
        prev=smooth
    return out


def _gsf_smart_reframe_cx_expression(track):
    """Smooth piecewise-linear normalized horizontal center for FFmpeg crop."""
    pts=[]
    for item in _gsf_smooth_reframe_track(track):
        try:
            pts.append((float(item["t"]),float(item["cx"])))
        except Exception:
            continue

    if not pts:
        return "0.5"

    pts=sorted(pts,key=lambda x:x[0])
    if len(pts)==1:
        return f"{pts[0][1]:.6f}"

    expr=f"{pts[-1][1]:.6f}"
    for i in range(len(pts)-2,-1,-1):
        t0,c0=pts[i]
        t1,c1=pts[i+1]
        dt=max(.001,t1-t0)
        segment=(
            f"({c0:.6f}+({c1-c0:.6f})*"
            f"(t-{t0:.3f})/{dt:.3f})"
        )
        expr=f"if(lt(t,{t1:.3f}),{segment},{expr})"
    return expr

'''
s=s[:old_start]+new_reframe+s[old_end+1:]

# ------------------------------------------------------------
# V94 — Selection quality: give more weight to a complete, publishable arc and
# slightly stronger penalties to dead/isolated windows.
# ------------------------------------------------------------
replacements=[
('''            0.27*f["motion_avg"]+
            0.14*f["motion_peak"]+
            0.12*f["motion_burst"]+
            0.11*f["active_ratio"]+
            0.07*f["audio_avg"]+
            0.07*f["synergy"]+
            0.06*hook+
            0.05*payoff+
            0.09*event_score+
            0.08*short_score-
            0.25*dead-
            0.16*dead_streak
''','''            0.24*f["motion_avg"]+
            0.12*f["motion_peak"]+
            0.10*f["motion_burst"]+
            0.10*f["active_ratio"]+
            0.06*f["audio_avg"]+
            0.07*f["synergy"]+
            0.08*hook+
            0.07*payoff+
            0.10*event_score+
            0.14*short_score-
            0.28*dead-
            0.18*dead_streak
''','action quality weights'),
('''            0.22*reaction+
            0.15*speech+
            0.16*f["audio_burst"]+
            0.11*reaction_cue+
            0.07*f["audio_peak"]+
            0.07*f["synergy"]+
            0.03*f["motion_avg"]+
            0.03*hook+
            0.03*payoff+
            0.10*event_score+
            0.08*short_score-
            0.22*dead-
            0.12*dead_streak
''','''            0.22*reaction+
            0.14*speech+
            0.14*f["audio_burst"]+
            0.12*reaction_cue+
            0.06*f["audio_peak"]+
            0.06*f["synergy"]+
            0.02*f["motion_avg"]+
            0.06*hook+
            0.06*payoff+
            0.10*event_score+
            0.14*short_score-
            0.25*dead-
            0.14*dead_streak
''','reaction quality weights'),
('''            0.21*f["arc"]+
            0.12*f["center_peak"]+
            0.10*f["activity_avg"]+
            0.08*f["synergy"]+
            0.08*f["active_ratio"]+
            0.08*hook+
            0.08*payoff+
            0.06*speech+
            0.04*reaction+
            0.03*f["motion_avg"]+
            0.12*event_score+
            0.10*short_score-
            0.24*dead-
            0.15*dead_streak
''','''            0.20*f["arc"]+
            0.10*f["center_peak"]+
            0.08*f["activity_avg"]+
            0.07*f["synergy"]+
            0.06*f["active_ratio"]+
            0.10*hook+
            0.10*payoff+
            0.04*speech+
            0.04*reaction+
            0.02*f["motion_avg"]+
            0.12*event_score+
            0.16*short_score-
            0.27*dead-
            0.17*dead_streak
''','director quality weights'),
('''            0.14*f["activity_avg"]+
            0.10*f["activity_peak"]+
            0.10*f["motion_avg"]+
            0.08*f["audio_avg"]+
            0.08*f["synergy"]+
            0.07*f["active_ratio"]+
            0.07*hook+
            0.06*payoff+
            0.05*speech+
            0.05*reaction+
            0.04*f["arc"]+
            0.02*reaction_cue+
            0.14*event_score+
            0.10*short_score-
            0.25*dead-
            0.15*dead_streak
''','''            0.12*f["activity_avg"]+
            0.08*f["activity_peak"]+
            0.08*f["motion_avg"]+
            0.06*f["audio_avg"]+
            0.07*f["synergy"]+
            0.06*f["active_ratio"]+
            0.09*hook+
            0.08*payoff+
            0.04*speech+
            0.05*reaction+
            0.05*f["arc"]+
            0.03*reaction_cue+
            0.14*event_score+
            0.15*short_score-
            0.28*dead-
            0.17*dead_streak
''','auto quality weights'),
]
for old,new,label in replacements:
    replace_once(old,new,label)

# Slightly better final visual quality without changing resolution/player logic.
replace_once('''"-global_quality","23",''','''"-global_quality","21",''','QSV quality')
replace_once('''"-crf","22",''','''"-crf","21",''','x264 quality')

s=s.replace(
    'Gaming Shorts Factory · V93 Deep Stability',
    'Gaming Shorts Factory · V94 Short Quality'
)

out.write_text(s,encoding='utf-8')
print(f'V94 patch applied: {out}')
