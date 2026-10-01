from pathlib import Path
import tempfile,sys

sys.path.insert(0,"/app/web")
from content_memory_v145 import candidate_fingerprint,memory_record,inspect_memory,upsert_memory,save_local,load_local

a={"start":10.0,"event":"kill","rank":1,"mount":{"trim":{"start":0,"end":15},"hook":"A"}}
b={"start":28.0,"event":"kill","rank":2,"mount":{"trim":{"start":0,"end":15},"hook":"B"}}
fa=candidate_fingerprint("source-1",a)
fb=candidate_fingerprint("source-1",b)
assert len(fa)==64 and len(fb)==64 and fa!=fb

ra=memory_record("source-1",a,{"game":"fortnite","status":"rendered"})
rb=memory_record("source-1",b,{"game":"fortnite","status":"rendered"})
state0=inspect_memory([],ra)
assert not state0["duplicate"] and state0["recommendation"]=="new_content"
rows=upsert_memory([],ra)
state1=inspect_memory(rows,ra)
assert state1["duplicate"] and state1["source_count"]==1
rows=upsert_memory(rows,rb)
state2=inspect_memory(rows,rb)
assert state2["duplicate"] and state2["source_count"]==2

with tempfile.TemporaryDirectory() as td:
    p=Path(td)/"memory.json"
    save_local(p,rows)
    assert len(load_local(p))==2

if len(sys.argv)>1:
    server=Path(sys.argv[1]).read_text(encoding="utf-8")
    for marker in (
        "/content-memory/check","/content-memory/record","content-memory/{sid}/memory_v145.json",
        "GSF_V145_MEMORY_RECORDED",
    ):
        assert marker in server,marker

if len(sys.argv)>2:
    app=Path(sys.argv[2]).read_text(encoding="utf-8")
    for marker in (
        "_gsf_v145_memory_api","GSF_V145_MEMORY_CHECK","GSF_V145_MEMORY_FINAL",
    ):
        assert marker in app,marker

print("V145 Persistent Content Memory: PASS")
