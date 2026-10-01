from pathlib import Path
import importlib.util
p=Path("/app/web/long_form_director_v141.py"); s=importlib.util.spec_from_file_location("v141",p); m=importlib.util.module_from_spec(s); s.loader.exec_module(m)
rows=[{"start":i*30,"event":"reaction" if i==6 else "kill","brain_score":i/10} for i in range(10)]
plan=m.build_long_form(rows,8)
assert plan["enabled"] and plan["target_seconds"]==480
roles=[x["role"] for x in plan["chapters"]]
for r in ("cold_open","setup","escalation","peak","reaction","resolution"): assert r in roles
assert any(x["op"]=="insert_moment" for x in m.compile_long_form_operations(plan))
print("V141 Long-form Director: PASS")
