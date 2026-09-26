from pathlib import Path
import ast
import sys

TARGET = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("GamingShortsFactory_V32_RANGE_SEEK_FINAL.py")

def fail(msg):
    print(f"[FAIL] {msg}")
    raise SystemExit(1)

def ok(msg):
    print(f"[ OK ] {msg}")

if not TARGET.exists():
    fail(f"File non trovato: {TARGET}")

src = TARGET.read_text(encoding="utf-8")

# 1) Syntax / compile guard
try:
    compile(src, str(TARGET), "exec")
    ok("Sintassi Python valida")
except SyntaxError as e:
    fail(f"Errore di sintassi: {e}")

# 2) Core functions that must survive future refactors
tree = ast.parse(src)
funcs = {n.name for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}
classes = {n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}

required_funcs = {
    "_gsf_transcribe_editor_scene",
    "_gsf_clean_transcript_words",
    "_gsf_subtitle_groups",
    "render_gsf_editor_live_player",
}
for name in sorted(required_funcs):
    if name not in funcs:
        fail(f"Funzione critica mancante: {name}")
    ok(f"Funzione presente: {name}")

if "_GSFQuietHandler" not in classes:
    fail("Server preview _GSFQuietHandler mancante")
ok("Server preview presente")

# 3) HTTP byte ranges: required for reliable seek / VAI
for marker in ('Accept-Ranges', 'Content-Range', '206'):
    if marker not in src:
        fail(f"Supporto byte-range incompleto: manca {marker}")
ok("Supporto HTTP Range/206 presente")

# 4) Subtitle language auto-detection
if "language=None" not in src:
    fail("Whisper non usa il rilevamento automatico lingua")
ok("Rilevamento automatico lingua attivo")

# 5) UI regression guards: V31's under-player navigator must never return
for forbidden in ("gsf-native-nav", "gsf-native-select", "gsf-native-go"):
    if forbidden in src:
        fail(f"Regressione UI: trovato controllo sotto-player {forbidden}")
ok("Nessun navigatore aggiunto sotto il player")

# 6) Existing right-side navigation remains available
if "Vai al testo" not in src or '"VAI"' not in src:
    fail("Controllo 'Vai al testo / VAI' non trovato nell'editor")
ok("Controllo VAI presente nell'area sottotitoli")

print("\nTUTTI I CONTROLLI BASE SONO PASSATI.")