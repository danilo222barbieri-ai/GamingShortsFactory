from pathlib import Path
import ast

src=Path("/app/GamingShortsFactory_V151_LIVING_HOME.py")
out=Path("/app/GamingShortsFactory_V152_UI_RESET.py")
s=src.read_text(encoding="utf-8")

# V152 rule: presentation reset only.
# Keep every Python function, Streamlit widget, session-state key and backend call.
# Keep the Game Editor visual layer. Remove legacy visual-only layers elsewhere.
tree=ast.parse(s)
lines=s.splitlines(keepends=True)

EDITOR_MARKERS=(
    "editor_",
    "st-key-editor",
    "game editor",
    "game-editor",
    "editor 2027",
    "editor-2027",
    "gsf-editor",
    "editor2027",
    "game vision",
)

REMOVE_MARKERS=(
    "gsf-v151-living-home",
    "gsf-v151-bar",
    "_gsf_v89_upload_visual_html",
    "_gsf_v86_upload_css",
    "_gsf_v88_loaded_circle_html",
    'class="v67-ad',
    "class='v67-ad",
    "gsf-v1056-ad",
    'class="v67-footer',
    "class='v67-footer",
)

replacements=[]
removed_styles=0
removed_visual_calls=0
kept_editor_styles=0

for node in ast.walk(tree):
    if not isinstance(node,ast.Call):
        continue
    fn=node.func
    if not (isinstance(fn,ast.Attribute) and fn.attr=="markdown"):
        continue
    seg=ast.get_source_segment(s,node) or ""
    low=seg.lower()
    has_style="<style" in low
    has_script="<script" in low
    is_editor=any(m in low for m in EDITOR_MARKERS)
    force_remove=any(m.lower() in low for m in REMOVE_MARKERS)

    remove=False
    if force_remove:
        remove=True
        removed_visual_calls+=1
    elif has_style and is_editor:
        kept_editor_styles+=1
    elif has_style and not has_script:
        # Pure legacy CSS is presentation only. Strip it structurally.
        remove=True
        removed_styles+=1

    if remove:
        start=node.lineno-1
        end=getattr(node,"end_lineno",node.lineno)
        indent=lines[start][:node.col_offset]
        replacements.append((start,end,indent+'st.markdown("", unsafe_allow_html=True)\n'))

for start,end,repl in sorted(replacements,key=lambda x:x[0],reverse=True):
    lines[start:end]=[repl]

s="".join(lines)

# A tiny neutral reset is intentionally NOT a new theme. It only prevents
# unstyled legacy decorative HTML from reappearing while leaving native
# Streamlit controls fully functional. Editor selectors are not touched.
reset=r'''
st.markdown(r"""
<style id="gsf-v152-neutral-reset">
html,body,[data-testid="stAppViewContainer"],.stApp{
  background:#fff !important;
  color:#172033 !important;
}
[data-testid="stAppViewContainer"] .main .block-container{
  max-width:1200px !important;
  padding-top:1rem !important;
  padding-bottom:4rem !important;
}
.hero-title,.hero-sub,.hero-orb,.flow,
.v67-ad,.gsf-v1056-ad,.v67-footer,
.gsf-v151-brand,.gsf-v151-whisper,.gsf-v151-bar,
.gsf-account-fab{
  display:none !important;
}
.v67-badge{display:none !important}
.gsf-icon-title{
  display:block !important;
  margin:.8rem 0 !important;
  padding:0 !important;
  background:none !important;
  border:0 !important;
  box-shadow:none !important;
}
.gsf-section-sub,.gsf-command,.v65-quality-note{
  background:none !important;
  border:0 !important;
  box-shadow:none !important;
  padding:0 !important;
}
[data-testid="stFileUploader"]{
  opacity:1 !important;
  visibility:visible !important;
  pointer-events:auto !important;
  position:static !important;
  width:100% !important;
  max-width:720px !important;
  height:auto !important;
  min-height:0 !important;
  margin:1rem auto !important;
  padding:0 !important;
  border:0 !important;
  background:none !important;
  box-shadow:none !important;
  overflow:visible !important;
}
[data-testid="stFileUploaderDropzone"]{
  position:relative !important;
  inset:auto !important;
  width:100% !important;
  height:auto !important;
  min-height:120px !important;
  opacity:1 !important;
  visibility:visible !important;
  border:1px dashed #b7c2d0 !important;
  border-radius:12px !important;
  background:#fff !important;
}
[data-testid="stFileUploaderDropzone"] button{
  position:static !important;
  width:auto !important;
  height:auto !important;
  min-width:0 !important;
  min-height:0 !important;
  max-width:none !important;
  max-height:none !important;
  opacity:1 !important;
  visibility:visible !important;
  display:inline-flex !important;
  margin:0 !important;
  padding:.55rem .9rem !important;
  border-radius:8px !important;
}
[data-testid="stFileUploaderDropzone"] button::before,
[data-testid="stFileUploaderDropzone"] button::after{
  content:none !important;
  display:none !important;
}
[data-testid="stFileUploaderDropzoneInstructions"]{
  display:block !important;
}
</style>
""",unsafe_allow_html=True)
'''

# Insert the neutral reset immediately AFTER st.set_page_config.
# Streamlit requires set_page_config to remain the first UI command.
_page_tree=ast.parse(s)
_page_node=None
for _node in ast.walk(_page_tree):
    if not isinstance(_node,ast.Call):
        continue
    _fn=_node.func
    if (
        isinstance(_fn,ast.Attribute)
        and isinstance(_fn.value,ast.Name)
        and _fn.value.id=="st"
        and _fn.attr=="set_page_config"
    ):
        _page_node=_node
        break
if _page_node is None:
    raise RuntimeError("V152 st.set_page_config anchor not found")
_page_lines=s.splitlines(keepends=True)
_insert_at=getattr(_page_node,"end_lineno",_page_node.lineno)
_page_lines[_insert_at:_insert_at]=["\n"+reset+"\n"]
s="".join(_page_lines)

# Hard guards: functionality markers remain; old V151 shell is gone; Editor survives.
for marker in (
    'st.file_uploader(',
    'gsf_final_recipe',
    'creator',
    'social',
    'editor_',
):
    if marker not in s:
        raise RuntimeError("V152 functional marker missing: "+marker)
if 'id="gsf-v151-living-home"' in s:
    raise RuntimeError("V152 old V151 Home style survived")
if 'id="gsf-v151-bar"' in s:
    raise RuntimeError("V152 old V151 Game Bar survived")
if kept_editor_styles < 1:
    raise RuntimeError("V152 did not preserve any Editor style block")

s=s.replace(
    "Gaming Shorts Factory · V151 Living Home",
    "Gaming Shorts Factory · V152 UI Reset",
)
compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print(
    "V152 UI RESET applied:",
    out,
    "removed_styles=",removed_styles,
    "removed_visual_calls=",removed_visual_calls,
    "kept_editor_styles=",kept_editor_styles,
)
