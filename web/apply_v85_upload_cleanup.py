from pathlib import Path

src = Path('/app/GamingShortsFactory_V84_MOBILE_MEDIA_FIX.py')
out = Path('/app/GamingShortsFactory_V85_UPLOAD_CLEANUP.py')
s = src.read_text(encoding='utf-8')

# Remove only the mobile beta caption under the duration controls.
old_beta = '''        if GSF_WEB_MODE:
            st.caption("Beta mobile: l’analisi viene eseguita sul server. Dopo il tap su CREA CON AI attendi il completamento senza chiudere la pagina.")
'''
if old_beta in s:
    s = s.replace(old_beta, '', 1)
    print('V85 mobile beta caption removed: 1')
else:
    print('V85 mobile beta caption removed: 0')

# Final uploader cleanup.
# - true circle on desktop and mobile
# - custom icon + text inside
# - no filename row
# - small real progress bar under the circle
# - centered New Video button
css = r'''
st.markdown("""
<style id="gsf-v85-upload-cleanup">
/* Reset the global V78 uploader skin so it cannot stretch into an oval. */
.st-key-v73-upload-shell{
    width:100% !important;
    display:block !important;
    text-align:center !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploader"]{
    width:100% !important;
    max-width:none !important;
    padding:0 !important;
    margin:0 !important;
    border:0 !important;
    border-radius:0 !important;
    background:transparent !important;
    box-shadow:none !important;
    overflow:visible !important;
    display:flex !important;
    flex-direction:column !important;
    align-items:center !important;
}

/* One real circle. Same geometry everywhere; only the diameter can shrink on phones. */
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]{
    --gsf-upload-size:min(252px,68vw);
    width:var(--gsf-upload-size) !important;
    min-width:var(--gsf-upload-size) !important;
    max-width:var(--gsf-upload-size) !important;
    height:var(--gsf-upload-size) !important;
    min-height:var(--gsf-upload-size) !important;
    max-height:var(--gsf-upload-size) !important;
    flex:0 0 var(--gsf-upload-size) !important;
    aspect-ratio:1 / 1 !important;
    margin:0 auto !important;
    padding:0 !important;
    border:3px dashed #86C6E8 !important;
    border-radius:50% !important;
    background:#F7FCFF !important;
    box-shadow:0 8px 24px rgba(27,75,113,.06) !important;
    box-sizing:border-box !important;
    position:relative !important;
    overflow:hidden !important;
}

/* Hide Streamlit's text/file metadata but keep the whole circle clickable. */
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzoneInstructions"],
.st-key-v73-upload-shell [data-testid="stFileUploaderFile"],
.st-key-v73-upload-shell [data-testid*="UploadedFile"],
.v73-upload-meta{
    display:none !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"] button{
    position:absolute !important;
    inset:0 !important;
    width:100% !important;
    height:100% !important;
    min-height:0 !important;
    margin:0 !important;
    padding:0 !important;
    border:0 !important;
    border-radius:50% !important;
    background:transparent !important;
    box-shadow:none !important;
    opacity:0 !important;
    z-index:10 !important;
    cursor:pointer !important;
}

/* Upload icon. */
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]::before{
    content:"⇧" !important;
    position:absolute !important;
    left:50% !important;
    top:36% !important;
    transform:translate(-50%,-50%) !important;
    width:auto !important;
    height:auto !important;
    color:#2B5985 !important;
    font-size:58px !important;
    line-height:1 !important;
    font-weight:500 !important;
    z-index:3 !important;
    pointer-events:none !important;
}

/* Upload label. This intentionally overrides the old ring pseudo-element. */
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]::after{
    content:"Carica il tuo video" !important;
    position:absolute !important;
    left:50% !important;
    top:67% !important;
    bottom:auto !important;
    inset:auto !important;
    transform:translate(-50%,-50%) !important;
    width:82% !important;
    height:auto !important;
    border:0 !important;
    border-radius:0 !important;
    background:transparent !important;
    box-shadow:none !important;
    filter:none !important;
    opacity:1 !important;
    animation:none !important;
    color:#244B7C !important;
    font-size:1rem !important;
    line-height:1.15 !important;
    font-weight:800 !important;
    text-align:center !important;
    white-space:normal !important;
    z-index:3 !important;
    pointer-events:none !important;
}

/* Explicitly kill every previous upload-ring state. */
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([role="progressbar"])
[data-testid="stFileUploaderDropzone"]::after,
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has(progress)
[data-testid="stFileUploaderDropzone"]::after,
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid*="Progress"])
[data-testid="stFileUploaderDropzone"]::after{
    content:"Carica il tuo video" !important;
    border:0 !important;
    animation:none !important;
    filter:none !important;
    opacity:1 !important;
}

/* Use Streamlit's real progress indicator as a small bar below the circle. */
.st-key-v73-upload-shell [role="progressbar"]{
    width:160px !important;
    max-width:160px !important;
    height:6px !important;
    min-height:6px !important;
    margin:12px auto 0 auto !important;
    border-radius:999px !important;
    overflow:hidden !important;
    background:rgba(34,197,94,.18) !important;
    position:relative !important;
}
.st-key-v73-upload-shell [role="progressbar"] > div{
    height:100% !important;
    border-radius:999px !important;
    background:#22C55E !important;
}
.st-key-v73-upload-shell progress{
    width:160px !important;
    height:6px !important;
    margin:12px auto 0 auto !important;
    accent-color:#22C55E !important;
}

/* Completed upload: clean success state inside the same circle. */
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"])
[data-testid="stFileUploaderDropzone"],
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid*="UploadedFile"])
[data-testid="stFileUploaderDropzone"]{
    border-style:solid !important;
    border-color:#22C55E !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"])
[data-testid="stFileUploaderDropzone"]::before,
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid*="UploadedFile"])
[data-testid="stFileUploaderDropzone"]::before{
    content:"✓" !important;
    color:#22C55E !important;
    font-size:54px !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"])
[data-testid="stFileUploaderDropzone"]::after,
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid*="UploadedFile"])
[data-testid="stFileUploaderDropzone"]::after{
    content:"Video caricato" !important;
    color:#1F7A43 !important;
}

/* + NUOVO VIDEO centered directly below the circle. */
.st-key-v81_new_video{
    width:100% !important;
    display:flex !important;
    justify-content:center !important;
    text-align:center !important;
}
.st-key-v81_new_video > div{
    width:auto !important;
    margin:0 auto !important;
}
.st-key-v81_new_video button{
    width:auto !important;
    min-width:172px !important;
    max-width:220px !important;
    min-height:2.6rem !important;
    margin:10px auto 0 auto !important;
    padding:.55rem 1.1rem !important;
    display:inline-flex !important;
    justify-content:center !important;
    align-items:center !important;
    border-radius:14px !important;
    background:#FFFFFF !important;
    color:#17324A !important;
    border:1px solid #9FCDEA !important;
    box-shadow:none !important;
    font-weight:750 !important;
}
.st-key-v81_new_video button p{
    color:#17324A !important;
    margin:0 !important;
}

@media(max-width:600px){
    .st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]{
        --gsf-upload-size:min(238px,68vw);
    }
    .st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]::before{
        font-size:52px !important;
    }
    .st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]::after{
        font-size:.95rem !important;
    }
}
</style>
""", unsafe_allow_html=True)
'''
s += "\n" + css + "\n"

s = s.replace(
    'Gaming Shorts Factory · V84 Mobile Media Fix',
    'Gaming Shorts Factory · V85 Upload Cleanup'
)

out.write_text(s, encoding='utf-8')
print(f'V85 patch applied: {out}')
