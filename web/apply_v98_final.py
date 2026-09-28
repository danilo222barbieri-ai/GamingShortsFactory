from pathlib import Path

src=Path('/app/GamingShortsFactory_V98_12_UPLOAD_64MB.py')
out=Path('/app/GamingShortsFactory_V98_FINAL.py')
s=src.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise RuntimeError(f'V98 FINAL target not found: {label}')
    s=s.replace(old,new,1)

# Four smaller parallel lanes perform better over real-world browser/proxy paths
# than two very large requests, while keeping the same ~128 MB maximum in flight.
replace_once(
'''const CHUNK=64*1024*1024;
const CONCURRENCY=2;
''',
'''const CHUNK=32*1024*1024;
const CONCURRENCY=4;
''',
'32MB x4 upload lanes')

# Retry only the failed lane; completed chunks are never retransmitted.
anchor='''function uploadChunk(blob,meta,onProgress){
'''
if anchor not in s:
    raise RuntimeError('V98 FINAL target not found: uploadChunk')
retry_helper=r'''
async function uploadChunkWithRetry(blob,meta,onProgress,maxAttempts=3){
  let lastError=null;
  for(let attempt=1;attempt<=maxAttempts;attempt++){
    try{
      return await uploadChunk(blob,meta,onProgress);
    }catch(err){
      lastError=err;
      onProgress(0);
      if(attempt<maxAttempts){
        await new Promise(resolve=>setTimeout(resolve,400*attempt));
      }
    }
  }
  throw lastError || new Error('Upload interrotto');
}

'''
# Insert helper after the uploadChunk function, immediately before change listener.
listener="""pick.addEventListener('change',async()=>{"""
if listener not in s:
    raise RuntimeError('V98 FINAL target not found: upload listener')
s=s.replace(listener,retry_helper+listener,1)

replace_once(
'''        await uploadChunk(blob,{id,name:file.name,size:file.size,start,index:i,count},(sent)=>{
''',
'''        await uploadChunkWithRetry(blob,{id,name:file.name,size:file.size,start,index:i,count},(sent)=>{
''',
'per-lane retry')

# A little more tolerance for slower mobile uplinks while parallel lanes keep speed.
replace_once(
'''    xhr.timeout=120000;
''',
'''    xhr.timeout=180000;
''',
'chunk timeout')

s=s.replace(
    'Gaming Shorts Factory · V98.12 Upload 64MB',
    'Gaming Shorts Factory · V98 FINAL'
)

out.write_text(s,encoding='utf-8')
print(f'V98 FINAL patch applied: {out}')
