from pathlib import Path
import ast,re,sys

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')
ast.parse(s)

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

# FINAL marker + uploader contract.
need('Gaming Shorts Factory · V98 FINAL' in s,'V98 FINAL marker')
need('const CHUNK=32*1024*1024;' in s,'32MB chunks')
need('const CONCURRENCY=4;' in s,'four parallel upload lanes')
need('uploadChunkWithRetry' in s and 'maxAttempts=3' in s,'per-lane retry')
need('xhr.timeout=180000' in s,'mobile-safe chunk timeout')
need('window.parent.location.reload()' not in s,'no hard browser refresh')
need('@st.fragment(run_every="0.35s")' in s,'automatic completion watcher')

# Editor acceptance: controls exist and the exact same session values feed the final recipe.
need('IN / OUT · ritaglio scena' in s,'IN/OUT control')
need('def render_gsf_editor_live_player' in s,'live editor preview')
need('inline_live_v32_' in s,'persistent editor player identity')
live_start=s.index('render_gsf_editor_live_player(')
live_end=s.index('with _side:',live_start)
live=s[live_start:live_end]
recipe_start=s.index('_inline_recipe=_gsf_recipe_selected',live_end)
recipe_end=s.index('_inline_recipe_selected=',recipe_start)
recipe=s[recipe_start:recipe_end]
for key in ('_zoom_key','_x_key','_y_key','_vol_key','_bri_key','_con_key','_spd_key'):
    need(key in live and key in recipe,f'preview/render shared state: {key}')
for marker in (
    '"zoom":st.session_state[_zoom_key]',
    '"x_pos":st.session_state[_x_key]',
    '"y_pos":st.session_state[_y_key]',
    '"brightness":st.session_state[_bri_key]',
    '"contrast":st.session_state[_con_key]',
    '"speed":st.session_state[_spd_key]',
    '"volume":st.session_state[_vol_key]',
):
    need(marker in recipe,f'final render recipe: {marker}')

# Approved UI/player dimensions are frozen.
need('((220,391,424) if vertical else (520,293,332))' in s,'editor player dimensions frozen')
need('_profile="PLAYER 16:9"; _target_width=640; _max_vw="640px"; _cap=430' in s,'main 16:9 player frozen')
need('width:208px;height:208px' in s,'mobile upload circle preserved')
need('CHIUDI EDITOR' not in s and 'CHIUDI' in s,'compact CHIUDI')
need('↶ RESET CONTROLLI' not in s and '↶ RESET' in s,'compact RESET')

# Product invariants.
need('numero_clip=3' in s,'three AI clips preserved')
need('GSF_AI_ENGINE_VERSION = "v51-speed-adaptive"' in s,'fast AI scan preserved')
need('def _gsf_smooth_reframe_track' in s,'Smart Reframe preserved')
need('def _gsf_subtitle_groups' in s,'subtitle grouping preserved')
need('"-crf","21"' in s,'final x264 quality preserved')
need('_legacy_seek=float(seek_target if seek_target is not None else start_seconds)' in s,'subtitle VAI preserved')
print('V98 FINAL application acceptance: PASS')
