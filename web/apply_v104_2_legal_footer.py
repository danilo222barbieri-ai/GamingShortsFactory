from pathlib import Path

src=Path('/app/GamingShortsFactory_V104_DIRECT_SOCIAL.py')
out=Path('/app/GamingShortsFactory_V104_2_LEGAL_FOOTER.py')
s=src.read_text(encoding='utf-8')

# Bounded V104.2 change: keep the known-good V104 app untouched and append
# only the legal links at the very end of the Streamlit page.
legal_footer = r'''
st.markdown("""
<div style="text-align:center;margin-top:18px;padding:14px 0 8px;font-size:.88rem;color:#60788d">
  <a href="/privacy" target="_blank" style="color:#60788d;text-decoration:none">Privacy</a>
  <span style="padding:0 10px">·</span>
  <a href="/terms" target="_blank" style="color:#60788d;text-decoration:none">Termini</a>
  <span style="padding:0 10px">·</span>
  <a href="/contact" target="_blank" style="color:#60788d;text-decoration:none">Contatti</a>
</div>
""", unsafe_allow_html=True)
'''

s = s.rstrip() + "\n\n" + legal_footer.lstrip()
compile(s, str(out), 'exec')
out.write_text(s, encoding='utf-8')
print(f'V104.2 legal footer applied and compiled: {out}')
