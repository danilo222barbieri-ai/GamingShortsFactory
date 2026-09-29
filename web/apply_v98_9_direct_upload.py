from pathlib import Path

src=Path('/app/GamingShortsFactory_V98_8_UPLOAD_MEMORY_FIX.py')
out=Path('/app/GamingShortsFactory_V98_9_DIRECT_UPLOAD.py')
s=src.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise RuntimeError(f'V98.9 target not found: {label}')
    s=s.replace(old,new,1)

old='''with st.container(key="v73-upload-shell"):
    video = st.file_uploader(
        "Carica il tuo video",
        type=["mp4", "mov", "mkv"],
        label_visibility="collapsed",
        key="upload_v73"
    )

    _gsf_recovered_source = None
    if video is None and GSF_WEB_MODE:
        _gsf_recovered_source = _gsf_find_recovered_source()
        if _gsf_recovered_source is not None:
            video = _GSFRecoveredUpload(
                _gsf_recovered_source,
                st.session_state.get("gsf_source_name", _gsf_recovered_source.name)
            )
            st.session_state["gsf_source_path"] = str(_gsf_recovered_source)

    st.markdown(_gsf_v89_upload_visual_html(video is not None), unsafe_allow_html=True)
'''

new=r'''def _gsf_v989_direct_ready():
    marker=GSF_PREVIEW_DIR / ".direct_upload_ready.json"
    try:
        if not marker.is_file():
            return None,""
        data=json.loads(marker.read_text(encoding="utf-8"))
        candidate=Path(str(data.get("path","") or ""))
        if not candidate.is_file():
            return None,""
        if candidate.parent.resolve()!=GSF_PREVIEW_DIR.resolve():
            return None,""
        return candidate,str(data.get("name","") or candidate.name)
    except Exception:
        return None,""


def _gsf_v989_direct_upload_html(loaded=False):
    if loaded:
        return r"""
<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;padding:0;background:transparent;overflow:hidden;font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.wrap{height:270px;display:flex;align-items:flex-start;justify-content:center;padding-top:26px;box-sizing:border-box}
.circle{box-sizing:border-box;width:218px;height:218px;border-radius:50%;display:flex;flex-direction:column;
align-items:center;justify-content:center;background:#FFE8E5;border:2px solid #F28B82;
box-shadow:0 10px 26px rgba(216,91,102,.12);color:#9F3844}
.icon{font-size:54px;font-weight:700;line-height:.82;color:#D85B66;margin-bottom:13px}
.label{width:150px;text-align:center;font-size:17px;font-weight:800;line-height:1.2}
@media(max-width:600px){.wrap{height:252px}.circle{width:208px;height:208px}.icon{font-size:52px}.label{width:144px;font-size:16px}}
</style></head><body><div class="wrap"><div class="circle"><div class="icon">✓</div><div class="label">Video caricato</div></div></div></body></html>
"""

    return r"""
<!doctype html><html><head><meta charset="utf-8"><style>
html,body{margin:0;padding:0;background:transparent;overflow:hidden;font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}
.wrap{height:290px;display:flex;flex-direction:column;align-items:center;justify-content:flex-start;padding-top:30px;box-sizing:border-box}
input{position:absolute;width:1px;height:1px;opacity:0;pointer-events:none}
.circle{box-sizing:border-box;width:218px;height:218px;border-radius:50%;display:flex;flex-direction:column;
align-items:center;justify-content:center;background:#FFE7E3;border:2px solid #F39A90;
box-shadow:0 10px 26px rgba(216,91,102,.12);color:#A94750;cursor:pointer;user-select:none}
.circle:hover{border-color:#EA7E72;box-shadow:0 12px 30px rgba(216,91,102,.18)}
.icon{font-size:58px;font-weight:500;line-height:.82;color:#D45A64;margin-bottom:13px}
.label{width:150px;text-align:center;font-size:17px;font-weight:800;line-height:1.2}
.status{display:none;margin-top:7px;width:174px;text-align:center;color:#B54A55;font-size:12px;font-weight:800}
.track{display:block;height:5px;margin-top:5px;border-radius:999px;background:rgba(216,91,102,.18);overflow:hidden}
.bar{display:block;height:100%;width:0;background:#D85B66;border-radius:999px;transition:width .12s linear}
.circle.busy{pointer-events:none;background:#FFF0EE}
.circle.done{background:#FFE8E5;border-color:#F28B82;color:#9F3844}
.circle.done .icon{color:#D85B66}
.error{color:#B42318}
@media(max-width:600px){.wrap{height:278px}.circle{width:208px;height:208px}.icon{font-size:54px}.label{width:144px;font-size:16px}}
</style></head><body>
<div class="wrap">
<input id="pick" type="file" accept="video/mp4,video/quicktime,video/x-matroska,.mp4,.mov,.mkv">
<label class="circle" id="circle" for="pick"><span class="icon" id="icon">⇧</span><span class="label" id="label">Carica il tuo video</span></label>
<div class="status" id="status"><span id="statusText">Caricamento video… 0%</span><span class="track"><span class="bar" id="bar"></span></span></div>
</div>
<script>
const pick=document.getElementById('pick');
const circle=document.getElementById('circle');
const icon=document.getElementById('icon');
const label=document.getElementById('label');
const status=document.getElementById('status');
const statusText=document.getElementById('statusText');
const bar=document.getElementById('bar');
const CHUNK=4*1024*1024;

function uploadChunk(blob,meta,onProgress){
  return new Promise((resolve,reject)=>{
    const xhr=new XMLHttpRequest();
    xhr.open('PUT','/direct-upload/chunk',true);
    xhr.setRequestHeader('Content-Type','application/octet-stream');
    xhr.setRequestHeader('X-GSF-Upload-ID',meta.id);
    xhr.setRequestHeader('X-GSF-Filename',encodeURIComponent(meta.name));
    xhr.setRequestHeader('X-GSF-File-Size',String(meta.size));
    xhr.setRequestHeader('X-GSF-Chunk-Start',String(meta.start));
    xhr.setRequestHeader('X-GSF-Chunk-Index',String(meta.index));
    xhr.setRequestHeader('X-GSF-Chunk-Count',String(meta.count));
    xhr.upload.onprogress=(e)=>{if(e.lengthComputable) onProgress(e.loaded);};
    xhr.onload=()=>{
      if(xhr.status>=200 && xhr.status<300) resolve(xhr.responseText);
      else reject(new Error('HTTP '+xhr.status));
    };
    xhr.onerror=()=>reject(new Error('Errore di rete'));
    xhr.ontimeout=()=>reject(new Error('Timeout'));
    xhr.timeout=120000;
    xhr.send(blob);
  });
}

pick.addEventListener('change',async()=>{
  const file=pick.files && pick.files[0];
  if(!file)return;
  const ext=(file.name.split('.').pop()||'').toLowerCase();
  if(!['mp4','mov','mkv'].includes(ext)){
    status.style.display='block';status.classList.add('error');statusText.textContent='Formato non supportato';return;
  }
  const count=Math.ceil(file.size/CHUNK);
  const id=Date.now().toString(36)+'_'+Math.random().toString(36).slice(2,12);
  circle.classList.add('busy');
  status.classList.remove('error');
  status.style.display='block';
  label.textContent='Caricamento…';
  try{
    for(let i=0;i<count;i++){
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
  }catch(err){
    circle.classList.remove('busy');
    status.classList.add('error');
    statusText.textContent='Upload interrotto — riprova';
    label.textContent='Carica il tuo video';
    bar.style.width='0';
  }
});
</script></body></html>
"""


_gsf_direct_source,_gsf_direct_name=(None,"")
if GSF_WEB_MODE:
    _gsf_direct_source,_gsf_direct_name=_gsf_v989_direct_ready()

_gsf_recovered_source=None
video=None
if _gsf_direct_source is not None:
    _gsf_recovered_source=_gsf_direct_source
    video=_GSFRecoveredUpload(_gsf_direct_source,_gsf_direct_name or _gsf_direct_source.name)
    st.session_state["gsf_source_path"]=str(_gsf_direct_source)
    st.session_state["gsf_source_name"]=_gsf_direct_name or _gsf_direct_source.name
elif GSF_WEB_MODE:
    _gsf_recovered_source=_gsf_find_recovered_source()
    if _gsf_recovered_source is not None:
        video=_GSFRecoveredUpload(
            _gsf_recovered_source,
            st.session_state.get("gsf_source_name",_gsf_recovered_source.name)
        )
        st.session_state["gsf_source_path"]=str(_gsf_recovered_source)

with st.container(key="v73-upload-shell"):
    if GSF_WEB_MODE:
        components.html(
            _gsf_v989_direct_upload_html(video is not None),
            height=280 if video is not None else 300,
            scrolling=False
        )
    else:
        video=st.file_uploader(
            "Carica il tuo video",
            type=["mp4","mov","mkv"],
            label_visibility="collapsed",
            key="upload_v73"
        )
        st.markdown(_gsf_v89_upload_visual_html(video is not None),unsafe_allow_html=True)

if GSF_WEB_MODE and video is None:
    @st.fragment(run_every="1s")
    def _gsf_v989_direct_upload_watch():
        _ready,_name=_gsf_v989_direct_ready()
        if _ready is not None:
            st.rerun()
    _gsf_v989_direct_upload_watch()
'''

replace_once(old,new,'replace Streamlit web uploader with direct chunk uploader')

# The robust active-video guard must not depend on a web-only native uploader widget.
replace_once(
'''        or st.session_state.get("upload_v73") is not None
''',
'''        or (not GSF_WEB_MODE and st.session_state.get("upload_v73") is not None)
''',
'active-video local uploader guard')

s=s.replace(
    'Gaming Shorts Factory · V98.8 Upload Memory Fix',
    'Gaming Shorts Factory · V98.9 Direct Upload'
)

out.write_text(s,encoding='utf-8')
print(f'V98.9 direct-upload patch applied: {out}')
