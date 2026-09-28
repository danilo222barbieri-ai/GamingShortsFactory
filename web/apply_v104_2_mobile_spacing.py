from pathlib import Path

src=Path('/app/GamingShortsFactory_V104_1_RENDER_DIAGNOSTICS.py')
out=Path('/app/GamingShortsFactory_V104_2_MOBILE_SPACING.py')
s=src.read_text(encoding='utf-8')

# Two graphic-only corrections requested after V104 testing.
# No render, editor, player, AI or social behavior changes.
final_anchor='''    if _show_final_flow:\n        st.divider()\n        st.markdown('<div class="gsf-icon-title">' + _gsf_v67_badge("play", "Crea lo Short finale", "peach") + '</div>', unsafe_allow_html=True)\n'''
final_new='''    if _show_final_flow:\n        st.divider()\n        st.markdown('<div class="gsf-section-gap-final" style="height:30px"></div>', unsafe_allow_html=True)\n        st.markdown('<div class="gsf-icon-title">' + _gsf_v67_badge("play", "Crea lo Short finale", "peach") + '</div>', unsafe_allow_html=True)\n'''
if final_anchor not in s:
    raise RuntimeError('V104.2 final section anchor missing')
s=s.replace(final_anchor,final_new,1)

social_anchor='''st.markdown('<div class="gsf-icon-title">' + _gsf_v67_badge("publish", "Pubblicazione diretta", "indigo") + '</div>', unsafe_allow_html=True)'''
social_new='''st.markdown('<div class="gsf-icon-title">' + _gsf_v67_badge("publish", "Pubblicazione diretta", "indigo") + '</div>', unsafe_allow_html=True)\nst.markdown('<div class="gsf-section-gap-social" style="height:30px"></div>', unsafe_allow_html=True)'''
if social_anchor not in s:
    raise RuntimeError('V104.2 social section anchor missing')
s=s.replace(social_anchor,social_new,1)

marker='Gaming Shorts Factory · V104.1 Render Diagnostics'
if marker not in s:
    raise RuntimeError('V104.2 marker missing')
s=s.replace(marker,'Gaming Shorts Factory · V104.2 Mobile Spacing',1)

out.write_text(s,encoding='utf-8')
print(f'V104.2 mobile spacing applied: {out}')
