from pathlib import Path

src=Path('/app/GamingShortsFactory_V98_7_NEW_VIDEO_FIX.py')
out=Path('/app/GamingShortsFactory_V98_8_UPLOAD_MEMORY_FIX.py')
s=src.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise RuntimeError(f'V98.8 target not found: {label}')
    s=s.replace(old,new,1)

# Release AI-only caches when starting a fresh upload.
# Streamlit itself buffers the incoming UploadedFile in RAM; on Railway's 1 GB
# container we must free Whisper/analysis caches before receiving another file.
replace_once(
'''    st.session_state["gsf_upload_generation"]=old_generation+1

    try:
        GSF_SESSION_STATE_FILE.unlink(missing_ok=True)
''',
'''    st.session_state["gsf_upload_generation"]=old_generation+1

    # V98.8: free AI / Whisper memory before the next Streamlit upload.
    try:
        _gsf_v93_release_analysis_memory()
    except Exception:
        try:
            import gc
            gc.collect()
        except Exception:
            pass

    try:
        GSF_SESSION_STATE_FILE.unlink(missing_ok=True)
''',
'new-video AI memory release')

s=s.replace(
    'Gaming Shorts Factory · V98.7 New Video Fix',
    'Gaming Shorts Factory · V98.8 Upload Memory Fix'
)

out.write_text(s,encoding='utf-8')
print(f'V98.8 patch applied: {out}')
