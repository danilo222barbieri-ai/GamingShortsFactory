from pathlib import Path

server=Path("/app/web/direct_upload_server.py").read_text(encoding="utf-8")
for marker in (
    "def _auto_highlights_rows_for_account(",
    "def _auto_highlights_cards_html(",
    'prefix=f"auto-highlights/{provider}/{account_id}/"',
    "AUTO HIGHLIGHTS PRONTI",
    "auto_highlights_html=_auto_highlights_cards_html(sid)",
    "<h2>Auto Highlights</h2>{auto_highlights_html}",
    "nessun render inutile del VOD completo",
):
    if marker not in server:
        raise SystemExit("V129 Creator Hub marker missing: "+marker)
compile(server,"<v129-server>","exec")
print("V129 Creator Hub Auto Highlights contracts: PASS")
