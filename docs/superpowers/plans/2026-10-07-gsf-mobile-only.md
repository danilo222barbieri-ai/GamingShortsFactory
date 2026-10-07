# GSF Mobile-Only Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Pubblicare Gaming Shorts Factory come esperienza mobile-only, bloccare la UI operativa su desktop, correggere la pagina Motore IA e rendere lo scrolling esclusivamente interno alle pagine secondarie.

**Architecture:** Nginx diventa il gate pubblico: i browser mobile/tablet continuano verso le superfici esistenti, mentre desktop/laptop ricevono una pagina statica minimale. La UI mobile esistente resta la sola fonte visuale; il flusso AI V288 viene corretto senza toccare i quattro motori o il bridge backend. Home resta non scrollabile, mentre AI/Creator Hub/Editor/Share gestiscono il proprio overflow interno. I mini-player usano fullscreen video nativo su iOS quando disponibile e Fullscreen API/fallback sugli altri browser.

**Tech Stack:** Nginx, HTML/CSS/JavaScript, Python regression scripts, Streamlit components, Railway/Docker.

**Spec:** `docs/superpowers/specs/2026-10-07-gsf-mobile-only-design.md`

## Global Constraints

- Prodotto pubblico mobile-only; nessuna UI desktop operativa.
- Non riutilizzare il branch V308; lavorare su `gsf-mobile-only` derivato da `main`.
- Non modificare pipeline render V100.4: libx264, preset medium, CRF 14, H.264 High, AAC, 60 fps, 1080x1920.
- Non cambiare i quattro motori AI, worker, upload, persistenza progetti/bozze o API social.
- Home senza scrolling; scrolling soltanto interno alle pagine secondarie.
- Rimuovere la line-up `1 Motore / 2 Momento / 3 Editor / 4 Crea Short / 5 Pronto`.
- Le tre migliori giocate restano sotto i motori e sono raggiungibili tramite scroll interno.
- Tap su mini-player apre fullscreen e l'uscita conserva selezione/stato.
- Nessun nuovo startup patcher visuale storico.
- Nessun deploy in produzione finché build e regression contract non sono verdi.

## Review Focus

- iPad/iPhone con user-agent desktop-like ma marker `Mobile`: devono entrare nell'app, non nel gate desktop.
- OAuth callback sulla root con `state=gsf...`: deve continuare a raggiungere il callback anche se il browser è desktop.
- Accesso diretto alle superfici `/ai-v221/`, `/editor-live/`, `/creator-hub-v156/`, `/share-v156/` da desktop: deve ricevere il gate, non la UI operativa.
- Uscita da fullscreen video: il momento selezionato e i pulsanti Editor/Crea Short devono restare attivi.
- Viewport mobile basso/orizzontale: nessun doppio scroll; Home resta ferma e la superficie interna resta scrollabile.

---

### Task 1: Mobile-only public gate

**Files:**
- Create: `web/mobile_only_gate.html`
- Create: `web/test_mobile_only_gate.py`
- Modify: `web/nginx.conf.template`

**Interfaces:**
- Consumes: header `Sec-CH-UA-Mobile`, `User-Agent`, route pubbliche esistenti.
- Produces: variabile Nginx `$gsf_mobile_client`; gate statico `mobile_only_gate.html`; blocco desktop sulle superfici UI.

- [ ] **Step 1: Write the failing gate contract test**

Creare `web/test_mobile_only_gate.py` con assert che richiedono:
- `mobile_only_gate.html` contiene `GSF è disponibile da smartphone`;
- nessun link/bottone nel gate offre una versione desktop;
- `nginx.conf.template` classifica mobile tramite `Sec-CH-UA-Mobile` e user-agent iPhone/iPad/Android/mobile/tablet;
- `/desktop-preview` e `/desktop-home` non servono più alias UI e tornano alla root;
- le superfici `/`, `/ai-v221/`, `/editor-live/`, `/creator-hub-v156/`, `/share-v156/` applicano il gate ai client desktop;
- i callback OAuth della root vengono valutati prima del gate desktop.

- [ ] **Step 2: Run the test and verify RED**

Run: `python web/test_mobile_only_gate.py web/nginx.conf.template web/mobile_only_gate.html`

Expected: FAIL perché gate e contratto non esistono ancora.

- [ ] **Step 3: Implement the static desktop gate**

Creare `web/mobile_only_gate.html` senza dipendenze esterne, con viewport responsive, titolo GSF e testo esatto `GSF è disponibile da smartphone`. Nessun link alla UI operativa.

- [ ] **Step 4: Implement Nginx mobile classification and UI blocking**

In `web/nginx.conf.template`:
- aggiungere mappe HTTP per `Sec-CH-UA-Mobile` e user-agent mobile/tablet;
- aggiungere un named/internal location per servire `mobile_only_gate.html` con `Cache-Control: no-store`;
- preservare gli `error_page` OAuth già presenti nella root e applicare il gate solo dopo i controlli `state=gsf...`;
- applicare lo stesso gate alle quattro superfici statiche AI/Editor/Hub/Share;
- sostituire `/desktop-preview` e `/desktop-home` con redirect alla root, senza alias delle vecchie UI.

- [ ] **Step 5: Run contract + Nginx syntax check**

Run: `python web/test_mobile_only_gate.py web/nginx.conf.template web/mobile_only_gate.html`
Expected: PASS.

Run in Docker/CI: `nginx -t -c /etc/nginx/nginx.conf`
Expected: syntax OK.

- [ ] **Step 6: Commit**

Commit message: `feat: gate GSF to mobile clients`

---

### Task 2: Remove Motore IA line-up without breaking the real flow

**Files:**
- Modify: `web/fix_v288_ai_journey.py`
- Modify: `web/test_v288_ai_journey.py`
- Create: `web/test_mobile_ai_surface.py`

**Interfaces:**
- Consumes: existing four engine buttons, preview data, `select_moment`, `open_editor`, `create_short` bridge events.
- Produces: same backend/event contract with no visible five-step journey bar.

- [ ] **Step 1: Write the failing mobile AI contract**

Creare `web/test_mobile_ai_surface.py` che verifica sul file patcher:
- nessuna iniezione di `.journeySteps` o dei testi `1 Motore`, `2 Momento`, `3 Editor`, `4 Crea Short`, `5 Pronto`;
- restano `TROVA I 3 MOMENTI MIGLIORI`, `momentNextActions`, `select_moment`, `open_editor`, `create_short`;
- restano quattro motori reali;
- la superficie AI mantiene overflow interno.

Aggiornare `web/test_v288_ai_journey.py` rimuovendo soltanto l'aspettativa della progress bar e sostituendola con l'aspettativa che la line-up sia assente.

- [ ] **Step 2: Run tests and verify RED**

Run: `python web/test_mobile_ai_surface.py web/fix_v288_ai_journey.py web/ai_v221_component/index.html`
Expected: FAIL perché V288 inietta ancora la line-up.

- [ ] **Step 3: Remove only the journey bar from V288**

In `web/fix_v288_ai_journey.py`:
- eliminare `AI_STEPS` e l'iniezione `<div class="journeySteps">...`;
- eliminare soltanto CSS/JS legato alla progress bar;
- mantenere selezione momento, action panel, bridge Home, CTA Editor e creazione Short diretta;
- recuperare lo spazio con margini/padding mobile più ariosi per titolo, durata e motori, lasciando i momenti sotto.

- [ ] **Step 4: Run AI contracts**

Run: `python web/test_mobile_ai_surface.py web/fix_v288_ai_journey.py web/ai_v221_component/index.html`
Expected: PASS.

Run sull'HTML patchato in CI/container: `python web/test_v288_ai_journey.py /app/web/ai_v221_component/index.html /app/web/home_v154_component/index.html /app/web/editor_2027_component/index.html /app/GamingShortsFactory_V154_STRUCTURAL_HOME.py`
Expected: PASS.

- [ ] **Step 5: Commit**

Commit message: `fix: simplify mobile AI journey`

---

### Task 3: Fullscreen mini-player with state preservation

**Files:**
- Modify: `web/fix_v288_ai_journey.py`
- Modify: `web/test_mobile_ai_surface.py`

**Interfaces:**
- Consumes: `state.previews`, `state.selectedMoment`, existing `.moment` cards/videos.
- Produces: `openMomentFullscreen(video, index)` behavior; same selected moment after fullscreen exit.

- [ ] **Step 1: Extend the failing AI contract**

Aggiungere assert per:
- iOS native path `webkitEnterFullscreen`;
- standard path `requestFullscreen`;
- fallback mobile fullscreen class/overlay senza nuova dipendenza;
- exit handlers che non azzerano `state.selectedMoment`;
- click/tap del mini-player usa il momento già selezionato.

- [ ] **Step 2: Run test and verify RED**

Run: `python web/test_mobile_ai_surface.py web/fix_v288_ai_journey.py web/ai_v221_component/index.html`
Expected: FAIL sulle nuove aspettative fullscreen.

- [ ] **Step 3: Implement fullscreen helper in V288 AI JS**

Nel JS iniettato da `fix_v288_ai_journey.py`:
- creare/mantenere il video dentro la thumb del momento selezionato;
- al tap tentare `video.webkitEnterFullscreen()` su iPhone/iPad;
- altrimenti usare `video.requestFullscreen()` o il contenitore fullscreen;
- fallback CSS/JS a overlay viewport se nessuna API è disponibile;
- su `webkitendfullscreen`/`fullscreenchange`/chiusura fallback tornare alla stessa card senza ricreare o azzerare `state.selectedMoment`;
- evitare che il tap fullscreen emetta una seconda navigazione verso Editor/Short.

- [ ] **Step 4: Run AI contract**

Run: `python web/test_mobile_ai_surface.py web/fix_v288_ai_journey.py web/ai_v221_component/index.html`
Expected: PASS.

- [ ] **Step 5: Commit**

Commit message: `feat: fullscreen AI moment previews`

---

### Task 4: One scroll owner per mobile page

**Files:**
- Modify: `web/home_v154_component/index.html`
- Modify: `web/ai_v221_component/index.html`
- Modify: `web/creator_hub_v156_component/index.html`
- Modify: `web/editor_2027_component/index.html`
- Modify: `web/share_v156_component/index.html`
- Create: `web/test_mobile_scroll_contract.py`

**Interfaces:**
- Consumes: each component's top-level root (`#home154`, `#ai221`, `#hub`, `#ng27`, Share root).
- Produces: Home fixed; exactly one internal scrolling surface per secondary page.

- [ ] **Step 1: Write the failing scroll contract**

Creare `web/test_mobile_scroll_contract.py` che verifica:
- Home `html,body` e `#home154` restano `overflow:hidden`;
- AI root usa `overflow-y:auto`/equivalente e `overscroll-behavior:contain`;
- Creator Hub usa la stage/view attiva come unico scroll owner, non il browser body;
- Editor root/shell può scorrere internamente nei viewport bassi senza rendere scrollabile il body;
- Share root può scorrere internamente senza body scroll;
- nessuna superficie introduce due `overflow-y:auto` annidati nel percorso principale mobile.

- [ ] **Step 2: Run test and verify RED**

Run: `python web/test_mobile_scroll_contract.py web/home_v154_component/index.html web/ai_v221_component/index.html web/creator_hub_v156_component/index.html web/editor_2027_component/index.html web/share_v156_component/index.html`
Expected: FAIL almeno su Hub/Editor/Share o overscroll contract.

- [ ] **Step 3: Normalize mobile scroll ownership**

Applicare alle superfici interne:
- `html,body { overflow:hidden; }`;
- un solo contenitore principale con `overflow-y:auto`, `overscroll-behavior:contain`, `-webkit-overflow-scrolling:touch`;
- Home invariata come superficie fissa;
- niente modifica a ordine/azioni della Game Bar o ai bridge JS.

Per Creator Hub, mantenere header/top fisso dentro `#hub` e rendere scrollabile la sola `.stage`/`.view.active`. Per Editor e Share scegliere il contenitore già esistente più interno che racchiude l'intera pagina funzionale, senza introdurre un secondo wrapper strutturale.

- [ ] **Step 4: Run scroll contract**

Run: `python web/test_mobile_scroll_contract.py web/home_v154_component/index.html web/ai_v221_component/index.html web/creator_hub_v156_component/index.html web/editor_2027_component/index.html web/share_v156_component/index.html`
Expected: PASS.

- [ ] **Step 5: Commit**

Commit message: `fix: keep mobile scrolling inside pages`

---

### Task 5: Startup regression gate and isolated build verification

**Files:**
- Modify: `web/start_web.sh`
- Create: `.github/workflows/mobile-only-check.yml`

**Interfaces:**
- Consumes: Tasks 1-4 test scripts and existing Dockerfile/startup chain.
- Produces: branch CI that proves Docker build + mobile-only contracts + container startup before production deploy.

- [ ] **Step 1: Add branch CI before touching Railway production**

Workflow trigger: pushes to `gsf-mobile-only`.

Steps:
- build the real `Dockerfile` image;
- run `test_mobile_only_gate.py`, `test_mobile_ai_surface.py`, `test_mobile_scroll_contract.py` against the built filesystem or checked-out canonical files as appropriate;
- start the image with a non-production local port;
- smoke HTTP with a mobile user-agent and verify app path does not return the desktop gate;
- smoke HTTP with desktop Chrome user-agent and verify response contains `GSF è disponibile da smartphone`;
- request `/desktop-home` and `/desktop-preview` and verify they no longer expose old desktop HTML.

- [ ] **Step 2: Add final startup contract calls only after CI is green**

In `web/start_web.sh`, add the mobile-only static regression tests after V288/V304 functional patches and before final render-memory generation. Do not remove unrelated functional patchers in this release.

- [ ] **Step 3: Run branch CI to terminal success**

Expected: Docker build PASS, contracts PASS, container startup PASS, both mobile and desktop HTTP smoke PASS.

- [ ] **Step 4: Verify no backend/render diff**

Compare branch with `main`; confirm no changes to FFmpeg/render modules, AI worker, upload server behavior, persistence contracts or social provider logic beyond Nginx UI gating.

- [ ] **Step 5: Commit**

Commit message: `test: verify mobile-only production contract`

---

### Task 6: Production rollout

**Files:**
- No new product files; deployment/config only after Tasks 1-5 are green.

**Interfaces:**
- Consumes: verified `gsf-mobile-only` branch head.
- Produces: Railway production deployment of the mobile-only release.

- [ ] **Step 1: Point/deploy Railway frontend to the verified commit**

Do not change the AI worker service unless source linkage requires no-op metadata refresh.

- [ ] **Step 2: Poll deployment to terminal state**

Expected: `SUCCESS`.

- [ ] **Step 3: Inspect production logs**

Require:
- no Python `SyntaxError`;
- no startup regression FAIL;
- Nginx starts cleanly;
- Streamlit healthcheck succeeds;
- no stale V308 patcher is executed.

- [ ] **Step 4: Production acceptance smoke**

Verify:
- desktop Chrome gets only the smartphone gate;
- iPhone/Android-class user-agent reaches GSF;
- `/desktop-preview` and `/desktop-home` do not expose desktop UI;
- AI page has no five-step line-up;
- the three moments remain below engines with internal scroll;
- fullscreen preview returns to the selected moment;
- Home does not scroll.

- [ ] **Step 5: Only then call the release published**

Do not report completion before Railway is `SUCCESS` and the production smoke passes.
