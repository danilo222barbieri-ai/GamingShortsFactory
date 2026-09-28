from pathlib import Path
import sys

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

need('Gaming Shorts Factory · V98.6 Player Sizes' in s,'V98.6 marker')

# Main preview.
need('_profile="PLAYER 16:9"; _target_width=640; _max_vw="640px"; _cap=430' in s,'main preview 16:9 is 640px')
need('_profile="PLAYER 9:16"; _target_width=300; _max_vw="300px"; _cap=680' in s,'main preview 9:16 unchanged')
need('_target_width=800; _max_vw="800px"' not in s,'old 800px main preview removed')

# Editor LIVE.
need('frame_w,frame_h,iframe_h=((220,391,424) if vertical else (560,315,354))' in s,'editor live 9:16 and 16:9 sizes correct')
need('((220,391,424) if vertical else (480,270,309))' not in s,'old 480x270 editor size removed')
need('[.44,.56] if editor_format=="16:9 Originale" else [.22,.78]' in s,'main editor 16:9 workspace widened')
need('[.44,.56] if st.session_state[_fmt_key]=="16:9 Originale" else [.22,.78]' in s,'inline editor 16:9 workspace widened')

# Reset label.
need('↶ RESET CONTROLLI' not in s,'old reset label removed')
need('↶ RESET' in s,'short reset label present')

# Step 1 styling stays intact.
need('width:fit-content;max-width:100%;margin:0 auto;' in s,'main preview card styling preserved')
need('0 0 0 9px #F8FCFF,0 0 0 10px #D4E4EF' in s,'editor live card styling preserved')

# Upload + functional guardrails.
need('key="upload_v73"' in s,'stable uploader preserved')
need('if _gsf_recovered_source is not None:' in s,'safe upload recovery flow preserved')
need('gsf-v91-upload-status' in s,'upload status preserved')
need('_legacy_seek=float(seek_target if seek_target is not None else start_seconds)' in s,'subtitle VAI fix preserved')
need('_main_recipe_selected=True' in s and '_inline_recipe_selected=True' in s,'apply changes fix preserved')
need('gsf-v98-3-home-compact' in s,'compact home preserved')
need('Zoom e posizione vengono applicati identici al render.' not in s,'framing cloud remains removed')
need('Audio, immagine e velocità restano sincronizzati con la preview.' not in s,'adjustment cloud remains removed')
need('numero_clip=3' in s,'three AI clips preserved')
need('def _gsf_smooth_reframe_track' in s,'Smart Reframe preserved')
need('def _gsf_subtitle_groups' in s,'subtitle grouping preserved')
need('"-crf","21"' in s,'final render quality preserved')
print('V98.6 player sizes regression: PASS')
