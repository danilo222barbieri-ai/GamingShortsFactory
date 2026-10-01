from pathlib import Path

living = Path("/app/web/living_ui.py").read_text(encoding="utf-8")
apply = Path("/app/web/apply_v152_ui_reset.py").read_text(encoding="utf-8")
app = Path("/app/GamingShortsFactory_V152_UI_RESET.py").read_text(encoding="utf-8")

assert "def render_tail(" in living, "Living UI must expose a tail renderer"
assert "render_tail as _gsf_render_living_tail" in apply, "V152 generator must import Living tail renderer"
assert 's += "\\n# V153 Living tail override' in apply, "V152 generator must append Living CSS after the app"
assert apply.rfind("_gsf_render_living_tail()") > apply.find("_gsf_render_living_shell()"), "Tail renderer must execute after shell renderer"

print("V153 Living tail cascade contract: PASS")

# V153.19: mixed legacy global/editor CSS must be gone from the generated app.
for legacy in (
    'id="gsf-v80-ui-fix"',
    'id="gsf-v151-living-home"',
):
    assert legacy not in app, f"legacy global CSS survived V152 reset: {legacy}"

assert "_gsf_render_living_shell()" in app, "Living shell call missing from generated app"
assert "_gsf_render_living_tail()" in app, "Living tail call missing from generated app"
assert "st.html(LIVING_CSS)" in living, "Living CSS must mount through st.html"
assert "st.html(SHELL_HTML)" in living, "Living shell HTML must mount through st.html"
assert "st.html(tail_css)" in living, "Living tail CSS must mount through st.html"

print("V153.19 legacy CSS purge contract: PASS")
