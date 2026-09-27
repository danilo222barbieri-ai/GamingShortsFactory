from pathlib import Path

src = Path('/app/GamingShortsFactory_V77_WEB_READY.py')
out = Path('/app/GamingShortsFactory_V78_MOBILE_BETA.py')
s = src.read_text(encoding='utf-8')

def replace_once(old, new, label):
    global s
    if old not in s:
        raise RuntimeError(f'V78 patch target not found: {label}')
    s = s.replace(old, new, 1)

replace_once(
'''GSF_WEB_MODE = str(os.environ.get("GSF_WEB_MODE", "0")).strip().lower() in ("1", "true", "yes", "on")
GSF_SESSION_TTL_SECONDS = max(1800, int(os.environ.get("GSF_SESSION_TTL_SECONDS", "7200") or 7200))
''',
'''GSF_WEB_MODE = str(os.environ.get("GSF_WEB_MODE", "0")).strip().lower() in ("1", "true", "yes", "on")
# V78 MOBILE BETA — profilo memoria prudente per hosting web/mobile.
# Sul desktop locale resta invariato. Su Railway evita che la prima analisi AI
# saturi il container da ~1 GB caricando Whisper durante lo scan iniziale.
GSF_LOW_MEMORY_WEB = str(
    os.environ.get("GSF_LOW_MEMORY_WEB", "1" if GSF_WEB_MODE else "0")
).strip().lower() in ("1", "true", "yes", "on")
GSF_AI_VOICE_TRANSCRIPTION = str(
    os.environ.get("GSF_AI_VOICE_TRANSCRIPTION", "0" if GSF_LOW_MEMORY_WEB else "1")
).strip().lower() in ("1", "true", "yes", "on")
GSF_SESSION_TTL_SECONDS = max(1800, int(os.environ.get("GSF_SESSION_TTL_SECONDS", "7200") or 7200))
''',
'web memory profile')

replace_once(
'''@st.cache_resource(show_spinner=False)
def _gsf_subtitle_whisper_model():
    """
    Modello dedicato ai sottotitoli.
    Small è molto più accurato di Tiny, ma viene usato solo sulle clip/scena
    selezionate, non sulla scansione AI dell'intero gameplay.
    """
    try:
        return WhisperModel("small", device="cpu", compute_type="int8")
    except Exception:
        # Fallback: l'app continua a funzionare anche se Small non è disponibile.
        return WhisperModel("tiny", device="cpu", compute_type="int8")
''',
'''@st.cache_resource(show_spinner=False)
def _gsf_subtitle_whisper_model():
    """
    Modello dedicato ai sottotitoli.
    In locale resta Small; nella beta web/mobile a memoria ridotta usiamo Tiny
    per non superare il limite del container durante render e trascrizione.
    """
    if GSF_LOW_MEMORY_WEB:
        return WhisperModel("tiny", device="cpu", compute_type="int8")
    try:
        return WhisperModel("small", device="cpu", compute_type="int8")
    except Exception:
        # Fallback: l'app continua a funzionare anche se Small non è disponibile.
        return WhisperModel("tiny", device="cpu", compute_type="int8")
''',
'subtitle model')

replace_once(
'''def _gsf_ai_voice_features(input_file,start,duration):
    """
    Secondo passaggio SOLO sui candidati migliori.
    Misura parlato, reazione e segnali semantici di eventi importanti.
    """
    wav=None
    try:
''',
'''def _gsf_ai_voice_features(input_file,start,duration):
    """
    Secondo passaggio SOLO sui candidati migliori.
    Misura parlato, reazione e segnali semantici di eventi importanti.
    V78: nella beta web low-memory salta Whisper durante l'analisi iniziale;
    il ranking continua a usare audio, movimento, picchi e signal-event.
    """
    if not GSF_AI_VOICE_TRANSCRIPTION:
        return 0.0,0.0,"",{"type":"","semantic":0.0,"time":None,"text":""}
    wav=None
    try:
''',
'AI voice low-memory')

replace_once(
'''@media(max-width:750px){.st-key-v69_engine_grid [data-testid="stHorizontalBlock"]{flex-wrap:wrap !important}.st-key-v69_engine_grid [data-testid="stColumn"]{min-width:145px !important;flex:1 1 145px !important}.st-key-v69_engine_grid button{height:192px !important;min-height:192px !important}.st-key-v69_engine_grid button::before{width:90px !important;height:90px !important;flex-basis:90px !important}}
''',
'''@media(max-width:750px){
  /* V78 MOBILE BETA — layout pensato per iPhone/Android, non desktop schiacciato. */
  .block-container{width:100% !important;max-width:100% !important;padding-left:.75rem !important;padding-right:.75rem !important;padding-top:.45rem !important}
  .hero-title{font-size:clamp(2.15rem,12vw,3.15rem) !important;line-height:.92 !important}
  .hero-sub{font-size:.92rem !important;margin-top:10px !important}
  .gsf-hero{padding:16px 6px 8px !important}
  .gsf-hero h1{font-size:1.72rem !important}
  [data-testid="stFileUploader"]{padding:8px !important;border-radius:22px !important}
  [data-testid="stFileUploaderDropzone"]{min-height:116px !important;border-radius:18px !important}
  .st-key-v69_engine_grid [data-testid="stHorizontalBlock"]{display:grid !important;grid-template-columns:repeat(2,minmax(0,1fr)) !important;gap:12px !important;align-items:stretch !important}
  .st-key-v69_engine_grid [data-testid="stColumn"],
  .st-key-v69_engine_grid [data-testid="column"]{width:100% !important;min-width:0 !important;max-width:none !important;flex:none !important}
  .st-key-v69_engine_grid [data-testid="stColumn"]:nth-child(5),
  .st-key-v69_engine_grid [data-testid="column"]:nth-child(5){grid-column:1 / -1 !important}
  .st-key-v69_engine_grid button{height:154px !important;min-height:154px !important;padding:14px 7px 9px !important;gap:10px !important;border-radius:20px !important}
  .st-key-v69_engine_grid button::before{width:68px !important;height:68px !important;min-width:68px !important;flex-basis:68px !important;background-size:34px !important}
  .st-key-v69_engine_grid button p{font-size:.88rem !important;line-height:1.2 !important;min-height:34px !important}
  .st-key-v73-duration{--duration-size:clamp(104px,31vw,126px) !important}
  .st-key-v73-duration [data-testid="stHorizontalBlock"]{gap:16px !important}
  .stButton>button[kind="primary"]{min-height:3.35rem !important;font-size:1rem !important}
  iframe{max-width:100% !important}
}
''',
'mobile CSS')

old_player = '''        video{{display:block;width:{_target_width}px;max-width:{_max_vw};height:auto;
        object-fit:contain;border-radius:18px;background:#000;
        box-shadow:0 14px 34px rgba(16,40,61,.14)}}
'''
if old_player not in s:
    raise RuntimeError('V78 patch target not found: responsive main player')
s = s.replace(old_player, '''        video{{display:block;width:{_target_width}px;max-width:min({_max_vw},100%);height:auto;
        object-fit:contain;border-radius:18px;background:#000;
        box-shadow:0 14px 34px rgba(16,40,61,.14)}}
''')

replace_once(
'''        if st.button("CREA CON AI", use_container_width=True):
            with _gsf_session_tempdir("gsf_analysis_") as analisi_temp:
''',
'''        if GSF_WEB_MODE:
            st.caption("Beta mobile: l’analisi viene eseguita sul server. Dopo il tap su CREA CON AI attendi il completamento senza chiudere la pagina.")
        if st.button("CREA CON AI", use_container_width=True):
            with _gsf_session_tempdir("gsf_analysis_") as analisi_temp:
''',
'mobile AI CTA')

out.write_text(s, encoding='utf-8')
print(f'V78 patch applied: {out}')
