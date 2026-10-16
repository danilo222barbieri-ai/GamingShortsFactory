"""V412 AI engines regression contract.

Covers the pieces that made Crea con IA look like it was not working:
results never reaching the page, every engine sharing one cache slot,
"Cambia short" disabled, and the chosen short not becoming the active one.
"""
import json
import sys
import tempfile
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "web"))

import ai_engines_v412 as v412  # noqa: E402


def require(condition, message):
    if not condition:
        raise SystemExit(f"[FAIL] {message}")
    print(f"[ OK ] {message}")


# ---------------------------------------------------------------- engines
require(v412.cache_profile("action") != v412.cache_profile("reaction"), "AZIONE e REAZIONI hanno cache separate")
require(v412.cache_profile("auto") != v412.cache_profile("director"), "AUTO e STORIA hanno cache separate")
require(v412.cache_profile("") == "legacy", "flusso classico senza motore resta compatibile")
require(v412.should_refine("auto") and v412.should_refine("director"), "AUTO/STORIA rifiniscono i bordi")
require(not v412.should_refine("action") and not v412.should_refine("reaction"), "AZIONE/REAZIONI non spostano il picco")
require(v412.should_refine("", "🚀 AUTO TOTALE") and not v412.should_refine("", "🧠 Smart Clip"), "regola classica invariata senza motore")

# ---------------------------------------------------------------- results sheet
brain = {
    "pool_size": 14,
    "selected": [
        {"rank": 1, "start": 262.0, "brain_score": 0.94, "confidence": 0.9, "event": "multi_kill", "category": "action",
         "director_plan": {"text": {"hook": "Tre secondi e cambia tutto."}}},
        {"rank": 2, "start": 611.2, "brain_score": 0.81, "confidence": 0.7, "event": "clutch", "category": "story"},
        {"rank": 3, "start": 138.0, "brain_score": 0.77, "confidence": 0.6, "event": "highlight", "category": "reaction"},
    ],
    "alternates": [
        {"rank": 1, "start": 720.0, "brain_score": 0.66, "confidence": 0.5, "event": "kill", "reason": "KILL"},
        {"rank": 2, "start": 180.0, "brain_score": 0.61, "confidence": 0.4, "event": "impact", "reason": "IMPATTO"},
    ],
}
meta = v412.build_results_meta([262.0, 611.0, 138.0], brain, duration=15, profile="action", request_id="req-1")
require(meta["request_id"] == "req-1" and meta["engine"] == "AZIONE", "scheda legata alla richiesta e al motore")
require(meta["pool_size"] == 14, "numero di momenti analizzati esposto")
require([i["index"] for i in meta["items"]] == [0, 1, 2], "tre short con indice 0-2")
first = meta["items"][0]
require(first["label"] == "Kill multipla" and first["score"] == 94, "titolo e punteggio reali dal ranker")
require("Tre secondi" in first["why"] and "Confidenza IA 90%" in first["why"], "motivo leggibile dalla scelta IA")
require(first["end_time"] - first["start_time"] == 15, "minutaggio coerente con la durata")
require(meta["items"][1]["label"] == "Clutch", "start rifinito abbinato al momento giusto")
require(len(first["alternates"]) == 2 and first["alternates"][0]["start_time"] == 720.0, "alternative per Cambia short")

with tempfile.TemporaryDirectory() as tmp:
    media = Path(tmp)
    v412.write_results_meta(media, meta)
    require(v412.read_results_meta(media)["request_id"] == "req-1", "scheda scritta e riletta")
    (media / "v71_mini_1_262.00_ab12cd34ef56ab78.mp4").write_bytes(b"x")
    (media / "v71_mini_2_611.00_ab12cd34ef56ab79.mp4").write_bytes(b"x")
    (media / "v71_mini_1.mp4").write_bytes(b"x")  # served alias without a start stamp
    (media / "v71_mini_3_999.00_ab12cd34ef56ab70.mp4").write_bytes(b"x")  # stale clip from another run
    url = lambda name: "/media/sid/media/" + name
    payload = v412.merge_results(v412.read_results_meta(media), v412.mini_files(media), url)
    require(payload["request_id"] == "req-1" and payload["pool_size"] == 14, "endpoint espone richiesta e analisi")
    require(payload["count"] == 2, "solo i clip davvero pronti contano")
    require(payload["previews"][0]["video"].endswith("v71_mini_1_262.00_ab12cd34ef56ab78.mp4"), "clip abbinato per indice e inizio")
    require(payload["previews"][2]["video"] == "", "clip vecchio di un'altra ricerca ignorato")
    (media / "v71_mini_3_138.00_ab12cd34ef56ab71.mp4").write_bytes(b"x")
    payload = v412.merge_results(v412.read_results_meta(media), v412.mini_files(media), url)
    require(payload["count"] == 3, "tre short pronti quando i tre clip esistono")
    require(v412.merge_results(None, [], url) is None, "senza scheda il server usa il vecchio comportamento")

# ---------------------------------------------------------------- Cambia short + selection
state = {
    "auto_clip_candidati": [262.0, 611.0, 138.0],
    "ai_director_scores": [(0.94, 262.0), (0.81, 611.0), (0.77, 138.0)],
    "clip_rifinite": {262.0: 15.0, 611.0: 15.0, 138.0: 15.0},
    "gsf_v112_brain_context": json.loads(json.dumps(brain)),
    "auto_clip_scelta": 262.0,
    "preview_bytes": b"old",
}
require(v412.apply_replacement(state, 1, 720.0, duration=15), "Cambia short sostituisce lo short 2")
require(state["auto_clip_candidati"] == [262.0, 720.0, 138.0], "lo short 2 ora è la scena alternativa")
require(state["auto_clip_scelta"] == 720.0 and "preview_bytes" not in state, "anteprima e short attivo seguono la sostituzione")
require(state["ai_director_scores"][1] == (0.66, 720.0), "punteggio aggiornato")
alts = [r["start"] for r in state["gsf_v112_brain_context"]["alternates"]]
require(alts[0] == 611.0 and 720.0 not in alts, "lo short sostituito diventa un'alternativa")
require(state["gsf_v112_brain_context"]["selected"][1]["start"] == 720.0, "contesto IA aggiornato per editor e render")
require(not v412.apply_replacement(state, 1, 5000.0), "inizio sconosciuto rifiutato")
require(v412.apply_replacement(state, 1, 611.0, restore=True), "Ripristina la scelta IA")
require(state["auto_clip_candidati"][1] == 611.0 and "1" not in state["gsf_v412_replaced"], "scelta originale ripristinata")
require(v412.select_candidate(state, 2, None) and state["auto_clip_scelta"] == 138.0, "selezione per indice")
require(v412.select_candidate(state, 0, 611.2) and state["auto_clip_scelta"] == 611.0, "selezione per inizio ha la precedenza")

# ---------------------------------------------------------------- wiring contracts
page = (ROOT / "web/ai_v221_component/index.html").read_text(encoding="utf-8")
home = (ROOT / "web/home_v154_component/index.html").read_text(encoding="utf-8")
app = (ROOT / "app.py").read_text(encoding="utf-8")
server = (ROOT / "web/direct_upload_server.py").read_text(encoding="utf-8")
require('fetch("/ai/results' in page and "request_id:requestId" in page, "la pagina legge i risultati reali legati alla sua richiesta")
require("j.request_id===requestId" in page, "risultati di ricerche precedenti non mostrati")
require('send("replace"' in page and "pollReplaced" in page, "Cambia short invia la sostituzione e aggiorna il clip")
require("overflow:hidden" in page and "100vh" not in page, "pagina senza scroll")
require("GSF_AI_SHELL_FIT" in page and 'getElementById("gsf-global-header")' in page and 'gsf-global-gamebar' in page, "su mobile la pagina misura header e Game Bar della shell")
require("var(--shell-top,0px)" in page and "var(--shell-bottom,0px)" in page, "contenuto e pannello Cambia short restano tra header e Game Bar")
require('action==="replace"' in home and 'event:"replace_moment"' in home, "Home inoltra Cambia short all'app")
require('request_id:String(e.data.request_id' in home, "Home inoltra l'id richiesta")
require("request_id:e.data.request_id" in app and "restore:e.data.restore===true" in app, "bridge host inoltra id e ripristino")
require("cache_profile(_gsf_v291_profile)" in app, "cache AI separata per motore")
require("_gsf_v412_replace(" in app and "_gsf_v412_select(" in app, "app applica sostituzione e selezione")
require('"index" not in _gsf_v154_event' in app, "aprire l'editor dai risultati non cancella la ricerca IA")
require("build_results_meta" in app and "write_results_meta" in app, "app scrive la scheda risultati")
require("_v412.merge_results(" in server, "endpoint unisce scheda e clip")
require('"draft_ai_"+' in app and "/drafts/save" in app and "gsf_v412_autosaved" in app, "bozza automatica unica nel Creator Hub")
compile(app, "app.py", "exec")
print("[ OK ] app.py compila")

print("\nV412 AI ENGINES: PASS")
