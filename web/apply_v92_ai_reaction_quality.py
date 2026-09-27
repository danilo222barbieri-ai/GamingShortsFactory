from pathlib import Path

src=Path('/app/GamingShortsFactory_V91_ROADMAP_POLISH.py')
out=Path('/app/GamingShortsFactory_V92_AI_REACTION_QUALITY.py')
s=src.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise RuntimeError(f'V92 patch target not found: {label}')
    s=s.replace(old,new,1)

replace_once(
'''def _gsf_ai_voice_cached(input_file, start, duration, cache_token=None):
''',
'''def _gsf_ai_voice_cached(input_file, start, duration, cache_token=None, force=False):
''',
'voice cache signature')

replace_once(
'''        round(float(duration), 2),
        str(st.session_state.get("gioco", "") or "")
    )
''',
'''        round(float(duration), 2),
        str(st.session_state.get("gioco", "") or ""),
        bool(force)
    )
''',
'voice cache force key')

replace_once(
'''    result = _gsf_ai_voice_features(input_file, start, duration)
''',
'''    result = _gsf_ai_voice_features(
        input_file, start, duration, force=force
    )
''',
'voice cache force call')

replace_once(
'''def _gsf_ai_voice_features(input_file,start,duration):
''',
'''def _gsf_ai_voice_features(input_file,start,duration,force=False):
''',
'voice feature signature')

replace_once(
'''    V78: nella beta web low-memory salta Whisper durante l'analisi iniziale;
    il ranking continua a usare audio, movimento, picchi e signal-event.
    """
    if not GSF_AI_VOICE_TRANSCRIPTION:
''',
'''    V92: nella beta web low-memory Whisper resta spento per i motori normali,
    ma il profilo Reazioni puo forzare Tiny SOLO sui migliori candidati.
    """
    if not GSF_AI_VOICE_TRANSCRIPTION and not bool(force):
''',
'voice low-memory forced mode')

replace_once(
'''    voice_cache_hits=0
    voice_checks=0
    refine_cache_hits=0
''',
'''    voice_cache_hits=0
    voice_checks=0
    forced_voice_checks=0
    refine_cache_hits=0
''',
'forced voice counter')

replace_once(
'''    for prelim,start,f in shortlist:
        f=dict(f)
        transcript=""
        _voice_result,_voice_hit=_gsf_ai_voice_cached(
            input_file,start,duration,cache_token=cache_token
        )
''',
'''    for prelim,start,f in shortlist:
        f=dict(f)
        transcript=""

        # V92: Reazioni deve davvero ascoltare la voce anche sul profilo web
        # low-memory. Limitiamo Whisper Tiny ai 6 candidati migliori: il primo
        # passaggio audio/video ha gia eliminato le zone deboli, quindi otteniamo
        # semantica e reazioni senza trascrivere inutilmente tutto il gameplay.
        _force_reaction_voice=bool(
            profile=="reaction" and len(enriched)<6
        )
        _voice_result,_voice_hit=_gsf_ai_voice_cached(
            input_file,start,duration,
            cache_token=cache_token,
            force=_force_reaction_voice
        )
        if _force_reaction_voice:
            forced_voice_checks+=1
''',
'reaction voice shortlist')

replace_once(
'''        "voice_cache_hits":int(voice_cache_hits),
        "voice_checks":int(voice_checks),
''',
'''        "voice_cache_hits":int(voice_cache_hits),
        "voice_checks":int(voice_checks),
        "forced_voice_checks":int(forced_voice_checks),
''',
'forced voice diagnostics')

# Small diversity polish: when two candidate windows overlap heavily,
# temporal overlap should matter a little more than feature similarity.
replace_once(
'''                    -0.10*worst_similarity
                    -0.24*worst_overlap
                    +category_bonus
''',
'''                    -0.10*worst_similarity
                    -0.29*worst_overlap
                    +category_bonus
''',
'diversity overlap weight')

replace_once(
'''                category_bonus=0.055 if this_category not in chosen_categories else -0.015
''',
'''                category_bonus=0.070 if this_category not in chosen_categories else -0.020
''',
'diversity category bonus')

s=s.replace(
    'Gaming Shorts Factory · V91 Roadmap Polish',
    'Gaming Shorts Factory · V92 AI Reaction Quality'
)

out.write_text(s,encoding='utf-8')
print(f'V92 patch applied: {out}')
