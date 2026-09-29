from pathlib import Path

contact=Path("/app/web/contact_server.py").read_text(encoding="utf-8")
nginx=Path("/app/web/nginx.conf.template").read_text(encoding="utf-8")
footer=Path("/app/web/apply_v104_2_legal_footer.py").read_text(encoding="utf-8")
start=Path("/app/web/start_web.sh").read_text(encoding="utf-8")

checks={
    "contact page": 'def _page(' in contact,
    "contact send": ('def _deliver(' in contact or 'def _send(' in contact),
    "gmail smtp default": 'smtp.gmail.com' in contact,
    "smtp secret env": 'GSF_SMTP_APP_PASSWORD' in contact,
    "recipient env": 'GSF_CONTACT_TO' in contact,
    "reply-to visitor": 'msg["Reply-To"]=email_addr' in contact,
    "honeypot": 'name="website"' in contact,
    "rate limit": 'def _rate_ok(' in contact,
    "nginx route": 'location = /contact' in nginx,
    "footer link": 'href="/contact"' in footer,
    "contact service startup": 'contact_server.py &' in start,
}
bad=[name for name,ok in checks.items() if not ok]
if bad:
    raise SystemExit("Contact form contract failed: "+", ".join(bad))

compile(contact,"contact_server.py","exec")
compile(footer,"apply_v104_2_legal_footer.py","exec")
print("Contact form contract: PASS")
