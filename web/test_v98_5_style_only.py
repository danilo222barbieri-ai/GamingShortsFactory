from pathlib import Path
import sys

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

need('Gaming Shorts Factory · V98.5 Style Only' in s,'V98.5 style-only marker')

# New appearance.
need('width:fit-content;max-width:100%;margin:0 auto;' in s,'main preview card wrapper styling')
need('border:1px solid #D4E4EF;border-radius:24px' in s,'main preview premium border')
need('0 0 0 9px #F8FCFF,0 0 0 10px #D4E4EF' in s,'editor live faux-card styling')

# Dimensions MUST be unchanged in Step 1.
need('_profile="PLAYER 16:9"; _target_width=800; _max_vw="800px"; _cap=540' in s,'main preview 16:9 remains 800px')
need('_profile="PLAYER 9:16"; _target_width=300; _max_vw="300px"; _cap=680' in s,'main preview 9:16 remains 300px')
need('frame_w,frame_h,iframe_h=((220,391,424) if vertical else (480,270,309))' in s,'editor dimensions unchanged')
need('studio_player, studio_side = st.columns([.22,.78],gap="medium")' in s,'main editor columns unchanged')
need('_pl,_side=st.columns([.22,.78],gap="medium")' in s,'inline editor columns unchanged')

# Upload and functional hotfixes preserved.
need('key="upload_v73"' in s,'stable uploader key preserved')
need('if _gsf_recovered_source is not None:' in s,'safe upload recovery flow preserved')
need('gsf-v91-upload-status' in s,'upload status preserved')
need('_legacy_seek=float(seek_target if seek_target is not None else start_seconds)' in s,'subtitle VAI fix preserved')
need('_main_recipe_selected=True' in s and '_inline_recipe_selected=True' in s,'apply changes fix preserved')
need('gsf-v98-3-home-compact' in s,'compact home preserved')
need('Zoom e posizione vengono applicati identici al render.' not in s,'framing cloud remains removed')
need('Audio, immagine e velocità restano sincronizzati con la preview.' not in s,'adjustment cloud remains removed')

# Core guardrails.
need('numero_clip=3' in s,'three AI clips preserved')
need('def _gsf_smooth_reframe_track' in s,'Smart Reframe preserved')
need('def _gsf_subtitle_groups' in s,'subtitle grouping preserved')
need('"-crf","21"' in s,'final render quality preserved')
print('V98.5 style-only regression: PASS')
