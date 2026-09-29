from pathlib import Path
import re

src=Path('/app/GamingShortsFactory_V105_2_UI_SOCIAL_MOBILE.py')
out=Path('/app/GamingShortsFactory_V105_3_POLISH.py')
s=src.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise RuntimeError(f'V105.3 target not found: {label}')
    s=s.replace(old,new,1)

# ------------------------------------------------------------
# 1) Social game detection: never invent ARC Raiders.
#    Prefer evidence from the actual uploaded filename / transcript.
# ------------------------------------------------------------
game_helper=r'''
def _gsf_v1053_detect_game():
    """Best-effort game name from the current upload, never a stale default."""
    corpus_parts=[
        str(st.session_state.get("gsf_source_name","") or ""),
        str(st.session_state.get("gsf_source_path","") or ""),
        str(st.session_state.get("editor_sub_text","") or ""),
        str(st.session_state.get("hook_testo","") or ""),
    ]
    try:
        _upload_obj=st.session_state.get("upload_v73")
        _upload_name=str(getattr(_upload_obj,"name","") or "")
        if _upload_name:
            corpus_parts.append(_upload_name)
    except Exception:
        pass
    try:
        corpus_parts.append(json.dumps(
            st.session_state.get("gsf_ai_v3_diagnostics",{}) or {},
            ensure_ascii=False,
        ))
    except Exception:
        pass

    corpus=" ".join(corpus_parts).lower()
    corpus=re.sub(r"[_\\.-]+"," ",corpus)

    aliases=[
        ("Halo Infinite",("halo infinite","master chief","cortana","spartan")),
        ("Halo",("halo","master chief","spartan")),
        ("ARC Raiders",("arc raiders","arcraiders")),
        ("Fortnite",("fortnite","battle royale")),
        ("Call of Duty",("call of duty","modern warfare","black ops")),
        ("Warzone",("warzone",)),
        ("EA Sports FC",("ea sports fc","fc 27","fc27","ultimate team")),
        ("Minecraft",("minecraft","creeper","enderman")),
        ("GTA V",("gta v","gta 5","grand theft auto")),
        ("Apex Legends",("apex legends","apex")),
        ("Valorant",("valorant",)),
        ("Overwatch",("overwatch",)),
        ("Rocket League",("rocket league",)),
        ("Rainbow Six Siege",("rainbow six","siege")),
        ("Battlefield",("battlefield",)),
        ("Destiny 2",("destiny 2","destiny")),
        ("Helldivers 2",("helldivers 2","helldivers")),
        ("PUBG",("pubg",)),
    ]
    for canonical,markers in aliases:
        if any(marker in corpus for marker in markers):
            return canonical

    # Never reuse a stale game from a previous upload. If this video gives us
    # no real evidence, use a neutral label instead of inventing the game.
    return "Gaming"


'''
anchor='def _gsf_social_clean_description(pack):\n'
if anchor not in s:
    raise RuntimeError('V105.3 social helper anchor missing')
s=s.replace(anchor,game_helper+anchor,1)

# Replace stale game reads in final social UI and direct uploader fallback.
s=s.replace(
    'game = st.session_state.get("gioco", "Gaming")',
    'game = _gsf_v1053_detect_game()',
)
s=s.replace(
    '_game = st.session_state.get("gioco","Gaming")',
    '_game = _gsf_v1053_detect_game()',
)

# Old final-flow compatibility values must no longer default to ARC Raiders.
s=s.replace(
    'gioco = st.session_state.get("gioco", "ARC Raiders")',
    'gioco = _gsf_v1053_detect_game()',
)

# ------------------------------------------------------------
# 2) Social composer cleanup and spacing.
# ------------------------------------------------------------
replace_once(
'''            if st.session_state.get("show_social_publish_v54", False):
                st.markdown('<div class="gsf-icon-title">' + _gsf_v67_badge("publish", "Pubblicazione diretta", "indigo") + '</div>', unsafe_allow_html=True)
                _selected_social = st.session_state.get("social_selected_v59")
''',
'''            if st.session_state.get("show_social_publish_v54", False):
                st.markdown('<div class="gsf-icon-title">' + _gsf_v67_badge("publish", "Pubblicazione diretta", "indigo") + '</div>', unsafe_allow_html=True)
                st.markdown('<div style="height:16px" aria-hidden="true"></div>', unsafe_allow_html=True)
                _selected_social = st.session_state.get("social_selected_v59")
''',
'publication title spacing')

cloud='''                    st.markdown(
                        '<div style="margin-top:14px;padding:14px 16px;border:1px solid rgba(112,142,168,.28);'
                        'border-radius:18px;background:rgba(255,255,255,.72)">'
                        '<strong>'+html.escape(_selected_social)+'</strong> · controlla i dati prima di pubblicare'
                        '</div>',
                        unsafe_allow_html=True,
                    )
'''
replace_once(cloud,'','remove social cloud')
s=s.replace(
    '''                    _title = st.text_input(
''',
    '''                    st.markdown('<div style="height:12px" aria-hidden="true"></div>', unsafe_allow_html=True)
                    _title = st.text_input(
''',
    1,
)

# ------------------------------------------------------------
# 3) Subtitle spacing: keep controls exactly as-is, only add air above them.
# ------------------------------------------------------------
css=r'''
st.markdown("""
<style id="gsf-v1053-spacing">
/* A little breathing room between "Sottotitoli" and Nessuno/Automatici/Manuali. */
.st-key-editor_sub_mode_v18{
    margin-top:12px !important;
}
/* Social cards should not touch the Pubblicazione diretta heading. */
.st-key-v69_social_youtube,
.st-key-v69_social_tiktok,
.st-key-v69_social_instagram{
    margin-top:2px !important;
}
</style>
""",unsafe_allow_html=True)
'''
s += "\n"+css+"\n"

# ------------------------------------------------------------
# 4) Ads: stable keyed containers across Streamlit reruns.
# ------------------------------------------------------------
ai_ad='''    st.caption(_engine_help.get(modalita, ""))

    st.markdown('<aside class="v67-ad" aria-label="Spazio pubblicitario">Pubblicità</aside>', unsafe_allow_html=True)
'''
ai_ad_new='''    st.caption(_engine_help.get(modalita, ""))

    with st.container(key="v1053_ad_ai"):
        st.markdown('<aside class="v67-ad" aria-label="Spazio pubblicitario">Pubblicità</aside>', unsafe_allow_html=True)
'''
replace_once(ai_ad,ai_ad_new,'persistent AI ad')

# The V105.2 ad immediately before final creation gets its own stable owner.
old_final='''    if _show_final_flow:
        st.markdown('<aside class="v67-ad" aria-label="Spazio pubblicitario">Pubblicità</aside>', unsafe_allow_html=True)
        st.divider()
'''
new_final='''    if _show_final_flow:
        with st.container(key="v1053_ad_before_final"):
            st.markdown('<aside class="v67-ad" aria-label="Spazio pubblicitario">Pubblicità</aside>', unsafe_allow_html=True)
        st.divider()
'''
replace_once(old_final,new_final,'persistent ad before final')

# Global bottom ad: keep it anchored even after final render/social reruns.
bottom='''st.markdown('<aside class="v67-ad" aria-label="Spazio pubblicitario">Pubblicità</aside>', unsafe_allow_html=True)
st.markdown('<footer class="v67-footer">Gaming Shorts Factory · V105.2 UI Social Mobile<br>Beta web/mobile · Sessione persistente</footer>', unsafe_allow_html=True)
'''
bottom_new='''with st.container(key="v1053_ad_footer"):
    st.markdown('<aside class="v67-ad" aria-label="Spazio pubblicitario">Pubblicità</aside>', unsafe_allow_html=True)
st.markdown('<footer class="v67-footer">Gaming Shorts Factory · V105.3 Polish<br>Beta web/mobile · Sessione persistente</footer>', unsafe_allow_html=True)
'''
replace_once(bottom,bottom_new,'persistent footer ad')

# ------------------------------------------------------------
# 5) ONE SCARICA button.
#    Desktop: normal MP4 download.
#    iPhone/iPad/mobile: open the MP4 in a new tab, keeping the app alive;
#    from iOS video viewer the system share menu exposes "Salva video".
#    Remove the failed extra Web Share iframe/button completely.
# ------------------------------------------------------------
start='''            with _download_col:
                st.download_button(
                    "SCARICA",
                    _final_video,
                    "gaming_short_finale.mp4",
                    "video/mp4",
                    use_container_width=True,
                    key="download_final_v54"
                )

            # V105.2: expose the final MP4 through the authenticated /media route
'''
a=s.find(start)
if a<0:
    raise RuntimeError('V105.3 download block start missing')
end_marker='''            if st.session_state.get("show_social_publish_v54", False):
'''
b=s.find(end_marker,a)
if b<0:
    raise RuntimeError('V105.3 download block end missing')

download='''            with _download_col:
                try:
                    _share_root=Path(os.environ.get("GSF_RUNTIME_ROOT","/tmp/gsf-runtime"))/"sessions"/str(GSF_SESSION_ID)/"media"
                    _share_root.mkdir(parents=True,exist_ok=True)
                    _share_path=_share_root/"gaming_short_finale_share.mp4"
                    if (not _share_path.exists()) or _share_path.stat().st_size!=len(_final_video):
                        _share_path.write_bytes(bytes(_final_video))
                    _share_url=f"/media/{quote(str(GSF_SESSION_ID),safe='')}/media/gaming_short_finale_share.mp4"

                    try:
                        _ua=str(st.context.headers.get("User-Agent","") or "").lower()
                    except Exception:
                        _ua=""
                    _mobile=any(x in _ua for x in ("iphone","ipad","ipod","android","mobile"))

                    if _mobile:
                        st.markdown(
                            '<a href="'+html.escape(_share_url,quote=True)+'" target="_blank" rel="noopener" '
                            'style="display:flex;width:100%;min-height:2.55rem;box-sizing:border-box;'
                            'align-items:center;justify-content:center;border:1px solid #9FCDEA;'
                            'border-radius:12px;background:#fff;color:#17324A;text-decoration:none;'
                            'font-weight:800">SCARICA</a>',
                            unsafe_allow_html=True,
                        )
                    else:
                        st.download_button(
                            "SCARICA",
                            _final_video,
                            "gaming_short_finale.mp4",
                            "video/mp4",
                            use_container_width=True,
                            key="download_final_v54",
                        )
                except Exception:
                    st.download_button(
                        "SCARICA",
                        _final_video,
                        "gaming_short_finale.mp4",
                        "video/mp4",
                        use_container_width=True,
                        key="download_final_v54_fallback",
                    )

'''
s=s[:a]+download+s[b:]

# Remove the V105.2 version marker if any extra occurrence survived.
s=s.replace(
    'Gaming Shorts Factory · V105.2 UI Social Mobile',
    'Gaming Shorts Factory · V105.3 Polish'
)

compile(s,str(out),'exec')
out.write_text(s,encoding='utf-8')
print(f'V105.3 polish applied: {out}')
