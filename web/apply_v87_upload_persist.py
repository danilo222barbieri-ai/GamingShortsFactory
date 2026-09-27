from pathlib import Path

src = Path('/app/GamingShortsFactory_V86_SINGLE_UPLOAD_CIRCLE.py')
out = Path('/app/GamingShortsFactory_V87_UPLOAD_PERSISTS.py')
s = src.read_text(encoding='utf-8')

anchor = '''/* Small, real progress bar under the circle. No animated outer ring. */'''
if anchor not in s:
    raise RuntimeError('V87 CSS anchor not found')

css = r'''/* V87: after Streamlit accepts a file, its Browse button can disappear.
   In that state the dropzone itself becomes the SAME circle, so the UI does
   not collapse. This rule only activates when an uploaded-file node exists. */
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"])
[data-testid="stFileUploaderDropzone"],
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid*="UploadedFile"])
[data-testid="stFileUploaderDropzone"]{
    width:218px !important;
    height:218px !important;
    min-width:218px !important;
    min-height:218px !important;
    max-width:218px !important;
    max-height:218px !important;
    margin:0 auto !important;
    padding:0 !important;
    display:flex !important;
    align-items:center !important;
    justify-content:center !important;
    position:relative !important;
    overflow:hidden !important;
    border-radius:50% !important;
    background:#DDF5E8 !important;
    border:2px solid #69BE8E !important;
    box-shadow:0 10px 26px rgba(31,78,121,.10) !important;
}
/* If Streamlit keeps a Browse button in this state, hide it so there is still
   exactly one circle rather than a circle inside a circle. */
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"])
[data-testid="stFileUploaderDropzone"] button,
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid*="UploadedFile"])
[data-testid="stFileUploaderDropzone"] button{
    display:none !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"])
[data-testid="stFileUploaderDropzone"]::before,
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid*="UploadedFile"])
[data-testid="stFileUploaderDropzone"]::before{
    content:"✓" !important;
    display:block !important;
    position:absolute !important;
    left:50% !important;
    top:38% !important;
    transform:translate(-50%,-50%) !important;
    color:#238A50 !important;
    font-size:54px !important;
    font-weight:700 !important;
    line-height:1 !important;
}
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"])
[data-testid="stFileUploaderDropzone"]::after,
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid*="UploadedFile"])
[data-testid="stFileUploaderDropzone"]::after{
    content:"Video caricato" !important;
    display:block !important;
    position:absolute !important;
    left:50% !important;
    top:66% !important;
    transform:translate(-50%,-50%) !important;
    width:150px !important;
    max-width:150px !important;
    color:#236B43 !important;
    font-size:17px !important;
    font-weight:800 !important;
    line-height:1.2 !important;
    text-align:center !important;
    white-space:normal !important;
}

'''
s = s.replace(anchor, css + anchor, 1)

mobile_anchor = '''    .st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"] button::before{\n        font-size:54px !important;'''
if mobile_anchor not in s:
    raise RuntimeError('V87 mobile anchor not found')
mobile_css = r'''    .st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"])
    [data-testid="stFileUploaderDropzone"],
    .st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid*="UploadedFile"])
    [data-testid="stFileUploaderDropzone"]{
        width:208px !important;
        height:208px !important;
        min-width:208px !important;
        min-height:208px !important;
        max-width:208px !important;
        max-height:208px !important;
    }
'''
s = s.replace(mobile_anchor, mobile_css + mobile_anchor, 1)

s = s.replace(
    'Gaming Shorts Factory · V86 Single Upload Circle',
    'Gaming Shorts Factory · V87 Upload Persists'
)

out.write_text(s, encoding='utf-8')
print(f'V87 patch applied: {out}')
