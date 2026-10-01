from pathlib import Path
import tempfile, importlib.util, json
p=Path("/app/web/performance_learning_v140.py"); s=importlib.util.spec_from_file_location("v140",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
good={"watch_time_ratio":.9,"completion_rate":.85,"rewatch_rate":.4,"share_rate":.1,"save_rate":.1,"scroll_away_rate":.15}
bad={"watch_time_ratio":.2,"completion_rate":.1,"scroll_away_rate":.8}
assert m.performance_score(good)>m.performance_score(bad)
with tempfile.TemporaryDirectory() as d:
 q=Path(d)/"memory.json"; row=m.update_memory(q,"abc",{"ab_strategy":"A","game":"fortnite","platform":"youtube"},good)
 data=json.loads(q.read_text()); a=m.aggregate_preferences(data)
 assert row["performance_score"]>0 and a["samples"]==1 and a["best_strategy"]=="A"
print("V140 Performance Learning: PASS")
