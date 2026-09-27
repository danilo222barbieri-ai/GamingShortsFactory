from pathlib import Path
import re

src=Path('/app/GamingShortsFactory_V83_UPLOAD_FIX.py')
out=Path('/app/GamingShortsFactory_V84_MOBILE_MEDIA_FIX.py')
s=src.read_text(encoding='utf-8')

def sub_required(pattern,repl,label,count=1,flags=0):
    global s
    s2,n=re.subn(pattern,repl,s,count=count,flags=flags)
    if n != count:
        raise RuntimeError(f'V84 patch target not found: {label} (matches={n})')
    s=s2

# Browser-visible player URLs must use the public /media route, never localhost.
# Match the real V83 source flexibly instead of depending on exact whitespace.
sub_required(
    r'(?m)^(\s*)served_name\s*,\s*_\s*=\s*_gsf_serve_path\(source_path,\s*key\)\s*\n\1url\s*=\s*f["\']http://127\.0\.0\.1:\{GSF_PREVIEW_PORT\}/\{quote\(served_name\)\}["\']\s*$',
    lambda m: m.group(1)+'served_name, served_path = _gsf_serve_path(source_path, key)\n'+m.group(1)+'_media_rel = served_path.relative_to(GSF_RUNTIME_ROOT).as_posix()\n'+m.group(1)+'url = "/media/" + quote(_media_rel, safe="/")',
    'unified player public media url'
)

sub_required(
    r'(?m)^(\s*)_video_url\s*=\s*f["\']http://127\.0\.0\.1:\{GSF_PREVIEW_PORT\}/\{quote\(_safe_name\)\}["\']\s*$',
    lambda m: m.group(1)+'_media_rel = _preview_path.relative_to(GSF_RUNTIME_ROOT).as_posix()\n'+m.group(1)+'_video_url = "/media/" + quote(_media_rel, safe="/")',
    'main player public media url'
)

# Remove the separate filename badge below the circular uploader.
sub_required(
    r'(?ms)^(\s*)st\.markdown\(\s*\n\s*f["\']<div class=["\']v73-upload-meta["\'].*?unsafe_allow_html=True,?\s*\n\s*\)\s*\n',
    '',
    'remove filename badge'
)

css=r'''
st.markdown("""
<style id="gsf-v84-centered-upload">
.st-key-v73-upload-shell{
    width:100% !important;
    display:flex !important;
    justify-content:center !important;
    align-items:center !important;
}
.st-key-v73-upload-shell > div,
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
    margin:0 auto !important;
    border-radius:50% !important;
    box-sizing:border-box !important;
    overflow:visible !important;
    display:flex !important;
    align-items:center !important;
    justify-content:center !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzoneInstructions"],
.st-key-v73-upload-shell [data-testid="stFileUploaderFile"],
.st-key-v73-upload-shell [data-testid*="UploadedFile"],
.v73-upload-meta{display:none !important;}
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]::before{
    content:"Carica il tuo video" !important;
    left:50% !important;
    top:auto !important;
    bottom:15% !important;
    transform:translateX(-50%) !important;
    width:80% !important;
    text-align:center !important;
    white-space:nowrap !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]::after{
    inset:-6px !important;
    border-radius:50% !important;
    box-sizing:border-box !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([role="progressbar"])
[data-testid="stFileUploaderDropzone"]::after,
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has(progress)
[data-testid="stFileUploaderDropzone"]::after{
    opacity:1 !important;
    border:5px solid rgba(34,197,94,.22) !important;
    border-top-color:#22C55E !important;
    border-right-color:#22C55E !important;
    animation:gsfV81UploadRing .85s linear infinite !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"])
[data-testid="stFileUploaderDropzone"]::after,
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid*="UploadedFile"])
[data-testid="stFileUploaderDropzone"]::after{
    opacity:1 !important;
    border:5px solid #22C55E !important;
    animation:none !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"])
[data-testid="stFileUploaderDropzone"]::before,
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid*="UploadedFile"])
[data-testid="stFileUploaderDropzone"]::before{content:"" !important;}
@media(max-width:600px){
    .st-key-v73-upload-shell > div,
    .st-key-v73-upload-shell [data-testid="stFileUploader"],
    .st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]{
        width:min(300px,78vw) !important;
        max-width:min(300px,78vw) !important;
    }
    .st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]{height:min(300px,78vw) !important;}
}
</style>
""",unsafe_allow_html=True)
'''
s += "\n"+css+"\n"
s=s.replace('Gaming Shorts Factory · V83 Upload Fix','Gaming Shorts Factory · V84 Mobile Media Fix')
out.write_text(s,encoding='utf-8')
print('V84 patch applied:',out)
