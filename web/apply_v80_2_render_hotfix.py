from pathlib import Path
import re

src=Path('/app/GamingShortsFactory_V80_1_HOTFIX.py')
out=Path('/app/GamingShortsFactory_V80_2_RENDER_HOTFIX.py')
s=src.read_text(encoding='utf-8')

def wrap_transcriber(func_name):
    global s
    start=s.find(f'def {func_name}(')
    if start<0:
        raise RuntimeError(f'V80.2 function not found: {func_name}')
    nxt=s.find('\ndef ',start+5)
    end=len(s) if nxt<0 else nxt
    wrapper_name=func_name+'_lowmem'
    wrapper=f'''

def {wrapper_name}(*args, **kwargs):
    """V80.2: release cached Whisper RAM before FFmpeg rendering."""
    try:
        return {func_name}(*args, **kwargs)
    finally:
        if GSF_LOW_MEMORY_WEB:
            try:
                _gsf_subtitle_whisper_model.clear()
            except Exception:
                pass
            try:
                import gc
                gc.collect()
            except Exception:
                pass
'''
    s=s[:end]+wrapper+s[end:]
    tail_start=end+len(wrapper)
    tail=s[tail_start:]
    count=tail.count(func_name+'(')
    tail=tail.replace(func_name+'(',wrapper_name+'(')
    s=s[:tail_start]+tail
    return count

c1=wrap_transcriber('_gsf_transcribe_editor_scene')
c2=wrap_transcriber('_gsf_render_transcribe_words')

# User-facing render errors should not dump enormous FFmpeg logs on mobile.
# Keep the useful tail, which normally contains the real cause.
needle='''st.error("Creazione Short finale non riuscita.")'''
if needle in s:
    pass

s=s.replace(
    'Gaming Shorts Factory · V80.1 Hotfix',
    'Gaming Shorts Factory · V80.2 Render Hotfix'
)

out.write_text(s,encoding='utf-8')
print(f'V80.2 wrapped editor transcriber calls={c1}, render transcriber calls={c2}')
print(f'V80.2 patch applied: {out}')
