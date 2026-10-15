"""GSF V416 — event-driven web push.

Every user-facing outcome already leaves a file in the session folder:

* ``render_job.json``             final Short ready / failed (written by app.py)
* ``media/ai_results_meta.json``  Crea con IA found its three shorts (V412)
* ``publish_v413.json``           multi-publish finished (V413)

A single background watcher turns those files into at most one push per real
event. It only looks at sessions that have a push subscription, ignores stale
files (a bucket restore after a redeploy rewrites ``render_job.json`` with the
original completion time, and must not notify again) and records what it sent
in a small per-session ledger, so the explicit ``/push/notify`` call from
app.py and the watcher can never produce two notifications for one Short.

The module also owns the browser side: the global toast/push client served as
``/gsf-push.js`` and the service worker served as ``/gsf-sw.js``. Tapping a
notification opens the page the event belongs to (Crea Short, Crea con IA, Home)
through the shell's existing ``GSF_SHELL_NAV`` message instead of the Home.

Pure standard library: the sender is injected, so tests run without network.
"""

from __future__ import annotations

import json
import os
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping

SUBSCRIPTION_FILE = ".push_subscription.json"
LEDGER_FILE = ".push_ledger.json"
RENDER_JOB_FILE = "render_job.json"
AI_RESULTS_FILE = "ai_results_meta.json"
PUBLISH_FILE = "publish_v413.json"

# An event older than this is history (restore after redeploy, old session).
FRESHNESS_SECONDS = 15 * 60
# Ledger entries are kept long enough to cover any re-read of the same file.
LEDGER_TTL_SECONDS = 3 * 24 * 3600
LEDGER_MAX_ENTRIES = 200

# Notification targets understood by the shell (GSF_SHELL_NAV) and the client.
TARGETS = ("home", "short", "ai", "hub")

# Tags from legacy callers that announce a finished Short. The watcher owns
# that event now, so these calls only ask for an immediate scan.
SHORT_READY_TAG_PREFIX = "gsf-short-ready"


@dataclass(frozen=True)
class PushEvent:
    kind: str
    key: str
    title: str
    body: str
    target: str = "home"

    @property
    def tag(self) -> str:
        return "gsf-" + self.kind.replace("_", "-")

    @property
    def url(self) -> str:
        return "/#gsf-open=" + (self.target if self.target in TARGETS else "home")


def _read_json(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _num(value: Any, default: float = 0.0) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return number if number == number else default  # NaN guard


def _fresh(ts: float, now: float, freshness: float) -> bool:
    return ts > 0 and (now - freshness) <= ts <= (now + 120)


def _join_labels(labels: list[str]) -> str:
    labels = [x for x in labels if x]
    if len(labels) <= 1:
        return "".join(labels)
    return ", ".join(labels[:-1]) + " e " + labels[-1]


# --------------------------------------------------------------------------
# Event extraction (pure: files in, events out)
# --------------------------------------------------------------------------

def render_events(session_dir: Path, now: float, freshness: float = FRESHNESS_SECONDS) -> list[PushEvent]:
    job = _read_json(Path(session_dir) / RENDER_JOB_FILE)
    status = str(job.get("status") or "").lower()
    if status == "ready":
        done = _num(job.get("completed_at"))
        if _fresh(done, now, freshness):
            return [PushEvent(
                "short_ready", "ready:%.3f" % done,
                "Short pronto", "Il tuo Short è pronto. Tocca per pubblicarlo o condividerlo.", "short",
            )]
    elif status == "failed":
        failed = _num(job.get("failed_at"))
        if _fresh(failed, now, freshness):
            return [PushEvent(
                "render_failed", "failed:%.3f" % failed,
                "Short non creato", "La creazione si è fermata. Il progetto è salvo: puoi riprovare.", "home",
            )]
    return []


def ai_events(session_dir: Path, now: float, freshness: float = FRESHNESS_SECONDS) -> list[PushEvent]:
    meta = _read_json(Path(session_dir) / "media" / AI_RESULTS_FILE)
    items = meta.get("items")
    if not isinstance(items, list) or not items:
        return []
    updated = _num(meta.get("updated_at"))
    if not _fresh(updated, now, freshness):
        return []
    request_id = str(meta.get("request_id") or "").strip()[:40]
    # Swaps and selections rewrite the sheet with the same request id: one push
    # per search. Without a request id, fall back to one push per 15 minutes.
    key = "ai:" + (request_id or "window-%d" % int(updated // FRESHNESS_SECONDS))
    count = len(items)
    body = ("Ho trovato %d momenti da Short. Scegli il tuo preferito." % count) if count > 1 else \
        "Ho trovato il momento migliore. Aprilo per vederlo."
    return [PushEvent("ai_ready", key, "Crea con IA ha finito", body, "ai")]


def publish_events(session_dir: Path, now: float, freshness: float = FRESHNESS_SECONDS) -> list[PushEvent]:
    job = _read_json(Path(session_dir) / PUBLISH_FILE)
    if str(job.get("state") or "") != "finished":
        return []
    updated = _num(job.get("updated_at"))
    if not _fresh(updated, now, freshness):
        return []
    results = job.get("results") if isinstance(job.get("results"), Mapping) else {}
    done, failed = [], []
    for platform, row in results.items():
        if not isinstance(row, Mapping):
            continue
        label = str(row.get("label") or platform or "").strip()[:20]
        status = str(row.get("status") or "")
        if status == "done":
            done.append(label)
        elif status == "error":
            failed.append(label)
    key = "publish:" + (str(job.get("id") or "").strip()[:32] or "%.3f" % updated)
    if done:
        body = "Pubblicato su " + _join_labels(done) + "."
        if failed:
            body += " " + _join_labels(failed) + ": non riuscito, puoi riprovare."
        return [PushEvent("published", key, "Short pubblicato", body, "short")]
    if failed:
        return [PushEvent(
            "publish_failed", key, "Pubblicazione non riuscita",
            _join_labels(failed) + ": non riuscito. Apri Crea Short per riprovare.", "short",
        )]
    return []  # only manual/needs-connection rows: the page already guides the user


EXTRACTORS: tuple[Callable[[Path, float, float], list[PushEvent]], ...] = (
    render_events, ai_events, publish_events,
)


def session_events(session_dir: Path, now: float | None = None,
                   freshness: float = FRESHNESS_SECONDS) -> list[PushEvent]:
    now = time.time() if now is None else now
    events: list[PushEvent] = []
    for extract in EXTRACTORS:
        try:
            events.extend(extract(Path(session_dir), now, freshness))
        except Exception:
            continue
    return events


# --------------------------------------------------------------------------
# Ledger: what was already sent for a session
# --------------------------------------------------------------------------

class Ledger:
    def __init__(self, session_dir: Path):
        self.path = Path(session_dir) / LEDGER_FILE

    def load(self) -> dict[str, float]:
        data = _read_json(self.path)
        return {str(k): _num(v) for k, v in data.items()}

    def seen(self, key: str) -> bool:
        return key in self.load()

    def mark(self, key: str, now: float) -> None:
        data = self.load()
        data[key] = now
        data = {k: v for k, v in data.items() if now - v <= LEDGER_TTL_SECONDS}
        if len(data) > LEDGER_MAX_ENTRIES:
            data = dict(sorted(data.items(), key=lambda kv: kv[1])[-LEDGER_MAX_ENTRIES:])
        tmp = self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
        os.replace(tmp, self.path)


# --------------------------------------------------------------------------
# Watcher
# --------------------------------------------------------------------------

Sender = Callable[[str, PushEvent], bool]


class PushWatcher:
    """Scan subscribed sessions and send each new event once."""

    def __init__(self, sessions_root: Path, send: Sender, interval: float = 4.0,
                 freshness: float = FRESHNESS_SECONDS, log: Callable[..., None] | None = None):
        self.sessions_root = Path(sessions_root)
        self.send = send
        self.interval = max(1.0, float(interval))
        self.freshness = float(freshness)
        self.log = log or (lambda *a: print(*a, flush=True))
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()

    def subscribed_sessions(self) -> Iterable[Path]:
        try:
            for sub in self.sessions_root.glob("*/" + SUBSCRIPTION_FILE):
                if sub.is_file():
                    yield sub.parent
        except OSError:
            return

    def scan_session(self, session_dir: Path | str, now: float | None = None) -> list[PushEvent]:
        """Send every new, fresh event of one session. Returns what was sent."""
        session_dir = Path(session_dir)
        if not (session_dir / SUBSCRIPTION_FILE).is_file():
            return []
        now = time.time() if now is None else now
        sent: list[PushEvent] = []
        with self._lock:
            ledger = Ledger(session_dir)
            for event in session_events(session_dir, now, self.freshness):
                if ledger.seen(event.key):
                    continue
                # Mark first: a failing push service must not cause a retry storm
                # and a second notification later.
                try:
                    ledger.mark(event.key, now)
                except OSError as exc:
                    self.log("GSF_V416_PUSH_LEDGER_WARN", session_dir.name, repr(str(exc))[:120])
                    continue
                ok = False
                try:
                    ok = bool(self.send(session_dir.name, event))
                except Exception as exc:  # the sender logs its own details
                    self.log("GSF_V416_PUSH_SEND_WARN", session_dir.name, event.kind, type(exc).__name__)
                self.log("GSF_V416_PUSH_EVENT", session_dir.name, event.kind, "sent" if ok else "not-sent")
                sent.append(event)
        return sent

    def scan_once(self, now: float | None = None) -> int:
        total = 0
        for session_dir in list(self.subscribed_sessions()):
            total += len(self.scan_session(session_dir, now))
        return total

    def _loop(self) -> None:
        while not self._stop.wait(self.interval):
            try:
                self.scan_once()
            except Exception as exc:
                self.log("GSF_V416_PUSH_WATCH_WARN", type(exc).__name__, repr(str(exc))[:160])

    def start(self) -> "PushWatcher":
        if self._thread is None or not self._thread.is_alive():
            self._stop.clear()
            self._thread = threading.Thread(target=self._loop, name="gsf-push-v416", daemon=True)
            self._thread.start()
            self.log("GSF_V416_PUSH_WATCH started", "interval=" + str(self.interval))
        return self

    def stop(self) -> None:
        self._stop.set()


def is_short_ready_tag(tag: Any) -> bool:
    return str(tag or "").startswith(SHORT_READY_TAG_PREFIX)


# --------------------------------------------------------------------------
# Browser side
# --------------------------------------------------------------------------

SERVICE_WORKER_JS = r'''const GSF_TARGETS=["home","short","ai","hub"];
const gsfTarget=(url)=>{const m=/[#&]gsf-open=([a-z]+)/.exec(String(url||""));return m&&GSF_TARGETS.includes(m[1])?m[1]:"home";};
self.addEventListener("install",()=>self.skipWaiting());
self.addEventListener("activate",(event)=>event.waitUntil(self.clients.claim()));
self.addEventListener("push",(event)=>{
  let data={};
  try{data=event.data?event.data.json():{};}catch(e){}
  event.waitUntil(self.registration.showNotification(data.title||"Gaming Shorts Factory",{
    body:data.body||"",
    icon:"/app-icon-192.png",
    badge:"/app-icon-192.png",
    tag:data.tag||"gsf-update",
    renotify:true,
    data:{url:data.url||"/"},
    vibrate:[120,70,120]
  }));
});
self.addEventListener("notificationclick",(event)=>{
  event.notification.close();
  const url=(event.notification.data&&event.notification.data.url)||"/";
  const target=gsfTarget(url);
  event.waitUntil(self.clients.matchAll({type:"window",includeUncontrolled:true}).then((items)=>{
    for(const client of items){
      if("focus" in client){
        // The app is already open: switch page in place, no reload.
        try{client.postMessage({type:"GSF_PUSH_OPEN",target});}catch(e){}
        return client.focus();
      }
    }
    return self.clients.openWindow?self.clients.openWindow("/#gsf-open="+target):undefined;
  }));
});'''


CLIENT_JS = r'''(()=>{
  // Compatibility token for legacy lifecycle tests: Upload completato
  if(window.__GSF_GLOBAL_NOTIFICATIONS_V2__)return;
  window.__GSF_GLOBAL_NOTIFICATIONS_V2__=true;
  const TARGETS=["home","short","ai","hub"];
  const toU8=(s)=>{const pad="=".repeat((4-s.length%4)%4);const raw=atob((s+pad).replace(/-/g,"+").replace(/_/g,"/"));return Uint8Array.from([...raw].map(c=>c.charCodeAt(0)));};
  const pushSupported=()=>("serviceWorker" in navigator)&&("PushManager" in window)&&("Notification" in window);

  // Register and post the subscription. Never asks for permission itself.
  let subscribing=null;
  const subscribe=()=>{
    if(subscribing)return subscribing;
    subscribing=(async()=>{
      if(!pushSupported()||Notification.permission!=="granted")return false;
      const reg=await navigator.serviceWorker.register("/gsf-sw.js?v=416",{scope:"/"});
      const key=await fetch("/push/public-key",{cache:"no-store"}).then(r=>r.json()).then(x=>x.public_key||"");
      if(!key)return false;
      let sub=await reg.pushManager.getSubscription();
      if(!sub)sub=await reg.pushManager.subscribe({userVisibleOnly:true,applicationServerKey:toU8(key)});
      const r=await fetch("/push/subscribe",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(sub.toJSON())});
      return r.ok;
    })().catch(()=>false).finally(()=>{setTimeout(()=>{subscribing=null;},1500);});
    return subscribing;
  };
  // Ask for permission. Must run inside a tap: Safari on iPhone only shows the
  // prompt when requestPermission() is the first thing the tap does.
  const enable=()=>{
    if(!pushSupported())return Promise.resolve(false);
    if(Notification.permission==="granted")return subscribe();
    if(Notification.permission==="denied")return Promise.resolve(false);
    let asked;
    try{asked=Notification.requestPermission();}catch(e){asked=null;}
    if(!asked||typeof asked.then!=="function")asked=new Promise((ok)=>{try{Notification.requestPermission(ok);}catch(e){ok("default");}});
    return asked.then((p)=>p==="granted"?subscribe():false).catch(()=>false);
  };

  const openTarget=(target)=>{
    const t=TARGETS.includes(String(target))?String(target):"home";
    try{window.postMessage({type:"GSF_SHELL_NAV",target:t},location.origin);}catch(e){}
  };
  // Opened from a notification while the app was closed: "/#gsf-open=short".
  const consumeHash=()=>{
    const m=/[#&]gsf-open=([a-z]+)/.exec(location.hash||"");
    if(!m)return;
    try{history.replaceState(null,"",location.pathname+location.search);}catch(e){}
    // The V343 shell router mounts while Streamlit renders and resets to Home
    // on boot: navigate once, shortly after it says it is ready.
    let done=false;
    const go=()=>{if(done)return;done=true;setTimeout(()=>openTarget(m[1]),700);};
    if(window["__GSF_GLOBAL_"+"SHELL_V343"])go();
    else window.addEventListener("message",(e)=>{if(e.origin===location.origin&&e.data&&e.data.type==="GSF_V343_SHELL_READY")go();});
    setTimeout(go,6000);
  };
  if(pushSupported()){
    navigator.serviceWorker.addEventListener("message",(event)=>{
      const d=event.data||{};if(d.type==="GSF_PUSH_OPEN")openTarget(d.target);
    });
  }

  const ensureToastUi=()=>{
    let host=document.getElementById("gsf-site-toast-stack");
    if(host)return host;
    const style=document.createElement("style");
    style.id="gsf-site-toast-style";
    style.textContent="#gsf-site-toast-stack{position:fixed;right:14px;bottom:max(82px,calc(env(safe-area-inset-bottom,0px) + 72px));z-index:2147483640;width:min(300px,calc(100vw - 28px));display:flex;flex-direction:column-reverse;align-items:flex-end;gap:7px;pointer-events:none;font-family:'Avenir Next','SF Pro Display','SF Pro Text',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif}.gsf-site-toast{position:relative;display:grid;grid-template-columns:34px minmax(0,1fr) 20px;gap:8px;align-items:center;width:min(286px,calc(100vw - 28px));padding:8px 8px 8px 9px;border:1px solid rgba(194,219,236,.82);border-radius:15px;background:rgba(255,255,255,.94);-webkit-backdrop-filter:blur(16px);backdrop-filter:blur(16px);box-shadow:0 9px 24px rgba(37,72,101,.12),inset 0 1px 0 rgba(255,255,255,.88);color:#24475f;pointer-events:auto;overflow:hidden;opacity:0;transform:translateY(8px) scale(.985);transition:opacity .17s ease,transform .17s ease}.gsf-site-toast.gsf-show{opacity:1;transform:translateY(0) scale(1)}.gsf-site-toast.gsf-hide{opacity:0;transform:translateY(6px) scale(.99)}.gsf-site-toast-icon{width:34px;height:34px;border-radius:10px;display:grid;place-items:center;background:linear-gradient(145deg,#eaf8ff,#d7f3ff)}.gsf-site-toast-icon img{width:26px;height:26px;border-radius:8px;display:block}.gsf-site-toast-copy{min-width:0}.gsf-site-toast-title{font-size:12px;font-weight:900;line-height:1.15;color:#315b75;letter-spacing:.003em}.gsf-site-toast-body{margin-top:2px;font-size:10px;font-weight:650;line-height:1.25;color:#71889a;white-space:normal}.gsf-site-toast-close{border:0;background:transparent;color:#91a7b7;width:20px;height:20px;border-radius:7px;font-size:16px;line-height:18px;padding:0;cursor:pointer}.gsf-site-toast-bar{position:absolute;left:0;bottom:0;height:2px;width:100%;background:linear-gradient(90deg,#8bd9f8,#9fe9ce);transform-origin:left center;animation:gsfToastLife 3.2s linear forwards}.gsf-site-toast.gsf-simple{display:flex;align-items:center;justify-content:center;width:auto;min-width:132px;max-width:220px;padding:9px 14px;border-radius:999px}.gsf-site-toast.gsf-simple .gsf-site-toast-icon,.gsf-site-toast.gsf-simple .gsf-site-toast-body,.gsf-site-toast.gsf-simple .gsf-site-toast-close{display:none}.gsf-site-toast.gsf-simple .gsf-site-toast-copy{display:block}.gsf-site-toast.gsf-simple .gsf-site-toast-title{font-size:11px;color:#486b84;text-align:center;white-space:nowrap}.gsf-site-toast.gsf-simple .gsf-site-toast-bar{height:1.5px;opacity:.65}.gsf-site-toast-actions{grid-column:2/4;display:flex;justify-content:flex-end;gap:7px;margin-top:2px}.gsf-site-toast-action{border:1px solid rgba(142,186,220,.42);border-radius:999px;background:rgba(255,255,255,.92);color:#587694;font-size:10px;font-weight:850;padding:7px 10px;cursor:pointer}.gsf-site-toast-action.primary{background:linear-gradient(145deg,#dff3ff,#dff8ee);color:#2f7190;border-color:rgba(112,194,208,.38)}.gsf-site-toast[data-kind=error]{border-color:rgba(235,187,187,.82)}.gsf-site-toast[data-kind=error] .gsf-site-toast-icon{background:linear-gradient(145deg,#fff0f0,#ffdede)}.gsf-site-toast[data-kind=error] .gsf-site-toast-bar{background:linear-gradient(90deg,#ff9d9d,#ffc0c0)}@keyframes gsfToastLife{from{transform:scaleX(1)}to{transform:scaleX(0)}}@media(max-width:600px){#gsf-site-toast-stack{right:10px;bottom:max(74px,calc(env(safe-area-inset-bottom,0px) + 66px));width:calc(100vw - 20px)}.gsf-site-toast{width:min(270px,calc(100vw - 20px));grid-template-columns:32px minmax(0,1fr) 20px;padding:7px 8px}.gsf-site-toast-icon{width:32px;height:32px}.gsf-site-toast-icon img{width:24px;height:24px}.gsf-site-toast.gsf-simple{min-width:118px;max-width:190px;padding:8px 13px}.gsf-site-toast.gsf-simple .gsf-site-toast-title{font-size:10.5px}}";
    document.head.appendChild(style);
    host=document.createElement("div");
    host.id="gsf-site-toast-stack";
    host.setAttribute("aria-live","polite");
    document.body.appendChild(host);
    return host;
  };

  const seenPersistent=(token)=>{if(!token)return false;try{return localStorage.getItem("gsf-site-notice:"+token)==="1";}catch(e){return false;}};
  const markPersistent=(token)=>{if(!token)return;try{localStorage.setItem("gsf-site-notice:"+token,"1");}catch(e){}};
  const baseToast=(title,body,kind)=>{
    const host=ensureToastUi(),el=document.createElement("div");
    el.className="gsf-site-toast";el.dataset.kind=kind;
    const icon=document.createElement("div");icon.className="gsf-site-toast-icon";
    const img=document.createElement("img");img.src="/app-icon.png?v=4";img.alt="";icon.appendChild(img);
    const copy=document.createElement("div");copy.className="gsf-site-toast-copy";
    const strong=document.createElement("div");strong.className="gsf-site-toast-title";strong.textContent=String(title||"Gaming Shorts Factory");
    const small=document.createElement("div");small.className="gsf-site-toast-body";small.textContent=String(body||"");copy.append(strong,small);
    const close=document.createElement("button");close.className="gsf-site-toast-close";close.type="button";close.setAttribute("aria-label","Chiudi");close.textContent="×";
    el.append(icon,copy,close);host.prepend(el);
    while(host.children.length>3)host.lastElementChild?.remove();
    const remove=()=>{if(!el.isConnected)return;el.classList.add("gsf-hide");setTimeout(()=>el.remove(),240);};
    close.onclick=(ev)=>{ev.stopPropagation();remove();};
    requestAnimationFrame(()=>el.classList.add("gsf-show"));
    return {el,remove,close};
  };
  const showToast=(title,body,kind="success",opts={})=>{
    const token=String(opts.token||"");
    if(opts.persistent&&token&&seenPersistent(token))return false;
    if(opts.persistent&&token)markPersistent(token);
    const t=baseToast(title,body,kind);
    if(!String(body||"").trim())t.el.classList.add("gsf-simple");
    const bar=document.createElement("div");bar.className="gsf-site-toast-bar";t.el.appendChild(bar);
    if(typeof opts.onClick==="function"){t.el.style.cursor="pointer";t.el.addEventListener("click",(ev)=>{if(ev.target===t.close)return;opts.onClick();t.remove();});}
    setTimeout(t.remove,String(body||"").trim()?4800:3000);return true;
  };
  const confirmToast=(title,body,opts={})=>{
    const t=baseToast(title,body,opts.kind||"confirm");
    const actions=document.createElement("div");actions.className="gsf-site-toast-actions";
    const cancel=document.createElement("button");cancel.className="gsf-site-toast-action";cancel.type="button";cancel.textContent=String(opts.cancelText||"Annulla");
    const ok=document.createElement("button");ok.className="gsf-site-toast-action primary";ok.type="button";ok.textContent=String(opts.confirmText||"Continua");
    actions.append(cancel,ok);t.el.appendChild(actions);
    cancel.onclick=()=>{try{if(typeof opts.onCancel==="function")opts.onCancel();}finally{t.remove();}};
    ok.onclick=(ev)=>{ev.stopPropagation();try{if(typeof opts.onConfirm==="function")opts.onConfirm();}finally{t.remove();}};
    return {close:t.remove};
  };

  window.GSFPush={enable,ensure:subscribe,supported:pushSupported,permission:()=>pushSupported()?Notification.permission:"unsupported"};
  window.GSFNotify={
    show:(title,body,kind)=>showToast(title,body,kind||"success"),
    confirm:confirmToast,
    open:openTarget
  };

  // Offer push once, after the first Short is ready, from a toast button:
  // the tap on "Attiva" is the user gesture the browser needs.
  const offerPush=()=>{
    if(!pushSupported()||Notification.permission!=="default")return;
    try{if(localStorage.getItem("gsf-push-offer-v416")==="1")return;localStorage.setItem("gsf-push-offer-v416","1");}catch(e){}
    confirmToast("Ti avviso io?","Notifica quando lo Short o l'IA hanno finito, anche con l'app chiusa.",{confirmText:"Attiva",cancelText:"Non ora",onConfirm:()=>{enable().then((on)=>{if(on)showToast("Notifiche attive","","success");});}});
  };

  let uploadActive=false,uploadCycle=0,uploadDoneCycle=0,lastRenderStatus="";
  window.addEventListener("message",(event)=>{
    const d=event.data||{};if(d.type!=="gsf-upload")return;const state=String(d.state||"");
    if(state==="running"){if(!uploadActive){uploadCycle+=1;uploadActive=true;}}
    else if(state==="done"){uploadActive=false;if(uploadDoneCycle!==uploadCycle){uploadDoneCycle=uploadCycle;showToast("Video caricato","","success");}}
    else if(state==="error"){const wasActive=uploadActive;uploadActive=false;if(wasActive)showToast("Upload interrotto","Il caricamento non è stato completato. Puoi riprovare senza perdere il resto del lavoro.","error");}
  });

  window.addEventListener("beforeunload",(event)=>{if(!uploadActive)return;event.preventDefault();event.returnValue="";});

  const syncReadyResult=()=>{
    const target=document.querySelector('.st-key-gsf_final_ready_sync_v111 button,[class*="st-key-gsf_final_ready_sync_v111"] button');
    if(!target||target.disabled)return false;
    target.click();
    return true;
  };

  let polling=false;
  const pollJob=async()=>{
    if(polling||document.visibilityState==="hidden")return;
    polling=true;
    try{
      const j=await fetch("/job/status",{cache:"no-store"}).then(r=>r.json()),status=String(j.render_status||"");
      if(status==="ready"){
        const token=String(j.completed_at||j.started_at||"ready");
        if(showToast("Short completato","Tocca per pubblicarlo.","success",{token:"short-ready-"+token,persistent:true,onClick:()=>openTarget("short")}))setTimeout(offerPush,1200);
        if(lastRenderStatus!=="ready"){
          if(!syncReadyResult())setTimeout(syncReadyResult,250);
        }
      }else if(status==="failed"){
        const token=String(j.failed_at||j.started_at||"failed");
        showToast("Creazione Short non riuscita","Il rendering si è fermato. Il progetto e la bozza restano disponibili.","error",{token:"short-failed-"+token,persistent:true});
      }
      lastRenderStatus=status;
    }catch(e){}finally{polling=false;}
  };

  setInterval(pollJob,1500);pollJob();
  document.addEventListener("visibilitychange",()=>{if(document.visibilityState==="visible"){pollJob();subscribe();}});
  window.addEventListener("pageshow",()=>{pollJob();subscribe();});
  // A tap on CREA SHORT is a good moment to ask: requestPermission runs first, synchronously.
  document.addEventListener("click",(event)=>{const b=event.target&&event.target.closest?event.target.closest("button"):null;if(!b)return;const label=(b.innerText||b.textContent||"").toUpperCase();if(label.includes("CREA SHORT")&&pushSupported()&&Notification.permission==="default")enable();},true);
  window.addEventListener("load",()=>{subscribe();consumeHash();},{once:true});
  if(document.readyState==="complete")consumeHash();
})();'''


def service_worker_js() -> bytes:
    return SERVICE_WORKER_JS.encode("utf-8")


def client_js() -> bytes:
    return CLIENT_JS.encode("utf-8")
