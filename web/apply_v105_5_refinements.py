from pathlib import Path
import re

src=Path('/app/GamingShortsFactory_V105_4_SOCIAL_STABILITY.py')
out=Path('/app/GamingShortsFactory_V105_5_REFINEMENTS.py')
s=src.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise RuntimeError(f'V105.5 target not found: {label}')
    s=s.replace(old,new,1)

# 1) Two persistent ad slots around the AI flow.
replace_once(
'''    st.caption(_engine_help.get(modalita, ""))
''',
'''    st.caption(_engine_help.get(modalita, ""))

    if modalita != "✋ Manuale":
        with st.container(key="v1055_ad_engine"):
            st.markdown(
                '<aside class="v67-ad" aria-label="Spazio pubblicitario">Pubblicità</aside>',
                unsafe_allow_html=True,
            )
''',
'engine ad slot')

replace_once(
'''    if modalita != "✋ Manuale":
        with st.container(key="v1054_ad_after_ai"):
            st.markdown(
                '<aside class="v67-ad" aria-label="Spazio pubblicitario">Pubblicità</aside>',
                unsafe_allow_html=True,
            )
''',
'''    if modalita != "✋ Manuale":
        with st.container(key="v1055_ad_after_ai"):
            st.markdown(
                '<aside class="v67-ad" aria-label="Spazio pubblicitario">Pubblicità</aside>',
                unsafe_allow_html=True,
            )
''',
'second persistent AI ad')

# 2) More room before Scegli la durata.
pos=s.find("Scegli la durata")
if pos<0:
    raise RuntimeError('V105.5 target not found: Scegli la durata')
line_start=s.rfind("\n",0,pos)+1
stmt_start=line_start
probe=line_start
for _ in range(10):
    prev=s.rfind("\n",0,max(0,probe-1))+1
    line=s[prev:probe].lstrip()
    if line.startswith("st.") or line.startswith("with st."):
        stmt_start=prev
        break
    if prev==0:
        break
    probe=prev
indent=re.match(r"[ \t]*",s[stmt_start:]).group(0)
spacer=indent+"st.markdown('<div style=\"height:20px\" aria-hidden=\"true\"></div>', unsafe_allow_html=True)\n"
s=s[:stmt_start]+spacer+s[stmt_start:]

# 3) Remove only the indicative Formato writing near Strumenti.
fmt_positions=[m.start() for m in re.finditer(r'["\']Formato["\']',s)]
fmt_target=None
for p in fmt_positions:
    if "Strumenti" in s[max(0,p-9000):p]:
        fmt_target=p
        break
if fmt_target is None:
    raise RuntimeError('V105.5 target not found: Strumenti Formato')
ls=s.rfind("\n",0,fmt_target)+1
le=s.find("\n",fmt_target)
if le<0:
    le=len(s)
line=s[ls:le]
if any(x in line for x in ("st.caption(","st.markdown(","st.write(","st.text(")):
    s=s[:ls]+s[le+1:]
else:
    quote=s[fmt_target]
    s=s[:fmt_target]+s[fmt_target:].replace(quote+"Formato"+quote,quote+" "+quote,1)

# 4) Exact no-speech wording.
if "Nessuna traccia parlata" not in s:
    raise RuntimeError('V105.5 target not found: no-speech wording')
s=s.replace("Nessuna traccia parlata","Nessuna traccia")

# 5) Social: connect first; connected accounts get empty fields with examples.
old_form='''                    _recipe = st.session_state.get("gsf_final_recipe", {}) or {}
                    _start = float(_recipe.get("start",0.0) or 0.0)
                    _detected_game = _gsf_v1053_detect_game()
                    _tone = st.session_state.get("tono_social","Gaming forte")
                    _base_pack = _gsf_finalize_publish_pack(
                        _gsf_build_publish_pack(
                            _start,
                            platform=_platform_name,
                            game=_detected_game,
                            tone=_tone,
                        )
                    )
                    _ctx = _gsf_publish_context_token(_base_pack)
                    _slug = _selected_social.lower()
                    _game_key=f"social_game_{_slug}_{_ctx}"
                    if _game_key not in st.session_state:
                        st.session_state[_game_key]=(
                            "" if _detected_game=="Gaming" else _detected_game
                        )

                    with st.container(key=f"v1054_social_composer_{_slug}"):
                        st.markdown(
                            '<div class="v1054-social-head"><strong>Dettagli '
                            +html.escape(_selected_social)
                            +'</strong><span>Modifica tutto prima di pubblicare</span></div>',
                            unsafe_allow_html=True,
                        )
                        _game_input=st.text_input(
                            "Gioco",
                            key=_game_key,
                            placeholder="Es. Halo Infinite",
                            help="Se il gioco non viene riconosciuto, scrivilo qui e rigenera i testi.",
                        )
                        _smart_game=str(_game_input or "").strip() or _detected_game
                        _smart_defaults=_gsf_v1054_social_defaults(
                            _smart_game,
                            _selected_social,
                            modalita,
                        )

                        _title_key=f"social_title_{_slug}_{_ctx}"
                        _description_key=f"social_description_{_slug}_{_ctx}"
                        _hashtags_key=f"social_hashtags_{_slug}_{_ctx}"
                        if _title_key not in st.session_state:
                            st.session_state[_title_key]=_smart_defaults["title"]
                        if _description_key not in st.session_state:
                            st.session_state[_description_key]=_smart_defaults["description"]
                        if _hashtags_key not in st.session_state:
                            st.session_state[_hashtags_key]=_smart_defaults["hashtags"]

                        if st.button(
                            "RIGENERA TESTI",
                            use_container_width=True,
                            key=f"social_regenerate_{_slug}_{_ctx}",
                        ):
                            st.session_state[_title_key]=_smart_defaults["title"]
                            st.session_state[_description_key]=_smart_defaults["description"]
                            st.session_state[_hashtags_key]=_smart_defaults["hashtags"]

                        _title=st.text_input("Titolo",key=_title_key)
                        _description=st.text_area(
                            "Descrizione",
                            key=_description_key,
                            height=120,
                        )
                        _hashtags=st.text_input("Hashtag",key=_hashtags_key)
'''
new_form='''                    _v1055_social_connected,_v1055_connect_error = _gsf_social_connection_status(_selected_social)
                    if not _v1055_social_connected:
                        st.session_state["social_auth_url_v77"]="/social-connect"
                        st.session_state["social_auth_platform_v77"]=_selected_social
                        st.session_state["social_error_v59"]=(
                            "Collega "+_selected_social+" per continuare con la pubblicazione."
                        )
                        _base_pack={}
                        _ctx="connect"
                        _slug=_selected_social.lower()
                        _title=_description=_hashtags=""
                    else:
                        st.session_state.pop("social_auth_url_v77",None)
                        st.session_state.pop("social_auth_platform_v77",None)
                        st.session_state["social_error_v59"]=""

                        _recipe = st.session_state.get("gsf_final_recipe", {}) or {}
                        _start = float(_recipe.get("start",0.0) or 0.0)
                        _detected_game = _gsf_v1053_detect_game()
                        _tone = st.session_state.get("tono_social","Gaming forte")
                        _base_pack = _gsf_finalize_publish_pack(
                            _gsf_build_publish_pack(
                                _start,
                                platform=_platform_name,
                                game=_detected_game,
                                tone=_tone,
                            )
                        )
                        _ctx = _gsf_publish_context_token(_base_pack)
                        _slug = _selected_social.lower()

                        with st.container(key=f"v1055_social_composer_{_slug}"):
                            st.markdown(
                                '<div class="v1055-social-head"><strong>Dettagli '
                                +html.escape(_selected_social)
                                +'</strong><span>Compila i dati da pubblicare</span></div>',
                                unsafe_allow_html=True,
                            )
                            _game_input=st.text_input(
                                "Gioco",
                                key=f"social_game_{_slug}_{_ctx}",
                                placeholder="Es. Halo Infinite",
                            )
                            _title=st.text_input(
                                "Titolo",
                                key=f"social_title_{_slug}_{_ctx}",
                                placeholder="Es. Halo Infinite · clutch all’ultimo secondo",
                            )
                            _description=st.text_area(
                                "Descrizione",
                                key=f"social_description_{_slug}_{_ctx}",
                                placeholder="Es. Il momento decisivo della partita, pronto per lo Short.",
                                height=120,
                            )
                            _hashtags=st.text_input(
                                "Hashtag",
                                key=f"social_hashtags_{_slug}_{_ctx}",
                                placeholder="Es. #HaloInfinite #Gaming #Shorts",
                            )
'''
replace_once(old_form,new_form,'connected-only social composer')

replace_once(
'''                    if st.button(
                        "PUBBLICA",
                        type="primary",
                        use_container_width=True,
                        key=f"social_publish_confirm_{_slug}_{_ctx}",
                    ):
''',
'''                    if _v1055_social_connected and st.button(
                        "PUBBLICA",
                        type="primary",
                        use_container_width=True,
                        key=f"social_publish_confirm_{_slug}_{_ctx}",
                    ):
''',
'connected-only publish')

s=s.replace('[class*="st-key-v1054_social_composer_"]','[class*="st-key-v1055_social_composer_"]')
s=s.replace('.v1054-social-head','.v1055-social-head')
s=re.sub(r'\n\[class\*="st-key-social_regenerate_"\] button\{.*?\n\}','',s,flags=re.S)

s=s.replace('Gaming Shorts Factory · V105.4 Social Stability','Gaming Shorts Factory · V105.5 Refinements')

compile(s,str(out),'exec')
out.write_text(s,encoding='utf-8')
print(f'V105.5 refinements applied: {out}')
