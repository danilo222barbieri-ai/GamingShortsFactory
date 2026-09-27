from pathlib import Path
import ast
import re

src=Path('/app/GamingShortsFactory_V80_UI_AUTOSUB_BETA.py')
out=Path('/app/GamingShortsFactory_V80_1_HOTFIX.py')
s=src.read_text(encoding='utf-8')

# ------------------------------------------------------------
# V80.1 — never restore Streamlit button values from disk.
# Streamlit 1.64 correctly rejects session_state preassignment for buttons.
# Build the list automatically from the actual app source so the fix covers
# current buttons and dynamic f-string button keys, not only v69_choose_0.
# ------------------------------------------------------------
tree=ast.parse(s)
exact=set()
prefixes=set()

def _f_prefix(node):
    if not isinstance(node, ast.JoinedStr):
        return ""
    pieces=[]
    for part in node.values:
        if isinstance(part, ast.Constant) and isinstance(part.value,str):
            pieces.append(part.value)
        else:
            break
    return "".join(pieces)

for node in ast.walk(tree):
    if not isinstance(node,ast.Call):
        continue
    fn=node.func
    name=fn.attr if isinstance(fn,ast.Attribute) else (fn.id if isinstance(fn,ast.Name) else "")
    if name not in {"button","download_button","form_submit_button","link_button"}:
        continue
    for kw in node.keywords:
        if kw.arg!="key":
            continue
        if isinstance(kw.value,ast.Constant) and isinstance(kw.value.value,str):
            exact.add(kw.value.value)
        elif isinstance(kw.value,ast.JoinedStr):
            p=_f_prefix(kw.value)
            if p:
                prefixes.add(p)

runtime_guard=f'''
_GSF_TRANSIENT_WIDGET_EXACT = {repr(sorted(exact))}
_GSF_TRANSIENT_WIDGET_PREFIXES = {repr(tuple(sorted(prefixes)))}

def _gsf_is_transient_widget_key(key):
    key=str(key or "")
    return (
        key in _GSF_TRANSIENT_WIDGET_EXACT
        or any(key.startswith(prefix) for prefix in _GSF_TRANSIENT_WIDGET_PREFIXES)
    )
'''

anchor='def _gsf_restore_persistent_state():\n'
if anchor not in s:
    raise RuntimeError('V80.1 restore anchor not found')
s=s.replace(anchor,runtime_guard+'\n'+anchor,1)

old='''        if key in st.session_state or key in _GSF_STATE_SKIP_EXACT:
            continue
        if any(part in str(key).lower() for part in _GSF_STATE_SKIP_PARTS):
            continue
'''
new='''        if key in st.session_state or key in _GSF_STATE_SKIP_EXACT:
            continue
        if _gsf_is_transient_widget_key(key):
            continue
        if any(part in str(key).lower() for part in _GSF_STATE_SKIP_PARTS):
            continue
'''
if old not in s:
    raise RuntimeError('V80.1 restore filter target not found')
s=s.replace(old,new,1)

old='''        if key.startswith("_") or key in _GSF_STATE_SKIP_EXACT:
            continue
        if any(part in key.lower() for part in _GSF_STATE_SKIP_PARTS):
            continue
'''
new='''        if key.startswith("_") or key in _GSF_STATE_SKIP_EXACT:
            continue
        if _gsf_is_transient_widget_key(key):
            continue
        if any(part in key.lower() for part in _GSF_STATE_SKIP_PARTS):
            continue
'''
if old not in s:
    raise RuntimeError('V80.1 save filter target not found')
s=s.replace(old,new,1)

# ------------------------------------------------------------
# V80.1 — subtitle language. Tiny's auto-detection on very short/noisy gaming
# clips can choose the wrong script. Beta default is Italian, while the gaming
# prompt still preserves English game/weapon/player terms.
# ------------------------------------------------------------
def force_language(func_name):
    global s
    start=s.find(f'def {func_name}(')
    if start<0:
        raise RuntimeError(f'V80.1 function not found: {func_name}')
    nxt=s.find('\ndef ',start+5)
    end=len(s) if nxt<0 else nxt
    block=s[start:end]
    if re.search(r'language\s*=\s*None',block):
        block2=re.sub(r'language\s*=\s*None','language="it"',block,count=1)
    else:
        m=re.search(r'(\.transcribe\(\s*\n?\s*[^,\n]+,)',block)
        if not m:
            raise RuntimeError(f'V80.1 transcribe call not found in {func_name}')
        block2=block[:m.end()]+ '\n            language="it",' + block[m.end():]
    s=s[:start]+block2+s[end:]

force_language('_gsf_transcribe_editor_scene')
force_language('_gsf_render_transcribe_words')

# Footer hotfix marker.
s=s.replace(
    'Gaming Shorts Factory · V80 UI + Auto Sub',
    'Gaming Shorts Factory · V80.1 Hotfix'
)

out.write_text(s,encoding='utf-8')
print(f'V80.1 transient exact={len(exact)} prefixes={len(prefixes)}')
print(f'V80.1 hotfix applied: {out}')
