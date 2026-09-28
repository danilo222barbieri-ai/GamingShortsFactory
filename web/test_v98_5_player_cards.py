from pathlib import Path
import sys

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

need('Gaming Shorts Factory · V98.5 Player Cards' in s,'V98.5 marker')

# Main preview: only 16:9 reduced to 640x360.
need('_profile="PLAYER 16:9"; _target_width=640; _max_vw="640px"; _cap=430' in s,'main 16:9 preview reduced to 640px')
need('_profile="PLAYER 9:16"; _target_width=300; _max_vw="300px"; _cap=680' in s,'vertical main preview unchanged')
need('_target_width=800; _max_vw="800px"' not in s,'old 800px main preview removed')

# Editor: 9:16 untouched; 16:9 enlarged to 560x315.
need('((220,391,424) if vertical else (560,315,354))' in s,'editor live sizes are 220x391 and 560x315')
need('((220,391,424) if vertical else (480,270,309))' not in s,'old editor 16:9 size removed')
need('[.44,.56] if editor_format=="16:9 Originale" else [.22,.78]' in s,'main editor gives 16:9 enough width')
need('[.44,.56] if st.session_state[_fmt_key]=="16:9 Originale" else [.22,.78]' in s,'inline editor gives 16:9 enough width')

# Dedicated boxes; no global player restyle.
need('key="v985-main-preview-card"' in s,'main preview card wrapper')
need('key="v985-editor-player-card"' in s,'main editor player card wrapper')
need('key=f"v985-inline-player-card-{_this_inline_id}"' in s,'inline editor player card wrapper')
need('gsf-v98-5-player-cards' in s,'coordinated player card style')
need('[class*="st-key-v71_short_card_"]' in s,'AI cards polished without changing mini player engine')

# Critical player and app guardrails.
need('def render_gsf_player' in s,'unified player engine preserved')
need('def render_gsf_editor_live_player' in s,'editor live player engine preserved')
need('inline_live_v32_' in s,'persistent inline identity preserved')
need('key="upload_v73"' in s,'stable uploader preserved')
need('_legacy_seek=float(seek_target if seek_target is not None else start_seconds)' in s,'subtitle VAI fix preserved')
need('_main_recipe_selected=True' in s and '_inline_recipe_selected=True' in s,'apply changes fix preserved')
need('gsf-v98-3-home-compact' in s,'compact home preserved')
need('Zoom e posizione vengono applicati identici al render.' not in s,'framing cloud stays removed')
need('Audio, immagine e velocità restano sincronizzati con la preview.' not in s,'adjustment cloud stays removed')
need('numero_clip=3' in s,'three AI clips preserved')
need('def _gsf_smooth_reframe_track' in s,'Smart Reframe preserved')
need('def _gsf_subtitle_groups' in s,'subtitle grouping preserved')
need('"-crf","21"' in s,'final render quality preserved')
print('V98.5 player cards regression: PASS')
