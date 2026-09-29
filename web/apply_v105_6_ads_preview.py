from pathlib import Path

src=Path('/app/GamingShortsFactory_V105_5_REFINEMENTS.py')
out=Path('/app/GamingShortsFactory_V105_6_ADS_PREVIEW.py')
s=src.read_text(encoding='utf-8')

old='<aside class="v67-ad" aria-label="Spazio pubblicitario">Pubblicità</aside>'
count=s.count(old)
if count < 3:
    raise RuntimeError(f'V105.6 expected at least 3 ad slots, found {count}')

# Keep the replacement on one physical Python source line: these slots live
# inside existing st.markdown('...') calls in the generated app.
new='<aside class="v67-ad gsf-v1056-ad" aria-label="Spazio pubblicitario"><span class="gsf-v1056-ad-kicker">Pubblicità</span><span class="gsf-v1056-ad-preview">Anteprima</span><span class="gsf-v1056-ad-copy">Spazio annuncio responsive</span></aside>'
s=s.replace(old,new)

ads_css=r'''
_GSF_V1056_ADS_MODE=str(os.environ.get("GSF_ADS_MODE","preview") or "preview").strip().lower()
if _GSF_V1056_ADS_MODE not in {"preview","live","off"}:
    _GSF_V1056_ADS_MODE="preview"

if _GSF_V1056_ADS_MODE=="off":
    st.markdown("""
    <style id="gsf-v1056-ads-off">
    .gsf-v1056-ad{display:none !important}
    </style>
    """,unsafe_allow_html=True)
else:
    st.markdown("""
    <style id="gsf-v1056-ads">
    .gsf-v1056-ad{
        position:relative !important;
        box-sizing:border-box !important;
        width:min(970px,100%) !important;
        min-height:96px !important;
        margin:20px auto !important;
        padding:24px 18px 16px !important;
        display:flex !important;
        align-items:center !important;
        justify-content:center !important;
        text-align:center !important;
        overflow:hidden !important;
        border:1px solid rgba(118,154,183,.30) !important;
        border-radius:20px !important;
        background:
          radial-gradient(circle at 16% 10%,rgba(218,239,255,.72),transparent 34%),
          linear-gradient(180deg,#FFFFFF 0%,#F8FBFE 100%) !important;
        box-shadow:0 10px 28px rgba(31,78,112,.06) !important;
        color:#627B91 !important;
    }
    .gsf-v1056-ad-kicker{
        position:absolute !important;
        top:9px !important;
        left:14px !important;
        font-size:10px !important;
        line-height:1 !important;
        font-weight:850 !important;
        letter-spacing:.08em !important;
        text-transform:uppercase !important;
        color:#7890A4 !important;
    }
    .gsf-v1056-ad-preview{
        position:absolute !important;
        top:7px !important;
        right:12px !important;
        padding:4px 7px !important;
        border-radius:999px !important;
        background:#EEF6FC !important;
        border:1px solid #D8E8F3 !important;
        color:#668096 !important;
        font-size:9px !important;
        line-height:1 !important;
        font-weight:850 !important;
        letter-spacing:.06em !important;
        text-transform:uppercase !important;
    }
    .gsf-v1056-ad-copy{
        font-size:14px !important;
        line-height:1.25 !important;
        font-weight:750 !important;
        color:#70869A !important;
    }

    /* Keep ad footprint stable across Streamlit reruns. */
    .st-key-v1055_ad_engine,
    .st-key-v1055_ad_after_ai,
    .st-key-v1054_ad_after_final_action,
    .st-key-v1054_ad_after_final_result,
    .st-key-v1053_ad_footer{
        min-height:96px !important;
    }

    @media(max-width:750px){
        .gsf-v1056-ad{
            width:100% !important;
            min-height:104px !important;
            margin:16px auto !important;
            padding:26px 12px 16px !important;
            border-radius:17px !important;
        }
        .gsf-v1056-ad-copy{
            font-size:13px !important;
        }
        .st-key-v1055_ad_engine,
        .st-key-v1055_ad_after_ai,
        .st-key-v1054_ad_after_final_action,
        .st-key-v1054_ad_after_final_result,
        .st-key-v1053_ad_footer{
            min-height:104px !important;
        }
    }
    </style>
    """,unsafe_allow_html=True)

    if _GSF_V1056_ADS_MODE=="live":
        st.markdown("""
        <style id="gsf-v1056-ads-live">
        .gsf-v1056-ad-preview{display:none !important}
        </style>
        """,unsafe_allow_html=True)
'''

s=s.rstrip()+"\n\n"+ads_css.lstrip()
s=s.replace(
    'Gaming Shorts Factory · V105.5 Refinements',
    'Gaming Shorts Factory · V105.6 Ads Preview'
)

compile(s,str(out),'exec')
out.write_text(s,encoding='utf-8')
print(f'V105.6 ads preview applied: {out} | slots={count}')
