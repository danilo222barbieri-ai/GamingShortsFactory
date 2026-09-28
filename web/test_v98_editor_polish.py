from pathlib import Path
import ast,sys,re

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')
ast.parse(s)

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

need('Gaming Shorts Factory · V98 Editor Polish' in s,'V98 marker')
need('IN / OUT · ritaglio scena' in s,'clear IN/OUT label')
need('DURATA {_ilen:.1f}s' in s,'live trim duration summary')
need('↶ RESET CONTROLLI' in s,'reset language is scoped to controls')
need('ANTEPRIMA LIVE · queste regolazioni sono le stesse usate dal render finale.' in s,'preview/render contract shown to user')
need('st.columns([.34,.33,.33],gap="medium")' in s,'editor controls have more breathing room')
need('Zoom e posizione vengono applicati identici al render.' in s,'framing help present')
need('Audio, immagine e velocità restano sincronizzati con la preview.' in s,'adjustment help present')

need('def render_gsf_editor_live_player' in s,'approved live player preserved')
need('inline_live_v32_' in s,'persistent inline player identity preserved')

live_start=s.index('render_gsf_editor_live_player(')
live_end=s.index('with _side:',live_start)
live=s[live_start:live_end]
recipe_start=s.index('_inline_recipe=_gsf_recipe_selected',live_end)
recipe_end=s.index('_inline_recipe_selected=',recipe_start)
recipe=s[recipe_start:recipe_end]
for key in ('_zoom_key','_x_key','_y_key','_vol_key','_bri_key','_con_key','_spd_key'):
    need(key in live and key in recipe,f'preview/render mapping preserved: {key}')

for marker in (
    '"zoom":st.session_state[_zoom_key]',
    '"x_pos":st.session_state[_x_key]',
    '"y_pos":st.session_state[_y_key]',
    '"brightness":st.session_state[_bri_key]',
    '"contrast":st.session_state[_con_key]',
    '"speed":st.session_state[_spd_key]',
    '"volume":st.session_state[_vol_key]',
):
    need(marker in recipe,f'final recipe mapping: {marker}')

m=re.search(r'def _gsf_reset_inline_all\([^\n]+\):\n(?P<body>(?:    .*\n)+)',s)
need(m is not None,'inline reset function exists')
reset_body=m.group('body')
need('inline_trans_words' not in reset_body and 'inline_trans_text' not in reset_body,'reset preserves transcription')
need('auto_clip_scelta' not in reset_body and 'inline_editor_id' not in reset_body,'reset preserves selected clip/editor')

need('numero_clip=3' in s,'three AI clips unchanged')
need('def _gsf_smooth_reframe_track' in s,'Smart Reframe smoothing preserved')
need('def _gsf_subtitle_groups' in s,'subtitle grouping preserved')
need('"-crf","21"' in s,'final x264 quality preserved')
need('gsf-v89-upload-visual' in s,'approved upload circle preserved')
print('V98 editor polish regression: PASS')
