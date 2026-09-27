from pathlib import Path

src=Path('/app/GamingShortsFactory_V83_UPLOAD_FIX.py')
out=Path('/app/GamingShortsFactory_V84_MOBILE_MEDIA_FIX.py')
s=src.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise RuntimeError(f'V84 patch target not found: {label}')
    s=s.replace(old,new,1)

# Player: the media is already exposed by nginx at /media/<session>/media/<file>.
# Do not point the browser to the container-only 127.0.0.1 preview server.
old='''    served_name, _ = _gsf_serve_path(source_path, key)
    url = f"http://127.0.0.1:{GSF_PREVIEW_PORT}/{quote(served_name)}"
'''
new='''    served_name, served_path = _gsf_serve_path(source_path, key)
    try:
        _media_rel = served_path.relative_to(GSF_RUNTIME_ROOT).as_posix()
        url = "/media/" + quote(_media_rel, safe="/")
    except Exception:
        url = "/media/sessions/" + quote(str(GSF_SESSION_ID), safe="") + "/media/" + quote(served_name)
'''
replace_once(old,new,'unified player public media url')

# Main player uses the same public URL path.
old='''        _video_url=f"http://127.0.0.1:{GSF_PREVIEW_PORT}/{quote(_safe_name)}"
'''
new='''        try:
            _media_rel = _preview_path.relative_to(GSF_RUNTIME_ROOT).as_posix()
            _video_url = "/media/" + quote(_media_rel, safe="/")
        except Exception:
            _video_url = "/media/sessions/" + quote(str(GSF_SESSION_ID), safe="") + "/media/" + quote(_safe_name)
'''
replace_once(old,new,'main player public media url')

# Remove the separate filename badge under the uploader.
old='''if video is not None:
    st.markdown(
        f'<div class="v73-upload-meta" role="status" title="{html.escape(video.name, quote=True)}">{html.escape(video.name)}</div>',
        unsafe_allow_html=True,
    )
    if _gsf_recovered_source is not None:
'''
new='''if video is not None:
    if _gsf_recovered_source is not None:
'''
replace_once(old,new,'remove filename badge')

# Keep only one upload label and center the complete circular control on phones/tablets.
css=r'''
st.markdown("""
<style id="gsf-v84-centered-upload">
/* Center the uploader as one unit. */
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
/* Hide Streamlit's internal upload text/file list; our icon/status remains. */
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzoneInstructions"],
.st-key-v73-upload-shell [data-testid="stFileUploaderFile"],
.st-key-v73-upload-shell [data-testid*="UploadedFile"],
.v73-upload-meta{
    display:none !important;
}
/* One clean label, centered inside the circle. */
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
/* The ring is always geometrically aligned with the circle. */
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]::after{
    inset:-6px !important;
    border-radius:50% !important;
    box-sizing:border-box !important;
}
/* Completed upload: full green ring. */
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"])
[data-testid="stFileUploaderDropzone"]::after,
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid*="UploadedFile"])
[data-testid="stFileUploaderDropzone"]::after{
    opacity:1 !important;
    border:5px solid #22C55E !important;
    animation:none !important;
}
/* Remove the duplicate label after completion but keep the circle clean. */
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"])
[data-testid="stFileUploaderDropzone"]::before,
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid*="UploadedFile"])
[data-testid="stFileUploaderDropzone"]::before{
    content:"" !important;
}
@media(max-width:600px){
    .st-key-v73-upload-shell > div,
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

s=s.replace('Gaming Shorts Factory · V83 Upload Fix','Gaming Shorts Factory · V84 Mobile Media Fix')
out.write_text(s,encoding='utf-8')
print(f'V84 patch applied: {out}')
