from pathlib import Path

src = Path('/app/GamingShortsFactory_V87_UPLOAD_PERSISTS.py')
out = Path('/app/GamingShortsFactory_V88_PERSISTENT_LOADED_CIRCLE.py')
s = src.read_text(encoding='utf-8')

# Root cause of V87: it still depended on Streamlit keeping the dropzone in the
# DOM after a file was accepted. On the current uploader build that node can be
# removed, so CSS cannot keep a circle that no longer exists.
# V88 renders the completed circle from Python state instead. It therefore does
# not depend on Streamlit's post-upload internal DOM at all.
v88_fn = r'''
def _gsf_v88_loaded_circle_html():
    return """
<style id="gsf-v88-persistent-loaded-circle">
/* Once Python has a video, hide Streamlit's changing post-upload uploader DOM.
   The stable completed-state circle below becomes the single visible control. */
.st-key-v73-upload-shell [data-testid="stFileUploader"]{display:none !important;}

.gsf-v88-loaded-wrap{
    width:100%;
    padding:18px 0 8px;
    display:flex;
    align-items:center;
    justify-content:center;
    text-align:center;
}
.gsf-v88-loaded-circle{
    box-sizing:border-box;
    width:218px;
    height:218px;
    min-width:218px;
    min-height:218px;
    max-width:218px;
    max-height:218px;
    margin:0 auto;
    padding:26px 22px;
    display:flex;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    border-radius:50%;
    background:#DDF5E8;
    border:2px solid #69BE8E;
    box-shadow:0 10px 26px rgba(31,78,121,.10);
    color:#236B43;
}
.gsf-v88-loaded-check{
    display:block;
    margin:0 0 13px 0;
    color:#238A50;
    font-size:54px;
    font-weight:700;
    line-height:.82;
}
.gsf-v88-loaded-label{
    display:block;
    width:150px;
    max-width:150px;
    margin:0;
    color:#236B43;
    font-size:17px;
    font-weight:800;
    line-height:1.2;
    white-space:normal;
    text-align:center;
}
@media(max-width:600px){
    .gsf-v88-loaded-circle{
        width:208px;
        height:208px;
        min-width:208px;
        min-height:208px;
        max-width:208px;
        max-height:208px;
    }
    .gsf-v88-loaded-check{font-size:54px;margin-bottom:12px;}
    .gsf-v88-loaded-label{width:144px;max-width:144px;font-size:16px;}
}
</style>
<div class="gsf-v88-loaded-wrap" role="status" aria-label="Video caricato">
  <div class="gsf-v88-loaded-circle">
    <span class="gsf-v88-loaded-check">✓</span>
    <span class="gsf-v88-loaded-label">Video caricato</span>
  </div>
</div>
"""

'''

anchor = 'with st.container(key="v73-upload-shell"):\n'
if anchor not in s:
    raise RuntimeError('V88 uploader container anchor not found')
s = s.replace(anchor, v88_fn + anchor, 1)

old = 'st.markdown(_gsf_v86_upload_css(video is not None), unsafe_allow_html=True)\n'
new = '''st.markdown(_gsf_v86_upload_css(video is not None), unsafe_allow_html=True)\nif video is not None:\n    st.markdown(_gsf_v88_loaded_circle_html(), unsafe_allow_html=True)\n'''
if old not in s:
    raise RuntimeError('V88 uploader CSS call anchor not found')
s = s.replace(old, new, 1)

s = s.replace(
    'Gaming Shorts Factory · V87 Upload Persists',
    'Gaming Shorts Factory · V88 Persistent Loaded Circle'
)

out.write_text(s, encoding='utf-8')
print(f'V88 patch applied: {out}')
