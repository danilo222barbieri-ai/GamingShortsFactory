from pathlib import Path
import sys
p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')

def need(ok,msg):
    if not ok: raise AssertionError(msg)
    print('PASS:',msg)

need('Gaming Shorts Factory · V98.12 Upload 64MB' in s,'V98.12 marker')
need('const CHUNK=64*1024*1024;' in s,'64MB browser chunks')
need('const CONCURRENCY=2;' in s,'two upload workers preserved')
need('window.parent.location.reload()' not in s,'hard refresh remains removed')
need('@st.fragment(run_every="0.35s")' in s,'fast completion watcher preserved')
need('CHIUDI EDITOR' not in s and 'CHIUDI' in s,'compact close label preserved')
need('↶ RESET CONTROLLI' not in s and '↶ RESET' in s,'compact reset preserved')
need('GSF_AI_ENGINE_VERSION = "v51-speed-adaptive"' in s,'AI speed profile preserved')
need('numero_clip=3' in s,'three AI clips preserved')
need('def _gsf_smooth_reframe_track' in s,'Smart Reframe preserved')
need('def _gsf_subtitle_groups' in s,'subtitle grouping preserved')
need('"-crf","21"' in s,'final render quality preserved')
need('((220,391,424) if vertical else (520,293,332))' in s,'editor dimensions preserved')
need('_profile="PLAYER 16:9"; _target_width=640; _max_vw="640px"; _cap=430' in s,'main preview preserved')
print('V98.12 upload-64MB regression: PASS')
