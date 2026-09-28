from pathlib import Path
import sys

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

need('Gaming Shorts Factory · V98.3 Home Compact' in s,'V98.3 marker')
need('gsf-v98-3-home-compact' in s,'home compact style installed')
need('.block-container{' in s and 'padding-top:0 !important' in s,'top page spacing reduced')
need('.gsf-hero{' in s and 'margin-top:-12px !important' in s,'hero moved upward on desktop')
need('.hero-title{' in s and 'line-height:.92 !important' in s,'hero title remains full size but tighter')
need('.hero-sub{' in s and 'margin-bottom:4px !important' in s,'hero subtitle spacing tightened')
need('.st-key-v73-upload-shell{' in s and 'margin-top:-18px !important' in s,'upload circle moved upward without resizing')

# Explicitly protect the approved circle dimensions.
need('width:218px' in s and 'height:218px' in s,'desktop upload circle size preserved')
need('width:208px' in s and 'height:208px' in s,'mobile upload circle size preserved')
need('gsf-v91-upload-status' in s,'real upload status remains present')

# Upload recovery and editor hotfixes remain intact.
need('key="upload_v73"' in s,'stable uploader key preserved')
need('if _gsf_recovered_source is not None:' in s,'safe conditional new-video flow preserved')
need('_legacy_seek=float(seek_target if seek_target is not None else start_seconds)' in s,'subtitle VAI fix preserved')
need('_main_recipe_selected=True' in s and '_inline_recipe_selected=True' in s,'apply-changes fixes preserved')
need('Sessione beta ripristinata automaticamente.' not in s,'session bubble remains removed')
need('Per il player LIVE persistente serve una versione recente di Streamlit con Components V2.' not in s,'technical warning remains removed')
need('IN {_istart:.1f}s · OUT {_iend:.1f}s · DURATA {_ilen:.1f}s' not in s,'trim cloud remains removed')
need('ANTEPRIMA LIVE · queste regolazioni sono le stesse usate dal render finale.' not in s,'preview cloud remains removed')

# Production guardrails.
need('numero_clip=3' in s,'three AI clips preserved')
need('def _gsf_smooth_reframe_track' in s,'Smart Reframe preserved')
need('def _gsf_subtitle_groups' in s,'subtitle grouping preserved')
need('"-crf","21"' in s,'final render quality preserved')
print('V98.3 home compact regression: PASS')
