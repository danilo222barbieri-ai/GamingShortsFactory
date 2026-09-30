from pathlib import Path

src=Path("/app/GamingShortsFactory_V110_HUB_SOLID.py")
out=Path("/app/GamingShortsFactory_V111_FINAL_VISIBLE.py")
s=src.read_text(encoding="utf-8")

# Persist the successful stable MP4 to the already configured bucket before
# telling the browser it is ready. This survives Railway redeploys.
anchor='''                        except Exception as _job_exc:
                            print("GSF_FINAL_JOB_READY_WARN",repr(str(_job_exc)),flush=True)
                        try:
                            _u=__import__("urllib.request",fromlist=["Request","urlopen"])
                            _payload=__import__("json").dumps({"title":"Short pronto","body":"Il tuo Short è pronto. Tocca per aprire lo Share Hub.","url":"/#share-hub","tag":"gsf-short-ready"}).encode("utf-8")
'''
replacement='''                        except Exception as _job_exc:
                            print("GSF_FINAL_JOB_READY_WARN",repr(str(_job_exc)),flush=True)
                        try:
                            _u=__import__("urllib.request",fromlist=["Request","urlopen"])
                            _persist_payload=__import__("json").dumps({
                                "path":str(_gsf_stable),
                                "started_at":float(_job.get("started_at") or 0.0),
                            },ensure_ascii=False).encode("utf-8")
                            _persist_req=_u.Request(
                                "http://127.0.0.1:8502/final/persist",
                                data=_persist_payload,
                                headers={"Content-Type":"application/json","X-GSF-Session-ID":_gsf_sid},
                                method="POST",
                            )
                            _u.urlopen(_persist_req,timeout=90).read()
                            print("GSF_FINAL_BUCKET_PERSISTED","sid="+_gsf_sid,flush=True)
                        except Exception as _persist_exc:
                            print("GSF_FINAL_BUCKET_PERSIST_WARN",repr(str(_persist_exc)),flush=True)
                        try:
                            _u=__import__("urllib.request",fromlist=["Request","urlopen"])
                            _payload=__import__("json").dumps({"title":"Short pronto","body":"Il tuo Short è pronto. Tocca per aprire lo Share Hub.","url":"/#share-hub","tag":"gsf-short-ready"}).encode("utf-8")
'''
if anchor not in s:
    raise RuntimeError("V111 final persist anchor missing")
s=s.replace(anchor,replacement,1)

# Browser poller clicks this invisible button exactly when /job/status becomes
# ready. The click causes a normal Streamlit rerun, and the existing restore
# block hydrates publication_final_bytes/publication_ready from the stable MP4.
sync=r'''
# ===== V111 FINAL READY SYNC =====
st.markdown("""
<style id="gsf-final-ready-sync-style-v111">
.st-key-gsf_final_ready_sync_v111,
[class*="st-key-gsf_final_ready_sync_v111"]{
  position:fixed !important;
  left:-10000px !important;
  top:-10000px !important;
  width:1px !important;
  height:1px !important;
  overflow:hidden !important;
  opacity:0 !important;
  pointer-events:none !important;
}
</style>
""", unsafe_allow_html=True)
st.button("SYNC SHORT READY",key="gsf_final_ready_sync_v111")
# ===== /V111 FINAL READY SYNC =====
'''
s=s.rstrip()+"\n\n"+sync.lstrip()

compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print("V111 final visibility + persistence applied:",out)
