from pathlib import Path

src=Path('/app/GamingShortsFactory_V105_3_POLISH.py')
out=Path('/app/GamingShortsFactory_V105_4_SOCIAL_STABILITY.py')
s=src.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise RuntimeError(f'V105.4 target not found: {label}')
    s=s.replace(old,new,1)

# ------------------------------------------------------------------
# 1) Single-rerun social switching + better metadata suggestions.
# ------------------------------------------------------------------
helper=r'''
def _gsf_v1054_select_social(platform):
    st.session_state["social_selected_v59"]=str(platform)
    st.session_state["social_started_v59"]=False
    st.session_state.pop("social_error_v59",None)
    st.session_state.pop("social_auth_url_v77",None)
    st.session_state.pop("social_auth_platform_v77",None)


def _gsf_v1054_social_defaults(game,platform,mode):
    game=str(game or "").strip()
    known=bool(game and game.lower() not in {"gaming","gioco","game"})
    mode_text=str(mode or "").lower()

    if "director" in mode_text:
        phrase="Il momento che cambia la partita"
    elif "smart" in mode_text or "azione" in mode_text:
        phrase="Azione pura, zero tempi morti"
    elif "reaz" in mode_text:
        phrase="La reazione che vale la clip"
    elif "auto" in mode_text:
        phrase="Il momento più forte del gameplay"
    else:
        phrase="Il momento da non perdere"

    title=(f"{game} · {phrase}" if known else phrase)

    if known:
        description=(
            f"{game}: {phrase.lower()}. "
            "Clip pronta per la pubblicazione, selezionata dal gameplay."
        )
    else:
        description=(
            f"{phrase}. Clip selezionata dal gameplay. "
            "Aggiungi il nome del gioco se vuoi rendere titolo e hashtag più precisi."
        )

    tags=["#Gaming","#Gameplay"]
    if known:
        clean=re.sub(r"[^A-Za-z0-9]+","",game)
        if clean:
            tags.insert(0,"#"+clean)
    platform_l=str(platform or "").lower()
    if "youtube" in platform_l:
        tags.extend(["#Shorts","#GamingShorts"])
    elif "tiktok" in platform_l:
        tags.extend(["#GamingTok","#TikTokGaming"])
    elif "instagram" in platform_l:
        tags.extend(["#Reels","#GamingReels"])

    # Preserve order while removing duplicates.
    dedup=[]
    seen=set()
    for tag in tags:
        key=tag.lower()
        if key not in seen:
            seen.add(key)
            dedup.append(tag)

    return {
        "title":title[:100],
        "description":description[:1200],
        "hashtags":" ".join(dedup),
    }


'''
anchor='def _gsf_social_clean_description(pack):\n'
if anchor not in s:
    raise RuntimeError('V105.4 social helper anchor missing')
s=s.replace(anchor,helper+anchor,1)

old_switch='''                        if st.button(
                            _platform,
                            type=("primary" if _selected_social == _platform else "secondary"),
                            use_container_width=True,
                            key="social_upload_v59_" + _platform.lower(),
                        ):
                            st.session_state["social_selected_v59"] = _platform
                            st.session_state["social_started_v59"] = False
                            st.session_state.pop("social_error_v59", None)
                            st.session_state.pop("social_auth_url_v77", None)
                            st.session_state.pop("social_auth_platform_v77", None)
                            st.rerun()
'''
new_switch='''                        st.button(
                            _platform,
                            type=("primary" if _selected_social == _platform else "secondary"),
                            use_container_width=True,
                            key="social_upload_v59_" + _platform.lower(),
                            on_click=_gsf_v1054_select_social,
                            args=(_platform,),
                        )
'''
replace_once(old_switch,new_switch,'single-rerun social switching')

old_form='''                    _recipe = st.session_state.get("gsf_final_recipe", {}) or {}
                    _start = float(_recipe.get("start",0.0) or 0.0)
                    _game = _gsf_v1053_detect_game()
                    _tone = st.session_state.get("tono_social","Gaming forte")
                    _base_pack = _gsf_finalize_publish_pack(
                        _gsf_build_publish_pack(
                            _start,
                            platform=_platform_name,
                            game=_game,
                            tone=_tone,
                        )
                    )
                    _ctx = _gsf_publish_context_token(_base_pack)
                    _slug = _selected_social.lower()
                    _default_title = str(_base_pack.get("selected_title",_base_pack.get("title","")) or "")
                    _default_description = _gsf_social_clean_description(_base_pack)
                    _default_hashtags = " ".join(_base_pack.get("hashtags",[]) or [])

                    st.markdown('<div style="height:12px" aria-hidden="true"></div>', unsafe_allow_html=True)
                    _title = st.text_input(
                        "Titolo",
                        value=_default_title,
                        key=f"social_title_{_slug}_{_ctx}",
                    )
                    _description = st.text_area(
                        "Descrizione",
                        value=_default_description,
                        key=f"social_description_{_slug}_{_ctx}",
                        height=120,
                    )
                    _hashtags = st.text_input(
                        "Hashtag",
                        value=_default_hashtags,
                        key=f"social_hashtags_{_slug}_{_ctx}",
                    )
'''
new_form='''                    _recipe = st.session_state.get("gsf_final_recipe", {}) or {}
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
replace_once(old_form,new_form,'styled social composer')

# ------------------------------------------------------------------
# 2) Ads remain visible after CREA CON AI and CREA SHORT FINALE.
# ------------------------------------------------------------------
old_ai_ad='''    with st.container(key="v1053_ad_ai"):
        st.markdown('<aside class="v67-ad" aria-label="Spazio pubblicitario">Pubblicità</aside>', unsafe_allow_html=True)
'''
replace_once(old_ai_ad,'','remove old conditional AI ad')

ai_anchor='''    # La clip AI selezionata si finalizza soltanto in fondo.
    _ai_selected_start = st.session_state.get("auto_clip_scelta")
'''
ai_new='''    if modalita != "✋ Manuale":
        with st.container(key="v1054_ad_after_ai"):
            st.markdown(
                '<aside class="v67-ad" aria-label="Spazio pubblicitario">Pubblicità</aside>',
                unsafe_allow_html=True,
            )

    # La clip AI selezionata si finalizza soltanto in fondo.
    _ai_selected_start = st.session_state.get("auto_clip_scelta")
'''
replace_once(ai_anchor,ai_new,'persistent ad after AI flow')

old_final_ad='''        with st.container(key="v1053_ad_before_final"):
            st.markdown('<aside class="v67-ad" aria-label="Spazio pubblicitario">Pubblicità</aside>', unsafe_allow_html=True)
        st.divider()
'''
replace_once(old_final_ad,'        st.divider()\n','remove old pre-final ad')

old_create='''        if not _has_final:
            if st.button(
                "CREA SHORT FINALE",
                type="primary",
                use_container_width=True,
                key="create_final_short_v54"
            ):
                _final_dir=_gsf_session_mkdtemp("gsf_final_v54_")
'''
new_create='''        if not _has_final:
            _v1054_create_final_clicked=st.button(
                "CREA SHORT FINALE",
                type="primary",
                use_container_width=True,
                key="create_final_short_v54"
            )
            with st.container(key="v1054_ad_after_final_action"):
                st.markdown(
                    '<aside class="v67-ad" aria-label="Spazio pubblicitario">Pubblicità</aside>',
                    unsafe_allow_html=True,
                )
            if _v1054_create_final_clicked:
                _final_dir=_gsf_session_mkdtemp("gsf_final_v54_")
'''
replace_once(old_create,new_create,'ad below create final button')

final_download_tail='''                except Exception:
                    st.download_button(
                        "SCARICA",
                        _final_video,
                        "gaming_short_finale.mp4",
                        "video/mp4",
                        use_container_width=True,
                        key="download_final_v54_fallback",
                    )

            if st.session_state.get("show_social_publish_v54", False):
'''
final_download_new='''                except Exception:
                    st.download_button(
                        "SCARICA",
                        _final_video,
                        "gaming_short_finale.mp4",
                        "video/mp4",
                        use_container_width=True,
                        key="download_final_v54_fallback",
                    )

            with st.container(key="v1054_ad_after_final_result"):
                st.markdown(
                    '<aside class="v67-ad" aria-label="Spazio pubblicitario">Pubblicità</aside>',
                    unsafe_allow_html=True,
                )

            if st.session_state.get("show_social_publish_v54", False):
'''
replace_once(final_download_tail,final_download_new,'ad persists after final result')

# ------------------------------------------------------------------
# 3) Match the existing rounded/light GSF visual language.
# ------------------------------------------------------------------
s += r'''
st.markdown("""
<style id="gsf-v1054-social-style">
[class*="st-key-v1054_social_composer_"]{
    margin-top:14px !important;
    padding:18px 18px 16px !important;
    border:1px solid rgba(116,154,184,.24) !important;
    border-radius:22px !important;
    background:linear-gradient(180deg,rgba(247,252,255,.96),rgba(255,255,255,.98)) !important;
    box-shadow:0 10px 28px rgba(36,85,125,.07) !important;
}
[class*="st-key-v1054_social_composer_"] .v1054-social-head{
    display:flex;
    flex-direction:column;
    gap:3px;
    margin:0 0 12px;
    color:#17324A;
}
[class*="st-key-v1054_social_composer_"] .v1054-social-head strong{
    font-size:1.05rem;
    font-weight:850;
}
[class*="st-key-v1054_social_composer_"] .v1054-social-head span{
    font-size:.82rem;
    color:#70869A;
}
[class*="st-key-v1054_social_composer_"] input,
[class*="st-key-v1054_social_composer_"] textarea{
    border-radius:14px !important;
    border-color:#C7DCEB !important;
    background:#FFFFFF !important;
}
[class*="st-key-v1054_social_composer_"] textarea{
    min-height:112px !important;
}
[class*="st-key-v1054_social_composer_"] label{
    color:#29485F !important;
    font-weight:750 !important;
}
[class*="st-key-social_regenerate_"] button{
    border-radius:14px !important;
    border:1px solid #A9D2EA !important;
    background:#EFF8FE !important;
    color:#214F6E !important;
    font-weight:800 !important;
}
@media(max-width:750px){
    [class*="st-key-v1054_social_composer_"]{
        padding:15px 13px 14px !important;
        border-radius:18px !important;
    }
}
</style>
""",unsafe_allow_html=True)
'''

s=s.replace(
    'Gaming Shorts Factory · V105.3 Polish',
    'Gaming Shorts Factory · V105.4 Social Stability'
)

compile(s,str(out),'exec')
out.write_text(s,encoding='utf-8')
print(f'V105.4 social stability applied: {out}')
