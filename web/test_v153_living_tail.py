from pathlib import Path

living = Path("/app/web/living_ui.py").read_text(encoding="utf-8")
apply = Path("/app/web/apply_v152_ui_reset.py").read_text(encoding="utf-8")

assert "def render_tail(" in living, "Living UI must expose a tail renderer"
assert "render_tail as _gsf_render_living_tail" in apply, "V152 generator must import Living tail renderer"
assert 's += "\\n# V153 Living tail override' in apply, "V152 generator must append Living CSS after the app"
assert apply.rfind("_gsf_render_living_tail()") > apply.find("_gsf_render_living_shell()"), "Tail renderer must execute after shell renderer"

print("V153 Living tail cascade contract: PASS")
