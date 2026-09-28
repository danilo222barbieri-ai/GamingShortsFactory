from pathlib import Path

src=Path('/app/GamingShortsFactory_V98_9_DIRECT_UPLOAD.py')
out=Path('/app/GamingShortsFactory_V98_10_SPEED_PASS1.py')
s=src.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise RuntimeError(f'V98.10 target not found: {label}')
    s=s.replace(old,new,1)

# 32 MB chunks, two in flight. The server writes each chunk independently,
# so we gain throughput without buffering the whole video in RAM.
replace_once(
'''const CHUNK=4*1024*1024;
''',
'''const CHUNK=32*1024*1024;
const CONCURRENCY=2;
''',
'upload chunk size')

old_loop='''    for(let i=0;i<count;i++){
      const start=i*CHUNK;
      const end=Math.min(file.size,start+CHUNK);
      const blob=file.slice(start,end);
      await uploadChunk(blob,{id,name:file.name,size:file.size,start,index:i,count},(sent)=>{
        const pct=Math.min(99,Math.round(((start+sent)/file.size)*100));
        bar.style.width=pct+'%';
        statusText.textContent='Caricamento video… '+pct+'%';
      });
      const pct=Math.min(99,Math.round((end/file.size)*100));
      bar.style.width=pct+'%';
      statusText.textContent='Caricamento video… '+pct+'%';
    }
    bar.style.width='100%';
    statusText.textContent='Video caricato';
    circle.classList.remove('busy');
    circle.classList.add('done');
    icon.textContent='✓';
    label.textContent='Video caricato';
    setTimeout(()=>{try{window.parent.location.reload();}catch(e){}},350);
'''
new_loop='''    let nextIndex=0;
    let completedBytes=0;
    const liveBytes=new Map();

    const updateProgress=()=>{
      let inflight=0;
      for(const value of liveBytes.values()) inflight+=value;
      const pct=Math.min(99,Math.round(((completedBytes+inflight)/file.size)*100));
      bar.style.width=pct+'%';
      statusText.textContent='Caricamento video… '+pct+'%';
    };

    const worker=async()=>{
      while(true){
        const i=nextIndex++;
        if(i>=count)return;
        const start=i*CHUNK;
        const end=Math.min(file.size,start+CHUNK);
        const blob=file.slice(start,end);
        liveBytes.set(i,0);
        await uploadChunk(blob,{id,name:file.name,size:file.size,start,index:i,count},(sent)=>{
          liveBytes.set(i,sent);
          updateProgress();
        });
        liveBytes.delete(i);
        completedBytes+=end-start;
        updateProgress();
      }
    };

    await Promise.all(
      Array.from({length:Math.min(CONCURRENCY,count)},()=>worker())
    );

    bar.style.width='100%';
    statusText.textContent='Video caricato';
    circle.classList.remove('busy');
    circle.classList.add('done');
    icon.textContent='✓';
    label.textContent='Video caricato';
    // No browser refresh: the Streamlit fragment watcher sees the disk marker
    // and reruns the app internally without reloading the page.
'''
replace_once(old_loop,new_loop,'parallel upload and no hard refresh')

# Shorter watcher interval for a seamless transition after upload.
replace_once(
'''@st.fragment(run_every="1s")
''',
'''@st.fragment(run_every="0.35s")
''',
'direct upload completion watcher')

# Compact close-editor copy requested by the user.
if 'CHIUDI EDITOR' not in s:
    raise RuntimeError('V98.10 target not found: CHIUDI EDITOR')
s=s.replace('CHIUDI EDITOR','CHIUDI')

s=s.replace(
    'Gaming Shorts Factory · V98.9 Direct Upload',
    'Gaming Shorts Factory · V98.10 Speed Pass 1'
)

out.write_text(s,encoding='utf-8')
print(f'V98.10 speed pass 1 applied: {out}')
