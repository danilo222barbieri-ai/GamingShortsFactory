from pathlib import Path
import tempfile, importlib.util
p=Path("/app/web/creator_learning_v138.py")
spec=importlib.util.spec_from_file_location("v138",p); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
with tempfile.TemporaryDirectory() as d:
 q=Path(d)/"profile.json"; x=m.load_profile(q); x=m.learn(x,{"signal":"published","cut_density":.9,"cold_open":1}); m.save_profile(q,x); y=m.load_profile(q)
 assert y["samples"]==1 and y["cut_density"]>.5
r=m.choose_ab({"hook_strength":.9,"payoff_delay_ratio":.1,"dead_air_ratio":0},{"hook_strength":.2,"payoff_delay_ratio":.8,"dead_air_ratio":.5})
assert r["winner"]=="A"
print("V138 Creator Learning + Retention A/B: PASS")
