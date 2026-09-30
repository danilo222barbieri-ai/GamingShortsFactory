from web.auto_highlights.live_scanner import WindowSignal
from web.auto_highlights.models import HighlightCandidate
from web.auto_highlights.refine import dense_region, refine_candidate
from web.auto_highlights.two_pass import two_pass_highlights

def test_dense_region_adds_context():
    c=HighlightCandidate(100,130,.9,"azione")
    assert dense_region(c)==(80,150)

def test_refinement_centers_on_local_peak():
    rows=[
      WindowSignal(90,95,action=.05),
      WindowSignal(105,110,action=.98,audio_peak=.8),
      WindowSignal(125,130,action=.08),
    ]
    out=refine_candidate(rows,engine="azione")
    assert out and out.start_seconds<=105<=out.end_seconds
    assert out.duration>=15

def test_two_pass_uses_dense_loader():
    coarse=[WindowSignal(100,130,action=.95),WindowSignal(300,330,action=.8)]
    calls=[]
    def loader(a,b):
        calls.append((a,b))
        mid=(a+b)/2
        return [WindowSignal(mid-2,mid+2,action=.99)]
    out=two_pass_highlights(coarse,dense_loader=loader,engine="azione",limit=2)
    assert len(out)==2 and len(calls)==2
