from pathlib import Path
import ast,sys
p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')
ast.parse(s)

def need(ok,msg):
    if not ok: raise AssertionError(msg)
    print('PASS:',msg)

need('Gaming Shorts Factory · V98 FINAL 6LANES' in s,'6LANES marker')
need('const CHUNK=16*1024*1024;' in s,'16MB chunks')
need('const CONCURRENCY=6;' in s,'six parallel lanes')
need('uploadChunkWithRetry' in s and 'maxAttempts=3' in s,'retry preserved')
need('xhr.timeout=180000' in s,'timeout preserved')
need('window.parent.location.reload()' not in s,'hard refresh absent')
need('@st.fragment(run_every="0.35s")' in s,'completion watcher preserved')
need('IN / OUT · ritaglio scena' in s,'IN/OUT preserved')
need('((220,391,424) if vertical else (520,293,332))' in s,'editor dimensions frozen')
need('_profile="PLAYER 16:9"; _target_width=640; _max_vw="640px"; _cap=430' in s,'main preview frozen')
need('numero_clip=3' in s,'three AI clips preserved')
need('GSF_AI_ENGINE_VERSION = "v51-speed-adaptive"' in s,'AI speed profile preserved')
need('def _gsf_smooth_reframe_track' in s,'Smart Reframe preserved')
need('def _gsf_subtitle_groups' in s,'subtitle grouping preserved')
need('"-crf","21"' in s,'final quality preserved')
print('V98 FINAL 6LANES regression: PASS')
