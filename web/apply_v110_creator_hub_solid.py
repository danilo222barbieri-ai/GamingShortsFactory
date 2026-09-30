from pathlib import Path

src=Path("/app/GamingShortsFactory_V109_ZOOMOUT.py")
out=Path("/app/GamingShortsFactory_V110_HUB_SOLID.py")
s=src.read_text(encoding="utf-8")

# V110 rule: Creator Hub is never translucent while open.
# Remove GPU backdrop blur from every historical Hub layer first.
replacements = [
    (
        "background:rgba(23,48,70,.34);\n  -webkit-backdrop-filter:blur(10px);\n  backdrop-filter:blur(10px);",
        "background:#EAF2F7;\n  -webkit-backdrop-filter:none;\n  backdrop-filter:none;",
    ),
    (
        "background:rgba(24,43,59,.62) !important;\n  -webkit-backdrop-filter:blur(11px) saturate(.96) !important;\n  backdrop-filter:blur(11px) saturate(.96) !important;",
        "background:#EAF2F7 !important;\n  -webkit-backdrop-filter:none !important;\n  backdrop-filter:none !important;",
    ),
    (
        "background:rgba(27,48,64,.72)!important;-webkit-backdrop-filter:blur(12px)!important;backdrop-filter:blur(12px)!important;opacity:1!important",
        "background:#EAF2F7!important;-webkit-backdrop-filter:none!important;backdrop-filter:none!important;opacity:1!important",
    ),
]
for old,new in replacements:
    s=s.replace(old,new)

lock = r'''
# ===== V110 CREATOR HUB SOLID LOCK =====
st.markdown("""
<style id="gsf-creator-hub-solid-v110">
/* Open Hub: fully opaque in every app phase, including render reruns. */
#gsf-creator-hub-portal-v107{
  opacity:1 !important;
  filter:none !important;
  mix-blend-mode:normal !important;
  isolation:isolate !important;
}
#gsf-creator-hub-portal-v107 .gsf-creator-hub-overlay,
.gsf-creator-hub-overlay{
  -webkit-backdrop-filter:none !important;
  backdrop-filter:none !important;
  filter:none !important;
  mix-blend-mode:normal !important;
  transition:none !important;
}
#gsf-creator-hub-portal-v107 .gsf-creator-hub-overlay.is-open,
#gsf-creator-hub-portal-v107 .gsf-creator-hub-overlay:target,
.gsf-creator-hub-overlay.is-open,
.gsf-creator-hub-overlay:target{
  opacity:1 !important;
  visibility:visible !important;
  pointer-events:auto !important;
  background:#EAF2F7 !important;
}
#gsf-creator-hub-portal-v107 .gsf-creator-hub-backdrop,
.gsf-creator-hub-backdrop{
  opacity:1 !important;
  background:#EAF2F7 !important;
  -webkit-backdrop-filter:none !important;
  backdrop-filter:none !important;
  filter:none !important;
  mix-blend-mode:normal !important;
}
#gsf-creator-hub-portal-v107 .gsf-creator-hub-shell,
.gsf-creator-hub-shell{
  opacity:1 !important;
  background:#F7FBFF !important;
  -webkit-backdrop-filter:none !important;
  backdrop-filter:none !important;
  filter:none !important;
  mix-blend-mode:normal !important;
  isolation:isolate !important;
  contain:paint !important;
  border-color:#D3E3ED !important;
  box-shadow:0 30px 86px rgba(19,45,65,.30) !important;
}
#gsf-creator-hub-portal-v107 .gsf-creator-hub-head,
.gsf-creator-hub-head{
  opacity:1 !important;
  background:#FFFFFF !important;
  -webkit-backdrop-filter:none !important;
  backdrop-filter:none !important;
  filter:none !important;
  mix-blend-mode:normal !important;
}
#gsf-creator-hub-portal-v107 .gsf-creator-hub-frame,
.gsf-creator-hub-frame{
  opacity:1 !important;
  background:#F7FBFF !important;
  -webkit-backdrop-filter:none !important;
  backdrop-filter:none !important;
  filter:none !important;
  mix-blend-mode:normal !important;
  color-scheme:light !important;
}
</style>
""", unsafe_allow_html=True)
# ===== /V110 CREATOR HUB SOLID LOCK =====
'''
s=s.rstrip()+"\n\n"+lock.lstrip()

compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print("V110 Creator Hub solid lock applied:",out)
