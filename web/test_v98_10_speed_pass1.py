from pathlib import Path
import sys
p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')
compile(s,str(p),'exec')

def need(ok,msg):
    if not ok: raise AssertionError(msg)
    print('PASS:',msg)

need('Gaming Shorts Factory · V98.10 Speed Pass 1' in s,'V98.10 marker')
need('const CHUNK=32*1024*1024;' in s,'32MB browser chunks')
need('const CONCURRENCY=2;' in s,'two upload workers')
need('Promise.all(' in s and 'const worker=async()=>{' in s,'parallel chunk upload')
need('window.parent.location.reload()' not in s,'hard page refresh removed')
need('@st.fragment(run_every="0.35s")' in s,'fast completion watcher')
need('CHIUDI EDITOR' not in s and 'CHIUDI' in s,'compact close label')
need('↶ RESET CONTROLLI' not in s and '↶ RESET' in s,'reset remains compact')
need('((220,391,424) if vertical else (520,293,332))' in s,'editor player dimensions preserved')
need('_profile="PLAYER 16:9"; _target_width=640; _max_vw="640px"; _cap=430' in s,'main preview size preserved')
need('numero_clip=3' in s,'three AI clips preserved')
need('"-crf","21"' in s,'final quality preserved')
print('V98.10 pass1 regression: PASS')
