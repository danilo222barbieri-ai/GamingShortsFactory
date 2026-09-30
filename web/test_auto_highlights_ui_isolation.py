from pathlib import Path

def test_prototype_is_not_wired_into_production():
    root=Path(__file__).resolve().parent
    prod=(root/"apply_v107_production_ui.py").read_text(encoding="utf-8")
    assert "creator_hub_ui" not in prod
    assert "render_auto_highlights_prototype" not in prod
