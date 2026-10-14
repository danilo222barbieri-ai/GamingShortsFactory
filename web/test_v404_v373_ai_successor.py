#!/usr/bin/env python3
from pathlib import Path

root = Path(__file__).resolve().parents[1]
v373 = (root / "web" / "fix_v373_creator_hub_spacing.py").read_text(encoding="utf-8")

assert 'id="ai404"' in v373, "V373 must detect the V404 AI successor"
assert "test_v404_crea_con_ia_simple.py" in v373, "V373 must validate V404 instead of applying V375"
assert "fix_v375_ai_header_breath.py" in v373, "legacy V375 fallback must remain for old AI"
assert "test_v375_ai_header_breath.py" in v373, "legacy V375 test fallback must remain"
assert "fix_v374_creator_hub_spacing_live.py" in v373, "V374 Hub continuation must remain"
assert "fix_v389_mobile_editor_bounded_reset.py" in v373, "editor continuation must remain"
assert "fix_v396_mobile_share_publish_surface.py" in v373, "share continuation must remain"

print("V404/V373 AI successor routing contract: PASS")
