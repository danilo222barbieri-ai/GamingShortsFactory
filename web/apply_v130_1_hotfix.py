from pathlib import Path

src=Path("/app/GamingShortsFactory_V130_ONE_CLICK_AI.py")
out=Path("/app/GamingShortsFactory_V130_1_HOTFIX.py")
s=src.read_text(encoding="utf-8")

# 1) Streamlit buttons cannot be restored by assigning values through
# session_state. Draft/session restore could contain this invisible sync key,
# causing StreamlitValueAssignmentNotAllowedError before the app rendered.
sync='st.button("SYNC SHORT READY",key="gsf_final_ready_sync_v111")'
if sync not in s:
    raise RuntimeError("V130.1 final-ready sync anchor missing")
s=s.replace(
    sync,
    '''try:
    st.session_state.pop("gsf_final_ready_sync_v111",None)
except Exception:
    pass
st.button("SYNC SHORT READY",key="gsf_final_ready_sync_v111")''',
    1,
)

# Never persist/restore the internal button key again.
skip_anchor='''_GSF_STATE_SKIP_PARTS = (
'''
if skip_anchor in s:
    # Existing persistent-state filter already excludes component-like state.
    # Add the exact internal sync key to the transient widget registry when
    # that registry exists, while keeping backwards compatibility.
    transient=r'''
try:
    if "gsf_final_ready_sync_v111" not in _GSF_TRANSIENT_WIDGET_EXACT:
        _GSF_TRANSIENT_WIDGET_EXACT.append("gsf_final_ready_sync_v111")
except Exception:
    pass

'''
    restore_anchor="_gsf_restore_persistent_state()\n"
    if restore_anchor in s:
        s=s.replace(restore_anchor,transient+restore_anchor,1)

# 2) Keep AI alternatives and One Click intelligence in the engine, but do not
# duplicate controls/status below the already-visible three scene choices.
alt='if _v125_rank>0 and _v125_alternates:'
if alt in s:
    s=s.replace(alt,'if False and _v125_rank>0 and _v125_alternates:',1)

one='if _v130_pack.get("ready") and _v130_short:'
if one in s:
    s=s.replace(one,'if False and _v130_pack.get("ready") and _v130_short:',1)

s=s.replace(
    "Gaming Shorts Factory · V130 One Click AI",
    "Gaming Shorts Factory · V130.1 Stability Hotfix",
)

compile(s,str(out),"exec")
out.write_text(s,encoding="utf-8")
print("V130.1 Stability Hotfix applied:",out)
