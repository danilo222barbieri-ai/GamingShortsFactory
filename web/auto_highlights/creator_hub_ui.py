"""Hidden Streamlit prototype for Creator Hub / Auto Highlights.

Not imported by production. It is intentionally self-contained so we can review
the UX before wiring OAuth, storage and the worker.
"""
from __future__ import annotations

def render_auto_highlights_prototype(st, *, connected_twitch=False, connected_youtube=False, folders=None,
                                     on_open_highlight=None):
    folders=folders or []
    st.markdown("""
    <style>
    .gsf-ah-wrap{border:1px solid rgba(120,145,190,.24);border-radius:24px;padding:20px;margin:12px 0;
      background:rgba(255,255,255,.035)}
    .gsf-ah-kicker{font-size:.78rem;letter-spacing:.14em;opacity:.65;font-weight:800}
    .gsf-ah-title{font-size:1.55rem;font-weight:900;margin:2px 0 4px}
    .gsf-ah-sub{opacity:.72;margin-bottom:14px}
    .gsf-ah-live{border-radius:18px;padding:13px 15px;margin:10px 0;background:rgba(255,255,255,.045)}
    .gsf-ah-score{font-weight:900}
    </style>""",unsafe_allow_html=True)
    st.markdown('<div class="gsf-ah-wrap"><div class="gsf-ah-kicker">CREATOR HUB</div>'
                '<div class="gsf-ah-title">AUTO HIGHLIGHTS</div>'
                '<div class="gsf-ah-sub">Tu fai la live. GSF trova i momenti da pubblicare.</div></div>',
                unsafe_allow_html=True)
    c1,c2=st.columns(2)
    with c1:
        st.button("Twitch ✓" if connected_twitch else "COLLEGA TWITCH",use_container_width=True,
                  disabled=connected_twitch,key="ah_proto_twitch")
    with c2:
        st.button("YouTube ✓" if connected_youtube else "COLLEGA YOUTUBE",use_container_width=True,
                  disabled=connected_youtube,key="ah_proto_youtube")
    enabled=st.toggle("Analizza automaticamente le mie live",value=connected_twitch or connected_youtube,
                      key="ah_proto_enabled")
    a,b,c=st.columns(3)
    with a: count=st.selectbox("Momenti",options=[3,5,10],index=1,key="ah_proto_count")
    with b: duration=st.selectbox("Durata",options=[15,30,60],index=1,key="ah_proto_duration")
    with c: engine=st.selectbox("Motore",options=["Automatico","Azione","Reazioni","Momento migliore"],key="ah_proto_engine")
    if folders:
        st.markdown("#### Le tue live")
        for folder in folders:
            title=folder.get("title") or "Live"
            items=folder.get("highlights") or []
            with st.expander(f"🎮 {title} · {len(items)} momenti"):
                for item in items:
                    score=item.get("score_percent",0); reason=item.get("reason","momento"); start=item.get("start_seconds",0)
                    st.markdown(f'<div class="gsf-ah-live"><span class="gsf-ah-score">🔥 {score}%</span> · '
                                f'{reason} · {int(start//60):02d}:{int(start%60):02d}</div>',unsafe_allow_html=True)
                    if st.button("APRI NEL GAME EDITOR",key=f"ah_proto_open_{item.get('id',start)}",use_container_width=True):
                        if callable(on_open_highlight):
                            on_open_highlight(folder,item)
    return {"enabled":enabled,"target_highlights":count,"target_duration":duration,"engine":engine}
