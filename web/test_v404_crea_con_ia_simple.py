from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "web" / "ai_v221_component" / "index.html"


def require(condition, message):
    if not condition:
        raise SystemExit(f"[FAIL] {message}")
    print(f"[ OK ] {message}")


src = TARGET.read_text(encoding="utf-8")

# V404 contract: Crea con IA is a two-step experience, not one crowded dashboard.
require('data-view="engines"' in src, "vista 1 motori presente")
require('data-view="moments"' in src, "vista 2 momenti presente")
require("Che cosa vuoi" in src and "trovare?" in src, "domanda motori semplice")

for label in ("AUTO", "AZIONE", "REAZIONI", "STORIA"):
    require(f">{label}<" in src, f"motore {label} presente")

require("TROVA I MOMENTI" in src, "CTA unica per avviare la ricerca")
require("I tuoi momenti" in src, "titolo risultati valido anche con un solo momento")
require("MIGLIORE" in src, "primo risultato evidenziato")
require("Cambia motore" in src, "ritorno alla scelta motore senza perdere il video")

# V412: results end in Pubblica / Apri nell'editor / Cambia short; drafts save themselves.
for action in ("Pubblica", "Apri nell'editor", "Cambia short"):
    require(action in src, f"azione finale {action} presente")
require('send("save"' in src and "autosave" in src, "bozza salvata in automatico")

# Existing parent protocol must stay wired so the redesign does not become a mockup.
for action in ('send("engine"', 'send("duration"', 'send("create"', 'send("preview"'):
    require(action in src, f"protocollo esistente mantenuto: {action}")

# Result actions keep the preview bridge (older hosts) and the explicit create_short/open_editor actions.
require('intent:"create_short"' in src and 'send("preview"' in src, "Crea Short usa il bridge preview compatibile")
require('intent:"edit"' in src and 'send("preview"' in src, "Modifica usa il bridge preview compatibile")

# Results are selected in-place and receiving them must release the local searching state.
require("function showView" in src, "navigazione interna a due viste")
require("state.selectedMoment" in src, "selezione momento persistente")
require("state.previews" in src, "risultati reali ricevuti dal parent")
require('send("create_short"' in src and 'send("open_editor"' in src, "Pubblica ed Editor usano le azioni esplicite")
require("hasPreviews" in src and "state.processing=false" in src, "risultati sbloccano lo stato di ricerca")

# Keep the component self-contained and syntax-shaped enough to catch accidental truncation.
require(src.count("<script>") == src.count("</script>") == 1, "script unico e chiuso")
require(src.strip().endswith("</html>"), "documento HTML completo")

print("\nV404 CREA CON IA SIMPLE FLOW: PASS")
