from pathlib import Path

HOME = Path('/app/web/home_v154_component/index.html')
APP = Path('/app/GamingShortsFactory_V154_STRUCTURAL_HOME.py')

PROFILE_MAP = {
    'auto': 'auto',
    'best': 'director',
    'action': 'action',
    'reaction': 'reaction',
}


def replace_once(text, old, new, label):
    if old not in text:
        raise RuntimeError('V291 anchor missing: ' + label)
    return text.replace(old, new, 1)


def patch_home():
    text = HOME.read_text(encoding='utf-8')
    before = text
    if 'V291 DIRECT AI ENGINE BRIDGE' in text:
        print('V291 Home bridge already applied:', HOME, flush=True)
        return

    old_cta = ''' cta.addEventListener("click",()=>{
   if(!engine)return;
   if(engine==="manual")shellNav("editor");
   else parentClick(["crea con ia","crea con ai","analizza con ia","genera con ia"]);
   value({event:engine==="manual"?"open_editor":"create_ai",duration,engine});
 });'''
    new_cta = ''' /* V291 DIRECT AI ENGINE BRIDGE */
 cta.addEventListener("click",()=>{
   if(!engine)return;
   if(engine==="manual"){
     shellNav("editor");
     value({event:"open_editor",duration,engine});
     return;
   }
   value({event:"create_ai",duration,engine});
 });'''
    text = replace_once(text, old_cta, new_cta, 'Home direct AI CTA')

    old_create = '''   if(action==="create"){
     const nextDuration=Number(e.data.duration)||duration;
     const nextEngine=String(e.data.engine||engine||"auto");
     setDuration(nextDuration,false);setEngine(nextEngine,false);
     parentClick(["crea con ia","crea con ai","analizza con ia","genera con ia"]);
     value({event:"create_ai",duration,engine:nextEngine});
     publishAiState();
   }'''
    new_create = '''   if(action==="create"){
     const nextDuration=Number(e.data.duration)||duration;
     const nextEngine=String(e.data.engine||engine||"auto");
     setDuration(nextDuration,false);setEngine(nextEngine,false);
     value({event:"create_ai",duration:nextDuration,engine:nextEngine});
     publishAiState();
   }'''
    text = replace_once(text, old_create, new_create, 'AI component create command')

    HOME.write_text(text, encoding='utf-8')
    print('V291 Home direct AI bridge applied:', HOME, 'changed=', text != before, flush=True)


def patch_app():
    text = APP.read_text(encoding='utf-8')
    before = text
    if '# V291 DIRECT AI ENGINE BRIDGE' in text:
        print('V291 app bridge already applied:', APP, flush=True)
        return

    state_anchor = '''        if _v154_engine in ("","auto","best","action","reaction","manual"):
            st.session_state["gsf_v154_engine"]=_v154_engine
'''
    state_block = state_anchor + '''
        # V291 DIRECT AI ENGINE BRIDGE
        # The custom AI surface is authoritative. Arm the real Streamlit AI
        # backend directly instead of clicking a hidden browser button.
        _gsf_v291_profile_map={
            "auto":"auto",
            "best":"director",
            "action":"action",
            "reaction":"reaction",
        }
        if _v154_event=="create_ai" and _v154_engine in _gsf_v291_profile_map:
            st.session_state["gsf_v291_engine_profile"]=_gsf_v291_profile_map[_v154_engine]
            st.session_state["gsf_v291_requested_duration"]=(
                30 if int(_v154_duration)==30 else 15
            )
            st.session_state["gsf_v291_ai_request"]={
                "engine":_v154_engine,
                "profile":_gsf_v291_profile_map[_v154_engine],
                "duration":30 if int(_v154_duration)==30 else 15,
            }
        elif _v154_engine=="manual" or _v154_event=="open_editor":
            st.session_state.pop("gsf_v291_engine_profile",None)
            st.session_state.pop("gsf_v291_ai_request",None)
'''
    text = replace_once(text, state_anchor, state_block, 'V154 AI event state')

    button_anchor = '''            _gsf_create_ai_clicked=st.button("CREA CON IA",use_container_width=True)
'''
    button_block = '''            _gsf_v291_ai_request=st.session_state.pop("gsf_v291_ai_request",None)
            _gsf_v291_direct_create=isinstance(_gsf_v291_ai_request,dict)
            _gsf_v291_profile=str(st.session_state.get("gsf_v291_engine_profile") or "")
            if _gsf_v291_profile in ("auto","director","action","reaction"):
                # Always enter the richest whole-video AI path. The V112+
                # ranker profile override below decides HOW candidates rank.
                modalita="🚀 AUTO TOTALE"
                _gsf_v291_duration=int(
                    st.session_state.get("gsf_v291_requested_duration",15) or 15
                )
                duration=float(30 if _gsf_v291_duration==30 else 15)
            _gsf_create_ai_clicked=(
                st.button("CREA CON IA",use_container_width=True)
                or _gsf_v291_direct_create
            )
'''
    text = replace_once(text, button_anchor, button_block, 'legacy AI create trigger')

    profile_old = '''    _mode=str(modalita or "").lower()
    if "reaz" in _mode or "reaction" in _mode:
        _profile="reaction"
    elif "azione" in _mode or "action" in _mode:
        _profile="action"
    elif "miglior" in _mode or "best" in _mode or "director" in _mode:
        _profile="director"
    else:
        _profile="auto"
'''
    profile_new = '''    _mode=str(modalita or "").lower()
    _v291_forced_profile=str(
        st.session_state.get("gsf_v291_engine_profile") or ""
    ).lower()
    if _v291_forced_profile in ("auto","director","action","reaction"):
        _profile=_v291_forced_profile
    elif "reaz" in _mode or "reaction" in _mode:
        _profile="reaction"
    elif "azione" in _mode or "action" in _mode:
        _profile="action"
    elif "miglior" in _mode or "best" in _mode or "director" in _mode:
        _profile="director"
    else:
        _profile="auto"
'''
    text = replace_once(text, profile_old, profile_new, 'Game Brain engine profile override')

    APP.write_text(text, encoding='utf-8')
    print('V291 app AI engine bridge applied:', APP, 'changed=', text != before, flush=True)


if __name__ == '__main__':
    for path in (HOME, APP):
        if not path.is_file():
            raise RuntimeError('V291 required file missing: ' + str(path))
    patch_home()
    patch_app()
