#!/usr/bin/env python3
import html
import os
import re
import smtplib
import ssl
import threading
import time
from email.message import EmailMessage
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

PORT=int(os.environ.get("GSF_CONTACT_PORT","8503"))
CONTACT_TO=str(os.environ.get("GSF_CONTACT_TO","") or "")
SMTP_HOST=str(os.environ.get("GSF_SMTP_HOST","smtp.gmail.com") or "smtp.gmail.com")
try:
    SMTP_PORT=int(os.environ.get("GSF_SMTP_PORT","587") or 587)
except Exception:
    SMTP_PORT=587
SMTP_USER=str(os.environ.get("GSF_SMTP_USER","") or "")
SMTP_PASSWORD=str(
    os.environ.get("GSF_SMTP_APP_PASSWORD")
    or os.environ.get("GSF_SMTP_PASSWORD")
    or ""
)
SMTP_FROM=str(os.environ.get("GSF_SMTP_FROM","") or SMTP_USER)
_RATE={}
_RATE_LOCK=threading.Lock()


def _recipients():
    return [
        item.strip()
        for item in re.split(r"[,;]",CONTACT_TO)
        if item.strip()
    ]


def _rate_ok(key,cooldown=45):
    now=time.time()
    with _RATE_LOCK:
        prev=float(_RATE.get(str(key),0) or 0)
        if prev and now-prev<float(cooldown):
            return False
        _RATE[str(key)]=now
    return True


def _page(message="",ok=False):
    status=""
    if message:
        cls="ok" if ok else "err"
        status=f'<div class="{cls}">{html.escape(str(message))}</div>'
    return f"""<!doctype html>
<html lang="it">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Gaming Shorts Factory · Contatti</title>
<style>
body{{font-family:Arial,sans-serif;background:#f5f8fc;color:#17324d;margin:0}}
main{{max-width:680px;margin:6vh auto;padding:24px}}
.card{{background:#fff;border-radius:24px;padding:30px;box-shadow:0 12px 40px #15304a18}}
h1{{margin:0 0 8px}} p{{line-height:1.5;color:#5c7185}}
label{{display:block;font-weight:700;margin:14px 0 6px}}
input,textarea{{width:100%;box-sizing:border-box;border:1px solid #cddde9;border-radius:12px;
padding:12px 13px;font:inherit;background:#fbfdff;color:#17324d}}
textarea{{min-height:150px;resize:vertical}}
button{{width:100%;border:0;background:#1687ff;color:#fff;font-weight:800;padding:14px 18px;
border-radius:14px;margin-top:18px;cursor:pointer;font-size:15px}}
.back{{display:block;text-align:center;margin-top:14px;color:#315c80;text-decoration:none}}
.ok{{padding:12px 14px;border-radius:12px;background:#e9f8ef;color:#236b43;margin:14px 0}}
.err{{padding:12px 14px;border-radius:12px;background:#fff0f0;color:#9f2f2f;margin:14px 0}}
.hp{{position:absolute;left:-9999px;width:1px;height:1px;overflow:hidden}}
.small{{font-size:12px;color:#71869a;margin-top:12px}}
</style>
</head>
<body>
<main><div class="card">
<h1>Contatti</h1>
<p>Scrivici direttamente da qui. Il messaggio verrà inoltrato al team di Gaming Shorts Factory.</p>
{status}
<form method="post" action="/contact">
<label for="name">Nome</label>
<input id="name" name="name" maxlength="100" autocomplete="name" required>
<label for="email">Email</label>
<input id="email" name="email" type="email" maxlength="254" autocomplete="email" required>
<label for="message">Messaggio</label>
<textarea id="message" name="message" maxlength="5000" required></textarea>
<div class="hp" aria-hidden="true">
<label>Sito<input name="website" tabindex="-1" autocomplete="off"></label>
</div>
<button type="submit">INVIA</button>
</form>
<div class="small">Gli indirizzi di destinazione non sono mostrati pubblicamente sul sito.</div>
<a class="back" href="/">← Torna a Gaming Shorts Factory</a>
</div></main>
</body></html>"""


def _send(name,email_addr,message):
    recipients=_recipients()
    if not recipients:
        raise RuntimeError("recipient not configured")
    if not SMTP_USER or not SMTP_PASSWORD:
        raise RuntimeError("smtp credentials not configured")

    msg=EmailMessage()
    msg["Subject"]="Gaming Shorts Factory · nuovo messaggio"
    msg["From"]=SMTP_FROM or SMTP_USER
    msg["To"]=", ".join(recipients)
    msg["Reply-To"]=email_addr
    msg.set_content(
        "Nuovo messaggio dal modulo Contatti di Gaming Shorts Factory\n\n"
        f"Nome: {name}\n"
        f"Email: {email_addr}\n\n"
        f"Messaggio:\n{message}\n"
    )

    context=ssl.create_default_context()
    if SMTP_PORT==465:
        with smtplib.SMTP_SSL(
            SMTP_HOST,SMTP_PORT,timeout=20,context=context
        ) as smtp:
            smtp.login(SMTP_USER,SMTP_PASSWORD)
            smtp.send_message(msg)
    else:
        with smtplib.SMTP(SMTP_HOST,SMTP_PORT,timeout=20) as smtp:
            smtp.ehlo()
            smtp.starttls(context=context)
            smtp.ehlo()
            smtp.login(SMTP_USER,SMTP_PASSWORD)
            smtp.send_message(msg)


class Handler(BaseHTTPRequestHandler):
    server_version="GSFContact/1.0"

    def log_message(self,fmt,*args):
        return

    def _html(self,status,body):
        raw=str(body).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type","text/html; charset=utf-8")
        self.send_header("Content-Length",str(len(raw)))
        self.send_header("Cache-Control","no-store")
        self.send_header("X-Content-Type-Options","nosniff")
        self.send_header("Referrer-Policy","same-origin")
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        clean=urlparse(self.path).path.rstrip("/")
        if clean=="/health":
            self._html(200,"ok")
            return
        if clean=="/contact":
            self._html(200,_page())
            return
        self._html(404,"Not found")

    def do_POST(self):
        clean=urlparse(self.path).path.rstrip("/")
        if clean!="/contact":
            self._html(404,"Not found")
            return

        try:
            length=int(self.headers.get("Content-Length","0") or 0)
            if length<=0 or length>65536:
                raise ValueError("Richiesta non valida.")
            raw=self.rfile.read(length).decode("utf-8","replace")
            form=parse_qs(raw,keep_blank_values=True)
            name=str((form.get("name") or [""])[0] or "").strip()
            email_addr=str((form.get("email") or [""])[0] or "").strip()
            message=str((form.get("message") or [""])[0] or "").strip()
            website=str((form.get("website") or [""])[0] or "").strip()

            if website:
                self._html(200,_page("Messaggio inviato. Grazie!",ok=True))
                return
            if not (2<=len(name)<=100):
                raise ValueError("Inserisci il tuo nome.")
            if (
                len(email_addr)>254
                or not re.fullmatch(r"[^\s@]+@[^\s@]+\.[^\s@]+",email_addr)
            ):
                raise ValueError("Inserisci un indirizzo email valido.")
            if not (10<=len(message)<=5000):
                raise ValueError("Il messaggio deve contenere almeno 10 caratteri.")
            if "\r" in name or "\n" in name or "\r" in email_addr or "\n" in email_addr:
                raise ValueError("Dati non validi.")

            client_key=(
                self.headers.get("X-GSF-Session-ID")
                or self.headers.get("X-Real-IP")
                or self.client_address[0]
            )
            if not _rate_ok(client_key):
                self._html(
                    429,
                    _page("Hai appena inviato un messaggio. Riprova tra poco.")
                )
                return

            _send(name,email_addr,message)
            self._html(200,_page("Messaggio inviato. Grazie!",ok=True))
        except ValueError as exc:
            self._html(400,_page(str(exc)))
        except Exception as exc:
            print(
                f"GSF contact send warning: {type(exc).__name__}: {str(exc)[:160]}",
                flush=True,
            )
            self._html(
                503,
                _page("Invio non disponibile in questo momento. Riprova più tardi.")
            )


if __name__=="__main__":
    server=ThreadingHTTPServer(("127.0.0.1",PORT),Handler)
    print(
        f"GSF contact server listening on 127.0.0.1:{PORT} "
        f"smtp={'on' if SMTP_USER and SMTP_PASSWORD else 'off'}",
        flush=True,
    )
    server.serve_forever()
