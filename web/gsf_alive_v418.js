/* GSF Alive 2 (V418) — one nervous system for the whole app.
   Canonical source. Every surface inlines this file verbatim between
   GSF_ALIVE:BEGIN / GSF_ALIVE:END (tools/gsf_alive_inline.py, tests/test_alive_runtime_v418.py).

   Heard   — every tap gets an echo, every real event a heartbeat of the orb.
   Guided  — the next real step glows; after a quiet moment a handwritten whisper points at it.
   Carried — long work follows the user across pages (companion bubble, real timer),
             completion celebrates and leads straight to the next step.

   Rules (docs/architecture/gsf-alive.md): motion only from real state, never moves
   controls, quiet by default, prefers-reduced-motion respected, no fake progress. */
(() => {
  "use strict";
  const W = typeof window !== "undefined" ? window : globalThis;
  if (W.GSFAlive) return;

  /* ---------------------------------------------------------------- core */
  const KEY = "gsf_alive_v418";
  const JOB_TTL_MS = { upload: 10 * 60e3, ai: 6 * 60e3, render: 16 * 60e3, publish: 10 * 60e3 };
  const CELEBRATE_MS = 2600;
  const ERROR_CALM_MS = 3 * 60e3;   /* an error colours the app for 3 minutes, then calms */
  const ERROR_BUBBLE_MS = 90e3;     /* the "Riprova" bubble follows the user for 90 seconds */
  const BASE = {
    mode: "idle", video_ready: false, active_job: null, progress: null, job_started: 0, job_updated: 0,
    moments_count: 0, moment_selected: false, short_ready: false, published: false,
    ready_at: 0, error: null, error_job: null, error_at: 0, message: "Pronto quando vuoi.",
    social_connected: null, celebrate_until: 0, updated: 0, seq: 0, last: "",
  };
  const clamp01 = v => {
    let n = Number(v);
    if (!Number.isFinite(n)) return null;
    if (n > 1) n = n / 100;
    return Math.max(0, Math.min(1, n));
  };
  function calmMode(s, now) {
    if (s.celebrate_until && now < s.celebrate_until) return "celebrate";
    if (s.error && now - (Number(s.error_at) || Number(s.updated) || 0) < ERROR_CALM_MS) return "error";
    if (s.active_job) return "working";
    if (s.video_ready || s.short_ready) return "active";
    return "idle";
  }
  function startJob(s, job, now, extra) {
    const keep = s.active_job === job && s.job_started ? s.job_started : now;
    return Object.assign({}, s, { active_job: job, job_started: keep, job_updated: now, progress: null, error: null, error_job: null, error_at: 0 }, extra || {});
  }
  function reduce(prev, type, data, now) {
    const d = data || {};
    now = Number(now) || Date.now();
    let s = Object.assign({}, BASE, prev || {});
    switch (String(type || "")) {
      case "upload.started":
        s = startJob(s, "upload", now, { progress: 0, short_ready: false, published: false, moments_count: 0, moment_selected: false, video_ready: false, message: "Ricevuto. Carico il gameplay." });
        break;
      case "upload.progress": {
        if (s.active_job !== "upload") s = startJob(s, "upload", now, { short_ready: false, published: false, moments_count: 0, moment_selected: false, video_ready: false, message: "Carico il gameplay." });
        const p = clamp01(d.progress);
        if (p !== null) { s.progress = p; s.job_updated = now; }
        break;
      }
      case "upload.completed":
        s = Object.assign(s, { video_ready: true, active_job: null, progress: null, error: null, error_job: null, message: "Video pronto. Scegli come crearlo." });
        break;
      case "video.cleared":
        s = Object.assign({}, BASE, { social_connected: s.social_connected, message: "Pronto quando vuoi." });
        break;
      case "ai.started":
        s = startJob(s, "ai", now, { video_ready: true, moments_count: 0, moment_selected: false, message: "Guardo tutto il video per te." });
        break;
      case "ai.found": {
        const n = Math.max(0, Math.round(Number(d.count) || 0));
        s = Object.assign(s, { active_job: s.active_job === "ai" ? null : s.active_job, progress: null, error: null, error_job: null, moments_count: n, moment_selected: false,
          message: n === 1 ? "Ho trovato un momento forte." : n ? "Ho trovato " + n + " momenti forti." : "Nessun momento questa volta." });
        break;
      }
      case "moment.selected":
        s = Object.assign(s, { moment_selected: true, message: "Bella scelta." });
        break;
      case "editor.opened":
        s = Object.assign(s, { message: "Modifichiamola insieme." });
        break;
      case "editor.saved":
        s = Object.assign(s, { message: "Salvato." });
        break;
      case "render.started":
        s = startJob(s, "render", now, { short_ready: false, published: false, ready_at: 0, message: "Monto il tuo Short. Puoi continuare a navigare." });
        if (Number(d.started_at) > 0) s.job_started = Math.min(now, Number(d.started_at));
        break;
      case "render.progress": {
        const p = clamp01(d.progress);
        if (s.active_job === "render" && p !== null) { s.progress = p; s.job_updated = now; }
        break;
      }
      case "render.completed":
        s = Object.assign(s, { active_job: s.active_job === "render" ? null : s.active_job, progress: null, error: null, error_job: null, short_ready: true, video_ready: true, published: false, ready_at: now, celebrate_until: now + CELEBRATE_MS, message: "È pronto! Pubblichiamolo?" });
        break;
      case "render.cancelled":
        if (s.active_job === "render") s = Object.assign(s, { active_job: null, progress: null, message: "Pronto quando vuoi." });
        break;
      case "publish.started":
        s = startJob(s, "publish", now, { message: "Lo mando fuori." });
        break;
      case "publish.completed": {
        const ok = Math.max(0, Number(d.ok) || 0), ko = Math.max(0, Number(d.ko) || 0);
        s = Object.assign(s, { active_job: s.active_job === "publish" ? null : s.active_job, progress: null });
        if (ok > 0) {
          s.published = true; s.error = null; s.error_job = null;
          s.celebrate_until = now + CELEBRATE_MS;
          s.message = ko ? ok + " pubblicati, " + ko + " da riprovare." : "Pubblicato. Grande!";
        } else {
          s.error = "La pubblicazione non è riuscita."; s.error_job = "publish"; s.error_at = now;
          s.message = "La pubblicazione non è riuscita. Riproviamo.";
        }
        break;
      }
      case "social.status":
        if (s.social_connected === (Number(d.connected) > 0)) return Object.assign({}, s, { mode: calmMode(s, now) });
        s.social_connected = Number(d.connected) > 0;
        break;
      case "failure": {
        const msg = String(d.message || "Qualcosa si è fermato. Riproviamo.").slice(0, 140);
        s = Object.assign(s, { error: msg, error_job: d.job || s.active_job || null, error_at: now, active_job: null, progress: null, celebrate_until: 0, message: msg });
        break;
      }
      case "sync": {
        /* Silent facts a page already knows (a video restored after reload, a short ready on the server). */
        const before = JSON.stringify([s.video_ready, s.short_ready, s.moments_count, s.published]);
        if (typeof d.video_ready === "boolean") s.video_ready = d.video_ready;
        if (typeof d.short_ready === "boolean" && !(d.short_ready && s.active_job === "render")) s.short_ready = d.short_ready;
        if (typeof d.published === "boolean") s.published = d.published;
        if (Number.isFinite(Number(d.moments_count)) && d.moments_count !== undefined) s.moments_count = Math.max(0, Number(d.moments_count));
        if (!s.video_ready && !s.short_ready) { s.moments_count = 0; s.moment_selected = false; }
        if (JSON.stringify([s.video_ready, s.short_ready, s.moments_count, s.published]) === before) return Object.assign({}, prev || BASE, { mode: calmMode(prev || BASE, now) });
        break;
      }
      case "recovered":
        s = Object.assign(s, { error: null, error_job: null, message: "Ci siamo." });
        break;
      default:
        return Object.assign({}, s, { mode: calmMode(s, now) });
    }
    s.last = String(type);
    s.seq = (Number(prev && prev.seq) || 0) + 1;
    s.updated = now;
    s.mode = calmMode(s, now);
    return s;
  }
  /* Drop jobs that outlived any real run (a page closed mid-upload, a lost worker). */
  function expire(s, now) {
    if (!s) return s;
    let out = s;
    if (s.active_job) {
      const ttl = JOB_TTL_MS[s.active_job] || 10 * 60e3;
      const since = Number(s.job_updated) || Math.max(Number(s.job_started) || 0, Number(s.updated) || 0);
      if (now - since > ttl) out = Object.assign({}, out, { active_job: null, progress: null });
    }
    if (s.error && now - (Number(s.error_at) || Number(s.updated) || 0) >= ERROR_CALM_MS) {
      out = Object.assign({}, out, { error: null, error_job: null, error_at: 0 });
    }
    const mode = calmMode(out, now);
    return mode === out.mode ? out : Object.assign({}, out, { mode });
  }
  function nextAction(s) {
    s = s || BASE;
    if (s.error) return "retry";
    if (s.active_job) return null;
    if (s.short_ready && !s.published) return s.social_connected === false ? "connect_social" : "publish";
    if (s.published) return "new_video";
    if (!s.video_ready) return "upload";
    if (s.moments_count && !s.moment_selected) return "choose_moment";
    if (s.moment_selected) return "create_short";
    return "create_with_ai";
  }
  function motion(s) {
    const P = {
      idle: { dur: 5.8, scale: 1.035, glow: 0.16 },
      active: { dur: 3.8, scale: 1.045, glow: 0.24 },
      working: { dur: 1.6, scale: 1.07, glow: 0.34 },
      celebrate: { dur: 1.1, scale: 1.1, glow: 0.42 },
      error: { dur: 3.2, scale: 1.02, glow: 0.18 },
    };
    const m = Object.assign({ mode: s.mode }, P[s.mode] || P.idle);
    if (s.mode === "working" && s.progress !== null && s.progress !== undefined) m.dur = Math.round(Math.max(1.05, 1.9 - s.progress * 0.8) * 100) / 100;
    return m;
  }
  const HUE = { upload: "#27AEF3", ai: "#9D82FF", render: "#5ED6A0", publish: "#53E0EA" };
  function hueOf(s) {
    if (s.error) return "#FFB547";
    if (s.active_job) return HUE[s.active_job];
    if (s.short_ready) return "#5ED6A0";
    if (s.moments_count) return "#9D82FF";
    return "#27AEF3";
  }
  const NUDGE = {
    upload: "Tocca il cerchio e scegli un video",
    create_with_ai: "Vuoi che l'IA trovi i momenti migliori?",
    choose_moment: "Scegli il momento che ti piace",
    create_short: "Quando sei pronto, crea lo Short",
    publish: "Il tuo Short aspetta solo di uscire",
    connect_social: "Collega un social per pubblicare",
    retry: "Riprova quando vuoi: il video è ancora qui",
    new_video: "Pronto per il prossimo highlight?",
  };
  const SPOKEN = new Set(["upload.started", "upload.completed", "ai.started", "ai.found", "moment.selected", "editor.saved",
    "render.started", "render.completed", "publish.started", "publish.completed", "failure", "recovered"]);
  function welcome(s) {
    if (s.error) return "Bentornato. Riprendiamo da dove si è fermato.";
    if (s.active_job) return "Bentornato. Ci sto ancora lavorando.";
    if (s.short_ready && !s.published) return "Bentornato. Il tuo Short è pronto.";
    if (s.video_ready) return "Bentornato. Riprendiamo da qui.";
    return "Bentornato.";
  }
  const core = { BASE, reduce, expire, nextAction, motion, hueOf, welcome, NUDGE, SPOKEN, calmMode };

  if (typeof document === "undefined" || !W.document || !W.document.documentElement) {
    W.GSFAlive = { _core: core };
    return;
  }

  /* ------------------------------------------------------------- runtime */
  const D = document, root = D.documentElement;
  const pendingTimers=new Set(),pendingFrames=new Set();
  let routeAbort=null,routeGeneration=0,whisperAnchor=null;
  function later(fn,ms){if(!visible())return 0;const id=W.setTimeout(()=>{pendingTimers.delete(id);if(visible())fn()},ms);pendingTimers.add(id);return id}
  function animate(fn){if(!visible())return 0;const id=W.requestAnimationFrame(t=>{pendingFrames.delete(id);if(visible())fn(t)});pendingFrames.add(id);return id}
  const ME = Math.random().toString(36).slice(2, 10);
  const reduced = () => { try { return W.matchMedia("(prefers-reduced-motion: reduce)").matches; } catch (_e) { return false; } };
  const store = {
    get() { try { return JSON.parse(localStorage.getItem(KEY) || "null"); } catch (_e) { return null; } },
    set(v) { try { localStorage.setItem(KEY, JSON.stringify(v)); } catch (_e) {} },
  };
  let channel = null;
  try { channel = new BroadcastChannel("gsf-alive-v418"); } catch (_e) { channel = null; }
  let state = expire(Object.assign({}, BASE, store.get() || {}), Date.now());
  state.mode = calmMode(state, Date.now());
  let page = { name: "page", target: null, voiceAnchor: null, dock: "top", orbs: [] };
  let mounted = false, lastSpokenSeq = state.seq, lastActivity = Date.now(), hiddenAt = 0;
  const listeners = new Set();
  const TARGET = { home: "home", ai: "ai", short: "social", hub: "hub", editor: "editor" };
  const JOB_PAGE = { upload: "home", ai: "ai", render: "social", publish: "social" };

  /* ----- environment ----- */
  function nav() { try { const P = W.parent; return P && P !== W && P.GSFNavigation ? P.GSFNavigation : null; } catch (_e) { return null; } }
  function surface() { const n = nav(); try { return n ? String(n.snapshot().target || "home") : null; } catch (_e) { return null; } }
  function visible() {
    if (D.hidden) return false;
    const t = surface();
    return t === null || !page.target || t === page.target;
  }
  function go(target) {
    const n = nav();
    if (n) { try { n.navigate({ target }); return true; } catch (_e) {} }
    try { W.parent.postMessage({ type: "GSF_SHELL_NAV", target }, location.origin); return true; } catch (_e) { return false; }
  }
  /* Same measurement the pages use to stay clear of the shell header and Game Bar. */
  function insets() {
    let top = 0, bottom = 0;
    try {
      const fe = W.frameElement, P = W.parent;
      if (fe && P && P !== W) {
        const fr = fe.getBoundingClientRect(), PD = P.document;
        const shown = el => { if (!el) return null; const cs = P.getComputedStyle(el); if (cs.display === "none" || cs.visibility === "hidden") return null; const r = el.getBoundingClientRect(); return r.height > 0 ? r : null; };
        const head = shown(PD.getElementById("gsf-global-header"));
        if (head) top = Math.max(0, Math.ceil(head.bottom - fr.top));
        const lows = ["gsf-global-gamebar", "gsf-global-footer"].map(id => shown(PD.getElementById(id))).filter(Boolean);
        if (lows.length) bottom = Math.max(0, Math.ceil(fr.bottom - Math.min.apply(null, lows.map(r => r.top))));
      }
    } catch (_e) {}
    return { top, bottom };
  }
  const haptic = p => { try { if (navigator.vibrate) navigator.vibrate(p); } catch (_e) {} };

  /* ----- style ----- */
  const CSS = `
:root{--alive-dur:5.8s;--alive-scale:1.035;--alive-glow:.16;--alive-hue:#27AEF3}
#gsf-alive-layer{position:fixed;inset:0;pointer-events:none;z-index:2147482000;contain:layout style}
#gsf-alive-aura{position:fixed;inset:-10%;pointer-events:none;z-index:-1;opacity:.55;background:radial-gradient(42% 32% at 50% 38%,color-mix(in srgb,var(--alive-hue) 22%,transparent),transparent 72%);transition:background 1.2s ease,opacity 1.2s ease;animation:gsfAliveAura calc(var(--alive-dur)*1.6) ease-in-out infinite}
html[data-alive-mode=idle] #gsf-alive-aura{opacity:.32}
@keyframes gsfAliveAura{0%,100%{transform:scale(1);opacity:.45}50%{transform:scale(1.06);opacity:.7}}
.gsf-alive-halo{position:absolute;inset:-7%;border-radius:50%;pointer-events:none;z-index:0;border:2px solid rgba(121,210,255,.55);border:2px solid color-mix(in srgb,var(--alive-hue) 70%,transparent);box-shadow:0 0 calc(56px*var(--alive-glow)*3) color-mix(in srgb,var(--alive-hue) 45%,transparent);animation:gsfAliveBreath var(--alive-dur) ease-in-out infinite;transition:border-color .8s ease,box-shadow .8s ease}
.gsf-alive-halo.beat{animation:gsfAliveBeat .62s cubic-bezier(.2,.8,.2,1) 1,gsfAliveBreath var(--alive-dur) ease-in-out .62s infinite}
@keyframes gsfAliveBreath{0%,100%{transform:scale(1);opacity:.6}50%{transform:scale(var(--alive-scale));opacity:1}}
@keyframes gsfAliveBeat{0%{transform:scale(1);opacity:.9}30%{transform:scale(1.09);opacity:1}55%{transform:scale(1.02)}75%{transform:scale(1.06)}100%{transform:scale(1);opacity:.8}}
.gsf-alive-echo{position:fixed;width:12px;height:12px;margin:-6px 0 0 -6px;border-radius:50%;border:2px solid var(--echo,#27AEF3);opacity:.85;animation:gsfAliveEcho .55s cubic-bezier(.2,.8,.2,1) forwards}
@keyframes gsfAliveEcho{to{transform:scale(6.5);opacity:0;border-width:1px}}
#gsf-alive-guide{position:fixed;display:none;border:2px solid rgba(121,210,255,.8);border:2px solid color-mix(in srgb,var(--alive-hue) 75%,white 10%);box-shadow:0 0 22px color-mix(in srgb,var(--alive-hue) 50%,transparent);animation:gsfAliveGuide 2.4s ease-in-out infinite;transition:none}
@keyframes gsfAliveGuide{0%,100%{opacity:.35;transform:scale(1)}50%{opacity:1;transform:scale(1.025)}}
#gsf-alive-whisper{position:fixed;left:50%;max-width:min(84vw,360px);transform:translate(-50%,6px);opacity:0;display:flex;align-items:center;gap:8px;padding:6px 14px 7px;border-radius:999px;background:rgba(5,13,22,.84);border:1px solid rgba(121,210,255,.3);border:1px solid color-mix(in srgb,var(--alive-hue) 35%,transparent);-webkit-backdrop-filter:blur(14px);backdrop-filter:blur(14px);color:#EAF6FF;font:600 18px/1.15 "Caveat","Segoe Print","Bradley Hand",cursive;letter-spacing:.2px;text-align:center;transition:opacity .45s ease,transform .45s cubic-bezier(.2,.8,.2,1);text-shadow:0 1px 10px rgba(0,0,0,.4)}
#gsf-alive-whisper.on{opacity:1;transform:translate(-50%,0)}
#gsf-alive-whisper i{flex:none;width:7px;height:7px;border-radius:50%;background:var(--alive-hue);box-shadow:0 0 10px var(--alive-hue);animation:gsfAliveBreath var(--alive-dur) ease-in-out infinite}
#gsf-alive-bubble{position:fixed;right:12px;transform:translateY(-8px) scale(.96);transform-origin:right center;opacity:0;pointer-events:none;display:flex;align-items:center;gap:9px;height:38px;padding:0 14px 0 5px;border-radius:999px;border:1px solid rgba(121,210,255,.35);border:1px solid color-mix(in srgb,var(--alive-hue) 40%,transparent);background:rgba(8,24,39,.82);-webkit-backdrop-filter:blur(16px);backdrop-filter:blur(16px);box-shadow:0 10px 28px rgba(0,0,0,.45),0 0 18px color-mix(in srgb,var(--alive-hue) 25%,transparent);color:#EAF6FF;font:700 13px/1 "Avenir Next","SF Pro Text",-apple-system,"Nunito Sans","Segoe UI",sans-serif;white-space:nowrap;cursor:pointer;transition:opacity .35s ease,transform .35s cubic-bezier(.2,.8,.2,1);-webkit-tap-highlight-color:transparent}
/* GSF_ALIVE_COMPACT_PILL */
#gsf-alive-bubble{max-width:min(78vw,320px);overflow:hidden}
#gsf-alive-bubble .l{display:block;min-width:0;overflow:hidden;text-overflow:ellipsis}
#gsf-alive-bubble small{flex:0 0 auto}
#gsf-alive-bubble.on{opacity:1;transform:none;pointer-events:auto}
#gsf-alive-bubble:focus-visible{outline:2px solid #79D2FF;outline-offset:2px}
#gsf-alive-bubble svg{flex:none;width:28px;height:28px;transform:rotate(-90deg)}
#gsf-alive-bubble .t{fill:none;stroke:rgba(255,255,255,.12);stroke-width:3}
#gsf-alive-bubble .v{fill:none;stroke:var(--alive-hue);stroke-width:3;stroke-linecap:round;transition:stroke-dashoffset .5s ease}
#gsf-alive-bubble.spin svg{animation:gsfAliveSpin 1.1s linear infinite}
#gsf-alive-bubble small{font-weight:600;color:#9FB7CA;font-variant-numeric:tabular-nums}
#gsf-alive-bubble b{color:var(--alive-hue)}
@keyframes gsfAliveSpin{to{transform:rotate(270deg)}}
#gsf-alive-bubble.done{animation:gsfAliveBeat .62s ease 2}
.gsf-alive-sr{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}
@media (prefers-reduced-motion:reduce){#gsf-alive-aura,.gsf-alive-halo,#gsf-alive-guide,#gsf-alive-whisper i,#gsf-alive-bubble.spin svg{animation:none!important}.gsf-alive-halo{opacity:.8}}
`;
  let layer = null, guideEl = null, whisperEl = null, bubbleEl = null, liveEl = null;
  function build() {
    if (layer || !D.body) return;
    const st = D.createElement("style"); st.id = "gsf-alive-v418-style"; st.textContent = CSS; D.head.appendChild(st);
    const aura = D.createElement("div"); aura.id = "gsf-alive-aura"; aura.setAttribute("aria-hidden", "true"); D.body.prepend(aura);
    layer = D.createElement("div"); layer.id = "gsf-alive-layer"; layer.setAttribute("aria-hidden", "true");
    guideEl = D.createElement("div"); guideEl.id = "gsf-alive-guide";
    whisperEl = D.createElement("div"); whisperEl.id = "gsf-alive-whisper"; whisperEl.innerHTML = "<i></i><span></span>";
    layer.append(guideEl, whisperEl);
    D.body.appendChild(layer);
    bubbleEl = D.createElement("button"); bubbleEl.type = "button"; bubbleEl.id = "gsf-alive-bubble"; bubbleEl.tabIndex = -1;
    bubbleEl.innerHTML = '<svg viewBox="0 0 32 32" aria-hidden="true"><circle class="t" cx="16" cy="16" r="12"/><circle class="v" cx="16" cy="16" r="12" stroke-dasharray="75.4" stroke-dashoffset="75.4"/></svg><span class="l"></span><small></small>';
    bubbleEl.addEventListener("click", onBubble);
    D.body.appendChild(bubbleEl);
    liveEl = D.createElement("div"); liveEl.className = "gsf-alive-sr"; liveEl.setAttribute("role", "status"); liveEl.setAttribute("aria-live", "polite");
    D.body.appendChild(liveEl);
  }

  /* ----- orbs (the lungs) ----- */
  function attachHalo(host) {
    if (!host || host.querySelector(":scope > .gsf-alive-halo")) return;
    try { if (getComputedStyle(host).position === "static") host.style.position = "relative"; } catch (_e) {}
    const h = D.createElement("span"); h.className = "gsf-alive-halo"; h.setAttribute("aria-hidden", "true");
    host.prepend(h);
  }
  function scanOrbs() { D.querySelectorAll("[data-alive-orb]").forEach(attachHalo); }
  function beat() {
    D.querySelectorAll(".gsf-alive-halo").forEach(h => { h.classList.remove("beat"); void h.offsetWidth; h.classList.add("beat"); });
    later(() => D.querySelectorAll(".gsf-alive-halo.beat").forEach(h => h.classList.remove("beat")), 700);
  }

  /* ----- apply state to the page ----- */
  function paint() {
    const m = motion(state), rs = root.style;
    rs.setProperty("--alive-dur", m.dur + "s");
    rs.setProperty("--alive-scale", String(m.scale));
    rs.setProperty("--alive-glow", String(m.glow));
    rs.setProperty("--alive-hue", hueOf(state));
    root.dataset.aliveMode = state.mode;
    root.dataset.aliveStep = nextAction(state) || "";
    root.dataset.aliveJob = state.active_job || "";
  }
  let celebrateTimer = 0;
  function apply(prev, fromRemote) {
    paint();
    clearTimeout(celebrateTimer);
    if (visible() && state.celebrate_until > Date.now()) celebrateTimer = later(() => { state.mode = calmMode(state, Date.now()); paint(); renderBubble(); }, state.celebrate_until - Date.now() + 30);
    const fresh = state.seq !== (prev && prev.seq);
    let notificationHandled = false;
    if (fresh) try { const notify = W.top.GSFNotify || W.GSFNotify; if (notify && notify.alive) notificationHandled = notify.alive(state); } catch (_e) {}
    if (fresh && mounted && visible()) {
      if (state.last && SPOKEN.has(state.last) && state.seq !== lastSpokenSeq) {
        lastSpokenSeq = state.seq;
        if (!notificationHandled) say(state.message, { anchor: page.voiceAnchor });
        beat();
        if (state.last === "render.completed" || (state.last === "publish.completed" && state.published)) { celebrate(); haptic([14, 50, 22]); }
        else if (/\.started$/.test(state.last) && !fromRemote) haptic(10);
        else if (state.last === "failure") haptic([30, 60, 30]);
      }
    } else if (fresh) {
      lastSpokenSeq = state.seq;
    }
    if (fresh) nudged = "";
    renderBubble();
    guide();
    listeners.forEach(fn => { try { fn(state); } catch (_e) {} });
  }
  function commit(next, fromRemote) {
    const prev = state;
    state = next;
    if (!fromRemote) {
      store.set(state);
      if (channel) { try { channel.postMessage({ from: ME, state }); } catch (_e) {} }
    }
    apply(prev, fromRemote);
  }
  function emit(type, data) {
    const next = reduce(state, type, data, Date.now());
    if (next.seq === state.seq && next.mode === state.mode) return state;
    commit(next, false);
    return state;
  }
  if (channel) channel.onmessage = e => {
    const d = e && e.data;
    if (!d || d.from === ME || !d.state) return;
    if ((Number(d.state.updated) || 0) < (Number(state.updated) || 0)) return;
    commit(Object.assign({}, BASE, d.state), true);
  };
  W.addEventListener("storage", e => {
    if (e.key !== KEY || !e.newValue) return;
    try { const s = JSON.parse(e.newValue); if ((Number(s.updated) || 0) > (Number(state.updated) || 0)) commit(Object.assign({}, BASE, s), true); } catch (_e) {}
  });

  /* ----- voice: one handwritten whisper, never a wall of text ----- */
  let whisperTimer = 0;
  function placeWhisper(anchor) {
    const ins = insets(), H = W.innerHeight || 700;
    let top = null;
    const el = typeof anchor === "string" ? D.querySelector(anchor) : anchor;
    if (el && el.getBoundingClientRect) {
      const r = el.getBoundingClientRect();
      if (r.width > 0 && r.height > 0) {
        const below = r.bottom + 12, above = r.top - 50;
        top = below + 40 < H - ins.bottom ? below : above > ins.top ? above : null;
      }
    }
    if (top === null) top = Math.max(ins.top + 12, H - ins.bottom - 64 - (page.dock === "bottom" && bubbleEl && bubbleEl.classList.contains("on") ? 52 : 0));
    whisperEl.style.top = Math.round(top) + "px";
  }
  function say(text, opts) {
    text = String(text || "").trim();
    if (!text || !layer) return;
    const o = opts || {};
    liveEl.textContent = text;
    if (!visible()) return;
    whisperEl.querySelector("span").textContent = text;
    whisperAnchor=o.anchor || page.voiceAnchor;
    placeWhisper(whisperAnchor);
    whisperEl.classList.add("on");
    clearTimeout(whisperTimer);
    whisperTimer = later(() => whisperEl.classList.remove("on"), Math.max(2200, Math.min(6000, 900 + text.length * 70)));
  }

  /* ----- heard: an echo under every finger ----- */
  const TAPPABLE = "button,a[href],label,[role=button],[data-alive-next],input[type=file],select,summary";
  function echo(e) {
    lastActivity = Date.now();
    if (!layer || reduced() || !visible()) return;
    const t = e.target && e.target.closest ? e.target.closest(TAPPABLE) : null;
    if (!t || t.disabled || t.closest("[data-alive-quiet]")) return;
    const r = D.createElement("span"); r.className = "gsf-alive-echo";
    let c = "";
    try { c = getComputedStyle(t).getPropertyValue("--na-area").trim(); } catch (_e) {}
    r.style.setProperty("--echo", c || getComputedStyle(root).getPropertyValue("--alive-hue").trim() || "#27AEF3");
    r.style.left = e.clientX + "px"; r.style.top = e.clientY + "px";
    layer.appendChild(r);
    later(() => r.remove(), 620);
  }

  /* ----- guided: the next real step glows, a quiet moment brings a whisper ----- */
  let guided = null, nudged = "";
  function targetFor(action) {
    if (!action) return null;
    const list = D.querySelectorAll('[data-alive-next~="' + action + '"]');
    for (const el of list) {
      if (el === root || el === D.body) continue;
      if (el.disabled || el.closest("[hidden],[aria-hidden=true],[inert]")) continue;
      const r = el.getBoundingClientRect();
      if (r.width < 8 || r.height < 8) continue;
      const cs = getComputedStyle(el);
      if (cs.visibility === "hidden" || Number(cs.opacity) < 0.2) continue;
      const ins=insets();let top=ins.top,bottom=(W.innerHeight||0)-ins.bottom;
      for(let parent=el.parentElement;parent&&parent!==D.body;parent=parent.parentElement){const css=getComputedStyle(parent);if(/auto|scroll|hidden|clip/.test(css.overflowY)){const clip=parent.getBoundingClientRect();top=Math.max(top,clip.top);bottom=Math.min(bottom,clip.bottom)}}
      if (r.bottom <= top || r.top >= bottom) continue;
      return el;
    }
    return null;
  }
  function guide() {
    if (!layer) return;
    const action = nextAction(state);
    const el = visible() ? targetFor(action) : null;
    guided = el;
    if (!el) { guideEl.style.display = "none"; return; }
    const r = el.getBoundingClientRect(), pad = 6,ins=insets();
    guideEl.style.clipPath=`inset(${Math.max(0,ins.top-r.top+pad)}px 0 ${Math.max(0,r.bottom+pad-((W.innerHeight||0)-ins.bottom))}px 0)`;
    let radius = 14;
    try { const br = parseFloat(getComputedStyle(el).borderTopLeftRadius); if (Number.isFinite(br)) radius = Math.min(br + pad, Math.max(r.width, r.height)); } catch (_e) {}
    if (el.hasAttribute("data-alive-round")) radius = 9999;
    Object.assign(guideEl.style, { display: "block", left: r.left - pad + "px", top: r.top - pad + "px", width: r.width + pad * 2 + "px", height: r.height + pad * 2 + "px", borderRadius: radius + "px" });
  }
  function idleCheck() {
    if (!mounted || !visible()) return;
    guide();
    const action = nextAction(state);
    if (!action || !guided) return;
    const key = page.name + ":" + action + ":" + state.seq;
    if (nudged === key || Date.now() - lastActivity < 9000) return;
    if (whisperEl.classList.contains("on")) return;
    nudged = key;
    say(NUDGE[action], { anchor: guided });
  }

  /* ----- carried: the work follows the user ----- */
  const fmt = ms => { const s = Math.max(0, Math.floor(ms / 1000)); return Math.floor(s / 60) + ":" + String(s % 60).padStart(2, "0"); };
  const JOB_LABEL = { upload: "Carico il video", ai: "L'IA sta cercando", render: "Monto lo Short", publish: "Pubblico" };
  function bubbleModel() {
    if (!page.target) return null;
    const here = page.target, now = Date.now();
    if (state.active_job) {
      if (JOB_PAGE[state.active_job] === here) return null;
      const p = state.progress;
      return { kind: "work", label: JOB_LABEL[state.active_job] || "Ci sto lavorando", meta: p !== null && p !== undefined ? Math.round(p * 100) + "%" : fmt(now - state.job_started), progress: p, go: JOB_PAGE[state.active_job] };
    }
    if (state.error && state.error_job && now - (Number(state.error_at) || Number(state.updated) || 0) < ERROR_BUBBLE_MS) {
      const where = JOB_PAGE[state.error_job] || "home";
      if (where === here) return null;
      return { kind: "error", label: "Si è fermato", meta: "Riprova ›", go: where };
    }
    if (state.short_ready && !state.published && state.ready_at && now - state.ready_at < 120e3 && here !== "social") {
      return { kind: "done", label: "Short pronto", meta: "Pubblica ›", go: "short" };
    }
    return null;
  }
  let bubbleGo = null, bubbleKind = "";
  function renderBubble() {
    if (!bubbleEl) return;
    let shared = false;
    try { shared = !!(W.top.GSFNotify && W.top.GSFNotify.alive); } catch (_e) {}
    const m = mounted && visible() && !shared ? bubbleModel() : null;
    bubbleGo = m ? m.go : null;
    if (!m) { bubbleEl.classList.remove("on", "spin", "done"); bubbleEl.tabIndex = -1; bubbleKind = ""; return; }
    const ins = insets();
    if (page.dock === "bottom") { bubbleEl.style.top = ""; bubbleEl.style.bottom = ins.bottom + 14 + "px"; }
    else { bubbleEl.style.bottom = ""; bubbleEl.style.top = ins.top + 10 + "px"; }
    bubbleEl.querySelector(".l").innerHTML = m.kind === "done" ? "<b>●</b> " + m.label : m.label;
    bubbleEl.querySelector("small").textContent = m.meta;
    const v = bubbleEl.querySelector(".v");
    const known = m.kind === "work" && m.progress !== null && m.progress !== undefined;
    v.style.strokeDashoffset = String(75.4 * (1 - (m.kind === "work" ? (known ? m.progress : 0.28) : 1)));
    bubbleEl.classList.toggle("spin", m.kind === "work" && !known);
    if (m.kind === "done" && bubbleKind !== "done") { bubbleEl.classList.remove("done"); void bubbleEl.offsetWidth; bubbleEl.classList.add("done"); }
    bubbleKind = m.kind;
    bubbleEl.setAttribute("aria-label", m.label + " · " + m.meta);
    bubbleEl.tabIndex = 0;
    bubbleEl.classList.add("on");
  }
  function onBubble() { if (bubbleGo) { haptic(8); go(bubbleGo); } }

  /* ----- celebrate: a burst of brand light, then calm ----- */
  function celebrate(origin) {
    if (!layer || reduced() || !visible()) return;
    const c = D.createElement("canvas"), dpr = Math.min(2, W.devicePixelRatio || 1), w = W.innerWidth, h = W.innerHeight;
    c.width = w * dpr; c.height = h * dpr; Object.assign(c.style, { position: "fixed", inset: "0", width: w + "px", height: h + "px" });
    layer.appendChild(c);
    const ctx = c.getContext("2d"); if (!ctx) { c.remove(); return; }
    ctx.scale(dpr, dpr);
    let ox = w / 2, oy = h * 0.42;
    const src = origin || D.querySelector("[data-alive-orb]");
    if (src && src.getBoundingClientRect) { const r = src.getBoundingClientRect(); if (r.width) { ox = r.left + r.width / 2; oy = r.top + r.height / 2; } }
    const hues = ["#27AEF3", "#53E0EA", "#5ED6A0", "#9D82FF", "#FFFFFF"], parts = [];
    for (let i = 0; i < 46; i++) { const a = Math.random() * Math.PI * 2, sp = 2.4 + Math.random() * 5.2; parts.push({ x: ox, y: oy, vx: Math.cos(a) * sp, vy: Math.sin(a) * sp - 1.6, r: 1.6 + Math.random() * 3.2, c: hues[i % hues.length], ring: i % 5 === 0 }); }
    const t0 = performance.now();
    const frame = t => {
      const k = (t - t0) / 1250;
      ctx.clearRect(0, 0, w, h);
      if (k >= 1) { c.remove(); return; }
      ctx.globalAlpha = Math.max(0, 1 - k * k);
      ctx.lineWidth = 2;
      ctx.strokeStyle = "rgba(94,214,160," + (0.6 * (1 - k)) + ")";
      ctx.beginPath(); ctx.arc(ox, oy, 30 + k * 160, 0, Math.PI * 2); ctx.stroke();
      for (const p of parts) {
        p.x += p.vx; p.y += p.vy; p.vy += 0.09; p.vx *= 0.985;
        ctx.beginPath(); ctx.arc(p.x, p.y, p.r * (p.ring ? 1.8 : 1), 0, Math.PI * 2);
        if (p.ring) { ctx.strokeStyle = p.c; ctx.stroke(); } else { ctx.fillStyle = p.c; ctx.fill(); }
      }
      animate(frame);
    };
    animate(frame);
  }

  /* ----- real render tracking: one page (the leader) asks the server ----- */
  const LEAD = "gsf_alive_leader_v418";
  function leader() {
    try {
      const now = Date.now(), cur = JSON.parse(localStorage.getItem(LEAD) || "null");
      if (!cur || cur.id === ME || now - cur.ts > 6000) { localStorage.setItem(LEAD, JSON.stringify({ id: ME, ts: now })); return true; }
      return false;
    } catch (_e) { return true; }
  }
  let polling = false, probed = false, watchFrom = 0, watchUntil = 0;
  const RENDER_WATCH="gsf_alive_render_watch_v418";
  function sharedRenderWatch(){try{const value=JSON.parse(localStorage.getItem(RENDER_WATCH)||"null");return value&&Number.isFinite(Number(value.from))&&Number.isFinite(Number(value.until))?{from:Number(value.from),until:Number(value.until)}:null}catch(_e){return null}}
  /* The pending intent survives route suspension; only server state starts a job. */
  function watchRender() {
    const now=Math.max(Date.now(),watchFrom+1,Number(sharedRenderWatch()?.from||0)+1);watchFrom=now;watchUntil=now+90e3;
    try{localStorage.setItem(RENDER_WATCH,JSON.stringify({from:watchFrom,until:watchUntil}))}catch(_e){}
    later(pollRender,1500);
  }
  async function jobStatus() {
    try { const r = await fetch("/job/status?alive=1&_=" + Date.now(), { cache: "no-store", credentials: "same-origin", signal:routeAbort?.signal }); return r.ok ? await r.json() : null; } catch (_e) { return null; }
  }
  async function pollRender() {
    if (polling || !leader()) return;
    const shared=sharedRenderWatch();
    if(shared&&Number(shared.until)>Date.now()&&Number(shared.from)>watchFrom){watchFrom=Number(shared.from);watchUntil=Number(shared.until)}
    const tracking = state.active_job === "render";
    const watchedFrom=watchFrom;
    const watching = Date.now() < watchUntil;
    if (!tracking && probed && !watching) return;
    polling = true;
    const generation=routeGeneration;
    try {
      const j = await jobStatus();
      const latestWatch=sharedRenderWatch();
      if(generation!==routeGeneration||!visible()||watchFrom!==watchedFrom||(latestWatch&&latestWatch.until>Date.now()&&latestWatch.from>watchedFrom))return;
      if (!j || !j.ok) return;
      const st = String(j.render_status || ""), started = Number(j.started_at) * 1000 || 0;
      if (!tracking) {
        probed = true;
        const recent = watching ? started >= watchedFrom - 10e3 : Date.now() - started < 15 * 60e3;
        if (st === "running" && started && recent) {
          watchUntil=0;
          try{const pending=sharedRenderWatch();if(pending&&Number(pending.from)<=watchedFrom)localStorage.removeItem(RENDER_WATCH)}catch(_e){}
          emit("render.started",{started_at:started});
        }
        return;
      }
      if (st === "running") return;
      if (st === "ready" && j.download_ready && (!started || started >= state.job_started - 120e3)) emit("render.completed");
      /* "missing" is a ready job whose file is still being restored: keep waiting, the TTL ends it. */
      else if (st === "failed" || st === "stale") emit("failure", { job: "render", message: "Il montaggio si è fermato. Riproviamo." });
      else if (st === "cancelled") emit("render.cancelled");
      else if (!st && Date.now() - state.job_started > 120e3) emit("render.cancelled");
    } finally { polling = false; }
  }

  /* ----- lifecycle ----- */
  function tick() {
    const now = Date.now();
    const e = expire(state, now);
    if (e !== state) commit(e, false);
    if (state.active_job || bubbleKind) renderBubble();
    idleCheck();
  }
  function onVisible() {
    if (D.hidden) { hiddenAt = Date.now(); return; }
    const away = hiddenAt ? Date.now() - hiddenAt : 0;
    hiddenAt = 0;
    const fresh = store.get();
    if (fresh && (Number(fresh.updated) || 0) > (Number(state.updated) || 0)) commit(Object.assign({}, BASE, fresh), true);
    if (away > 120e3 && mounted && visible()) later(() => say(welcome(state), { anchor: page.voiceAnchor }), 500);
    paint(); renderBubble(); guide();
  }
  function suspendRoute(){
    ++routeGeneration;
    if(routeAbort){routeAbort.abort();routeAbort=null}
    for(const timer of pendingTimers)W.clearTimeout(timer);pendingTimers.clear();
    for(const frame of pendingFrames)W.cancelAnimationFrame(frame);pendingFrames.clear();
    clearTimeout(whisperTimer);clearTimeout(celebrateTimer);
    if(layer){layer.style.display="none";layer.querySelectorAll(".gsf-alive-echo,canvas").forEach(el=>el.remove())}
    if(whisperEl)whisperEl.classList.remove("on");
    if(guideEl)guideEl.style.display="none";
    D.querySelectorAll(".gsf-alive-halo.beat").forEach(el=>el.classList.remove("beat"));
    if(liveEl)liveEl.textContent="";
    whisperAnchor=null;guided=null;lastSpokenSeq=state.seq;renderBubble();
  }
  function syncRoute(){
    if(!visible()){suspendRoute();return}
    if(routeAbort)return;
    routeAbort=new AbortController();const signal=routeAbort.signal;
    if(layer)layer.style.display="";
    const fresh=store.get();if(fresh&&(Number(fresh.updated)||0)>(Number(state.updated)||0))state=Object.assign({},BASE,fresh);
    lastSpokenSeq=state.seq;
    D.addEventListener("pointerdown",echo,{capture:true,passive:true,signal});
    D.addEventListener("keydown",()=>{lastActivity=Date.now()},{capture:true,passive:true,signal});
    const position=()=>{guide();renderBubble();if(whisperEl.classList.contains("on"))placeWhisper(whisperAnchor)};
    W.addEventListener("resize",position,{passive:true,signal});
    W.addEventListener("scroll",()=>{lastActivity=Date.now();position()},{capture:true,passive:true,signal});
    const intervals=[W.setInterval(tick,1000),W.setInterval(()=>{pollRender();scanOrbs()},3000),W.setInterval(()=>{if(Date.now()<watchUntil)pollRender()},2000)];
    signal.addEventListener("abort",()=>intervals.forEach(id=>W.clearInterval(id)),{once:true});
    scanOrbs();paint();renderBubble();guide();later(pollRender,1200);
  }
  function mount(opts) {
    const o=opts||{};
    page={name:String(o.page||"page"),target:TARGET[o.page]||o.target||null,voiceAnchor:o.voiceAnchor||null,dock:o.dock==="bottom"?"bottom":"top"};
    root.dataset.alivePage=page.name;
    const start=()=>{
      build();if(mounted){syncRoute();return}mounted=true;
      // Only these lifetime observers survive a route: shared facts stay intact,
      // while per-route listeners, timers, fetches and animation are cancelled.
      try{W.parent.addEventListener("gsf:surfacechange",syncRoute)}catch(_e){}
      D.addEventListener("visibilitychange",()=>{syncRoute();if(!D.hidden)onVisible()});
      W.addEventListener("message",e=>{if(e.origin!==location.origin||!e.data)return;if(e.data.type==="GSF_APP_SUSPEND"&&!visible())suspendRoute();if(e.data.type==="GSF_APP_RESUME")syncRoute()});
      W.addEventListener("pagehide",()=>{suspendRoute();try{W.parent.removeEventListener("gsf:surfacechange",syncRoute)}catch(_e){}});W.addEventListener("pageshow",()=>{try{W.parent.addEventListener("gsf:surfacechange",syncRoute)}catch(_e){}syncRoute()});
      syncRoute();
    };
    if(D.body)start();else D.addEventListener("DOMContentLoaded",start,{once:true});
    return W.GSFAlive;
  }

  W.GSFAlive = {
    mount, emit, say, celebrate, beat, go, watchRender,
    state: () => Object.assign({}, state),
    next: () => nextAction(state),
    on(fn) { listeners.add(fn); return () => listeners.delete(fn); },
    refresh() {
      scanOrbs(); paint(); guide(); renderBubble();
      if (whisperEl && whisperEl.classList.contains("on") && whisperAnchor) {
        const anchor = typeof whisperAnchor === "string" ? D.querySelector(whisperAnchor) : whisperAnchor;
        const rect = anchor && anchor.getBoundingClientRect();
        if (!rect || !rect.width || !rect.height) {
          clearTimeout(whisperTimer); whisperEl.classList.remove("on"); whisperAnchor = null;
          if (liveEl) liveEl.textContent = "";
        }
      }
    },
    _core: core,
  };
})();
