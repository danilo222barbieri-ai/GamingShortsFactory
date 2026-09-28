from pathlib import Path

src=Path('/app/GamingShortsFactory_V104_1_RENDER_DIAGNOSTICS.py')
out=Path('/app/GamingShortsFactory_V104_2_LEGAL_FOOTER.py')
s=src.read_text(encoding='utf-8')

# Add the two public legal links to the existing bottom footer only.
needle='Beta web/mobile · Sessione persistente'
pos=s.find(needle)
if pos < 0:
    raise RuntimeError('V104.2 footer marker missing')

# Find the Streamlit markdown statement containing the footer marker and append
# a compact legal-links row immediately after it, preserving the current UI.
line_start=s.rfind('\n',0,pos)+1
line_end=s.find('\n',pos)
if line_end < 0:
    line_end=len(s)
insert='''\nst.markdown("""<div style="text-align:center;margin-top:8px;font-size:.88rem;color:#60788d"><a href="/privacy" target="_blank" style="color:#60788d;text-decoration:none">Privacy</a><span style="padding:0 10px">·</span><a href="/terms" target="_blank" style="color:#60788d;text-decoration:none">Termini</a></div>""", unsafe_allow_html=True)\n'''
s=s[:line_end]+insert+s[line_end:]

marker='Gaming Shorts Factory · V104 Direct Social'
if marker in s:
    s=s.replace(marker,'Gaming Shorts Factory · V104 Direct Social',1)

out.write_text(s,encoding='utf-8')
print(f'V104.2 legal footer applied: {out}')
