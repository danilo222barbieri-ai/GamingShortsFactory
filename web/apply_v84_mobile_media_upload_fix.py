from pathlib import Path
import re

src=Path('/app/GamingShortsFactory_V83_UPLOAD_FIX.py')
out=Path('/app/GamingShortsFactory_V84_MOBILE_MEDIA_FIX.py')
s=src.read_text(encoding='utf-8')

# V84: the V83 player already builds public /media URLs correctly through
# _gsf_media_relative() + _gsf_media_url(). The actual playback bug was the
# Nginx filesystem mapping, so do not rewrite player internals here.

# Remove the visible filename row below the circular uploader.
s,n=re.subn(
    r'''(?ms)^\s*st\.markdown\(\s*\n\s*f['"]<div class=["']v73-upload-meta["'].*?unsafe_allow_html=True,?\s*\n\s*\)\s*\n''',
    '',
    s,
    count=1,
)
print(f'V84 filename badge removed: {n}')

css=r'''
st.markdown("""
<style id="gsf-v84-centered-upload">
/* Keep the upload control centered as a single circular unit. */
.st-key-v73-upload-shell{
    width:100% !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploader"]{
    width:min(330px,82vw) !important;
    max-width:min(330px,82vw) !important;
    margin-left:auto !important;
    margin-right:auto !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]{
    width:min(330px,82vw) !important;
    height:min(330px,82vw) !important;
    min-height:0 !important;
    aspect-ratio:1/1 !important;
    margin-left:auto !important;
    margin-right:auto !important;
    border-radius:50% !important;
    box-sizing:border-box !important;
    overflow:visible !important;
    position:relative !important;
    display:flex !important;
    align-items:center !important;
    justify-content:center !important;
}

/* Hide Streamlit's file list/name after upload. */
.st-key-v73-upload-shell [data-testid="stFileUploaderFile"],
.st-key-v73-upload-shell [data-testid*="UploadedFile"],
.v73-upload-meta{
    display:none !important;
}

/* Hide duplicate Streamlit instructions; render one centered label. */
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzoneInstructions"]{
    visibility:hidden !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]::before{
    content:"Carica il tuo video" !important;
    position:absolute !important;
    left:50% !important;
    bottom:15% !important;
    transform:translateX(-50%) !important;
    width:82% !important;
    text-align:center !important;
    white-space:nowrap !important;
    font-weight:800 !important;
    color:#244B7C !important;
    z-index:3 !important;
    pointer-events:none !important;
}

/* Base ring: invisible until Safari/Streamlit reports upload progress. */
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]::after{
    content:"" !important;
    position:absolute !important;
    inset:-7px !important;
    border-radius:50% !important;
    box-sizing:border-box !important;
    border:6px solid transparent !important;
    opacity:0 !important;
    pointer-events:none !important;
    z-index:4 !important;
}
@keyframes gsfV84UploadRing{
    from{transform:rotate(0deg)}
    to{transform:rotate(360deg)}
}

/* Upload in progress: green animated ring around the circle. */
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([role="progressbar"])
[data-testid="stFileUploaderDropzone"]::after,
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has(progress)
[data-testid="stFileUploaderDropzone"]::after,
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid*="Progress"])
[data-testid="stFileUploaderDropzone"]::after{
    opacity:1 !important;
    border-color:rgba(34,197,94,.18) !important;
    border-top-color:#22C55E !important;
    border-right-color:#22C55E !important;
    animation:gsfV84UploadRing .8s linear infinite !important;
    filter:drop-shadow(0 0 5px rgba(34,197,94,.30));
}

/* Upload finished: full green ring, no filename below. */
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"])
[data-testid="stFileUploaderDropzone"]::after,
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid*="UploadedFile"])
[data-testid="stFileUploaderDropzone"]::after{
    opacity:1 !important;
    border-color:#22C55E !important;
    animation:none !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"])
[data-testid="stFileUploaderDropzone"]::before,
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid*="UploadedFile"])
[data-testid="stFileUploaderDropzone"]::before{
    content:"" !important;
}

/* Make Streamlit's own progress indicator green too, when present. */
.st-key-v73-upload-shell [role="progressbar"] > div{
    background:#22C55E !important;
}
.st-key-v73-upload-shell progress{
    accent-color:#22C55E !important;
}

@media(max-width:600px){
    .st-key-v73-upload-shell [data-testid="stFileUploader"],
    .st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]{
        width:min(300px,78vw) !important;
        max-width:min(300px,78vw) !important;
    }
    .st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]{
        height:min(300px,78vw) !important;
    }
}
</style>
""",unsafe_allow_html=True)
'''
s += "\n"+css+"\n"

s=s.replace(
    'Gaming Shorts Factory · V83 Upload Fix',
    'Gaming Shorts Factory · V84 Mobile Media Fix'
)

out.write_text(s,encoding='utf-8')
print(f'V84 patch applied: {out}')
