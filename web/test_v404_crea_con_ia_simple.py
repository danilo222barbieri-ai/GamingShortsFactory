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
require("Che cosa vuoi trovare?" in src, "domanda motori semplice")

for label in ("AUTO", "AZIONE", "REAZIONI", "STORIA"):
    require(f">{label}<" in src, f"motore {label} presente")

require("TROVA I MOMENTI" in src, "CTA unica per avviare la ricerca")
require("I tuoi momenti migliori" in src, "titolo risultati semplice")
require("MIGLIORE" in src, "primo risultato evidenziato")
require("Cambia ricerca" in src, "ritorno alla scelta motore senza perdere il video")

for action in ("CREA SHORT", "MODIFICA", "Salva"):
    require(action in src, f"azione finale {action} presente")

# Existing parent protocol must stay wired so the redesign does not become a mockup.
for action in ('send("engine"', 'send("duration"', 'send("create"', 'send("preview"'):
    require(action in src, f"protocollo esistente mantenuto: {action}")

# Result actions use the already-supported preview bridge so older hosts do not expose dead buttons.
require('intent:"create_short"' in src and 'send("preview"' in src, "Crea Short usa il bridge preview compatibile")
require('intent:"edit"' in src and 'send("preview"' in src, "Modifica usa il bridge preview compatibile")

# Results are selected in-place and receiving them must release the local searching state.
require("function showView" in src, "navigazione interna a due viste")
require("state.selectedMoment" in src, "selezione momento persistente")
require("state.previews" in src, "risultati reali ricevuti dal parent")
require("hasPreviews" in src and "state.processing=false" in src, "risultati sbloccano lo stato di ricerca")

# Keep the component self-contained and syntax-shaped enough to catch accidental truncation.
require(src.count("<script>") == src.count("</script>") == 1, "script unico e chiuso")
require(src.strip().endswith("</html>"), "documento HTML completo")

print("\nV404 CREA CON IA SIMPLE FLOW: PASS")
