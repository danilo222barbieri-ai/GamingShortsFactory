from pathlib import Path
import ast

src=Path('/app/GamingShortsFactory_V81_MOBILE_TABLET_POLISH.py')
out=Path('/app/GamingShortsFactory_V82_BETA_FIXPACK.py')
s=src.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise RuntimeError(f'V82 patch target not found: {label}')
    s=s.replace(old,new,1)

# ============================================================
# V82 FIX 1 — l'uploader NON è stato applicativo persistente.
# Il valore di st.file_uploader appartiene al frontend Streamlit e non può
# essere reimpostato da st.session_state. Escludiamo sia upload_v73 storico
# sia le chiavi generazionali V81 (upload_v73_0, upload_v73_1, ...).
# ============================================================
replace_once(
'''_GSF_STATE_SKIP_PARTS = (
    "secret", "password", "access_token", "refresh_token", "client_secret",
    "oauth", "credential", "inline_final_bytes", "editor_output_bytes",
    "editor_quick_bytes", "source_bytes",
)
''',
'''_GSF_STATE_SKIP_PARTS = (
    "secret", "password", "access_token", "refresh_token", "client_secret",
    "oauth", "credential", "inline_final_bytes", "editor_output_bytes",
    "editor_quick_bytes", "source_bytes",
    "upload_v73",
)
''',
'file uploader persistent-state exclusion')

# Pulisce eventuali chiavi uploader già rimaste nella sessione persistente
# PRIMA che Streamlit costruisca il nuovo widget.
restore_call='''_gsf_restore_persistent_state()
'''
guard='''_gsf_restore_persistent_state()

for _gsf_upload_state_key in list(st.session_state.keys()):
    if str(_gsf_upload_state_key).startswith("upload_v73_"):
        # Se arriva da un vecchio snapshot V81, non deve diventare un valore
        # assegnato server-side al file_uploader.
        try:
            st.session_state.pop(_gsf_upload_state_key,None)
        except Exception:
            pass
'''
# Inserisci solo sulla chiamata reale dopo la definizione della funzione.
idx=s.rfind(restore_call)
if idx<0:
    raise RuntimeError('V82 real restore call not found')
s=s[:idx]+guard+s[idx+len(restore_call):]

# ============================================================
# V82 FIX 2 — rimuove il testo tecnico "Materializza il gameplay..."
# dall'interfaccia, senza toccare i commenti o la logica sottostante.
# ============================================================
tree=ast.parse(s)
remove_ranges=[]
for node in ast.walk(tree):
    if not isinstance(node,ast.Expr) or not isinstance(node.value,ast.Call):
        continue
    call=node.value
    func=call.func
    if not (isinstance(func,ast.Attribute) and isinstance(func.value,ast.Name)
            and func.value.id=="st" and func.attr in {"write","caption","markdown","info"}):
        continue
    found=False
    for sub in ast.walk(call):
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
else:
    # Fallback conservativo: se la frase è ancora presente ma non è una
    # chiamata Streamlit semplice, svuota solo il testo visibile.
    s=s.replace(
        "Materializza il gameplay UNA sola volta in GSF_PREVIEW_DIR. Player, AI, editor, preview, batch e render finale riusano lo stesso file.",
        ""
    )

# ============================================================
# V82 UX — nuovo upload: feedback più evidente anche dopo il reset.
# ============================================================
extra_css=r'''
st.markdown("""
<style id="gsf-v82-upload-fix">
/* Il nuovo-video resta chiaramente separato dall'upload precedente. */
.st-key-v81_new_video button{
    background:#FFFFFF !important;
    color:#17324A !important;
    border:1px solid #9FCDEA !important;
    font-weight:750 !important;
}
.st-key-v81_new_video button p{color:#17324A !important}

/* Rafforza il feedback verde dell'uploader V81. */
.st-key-v73-upload-shell [role="progressbar"]{
    accent-color:#22C55E !important;
}
.st-key-v73-upload-shell progress{
    accent-color:#22C55E !important;
}
</style>
""",unsafe_allow_html=True)
'''
# Appendi il CSS; nessuna dimensione player viene modificata.
s += "\n"+extra_css+"\n"

s=s.replace(
    'Gaming Shorts Factory · V81 Mobile/Tablet',
    'Gaming Shorts Factory · V82 Beta Fixpack'
)

out.write_text(s,encoding='utf-8')
print(f'V82 debug UI blocks removed: {len(remove_ranges)}')
print(f'V82 patch applied: {out}')
