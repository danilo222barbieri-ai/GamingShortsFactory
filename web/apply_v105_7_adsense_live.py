from pathlib import Path
import re

src=Path('/app/GamingShortsFactory_V105_6_ADS_PREVIEW.py')
out=Path('/app/GamingShortsFactory_V105_7_ADSENSE_READY.py')
s=src.read_text(encoding='utf-8')

# V105.7: production-safe default. Preview is opt-in (used by the demo);
# live serving is enabled only when a valid publisher id + slot id exist.
s=s.replace(
    '_GSF_V1056_ADS_MODE=str(os.environ.get("GSF_ADS_MODE","preview") or "preview").strip().lower()',
    '_GSF_V1056_ADS_MODE=str(os.environ.get("GSF_ADS_MODE","off") or "off").strip().lower()',
    1,
)
s=s.replace(
    'if _GSF_V1056_ADS_MODE not in {"preview","live","off"}:\n    _GSF_V1056_ADS_MODE="preview"',
    'if _GSF_V1056_ADS_MODE not in {"preview","live","off"}:\n    _GSF_V1056_ADS_MODE="off"',
    1,
)

literal = '\'<aside class="v67-ad gsf-v1056-ad" aria-label="Spazio pubblicitario"><span class="gsf-v1056-ad-kicker">Pubblicità</span><span class="gsf-v1056-ad-preview">Anteprima</span><span class="gsf-v1056-ad-copy">Spazio annuncio responsive</span></aside>\''
if s.count(literal) != 6:
    raise RuntimeError(f'V105.7 expected exactly 6 V105.6 ad slots, found {s.count(literal)}')

first = s.find(literal)
line_start = s.rfind("\n", 0, first) + 1
helper = r'''
_GSF_V1057_ADS_MODE=str(os.environ.get("GSF_ADS_MODE","off") or "off").strip().lower()
if _GSF_V1057_ADS_MODE not in {"preview","live","off"}:
    _GSF_V1057_ADS_MODE="off"

_GSF_V1057_ADSENSE_CLIENT=str(os.environ.get("GSF_ADSENSE_CLIENT","") or "").strip()
_GSF_V1057_ADSENSE_SLOTS=[
    str(os.environ.get(f"GSF_ADSENSE_SLOT_{i}","") or "").strip()
    for i in range(1,7)
]
_GSF_V1057_CLIENT_RE=re.compile(r"^ca-pub-\d{10,20}$")
_GSF_V1057_SLOT_RE=re.compile(r"^\d{5,20}$")


def _gsf_v1057_ad_markup(index):
    idx=int(index)
    base=(
        f'<aside class="v67-ad gsf-v1056-ad gsf-v1057-ad gsf-v1057-slot-{idx}" '
        'aria-label="Pubblicità">'
    )

    if _GSF_V1057_ADS_MODE=="off":
        return base.replace('">','" style="display:none!important">',1)+'</aside>'

    if _GSF_V1057_ADS_MODE=="preview":
        return (
            base
            +'<span class="gsf-v1056-ad-kicker">Pubblicità</span>'
            +'<span class="gsf-v1056-ad-preview">Anteprima</span>'
            +'<span class="gsf-v1056-ad-copy">Spazio annuncio responsive</span>'
            +'</aside>'
        )

    slot=(
        _GSF_V1057_ADSENSE_SLOTS[idx-1]
        if 1 <= idx <= len(_GSF_V1057_ADSENSE_SLOTS)
        else ""
    )
    valid=bool(
        _GSF_V1057_CLIENT_RE.fullmatch(_GSF_V1057_ADSENSE_CLIENT)
        and _GSF_V1057_SLOT_RE.fullmatch(slot)
    )
    if not valid:
        # Never show a fake/empty ad in live mode if credentials are incomplete.
        return base.replace('">','" style="display:none!important">',1)+'</aside>'

    return (
        base[:-1]
        +f' gsf-v1057-live" data-ad-client="{html.escape(_GSF_V1057_ADSENSE_CLIENT,quote=True)}" '
        +f'data-ad-slot="{html.escape(slot,quote=True)}" data-gsf-placement="{idx}">'
        +'<span class="gsf-v1056-ad-kicker">Pubblicità</span>'
        +'<div class="gsf-v1057-ad-mount" aria-label="Annuncio Google"></div>'
        +'</aside>'
    )


'''
s=s[:line_start]+helper+s[line_start:]

for i in range(1,7):
    if literal not in s:
        raise RuntimeError(f'V105.7 missing ad literal for slot {i}')
    s=s.replace(literal,f'_gsf_v1057_ad_markup({i})',1)

extra_css=r'''
st.markdown("""
<style id="gsf-v1057-adsense-ready">
.gsf-v1057-live{
    min-height:112px !important;
    padding:26px 14px 12px !important;
    background:#fff !important;
}
.gsf-v1057-ad-mount{
    display:block !important;
    width:100% !important;
    min-height:72px !important;
}
.gsf-v1057-ad-mount .adsbygoogle{
    width:100% !important;
    min-height:70px !important;
}
.gsf-v1057-slot-1{margin-top:36px !important}
.gsf-v1057-slot-2{margin-top:28px !important}
.gsf-v1057-slot-3{margin-top:36px !important}
.gsf-v1057-slot-4{margin-top:52px !important}
.gsf-v1057-slot-5{margin-top:68px !important}
.gsf-v1057-slot-6{margin-top:44px !important}
@media(max-width:750px){
    .gsf-v1057-slot-1{margin-top:32px !important}
    .gsf-v1057-slot-2{margin-top:26px !important}
    .gsf-v1057-slot-3{margin-top:32px !important}
    .gsf-v1057-slot-4{margin-top:48px !important}
    .gsf-v1057-slot-5{margin-top:64px !important}
    .gsf-v1057-slot-6{margin-top:40px !important}
}
</style>
""",unsafe_allow_html=True)
'''

s=s.rstrip()+"\n\n"+extra_css.lstrip()
s=s.replace(
    'Gaming Shorts Factory · V105.6 Ads Preview',
    'Gaming Shorts Factory · V105.7 AdSense Ready'
)

compile(s,str(out),'exec')
out.write_text(s,encoding='utf-8')
print(f'V105.7 AdSense-ready applied: {out} | slots=6')
