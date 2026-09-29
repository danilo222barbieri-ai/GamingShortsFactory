from pathlib import Path
import sys

p=Path(sys.argv[1])
s=p.read_text(encoding="utf-8")
checks={
    "S3 inbox": "contact-inbox/" in s and "def _store_message" in s,
    "HTTPS email support": "https://api.resend.com/emails" in s and "GSF_RESEND_API_KEY" in s,
    "nonblocking SMTP": "threading.Thread(" in s and "timeout=4" in s,
    "old blocking timeout removed": "timeout=20" not in s,
    "truthful success": "Messaggio ricevuto. Grazie!" in s,
    "delivery guard": "contact delivery unavailable" in s,
}
bad=[k for k,v in checks.items() if not v]
if bad:
    raise SystemExit("V105.5 contact contract failed: "+", ".join(bad))
compile(s,str(p),"exec")
print("V105.5 contact contract: PASS")
