from pathlib import Path
import re

src = Path('/app/GamingShortsFactory_V85_UPLOAD_CLEANUP.py')
out = Path('/app/GamingShortsFactory_V86_SINGLE_UPLOAD_CIRCLE.py')
s = src.read_text(encoding='utf-8')

# Root-cause fix: V83/V84/V85 each appended another uploader skin. Remove those
# late style blocks entirely so the uploader has one owner again.
def remove_style_block(text, style_id):
    pattern = re.compile(
        rf'''(?ms)\n?st\.markdown\(\s*"""\s*<style id="{re.escape(style_id)}">.*?</style>\s*"""\s*,\s*unsafe_allow_html\s*=\s*True\s*\)\s*'''
    )
    return pattern.subn('\n', text, count=1)

for _style_id in ('gsf-v83-upload-fix', 'gsf-v84-centered-upload', 'gsf-v85-upload-cleanup'):
    s, n = remove_style_block(s, _style_id)
    if n != 1:
        raise RuntimeError(f'V86 expected one {_style_id} block, removed {n}')
    print(f'V86 removed {_style_id}: {n}')

# One clean skin, rendered exactly where the uploader flow already renders its
# CSS. The actual Streamlit button is the circle; the outer dropzone is fully
# transparent. This avoids nested circles and keeps the native upload behavior.
v86_fn = r'''
def _gsf_v86_upload_css(_uploaded=False):
    return """
<style id="gsf-v86-single-upload-circle">
/* One owner, one circle: the real Streamlit upload button. */
.st-key-v73-upload-shell{
    width:100% !important;
    padding:18px 0 8px !important;
    text-align:center !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploader"]{
    width:100% !important;
    max-width:330px !important;
    margin:0 auto !important;
    padding:0 !important;
    background:transparent !important;
    border:0 !important;
    border-radius:0 !important;
    box-shadow:none !important;
    overflow:visible !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]{
    width:100% !important;
    min-height:236px !important;
    height:auto !important;
    margin:0 auto !important;
    padding:8px !important;
    display:flex !important;
    align-items:center !important;
    justify-content:center !important;
    background:transparent !important;
    border:0 !important;
    border-radius:0 !important;
    box-shadow:none !important;
    overflow:visible !important;
    position:relative !important;
}

/* Kill every old outer-ring/outer-label pseudo element. */
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]::before,
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]::after{
    content:none !important;
    display:none !important;
    border:0 !important;
    background:none !important;
    box-shadow:none !important;
    animation:none !important;
    filter:none !important;
}

/* Hide native helper/file rows; the control itself remains fully functional. */
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzoneInstructions"],
.st-key-v73-upload-shell [data-testid="stFileUploaderFile"],
.st-key-v73-upload-shell [data-testid="stFileUploaderFileList"],
.st-key-v73-upload-shell [data-testid="stFileUploaderFileName"],
.st-key-v73-upload-shell [data-testid="stFileChips"],
.st-key-v73-upload-shell [data-testid*="UploadedFile"],
.v73-upload-meta{
    display:none !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"] > div:has(button){
    width:auto !important;
    margin:0 auto !important;
    display:flex !important;
    align-items:center !important;
    justify-content:center !important;
}

/* The only visible upload circle. */
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"] button{
    all:unset !important;
    box-sizing:border-box !important;
    width:218px !important;
    height:218px !important;
    min-width:218px !important;
    min-height:218px !important;
    max-width:218px !important;
    max-height:218px !important;
    margin:0 auto !important;
    padding:26px 22px !important;
    display:flex !important;
    flex-direction:column !important;
    align-items:center !important;
    justify-content:center !important;
    border-radius:50% !important;
    background:#DCEBFC !important;
    border:2px solid #8DB4E2 !important;
    box-shadow:0 10px 26px rgba(31,78,121,.10) !important;
    cursor:pointer !important;
    color:#214F82 !important;
    text-align:center !important;
    position:relative !important;
    overflow:hidden !important;
    -webkit-tap-highlight-color:transparent !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"] button:hover{
    background:#D2E6FB !important;
    border-color:#6FA1D8 !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"] button > *{
    display:none !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"] button::before{
    content:"⇧" !important;
    display:block !important;
    width:auto !important;
    height:auto !important;
    margin:0 0 13px 0 !important;
    padding:0 !important;
    background:none !important;
    color:#24558B !important;
    font-size:58px !important;
    font-weight:500 !important;
    line-height:.82 !important;
    transform:none !important;
    flex:0 0 auto !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"] button::after{
    content:"Carica il tuo video" !important;
    display:block !important;
    width:150px !important;
    max-width:150px !important;
    margin:0 !important;
    padding:0 !important;
    color:#244B7C !important;
    font-size:17px !important;
    font-weight:800 !important;
    line-height:1.2 !important;
    white-space:normal !important;
    text-align:center !important;
    flex:0 0 auto !important;
}

/* Completed state stays inside the same circle; no filename underneath. */
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"])
[data-testid="stFileUploaderDropzone"] button,
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid*="UploadedFile"])
[data-testid="stFileUploaderDropzone"] button{
    background:#DDF5E8 !important;
    border-color:#69BE8E !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"])
[data-testid="stFileUploaderDropzone"] button::before,
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid*="UploadedFile"])
[data-testid="stFileUploaderDropzone"] button::before{
    content:"✓" !important;
    color:#238A50 !important;
    font-size:54px !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"])
[data-testid="stFileUploaderDropzone"] button::after,
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid*="UploadedFile"])
[data-testid="stFileUploaderDropzone"] button::after{
    content:"Video caricato" !important;
    color:#236B43 !important;
}

/* Small, real progress bar under the circle. No animated outer ring. */
.st-key-v73-upload-shell [role="progressbar"]{
    width:154px !important;
    max-width:154px !important;
    height:6px !important;
    min-height:6px !important;
    margin:12px auto 0 !important;
    border-radius:999px !important;
    overflow:hidden !important;
    background:rgba(34,197,94,.18) !important;
}
.st-key-v73-upload-shell [role="progressbar"] > div{
    height:100% !important;
    border-radius:999px !important;
    background:#22C55E !important;
}
.st-key-v73-upload-shell progress{
    width:154px !important;
    height:6px !important;
    margin:12px auto 0 !important;
    accent-color:#22C55E !important;
}

/* New video is centered directly below the upload circle. */
.st-key-v81_new_video{
    width:100% !important;
    display:flex !important;
    justify-content:center !important;
    align-items:center !important;
    text-align:center !important;
}
.st-key-v81_new_video > div,
.st-key-v81_new_video [data-testid="stButton"]{
    width:auto !important;
    margin:0 auto !important;
}
.st-key-v81_new_video button{
    width:auto !important;
    min-width:176px !important;
    min-height:44px !important;
    margin:10px auto 0 !important;
    padding:9px 18px !important;
    display:inline-flex !important;
    align-items:center !important;
    justify-content:center !important;
    border-radius:14px !important;
    background:#FFFFFF !important;
    color:#17324A !important;
    border:1px solid #9FCDEA !important;
    box-shadow:none !important;
    font-weight:800 !important;
}
.st-key-v81_new_video button p{
    display:block !important;
    margin:0 !important;
    color:#17324A !important;
}

@media(max-width:600px){
    .st-key-v73-upload-shell [data-testid="stFileUploader"]{
        max-width:286px !important;
    }
    .st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]{
        min-height:222px !important;
        padding:6px !important;
    }
    .st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"] button{
        width:208px !important;
        height:208px !important;
        min-width:208px !important;
        min-height:208px !important;
        max-width:208px !important;
        max-height:208px !important;
    }
    .st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"] button::before{
        font-size:54px !important;
        margin-bottom:12px !important;
    }
    .st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"] button::after{
        width:144px !important;
        max-width:144px !important;
        font-size:16px !important;
    }
}
</style>
"""

'''

anchor = 'with st.container(key="v73-upload-shell"):\n'
if anchor not in s:
    raise RuntimeError('V86 uploader container anchor not found')
s = s.replace(anchor, v86_fn + anchor, 1)

old_call = 'st.markdown(_gsf_v73_upload_css(video is not None), unsafe_allow_html=True)'
new_call = 'st.markdown(_gsf_v86_upload_css(video is not None), unsafe_allow_html=True)'
if old_call not in s:
    raise RuntimeError('V86 uploader CSS call anchor not found')
s = s.replace(old_call, new_call, 1)

s = s.replace(
    'Gaming Shorts Factory · V85 Upload Cleanup',
    'Gaming Shorts Factory · V86 Single Upload Circle'
)

out.write_text(s, encoding='utf-8')
print(f'V86 patch applied: {out}')
