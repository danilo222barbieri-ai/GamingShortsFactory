from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_home_reserves_only_real_gamebar_overlap():
    source = (ROOT / "web/home_v154_embed.py").read_text(encoding="utf-8")

    assert "GSF_V430_HOME_GAMEBAR_OVERLAP" in source
    assert "--gsf-v430-gamebar-overlap" in source
    assert "frame.getBoundingClientRect().bottom" in source
    assert "P.innerHeight-shellBottom" in source
    assert "Math.max(0,Math.ceil(frameBottom-intendedBottom))" in source
    assert "height:calc(100dvh - var(--gsf-v430-gamebar-overlap,0px))!important" in source
    assert "min-height:calc(100dvh - var(--gsf-v430-gamebar-overlap,0px))!important" in source
    # The legacy mobile stylesheet forces .ui to 100dvh; shrinking only #home154
    # leaves the action cards in the old full-height flow behind the Game Bar.
    assert "#home154 .ui{" in source
    assert "height:100%!important" in source
    assert "min-height:0!important" in source
    assert "max-height:100%!important" in source
    assert "#home154 #view{min-height:0!important}" in source
