from pathlib import Path

src=Path('/app/GamingShortsFactory_V100_4_RENDER_STABLE.py')
out=Path('/app/GamingShortsFactory_V100_5_MAX_UPLOAD.py')
s=src.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise RuntimeError(f'V100.5 target not found: {label}')
    s=s.replace(old,new,1)

replace_once(
'''  const concurrency=Math.max(1,Number(init.concurrency||caps.concurrency||6));
''',
'''  const requestedConcurrency=Math.max(1,Number(init.concurrency||caps.concurrency||10));
  const mobileUpload=/Android|iPhone|iPad|iPod|Mobile/i.test(navigator.userAgent||'') ||
    (navigator.maxTouchPoints>1 && Math.min(screen.width,screen.height)<900);
  const concurrency=mobileUpload?Math.min(6,requestedConcurrency):Math.min(10,requestedConcurrency);
''',
'adaptive 10 desktop / 6 mobile bucket lanes'
)

replace_once(
'''  const update=()=>{
    let inflight=0;
    for(const value of live.values())inflight+=value;
    const pct=Math.min(99,Math.round(((completedBytes+inflight)/file.size)*100));
    bar.style.width=pct+'%';
    statusText.textContent='Upload diretto… '+pct+'%';
  };
''',
'''  const uploadStartedAt=performance.now();
  const update=()=>{
    let inflight=0;
    for(const value of live.values())inflight+=value;
    const bytesNow=completedBytes+inflight;
    const pct=Math.min(99,Math.round((bytesNow/file.size)*100));
    const elapsed=Math.max(0.25,(performance.now()-uploadStartedAt)/1000);
    const speedMBs=(bytesNow/1048576)/elapsed;
    bar.style.width=pct+'%';
    statusText.textContent='Upload diretto… '+pct+'% · '+speedMBs.toFixed(1)+' MB/s';
  };
''',
'live upload throughput display'
)

replace_once(
'''Gaming Shorts Factory · V100.4 Render Stable''',
'''Gaming Shorts Factory · V100.5 MAX Upload''',
'V100.5 marker'
)

out.write_text(s,encoding='utf-8')
print(f'V100.5 MAX Upload patch applied: {out}')
