from pathlib import Path
import importlib.util
p=Path("/app/web/render_director_v139.py"); spec=importlib.util.spec_from_file_location("v139",p); m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
pkg={"mount":{"trim":{"start":1,"end":14},"framing":{"smart_reframe":True,"zoom":1.2},"captions":{"mode":"semantic-auto"},"audio":{"normalize":True},"cinematic":{"cold_open":{"enabled":True,"duration":.7},"pattern_interrupts":[{"start":4,"duration":2,"action":"micro_cut"}],"replay":{"enabled":True}}}}
v={"cover_candidates":[{"path":"best.jpg","time":5,"score":.9}],"cleanup_recommended":True,"overlay_findings":[{"time":2}],"publish_guard":"clear"}
r=m.compile_render_plan(pkg,{"cut_density":.7},{"winner":"A","scores":{"A":.8,"B":.6}},v)
ops=[x["op"] for x in r["operations"]]
for x in ("trim","reframe","cold_open","pattern_interrupt","replay","captions","audio","creator_style","ab_strategy","cover","visual_cleanup"): assert x in ops,x
assert r["ready"]
print("V139 Render Director: PASS")
