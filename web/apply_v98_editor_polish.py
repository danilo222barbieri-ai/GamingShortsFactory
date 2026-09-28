from pathlib import Path

src=Path('/app/GamingShortsFactory_V95_RENDER_TEXT_POLISH.py')
out=Path('/app/GamingShortsFactory_V98_EDITOR_POLISH.py')
s=src.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise RuntimeError(f'V98 patch target not found: {label}')
    s=s.replace(old,new,1)

replace_once(
'''                        _trim=st.slider(
                            "IN / OUT",0.0,float(max(.5,_idur)),
''',
'''                        _trim=st.slider(
                            "IN / OUT · ritaglio scena",0.0,float(max(.5,_idur)),
''',
'inline trim label')

replace_once(
'''                        _istart=float(_trim[0])
                        _iend=float(_trim[1])
                        _ilen=max(.1,_iend-_istart)

                        # Stato grafico indipendente dalla trascrizione.
''',
'''                        _istart=float(_trim[0])
                        _iend=float(_trim[1])
                        _ilen=max(.1,_iend-_istart)
                        st.caption(
                            f"IN {_istart:.1f}s · OUT {_iend:.1f}s · DURATA {_ilen:.1f}s"
                        )

                        # Stato grafico indipendente dalla trascrizione.
''',
'inline trim summary')

replace_once(
'''                            _ith,_itr,_itc=st.columns([.50,.25,.25],gap="small")
''',
'''                            _ith,_itr,_itc=st.columns([.50,.25,.25],gap="medium")
''',
'toolbar spacing')

replace_once(
'''                                    "↶ RESET TUTTO",use_container_width=True,key=f"reset_inline_all_v29_{_this_inline_id}",
''',
'''                                    "↶ RESET CONTROLLI",use_container_width=True,key=f"reset_inline_all_v29_{_this_inline_id}",
''',
'reset label')

replace_once(
'''                            _fc,_ic,_rc=st.columns([.30,.35,.35],gap="small")
''',
'''                            st.caption("ANTEPRIMA LIVE · queste regolazioni sono le stesse usate dal render finale.")
                            _fc,_ic,_rc=st.columns([.34,.33,.33],gap="medium")
''',
'editor controls spacing')

replace_once(
'''                                with st.popover("INQUADRATURA",use_container_width=True):
                                    st.session_state[_zoom_key]=st.slider("Zoom",1.0,2.0,float(st.session_state[_zoom_key]),.05,key=f"inline_zoom_widget_v18_{_this_inline_id}")
''',
'''                                with st.popover("INQUADRATURA",use_container_width=True):
                                    st.caption("Zoom e posizione vengono applicati identici al render.")
                                    st.session_state[_zoom_key]=st.slider("Zoom",1.0,2.0,float(st.session_state[_zoom_key]),.05,key=f"inline_zoom_widget_v18_{_this_inline_id}")
''',
'framing help')

replace_once(
'''                                with st.popover("REGOLAZIONI",use_container_width=True):
                                    _reg=st.selectbox("Parametro",["Volume","Luminosità","Contrasto","Velocità"],key=f"inline_reg_v18_{_this_inline_id}")
''',
'''                                with st.popover("REGOLAZIONI",use_container_width=True):
                                    st.caption("Audio, immagine e velocità restano sincronizzati con la preview.")
                                    _reg=st.selectbox("Parametro",["Volume","Luminosità","Contrasto","Velocità"],key=f"inline_reg_v18_{_this_inline_id}")
''',
'adjustment help')

s=s.replace(
    'Gaming Shorts Factory · V95 Render Text Polish',
    'Gaming Shorts Factory · V98 Editor Polish'
)

out.write_text(s,encoding='utf-8')
print(f'V98 patch applied: {out}')
