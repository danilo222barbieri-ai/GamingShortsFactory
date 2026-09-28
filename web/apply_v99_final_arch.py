from pathlib import Path

src=Path('/app/GamingShortsFactory_V99_AI_TURBO.py')
out=Path('/app/GamingShortsFactory_V99_FINAL_ARCH.py')
s=src.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise RuntimeError(f'V99 FINAL ARCH target not found: {label}')
    s=s.replace(old,new,1)

bucket_helpers=r'''
async function gsfUploadCapabilities(){
  try{
    const r=await fetch('/direct-upload/capabilities',{cache:'no-store'});
    if(!r.ok)return {bucket:false};
    return await r.json();
  }catch(e){
    return {bucket:false};
  }
}

function gsfPutPresigned(url,blob,onProgress){
  return new Promise((resolve,reject)=>{
    const xhr=new XMLHttpRequest();
    xhr.open('PUT',url,true);
    xhr.upload.onprogress=(e)=>{if(e.lengthComputable)onProgress(e.loaded);};
    xhr.onload=()=>{
      if(xhr.status>=200 && xhr.status<300){
        const etag=xhr.getResponseHeader('ETag')||xhr.getResponseHeader('etag');
        if(!etag)reject(new Error('ETag non disponibile'));
        else resolve(etag);
      }else reject(new Error('Bucket HTTP '+xhr.status));
    };
    xhr.onerror=()=>reject(new Error('Errore rete bucket'));
    xhr.ontimeout=()=>reject(new Error('Timeout bucket'));
    xhr.timeout=240000;
    xhr.send(blob);
  });
}

async function gsfPutPresignedRetry(url,blob,onProgress,maxAttempts=3){
  let lastError=null;
  for(let attempt=1;attempt<=maxAttempts;attempt++){
    try{
      return await gsfPutPresigned(url,blob,onProgress);
    }catch(err){
      lastError=err;
      onProgress(0);
      if(attempt<maxAttempts){
        await new Promise(resolve=>setTimeout(resolve,450*attempt));
      }
    }
  }
  throw lastError||new Error('Upload bucket interrotto');
}

async function gsfBucketUpload(file,caps){
  const initResp=await fetch('/direct-upload/bucket/init',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      name:file.name,
      size:file.size,
      type:file.type||'application/octet-stream'
    })
  });
  const init=await initResp.json();
  if(!initResp.ok||!init.ok)throw new Error(init.error||'Impossibile inizializzare bucket');

  const partSize=Number(init.part_size||caps.part_size||32*1024*1024);
  const concurrency=Math.max(1,Number(init.concurrency||caps.concurrency||6));
  const descriptors=Array.isArray(init.parts)?init.parts:[];
  let next=0;
  let completedBytes=0;
  const live=new Map();
  const results=[];

  const update=()=>{
    let inflight=0;
    for(const value of live.values())inflight+=value;
    const pct=Math.min(99,Math.round(((completedBytes+inflight)/file.size)*100));
    bar.style.width=pct+'%';
    statusText.textContent='Upload diretto… '+pct+'%';
  };

  const worker=async()=>{
    while(true){
      const idx=next++;
      if(idx>=descriptors.length)return;
      const desc=descriptors[idx];
      const start=idx*partSize;
      const end=Math.min(file.size,start+partSize);
      const blob=file.slice(start,end);
      live.set(idx,0);
      const etag=await gsfPutPresignedRetry(desc.url,blob,(sent)=>{
        live.set(idx,sent);
        update();
      });
      live.delete(idx);
      completedBytes+=end-start;
      results[idx]={PartNumber:Number(desc.number),ETag:etag};
      update();
    }
  };

  try{
    await Promise.all(
      Array.from({length:Math.min(concurrency,descriptors.length)},()=>worker())
    );
    bar.style.width='100%';
    statusText.textContent='Preparazione video…';

    const doneResp=await fetch('/direct-upload/bucket/complete',{
      method:'POST',
      headers:{'Content-Type':'application/json'},
      body:JSON.stringify({
        upload_id:init.upload_id,
        multipart_id:init.multipart_id,
        key:init.key,
        analysis_key:init.analysis_key,
        name:file.name,
        size:file.size,
        parts:results
      })
    });
    const done=await doneResp.json();
    if(!doneResp.ok||!done.ok)throw new Error(done.error||'Finalizzazione bucket fallita');

    const deadline=Date.now()+300000;
    while(Date.now()<deadline){
      const sr=await fetch('/direct-upload/bucket/status?upload_id='+encodeURIComponent(init.upload_id),{cache:'no-store'});
      const st=await sr.json();
      if(sr.ok&&st.ready)return true;
      if(!sr.ok&&st.error)throw new Error(st.error);
      await new Promise(resolve=>setTimeout(resolve,500));
    }
    throw new Error('Preparazione video troppo lunga');
  }catch(err){
    try{
      await fetch('/direct-upload/bucket/abort',{
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body:JSON.stringify({
          upload_id:init.upload_id,
          multipart_id:init.multipart_id,
          key:init.key
        })
      });
    }catch(e){}
    throw err;
  }
}

'''

listener="""pick.addEventListener('change',async()=>{"""
if listener not in s:
    raise RuntimeError('V99 FINAL ARCH target not found: upload listener')
s=s.replace(listener,bucket_helpers+listener,1)

replace_once(
'''  try{
    let nextIndex=0;
''',
'''  try{
    const caps=await gsfUploadCapabilities();
    if(caps && caps.bucket===true){
      await gsfBucketUpload(file,caps);
      bar.style.width='100%';
      statusText.textContent='Video caricato';
      circle.classList.remove('busy');
      circle.classList.add('done');
      icon.textContent='✓';
      label.textContent='Video caricato';
      return;
    }

    let nextIndex=0;
''',
'bucket-first upload flow')

replace_once(
'''    scan = _gsf_ai_scan_base(input_file)
    cache[key] = scan
''',
'''    scan = None
    try:
        import sys as _gsf_sys
        if "/app/web" not in _gsf_sys.path:
            _gsf_sys.path.insert(0,"/app/web")
        from gsf_bucket_bridge import load_prescan_from_marker as _gsf_load_prescan
        scan = _gsf_load_prescan(
            GSF_PREVIEW_DIR,
            GSF_AI_ENGINE_VERSION
        )
    except Exception:
        scan = None

    if scan is None:
        scan = _gsf_ai_scan_base(input_file)

    cache[key] = scan
''',
'worker prescan bridge')

s=s.replace(
    'Gaming Shorts Factory · V99 AI Turbo',
    'Gaming Shorts Factory · V99 FINAL Architecture'
)

out.write_text(s,encoding='utf-8')
print(f'V99 FINAL Architecture patch applied: {out}')
