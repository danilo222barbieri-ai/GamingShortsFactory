from pathlib import Path

app=Path("/app/GamingShortsFactory_V154_STRUCTURAL_HOME.py")
embed=Path("/app/web/home_v154_embed.py")
html=Path("/app/web/home_v154_component/index.html")

assert app.is_file(), "V154 app missing"
assert embed.is_file(), "V154 embed missing"
assert html.is_file(), "V154 component missing"

s=app.read_text(encoding="utf-8")
e=embed.read_text(encoding="utf-8")
h=html.read_text(encoding="utf-8")

for marker in (
    'key="gsf_home_v154_live"',
    "render_home_v154",
    "gsf-v154-parent-shell",
    'with st.container(key="v73-upload-shell")',
    "gsf_v154_duration",
    "gsf_v154_engine",
):
    assert marker in s, "missing app marker: "+marker

for marker in (
    "Carica il tuo video",
    "GAMING SHORTS FACTORY",
    "Creator Hub",
    "CARICA IL TUO GAMEPLAY",
    "Crea con IA",
    "Game Editor",
    "Crea Short",
    "I tuoi ultimi progetti",
    "Vedi tutti",
    "Warzone #024",
    "Forza #012",
    "Fortnite #008",
    "Home",
    "AI",
    "Editor",
    "Progetti",
    "Social",
    "Automatico",
    "Momento migliore",
    "Più azione",
    "Reazioni",
    "Manuale",
    "/direct-upload/bucket/init",
    "/direct-upload/chunk",
    "streamlit:setComponentValue",
):
    assert marker in h, "missing component marker: "+marker

assert "declare_component" in e
assert "gsf-living-bar" in s and "display:none !important" in s
compile(s,str(app),"exec")
compile(e,str(embed),"exec")
print("V154 structural Home contract: PASS")
