from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")


def write(path: str, text: str) -> None:
    (ROOT / path).write_text(text, encoding="utf-8")


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one match, found {count}")
    return text.replace(old, new, 1)


def sub_once(text: str, pattern: str, replacement: str, label: str, flags: int = 0) -> str:
    next_text, count = re.subn(pattern, replacement, text, count=1, flags=flags)
    if count != 1:
        raise RuntimeError(f"{label}: expected exactly one regex match, found {count}")
    return next_text


# 1) Editor: Done == save/close; only the explicit Crea Short CTA continues to render.
path = "web/game_editor_mobile_component/editor.mjs"
text = read(path)
text = replace_once(
    text,
    '$("#continueButton").addEventListener("click", () => requestEditorAction("continue_to_short"));',
    '$("#continueButton").addEventListener("click", () => requestEditorAction("close"));',
    "editor Done action",
)
write(path, text)

path = "web/game_editor_mobile_component/index.html"
text = read(path)
text = replace_once(
    text,
    '/* GSF_V427_MINI_EDITOR_HEADER_CLEANUP */\n.editor-app.is-mini .editor-header{display:none!important}',
    '/* GSF_V427_MINI_EDITOR_HEADER_CLEANUP */\n.editor-app.is-mini .editor-header{display:none!important}\n/* GSF_V428_HIDE_EXPANDED_PLACEHOLDER_TITLE: fullscreen keeps controls, not the redundant project label. */\n.editor-app.is-expanded .project-identity{display:none!important}',
    "expanded editor title cleanup",
)
write(path, text)


# 2) Home: the parent/global Game Bar owns navigation; the old child nav must not paint at all.
path = "web/home_v154_component/index.html"
text = read(path)
anchor = 'html.gsf-v343-parent-ready #home154 .features{top:0!important}'
text = replace_once(
    text,
    anchor,
    anchor + '\n/* GSF_V428_GLOBAL_GAMEBAR_OWNS_NAV */\nhtml.gsf-v343-parent-ready #home154 .bottomNav{display:none!important}',
    "home global gamebar ownership",
)
write(path, text)


# 3) Instagram: when direct Instagram credentials exist, use Instagram OAuth even if Meta is configured.
path = "web/direct_upload_server.py"
text = read(path)
text = replace_once(
    text,
    '    # GSF_V427_INSTAGRAM_META_FIRST: when the Meta professional flow is\n'
    '    # configured, prefer it for publishing so users do not hit Instagram\n'
    '    # Login\'s development-role gate. Direct Instagram Login remains fallback.\n'
    '    if INSTAGRAM_APP_ID and INSTAGRAM_APP_SECRET and not (META_APP_ID and META_APP_SECRET):',
    '    # GSF_V428_INSTAGRAM_DIRECT_FIRST: connection and publishing are separate.\n'
    '    # Prefer the dedicated Instagram Login whenever its credentials exist;\n'
    '    # Facebook Login remains a compatibility fallback for Meta-only installs.\n'
    '    if INSTAGRAM_APP_ID and INSTAGRAM_APP_SECRET:',
    "Instagram direct OAuth preference",
)

# 4) Notifications: one parent-owned surface, never squeezed between brand/profile, readable long enough,
#    and visually closer to a handwritten GSF note than a generic system toast.
text = replace_once(
    text,
    "const ttl=r.data.ttl===undefined?(r.data.kind==='error'?7000:4200):Number(r.data.ttl);",
    "const ttl=r.data.ttl===undefined?(r.data.kind==='error'?9000:6500):Number(r.data.ttl);",
    "notification lifetime",
)
text = sub_once(
    text,
    r"\s*const inline=visible\(header\)&&header\.id==='gsf-global-header'&&!\[\.\.\.records\.values\(\)\]\.some\(r=>r\.el&&r\.data\.kind==='confirm'\);\n"
    r"\s*host\.classList\.toggle\('gsf-inline',inline\);host\.classList\.toggle\('gsf-pill',!\[\.\.\.records\.values\(\)\]\.some\(r=>r\.el&&r\.data\.kind==='confirm'\)\);\n"
    r"\s*if\(inline\)\{.*?\n\s*\}\n",
    "\n      /* GSF_V428_PEN_NOTIFICATIONS: one readable surface, never inside the profile header. */\n"
    "      const inline=false;\n"
    "      host.classList.remove('gsf-inline');host.classList.remove('gsf-pill');\n",
    "remove header-inline notification placement",
    flags=re.S,
)
text = replace_once(
    text,
    "#gsf-site-toast-stack{position:fixed;right:max(12px,env(safe-area-inset-right,0px));top:max(10px,env(safe-area-inset-top,0px));z-index:2147483647;width:min(320px,calc(100vw - 24px));display:flex;flex-direction:column;gap:8px;pointer-events:none;font-family:'Avenir Next','SF Pro Text',-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;overflow:hidden;contain:layout style}",
    "#gsf-site-toast-stack{position:fixed;left:50%;right:auto;top:max(10px,env(safe-area-inset-top,0px));z-index:2147483647;width:min(360px,calc(100vw - 32px));display:flex;flex-direction:column;gap:8px;pointer-events:none;font-family:'Caveat','Segoe Print','Bradley Hand',cursive;overflow:hidden;contain:layout style;transform:translateX(-50%)}",
    "notification handwritten stack",
)
text = replace_once(
    text,
    ".gsf-site-toast-icon{width:28px;height:28px;display:grid;place-items:center;color:#79d2ff}.gsf-site-toast-icon img{width:26px;height:26px;object-fit:contain;border-radius:7px}.gsf-site-toast-copy{min-width:0}.gsf-site-toast-title{font-size:12px;font-weight:800;line-height:1.35;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.gsf-site-toast-body{font-size:11px;line-height:1.4;color:#abc3d5;min-height:15px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;margin-top:3px}",
    ".gsf-site-toast-icon{width:28px;height:28px;display:grid;place-items:center;color:#79d2ff}.gsf-site-toast-icon img{width:26px;height:26px;object-fit:contain;border-radius:7px}.gsf-site-toast-copy{min-width:0}.gsf-site-toast-title{font-size:17px;font-weight:700;line-height:1.05;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}.gsf-site-toast-body{font-size:15px;line-height:1.15;color:#c8deed;min-height:17px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;margin-top:4px}",
    "notification pen typography",
)
write(path, text)


# 5) AI moments: remove status clutter, expose existing re-search action, make the three moments swipeable,
#    keep details synchronized, and reserve final generation for the explicit Crea Short CTA.
path = "web/ai_v221_component/index.html"
text = read(path)
text = replace_once(
    text,
    '.portals{flex:1;min-height:0;display:flex;align-items:center;justify-content:center;gap:clamp(6px,2.5vw,26px)}',
    '/* GSF_V428_MOMENT_CAROUSEL */\n.portals{flex:1;min-height:0;display:flex;align-items:center;justify-content:flex-start;gap:clamp(16px,5vw,28px);overflow-x:auto;overscroll-behavior-x:contain;scroll-snap-type:x mandatory;scrollbar-width:none;padding:12px calc(50% - min(19vw,14.5vh,115px))}\n.portals::-webkit-scrollbar{display:none}',
    "moments carousel container",
)
text = replace_once(
    text,
    '.short{--s:min(25vw,19vh,150px);position:relative;flex:0 0 auto;width:var(--s);height:var(--s);border-radius:50%;cursor:pointer;transition:width .4s var(--ease),height .4s var(--ease)}',
    '.short{--s:min(38vw,29vh,230px);position:relative;flex:0 0 auto;width:var(--s);height:var(--s);border-radius:50%;cursor:pointer;scroll-snap-align:center;scroll-snap-stop:always;opacity:.66;transform:scale(.88);transition:transform .32s var(--ease),opacity .32s var(--ease)}',
    "moment snap item",
)
text = replace_once(
    text,
    '.short.is-selected{--s:min(38vw,29vh,230px)}',
    '.short.is-selected{opacity:1;transform:scale(1)}',
    "selected moment scale",
)
# Add compact page indicators just below the swipe surface.
text = replace_once(
    text,
    '.short.is-selected{opacity:1;transform:scale(1)}',
    '.short.is-selected{opacity:1;transform:scale(1)}\n.moment-dots{flex:0 0 auto;display:flex;justify-content:center;align-items:center;gap:7px;min-height:18px;margin:-2px 0 5px}.moment-dot{width:7px;height:7px;padding:0;border-radius:50%;background:rgba(159,183,202,.38);transition:transform .22s var(--ease),background .22s var(--ease)}.moment-dot.is-selected{transform:scale(1.45);background:var(--gsf-cyan)}',
    "moment dots css",
)
text = sub_once(
    text,
    r'<div class="side">\s*<button id="changeSearch".*?</button>\s*<span id="runChip".*?</span>\s*<span id="savedChip".*?</span>\s*</div>',
    '<div class="side">\n        <button id="changeSearch" class="back" type="button"><svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 3 5 8l5 5"/></svg>Cambia motore</button>\n        <button id="findMoreMoments" class="back" type="button">Trova altri momenti</button>\n      </div>',
    "moments top actions",
    flags=re.S,
)
text = replace_once(
    text,
    '<div id="previews" class="portals" aria-live="polite" data-alive-next="choose_moment"></div>',
    '<div id="previews" class="portals" aria-live="polite" data-alive-next="choose_moment"></div>\n    <div id="momentDots" class="moment-dots" aria-label="Momenti trovati"></div>',
    "moment dots markup",
)
text = replace_once(text, '>Pubblica</button>', '>Crea Short</button>', "create short label")
text = replace_once(
    text,
    '  const chip=$("savedChip"),text=$("savedText");chip.classList.add("busy");text.textContent="Salvo la bozza…";\n',
    '',
    "remove saved chip busy state",
)
text = sub_once(
    text,
    r'\s*const t=new Date\(\);chip\.classList\.remove\("busy"\);text\.textContent=`Bozza salvata · \$\{String\(t\.getHours\(\)\)\.padStart\(2,"0"\)\}:\$\{String\(t\.getMinutes\(\)\)\.padStart\(2,"0"\)\}`;',
    '',
    "remove saved chip completion state",
)
text = sub_once(
    text,
    r'  const r=rows\(\);\$\("runText"\)\.textContent=.*?;\$\("runChip"\)\.classList\.toggle\("ok",r\.length>0\);',
    '  const r=rows();',
    "remove run chip render state",
)
# Insert reusable dot renderer before the portal renderer.
text = replace_once(
    text,
    'function renderMoments(){',
    'function renderMomentDots(){\n  const host=$("momentDots"),r=rows();host.innerHTML="";\n  r.forEach((_item,index)=>{const dot=document.createElement("button");dot.type="button";dot.className="moment-dot"+(Number(state.selectedMoment)===index?" is-selected":"");dot.setAttribute("aria-label",`Vai al momento ${index+1}`);dot.addEventListener("click",()=>selectMoment(index));host.appendChild(dot)});\n}\n\nfunction renderMoments(){',
    "moment dots renderer",
)
text = replace_once(
    text,
    '  if(!r.length){host.innerHTML=\'<span class="sr">Sto preparando i tuoi momenti…</span>\'+[0,1,2].map(i=>\'<div class="short skel" style="--i:\'+i+\'" aria-hidden="true"><div class="frame"></div></div>\').join("");return}',
    '  if(!r.length){host.innerHTML=\'<span class="sr">Sto preparando i tuoi momenti…</span>\'+[0,1,2].map(i=>\'<div class="short skel" style="--i:\'+i+\'" aria-hidden="true"><div class="frame"></div></div>\').join("");renderMomentDots();return}',
    "empty carousel dots",
)
text = replace_once(
    text,
    '    host.appendChild(card)});\n}\nfunction renderDetail(){',
    '    host.appendChild(card)});\n  renderMomentDots();\n  requestAnimationFrame(()=>host.querySelector(`.short[data-index="${Number(state.selectedMoment)||0}"]`)?.scrollIntoView({behavior:"smooth",block:"nearest",inline:"center"}));\n}\nfunction renderDetail(){',
    "carousel selected centering",
)
# Swipe settles to the card closest to the viewport center, reusing the existing selection/save flow.
text = replace_once(
    text,
    '/* ---------- events ---------- */',
    'let momentScrollTimer=0;\nfunction syncMomentFromCarousel(){\n  const host=$("previews"),cards=[...host.querySelectorAll(".short[data-index]")];if(!cards.length)return;\n  const hr=host.getBoundingClientRect(),center=hr.left+hr.width/2;let best=cards[0],distance=Infinity;\n  cards.forEach(card=>{const r=card.getBoundingClientRect(),d=Math.abs((r.left+r.width/2)-center);if(d<distance){distance=d;best=card}});\n  const index=Number(best.dataset.index);if(Number.isInteger(index)&&index!==Number(state.selectedMoment))selectMoment(index);\n}\n$("previews").addEventListener("scroll",()=>{clearTimeout(momentScrollTimer);momentScrollTimer=setTimeout(syncMomentFromCarousel,130)},{passive:true});\n\n/* ---------- events ---------- */',
    "carousel swipe selection",
)
text = replace_once(
    text,
    '$("changeSearch").addEventListener("click",()=>{awaitingResults=false;pollToken++;state.processing=false;stopPlayback();setScan("off");showView("engines");send("change_engine");render()});',
    '$("changeSearch").addEventListener("click",()=>{awaitingResults=false;pollToken++;state.processing=false;stopPlayback();setScan("off");showView("engines");send("change_engine");render()});\n$("findMoreMoments").addEventListener("click",()=>{if(state.processing)return;stopPlayback();startSearch()});',
    "find more moments action",
)
write(path, text)

print("V428 deterministic mobile polish patch applied")
