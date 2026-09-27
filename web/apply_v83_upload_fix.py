from pathlib import Path
import ast

src=Path('/app/GamingShortsFactory_V82_BETA_FIXPACK.py')
out=Path('/app/GamingShortsFactory_V83_UPLOAD_FIX.py')
s=src.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise RuntimeError(f'V83 patch target not found: {label}')
    s=s.replace(old,new,1)

# ============================================================
# V83 FIX — file_uploader: non cancellare il valore appena caricato.
# V82 ripuliva upload_v73_* ad OGNI rerun; su iPhone il PUT finiva (204),
# poi il rerun cancellava il widget prima che l'app potesse usarlo.
# ============================================================
bad_guard='''_gsf_restore_persistent_state()

for _gsf_upload_state_key in list(st.session_state.keys()):
    if str(_gsf_upload_state_key).startswith("upload_v73_"):
        # Se arriva da un vecchio snapshot V81, non deve diventare un valore
        # assegnato server-side al file_uploader.
        try:
            st.session_state.pop(_gsf_upload_state_key,None)
        except Exception:
            pass
'''
replace_once(
    bad_guard,
    '''_gsf_restore_persistent_state()
''',
    'remove uploader self-clearing loop'
)

# Torniamo a una chiave stabile. Il pulsante NUOVO VIDEO già pulisce lo stato
# nel callback, quindi non serve cambiare chiave ad ogni generazione.
replace_once(
'''        key=f"upload_v73_{int(st.session_state.get('gsf_upload_generation',0) or 0)}"
    )
''',
'''        key="upload_v73"
    )
''',
'stable uploader key'
)

# La persistenza V82 già esclude "upload_v73", quindi il widget non viene
# mai ricostruito server-side da session_state dopo un refresh.

# ============================================================
# V83 FIX — rimuovi davvero il testo tecnico mostrato da Streamlit "magic".
# Era un'espressione stringa standalone, non necessariamente st.write(...).
# ============================================================
tree=ast.parse(s)
remove_ranges=[]
for node in ast.walk(tree):
    if not isinstance(node,ast.Expr):
        continue
    found=False
    for sub in ast.walk(node.value):
        if isinstance(sub,ast.Constant) and isinstance(sub.value,str):
            if "Materializza il gameplay UNA sola volta" in sub.value:
                found=True
                break
    if found:
        remove_ranges.append((node.lineno,node.end_lineno))

if remove_ranges:
    lines=s.splitlines(True)
    doomed=set()
    for a,b in remove_ranges:
        doomed.update(range(a-1,b))
    s=''.join(line for i,line in enumerate(lines) if i not in doomed)

# ============================================================
# V83 UX — testo upload esplicito + feedback verde.
# ============================================================
css=r'''
st.markdown("""
<style id="gsf-v83-upload-fix">
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]{
    position:relative !important;
}

/* Il testo non deve dipendere dal markup interno di Streamlit/iOS. */
.st-key-v73-upload-shell [data-testid="stFileUploaderDropzone"]::before{
    content:"Carica il tuo video";
    position:absolute;
    left:50%;
    bottom:18%;
    transform:translateX(-50%);
    width:82%;
    text-align:center;
    font-weight:800;
    font-size:clamp(.88rem,3.7vw,1.05rem);
    color:#244B7C;
    line-height:1.1;
    pointer-events:none;
    z-index:3;
}

/* In upload: anello verde animato. */
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([role="progressbar"])
[data-testid="stFileUploaderDropzone"]::after,
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has(progress)
[data-testid="stFileUploaderDropzone"]::after{
    opacity:1 !important;
    border-top-color:#22C55E !important;
    border-right-color:#22C55E !important;
    border-bottom-color:rgba(34,197,94,.22) !important;
    border-left-color:rgba(34,197,94,.22) !important;
    animation:gsfV81UploadRing .85s linear infinite !important;
}

/* Streamlit mostra anche la propria progress bar: rendiamola verde. */
.st-key-v73-upload-shell [role="progressbar"] > div,
.st-key-v73-upload-shell progress{
    accent-color:#22C55E !important;
}

/* Dopo upload il testo lascia spazio allo stato "Video caricato". */
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid="stFileUploaderFile"])
[data-testid="stFileUploaderDropzone"]::before,
.st-key-v73-upload-shell [data-testid="stFileUploader"]:has([data-testid*="UploadedFile"])
[data-testid="stFileUploaderDropzone"]::before{
    content:"";
}
</style>
""",unsafe_allow_html=True)
'''
s += "\n"+css+"\n"

s=s.replace(
    'Gaming Shorts Factory · V82 Beta Fixpack',
    'Gaming Shorts Factory · V83 Upload Fix'
)

out.write_text(s,encoding='utf-8')
print(f'V83 removed technical magic blocks: {len(remove_ranges)}')
print(f'V83 patch applied: {out}')
