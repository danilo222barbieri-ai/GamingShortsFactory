from pathlib import Path
import sys

p=Path(sys.argv[1])
s=p.read_text(encoding="utf-8")

checks={
    "single-rerun callback": "def _gsf_v1054_select_social" in s,
    "social callback wired": "on_click=_gsf_v1054_select_social" in s,
    "old explicit social rerun gone": 'st.session_state["social_selected_v59"] = _platform' not in s or "st.rerun()" not in s[s.find('key="social_upload_v59_'):s.find('key="social_upload_v59_')+1200],
    "editable game": '"Gioco"' in s and "social_game_" in s,
    "regenerate copy": '"RIGENERA TESTI"' in s,
    "styled composer": "gsf-v1054-social-style" in s,
    "AI persistent ad": "v1054_ad_after_ai" in s,
    "final action ad": "v1054_ad_after_final_action" in s,
    "final result ad": "v1054_ad_after_final_result" in s,
    "old AI ad removed": 'key="v1053_ad_ai"' not in s,
    "old final ad removed": 'key="v1053_ad_before_final"' not in s,
    "version": "Gaming Shorts Factory · V105.4 Social Stability" in s,
}
bad=[k for k,v in checks.items() if not v]
if bad:
    raise SystemExit("V105.4 contract failed: "+", ".join(bad))
compile(s,str(p),"exec")
print("V105.4 social stability contract: PASS")
