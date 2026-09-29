from pathlib import Path

src=Path('/app/GamingShortsFactory_V98_2_UPLOAD_RECOVERY.py')
out=Path('/app/GamingShortsFactory_V98_3_HOME_COMPACT.py')
s=src.read_text(encoding='utf-8')

# V98.3 — compact the first screen without shrinking the approved upload circle.
# Goal: keep title, four-step guide, upload circle and real upload status visible
# together on a normal laptop viewport.
home_css=r'''
st.markdown("""
<style id="gsf-v98-3-home-compact">
/* Use the available viewport instead of leaving decorative empty space above. */
.block-container{
    padding-top:0 !important;
}

/* Hero: preserve typography, only remove vertical air. */
.gsf-hero{
    padding-top:2px !important;
    padding-bottom:4px !important;
    margin-top:-16px !important;
    margin-bottom:0 !important;
}
.hero-title{
    margin-top:0 !important;
    margin-bottom:0 !important;
    line-height:.92 !important;
}
.hero-sub{
    margin-top:6px !important;
    margin-bottom:4px !important;
}

/* Pull the approved upload circle slightly upward; do not resize it. */
.st-key-v73-upload-shell{
    margin-top:-22px !important;
}

@media(max-width:750px){
    .block-container{
        padding-top:0 !important;
    }
    .gsf-hero{
        padding-top:2px !important;
        padding-bottom:3px !important;
        margin-top:-8px !important;
    }
    .hero-sub{
        margin-top:5px !important;
        margin-bottom:3px !important;
    }
    .st-key-v73-upload-shell{
        margin-top:-14px !important;
    }
}
</style>
""",unsafe_allow_html=True)
'''
s += "\n"+home_css+"\n"

s=s.replace(
    'Gaming Shorts Factory · V98.2 Upload Recovery',
    'Gaming Shorts Factory · V98.3 Home Compact'
)

out.write_text(s,encoding='utf-8')
print(f'V98.3 patch applied: {out}')
