from pathlib import Path
import sys

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

need('Gaming Shorts Factory · V98.4 Editor Cleanup' in s,'V98.4 marker')
need('Zoom e posizione vengono applicati identici al render.' not in s,'framing info cloud removed')
need('Audio, immagine e velocità restano sincronizzati con la preview.' not in s,'adjustments info cloud removed')

# Existing cleanup remains.
need('Sessione beta ripristinata automaticamente.' not in s,'session bubble remains removed')
need('Per il player LIVE persistente serve una versione recente di Streamlit con Components V2.' not in s,'technical warning remains removed')
need('IN {_istart:.1f}s · OUT {_iend:.1f}s · DURATA {_ilen:.1f}s' not in s,'trim cloud remains removed')
need('ANTEPRIMA LIVE · queste regolazioni sono le stesse usate dal render finale.' not in s,'preview cloud remains removed')

# Core controls and regressions remain.
need('with st.popover("INQUADRATURA",use_container_width=True):' in s,'framing controls preserved')
need('with st.popover("REGOLAZIONI",use_container_width=True):' in s,'adjustment controls preserved')
need('key="upload_v73"' in s,'stable uploader preserved')
need('_legacy_seek=float(seek_target if seek_target is not None else start_seconds)' in s,'subtitle VAI fix preserved')
need('_main_recipe_selected=True' in s and '_inline_recipe_selected=True' in s,'apply changes fix preserved')
need('gsf-v98-3-home-compact' in s,'compact home preserved')
need('numero_clip=3' in s,'three AI clips preserved')
need('def _gsf_smooth_reframe_track' in s,'Smart Reframe preserved')
need('def _gsf_subtitle_groups' in s,'subtitle grouping preserved')
need('"-crf","21"' in s,'final render quality preserved')
print('V98.4 editor cleanup regression: PASS')
