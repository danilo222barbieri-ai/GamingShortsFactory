from pathlib import Path
import sys

p=Path(sys.argv[1])
s=p.read_text(encoding="utf-8")
checks={
    "game detector": "def _gsf_v1053_detect_game",
    "halo detection": '"Halo Infinite"',
    "social uses detected game": '_game = _gsf_v1053_detect_game()',
    "source path considered": 'gsf_source_path',
    "social cloud removed": "controlla i dati prima di pubblicare",
    "publication spacing": 'height:16px',
    "subtitle spacing css": ".st-key-editor_sub_mode_v18",
    "persistent ai ad": 'with st.container(key="v1053_ad_ai")',
    "persistent final ad": 'v1053_ad_before_final',
    "persistent footer ad": 'v1053_ad_footer',
    "single mobile download": 'target="_blank"',
    "mobile preserves app": '_mobile=any(x in _ua',
    "old mobile share removed": "SALVA / CONDIVIDI SU MOBILE",
    "version": "Gaming Shorts Factory · V105.3 Polish",
}
errors=[]
for name,needle in checks.items():
    present=needle in s
    if name in {"social cloud removed","old mobile share removed"}:
        if present: errors.append(name)
    elif not present:
        errors.append(name)
if errors:
    raise SystemExit("V105.3 contract failed: "+", ".join(errors))
compile(s,str(p),"exec")
print("V105.3 polish contract: PASS")
