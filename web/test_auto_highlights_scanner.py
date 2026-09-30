from web.auto_highlights.live_scanner import WindowSignal, rank_windows
from web.auto_highlights.sampling import sparse_sampling_plan, estimated_sample_ratio

def test_sparse_plan_does_not_decode_whole_live():
    plan=sparse_sampling_plan(3*60*60,sample_seconds=8,every_seconds=30)
    sampled=sum(x.duration_seconds for x in plan)
    assert sampled < 3*60*60*.30
    assert estimated_sample_ratio(sample_seconds=8,every_seconds=30) < .30

def test_ranker_prefers_reaction_in_reactions_mode():
    signals=[
      WindowSignal(0,30,action=.95,reaction=.10,audio_peak=.3),
      WindowSignal(60,90,action=.30,reaction=.95,audio_peak=.7,speech=.8),
    ]
    best=rank_windows(signals,engine="reazioni",limit=1)
    assert best[0].start_seconds==60

def test_ranker_avoids_duplicate_overlapping_highlights():
    signals=[
      WindowSignal(100,130,action=.9,reaction=.9),
      WindowSignal(105,135,action=.88,reaction=.88),
      WindowSignal(300,330,action=.8,reaction=.8),
    ]
    picked=rank_windows(signals,limit=3)
    assert len(picked)==2
