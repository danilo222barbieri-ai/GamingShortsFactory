# GSF Mobile Master Responsive UI Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rendere la UI mobile approvata l’unica interfaccia visiva autorevole di Gaming Shorts Factory e farla scalare in modo fluido su tablet e desktop, eliminando layout desktop separati, cache-key storici e patch visuali in conflitto.

**Architecture:** Le cinque superfici HTML principali (Home, AI, Editor, Creator Hub, Share) mantengono un solo DOM e una sola logica. Il responsive avviene tramite CSS fluido e griglie automatiche, non tramite una seconda composizione desktop. Un modulo centrale `web/ui_release.py` possiede l’unico identificatore cache/UI; lo startup non ricostruisce più la grafica attraverso patch visuali storiche, ma valida sorgenti già canoniche prima di avviare Streamlit/Nginx.

**Tech Stack:** Python 3.12, Streamlit custom components, HTML/CSS/JavaScript, Nginx, Railway.

**Spec:** `docs/superpowers/specs/2026-10-07-mobile-master-responsive-ui-design.md`

## Global Constraints

- Un solo DOM, un solo set di componenti, un solo CSS master e una sola logica JavaScript per superficie.
- Desktop, tablet e mobile devono mostrare la stessa UI; cambiano solo scala, gap, larghezze e distribuzione dello spazio.
- Vietati nuovi layout `desktop`, `desk`, `mobile-copy`, `desktop-layout` o markup duplicati per viewport.
- Non modificare pipeline video, AI backend, worker, render FFmpeg, API progetto/bozza, route funzionali o persistenza.
- Home mobile approvata resta il riferimento visivo master.
- Game Bar e Footer restano globali.
- Il browser deve ricevere asset nuovi dopo il deploy senza richiedere svuotamento manuale della cache.
- Ogni file Python modificato deve compilare prima del deploy.
- La migrazione è completa solo con test funzionali verdi, Railway `SUCCESS` e verifica visiva finale mobile/desktop.

## Review Focus

- Viewport desktop basso (es. 1366×768): stessa UI senza tagli, sovrapposizioni o scroll inutile.
- Tablet 768–1024 px: nessun salto verso una seconda composizione; stessa gerarchia e stessi controlli.
- Browser con vecchi asset/cache-key: il nuovo release id deve forzare riferimenti freschi e le route UI devono restare `no-store`.
- Startup ripetuto: nessuna patch storica deve reintrodurre CSS DESK/DESKTOP o cache versionate vecchie.
- Funzioni reali (upload, AI, Editor, bozze/progetti, Game Bar, Share/download): i test visivi non devono rimuovere marker o bridge funzionali.

---

### Task 1: Centralizzare release UI e cache ownership

**Files:**
- Create: `web/ui_release.py`
- Create: `web/test_v308_ui_release.py`
- Modify: `web/home_v154_embed.py`
- Modify: `web/editor_2027_embed.py`

**Interfaces:**
- Produces: `GSF_UI_RELEASE: str = "308"`
- Produces: `versioned_path(path: str) -> str`, che restituisce `path` con un solo `?v=308` coerente.
- Consumes: nessuna dipendenza nuova oltre alla stdlib.

- [ ] **Step 1: Write the failing test**

Creare `web/test_v308_ui_release.py` con assert su:
- `GSF_UI_RELEASE == "308"`;
- `versioned_path("/ai-v221/") == "/ai-v221/?v=308"`;
- `versioned_path("/ai-v221/?v=287") == "/ai-v221/?v=308"`;
- Home embed dichiara il componente usando `GSF_UI_RELEASE`;
- Editor embed dichiara il componente usando `GSF_UI_RELEASE`.

- [ ] **Step 2: Run test to verify it fails**

Run: `python web/test_v308_ui_release.py .`

Expected: FAIL perché `web/ui_release.py` non esiste e gli embed usano ancora nomi hard-coded storici.

- [ ] **Step 3: Implement the release module and wire the embeds**

Creare `web/ui_release.py` con `GSF_UI_RELEASE = "308"` e `versioned_path(path: str) -> str`. Modificare `home_v154_embed.py` e `editor_2027_embed.py` affinché i nomi Streamlit custom component derivino dalla costante centrale, senza alterare parametri, state key o logica video.

- [ ] **Step 4: Verify green and compile**

Run: `python web/test_v308_ui_release.py . && python -m py_compile web/ui_release.py web/home_v154_embed.py web/editor_2027_embed.py`

Expected: PASS, nessun warning/error di sintassi.

- [ ] **Step 5: Commit**

```bash
git add web/ui_release.py web/test_v308_ui_release.py web/home_v154_embed.py web/editor_2027_embed.py
git commit -m "refactor: centralize GSF UI release version"
```

### Task 2: Rendere Home mobile-master realmente fluida

**Files:**
- Modify: `web/home_v154_component/index.html`
- Modify: `web/home_v154_embed.py`
- Create: `web/test_v308_home_mobile_master.py`

**Interfaces:**
- Consumes: `GSF_UI_RELEASE` da Task 1.
- Produces: Home con un solo DOM e CSS master, stesso ordine/componenti su ogni viewport.

- [ ] **Step 1: Write the failing Home contract test**

Il test deve verificare:
- assenza dei marker visuali desktop storici `V267`, `V268`, `V294`, `V296`, `V297`, `V298`, `V301`, `V305` nella Home;
- nessun `@media (min-width` che ricostruisca la Home;
- presenza di uploader, anelli, murales, tre CTA, Game Bar/footer e bridge upload correnti;
- un solo markup per le tre CTA;
- CSS fluido con `clamp(` e/o `min(`/`max(` per cerchio, tipografia, gap e margini;
- `home_v154_embed.py` non contenga più un blocco fullscreen valido solo `max-width:760px`; il parent shell deve trattare tutti i viewport con la stessa superficie.

- [ ] **Step 2: Run test to verify it fails**

Run: `python web/test_v308_home_mobile_master.py .`

Expected: FAIL sui residui desktop e sul parent shell mobile-only.

- [ ] **Step 3: Promote the approved mobile composition to base CSS**

Usare la geometria dell’attuale branch mobile come base. Conservare DOM e JavaScript. Convertire le misure fisse in valori fluidi mantenendo i minimi mobile attuali. Per viewport larghi usare solo scaling naturale: contenitore più ampio, `.rings` più grande, `.scribble` più distante dal centro, CTA più larghe/alte, font e icone più grandi. Non aggiungere un secondo layout desktop.

Per le tre CTA e le aree orizzontali usare grid/flex fluidi (`auto-fit`/`minmax`) solo se non cambia ordine o significato dei componenti.

- [ ] **Step 4: Make the Streamlit parent shell viewport-neutral**

Sostituire il CSS parent mobile-only di `home_v154_embed.py` con un contratto unico: iframe e container occupano il viewport disponibile su tutti i dispositivi; nessun ramo separato desktop/mobile; gli overlay persistenti mantengono z-index e comportamento esistenti.

- [ ] **Step 5: Verify Home**

Run: `python web/test_v308_home_mobile_master.py . && python -m py_compile web/home_v154_embed.py`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add web/home_v154_component/index.html web/home_v154_embed.py web/test_v308_home_mobile_master.py
git commit -m "refactor: make Home mobile master responsive"
```

### Task 3: Unificare AI, Creator Hub e Share sullo stesso responsive model

**Files:**
- Modify: `web/ai_v221_component/index.html`
- Modify: `web/creator_hub_v156_component/index.html`
- Modify: `web/share_v156_component/index.html`
- Create: `web/test_v308_surfaces_mobile_master.py`

**Interfaces:**
- Consumes: DOM e marker funzionali esistenti.
- Produces: tre superfici senza rami visuali desktop separati, con grid fluidi e stessa gerarchia mobile/desktop.

- [ ] **Step 1: Write the failing surfaces contract test**

Assert per tutti e tre i componenti:
- nessun marker `DESKTOP`/`DESK` storico autorevole;
- nessun runtime JS dedicato a layout desk;
- nessun `@media (min-width` che cambi composizione;
- marker funzionali preservati (`data-engine`, `data-folder`, social/download actions);
- uso di griglie fluide sullo stesso markup.

Assert specifici:
- AI mantiene 4 motori reali e selezione/durata;
- Hub mantiene Profilo/Progetti/Social/Live/Abbonamento e Game Bar routing;
- Share mantiene 4 social, download e stato finale.

- [ ] **Step 2: Run test to verify it fails**

Run: `python web/test_v308_surfaces_mobile_master.py .`

Expected: FAIL per i blocchi V267/V268 e altri override desktop ancora presenti.

- [ ] **Step 3: Canonicalize AI**

Promuovere la struttura mobile corrente a base. Sostituire `2 colonne mobile / 4 colonne desktop` con una sola grid fluida (`repeat(auto-fit, minmax(...))`) che aumenta le colonne solo quando lo spazio lo permette, senza duplicare markup o cambiare ordine. Scalare card, preview, titolo, duration selector e gap con `clamp()`.

- [ ] **Step 4: Canonicalize Creator Hub**

Mantenere un solo set di cartelle e viste. Usare una sola grid fluida per `.folders`; su mobile devono restare leggibili 2 colonne, su desktop può crescere naturalmente a 3 colonne senza branch separato. Preservare click handlers, profile overview, projects/drafts actions, Social, Live e Game Bar.

- [ ] **Step 5: Canonicalize Share**

Mantenere un solo set di 4 card social e un solo blocco download. Usare `auto-fit/minmax` e scaling fluido per card, murales, pulsanti e gap; nessuna card/CTA alternativa per desktop.

- [ ] **Step 6: Verify surfaces**

Run: `python web/test_v308_surfaces_mobile_master.py .`

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add web/ai_v221_component/index.html web/creator_hub_v156_component/index.html web/share_v156_component/index.html web/test_v308_surfaces_mobile_master.py
git commit -m "refactor: unify AI Hub and Share responsive UI"
```

### Task 4: Unificare Game Editor senza desktop editor alternativo

**Files:**
- Modify: `web/editor_2027_component/index.html`
- Modify: `web/editor_2027_embed.py`
- Create: `web/test_v308_editor_mobile_master.py`

**Interfaces:**
- Consumes: Editor state/render API esistente.
- Produces: stesso cockpit/player/timeline/rails su ogni viewport, scalato fluidamente.

- [ ] **Step 1: Write the failing Editor contract test**

Assert:
- un solo `#ng27` e un solo `.cockpit`;
- FRAME/CAPTION/LOOK/AUDIO/AI presenti una sola volta;
- player 9:16 e timeline presenti;
- assenza di `v297EditorRuntime`, `v298EditorGraphicOnly`, `v298EditorWorkspace`, `V305 EDITOR DESKTOP SINGLE SURFACE`;
- nessun attributo `data-v297-layout` / `data-v298-layout`;
- nessun breakpoint che costruisca una seconda disposizione desk;
- `editor_2027_embed.py` continua a produrre gli stessi render kwargs funzionali.

- [ ] **Step 2: Run test to verify it fails**

Run: `python web/test_v308_editor_mobile_master.py .`

Expected: FAIL sui residui desktop/versionati attuali.

- [ ] **Step 3: Make Editor fluid without changing controls**

Usare lo stesso cockpit mobile come sorgente. Rendere `.shell`, `.cockpit`, `.railBtn`, `.stage.r916`, `.timeline` e pannelli fluidi con `clamp()`/`min()`/`max()` e grid/flex del medesimo DOM. Lo spazio desktop deve soltanto ingrandire player, controlli e distanze; non introdurre un’altra toolbar o workspace.

- [ ] **Step 4: Verify Editor**

Run: `python web/test_v308_editor_mobile_master.py . && python -m py_compile web/editor_2027_embed.py`

Expected: PASS.

- [ ] **Step 5: Commit**

```bash
git add web/editor_2027_component/index.html web/editor_2027_embed.py web/test_v308_editor_mobile_master.py
git commit -m "refactor: make Game Editor single responsive surface"
```

### Task 5: Eliminare cache-key storici e route desktop parallele

**Files:**
- Modify: `GamingShortsFactory_V154_STRUCTURAL_HOME.py`
- Modify: `web/nginx.conf.template`
- Modify: `web/ui_release.py`
- Create: `web/test_v308_cache_contract.py`

**Interfaces:**
- Consumes: `GSF_UI_RELEASE`, `versioned_path()`.
- Produces: un solo release id per Home/AI/Editor/Hub/Share e nessuna pagina desk alternativa autorevole.

- [ ] **Step 1: Write the failing cache contract test**

Assert:
- shell non contiene query attive `?v=285`, `287`, `300`, `305`, `306`, `307`;
- Hub, Share e AI vengono aperti con `?v=308` derivato dal release centrale;
- Home e Editor component names usano lo stesso `308`;
- Nginx serve `/ai-v221/`, `/creator-hub-v156/`, `/share-v156/`, `/editor-live/` con `Cache-Control no-store` `always`;
- `/desktop-preview` e `/desktop-home` non servono più layout alternativi: redirect a `/` oppure rimozione;
- il file Python shell compila.

- [ ] **Step 2: Run test to verify it fails**

Run: `python web/test_v308_cache_contract.py .`

Expected: FAIL per versioni storiche e route desktop parallele.

- [ ] **Step 3: Replace scattered route versions with the central release**

Importare `GSF_UI_RELEASE`/helper nel shell Python e costruire i src iframe/route versionati da un solo valore. Non cambiare nomi delle route funzionali.

- [ ] **Step 4: Remove alternate desktop entry points and harden cache headers**

Aggiornare Nginx: `/desktop-preview` e `/desktop-home` devono reindirizzare alla Home unica; le superfici UI statiche devono usare `Cache-Control "no-store, max-age=0" always`.

- [ ] **Step 5: Verify cache contract and Python syntax**

Run: `python web/test_v308_cache_contract.py . && python -m py_compile GamingShortsFactory_V154_STRUCTURAL_HOME.py`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add GamingShortsFactory_V154_STRUCTURAL_HOME.py web/nginx.conf.template web/ui_release.py web/test_v308_cache_contract.py
git commit -m "refactor: unify GSF UI cache and routes"
```

### Task 6: Semplificare lo startup e impedire il ritorno delle vecchie patch visuali

**Files:**
- Modify: `web/start_web.sh`
- Modify: existing visual regression tests only where they still claim final cache/layout ownership
- Delete or stop invoking: `web/fix_v307_mobile_visual_source.py` after V308 source is canonical
- Keep: functional backend/bridge patchers still required by current source
- Create: `web/test_v308_startup_contract.py`

**Interfaces:**
- Consumes: canonical source from Tasks 1–5.
- Produces: startup idempotente che valida la UI invece di ricostruirla.

- [ ] **Step 1: Write the failing startup contract test**

Assert:
- `start_web.sh` non invoca V307 visual sanitizer;
- non invoca patch visual-only obsolete V295/V303/V306 dopo che le loro modifiche sono state incorporate nelle sorgenti canoniche;
- nessun test pre-V308 pretende un layout desktop separato o un vecchio cache-key;
- V308 tests vengono eseguiti prima di `apply_v293_render_memory_guard.py`;
- `apply_v293_render_memory_guard.py` resta dopo la validazione UI;
- `sh -n web/start_web.sh` passa.

- [ ] **Step 2: Run test to verify it fails**

Run: `python web/test_v308_startup_contract.py .`

Expected: FAIL perché lo startup invoca ancora V295/V303/V306/V307 visuali.

- [ ] **Step 3: Bake then remove each visual startup mutator**

Per ogni fixer visuale candidato alla rimozione, eseguire il fixer su una working copy e verificare se produce ancora diff. Se produce diff funzionale necessario, incorporare quel risultato direttamente nel file sorgente canonico e rieseguire il relativo test. Solo quando il fixer diventa no-op, rimuoverlo dallo startup.

Non rimuovere in questa task i bridge funzionali V291/V293/V304 o altri fixer che modificano backend/API/state senza prima sostituirne esplicitamente la responsabilità.

- [ ] **Step 4: Move final ownership to V308 tests**

Aggiornare i vecchi test solo per rimuovere assert su cache/versioning/layout desktop ormai posseduti da V308; conservare gli assert funzionali (click, route, API, action bridge, project state, social state).

- [ ] **Step 5: Verify startup contract**

Run: `python web/test_v308_startup_contract.py . && sh -n web/start_web.sh`

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add web/start_web.sh web/test_v308_startup_contract.py web/test_v*.py
git commit -m "refactor: make V308 the final UI startup contract"
```

### Task 7: Eseguire regressione funzionale completa e deploy Railway

**Files:**
- Modify only if a failing functional regression proves a real compatibility issue.

**Interfaces:**
- Consumes: all previous tasks.
- Produces: verified release deployable to Railway.

- [ ] **Step 1: Run V308 integration suite**

Run:

```bash
python web/test_v308_ui_release.py .
python web/test_v308_home_mobile_master.py .
python web/test_v308_surfaces_mobile_master.py .
python web/test_v308_editor_mobile_master.py .
python web/test_v308_cache_contract.py .
python web/test_v308_startup_contract.py .
```

Expected: all PASS.

- [ ] **Step 2: Run functional regression tests that protect real behavior**

Run the current functional tests for Creator Hub clicks/Game Bar, AI journey and engine bridge, Share state/actions, project/draft details and Editor controls. Any obsolete visual/cache assertion must already have been reassigned to V308 in Task 6; do not ignore failures.

Expected: all functional assertions PASS.

- [ ] **Step 3: Compile every modified Python file**

Run: `python -m py_compile web/ui_release.py web/home_v154_embed.py web/editor_2027_embed.py GamingShortsFactory_V154_STRUCTURAL_HOME.py web/apply_v293_render_memory_guard.py`

Expected: PASS with no syntax error.

- [ ] **Step 4: Verify generated production app path**

Run the startup patch/test sequence in the same order as `web/start_web.sh` up through `apply_v293_render_memory_guard.py`, then compile the generated `GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py`.

Expected: generated production app compiles; no historical desktop marker/cache version reappears.

- [ ] **Step 5: Commit any final test-only cleanup**

```bash
git add -A
git commit -m "test: verify V308 mobile master release"
```

Skip the commit if there are no changes.

- [ ] **Step 6: Push/deploy and poll Railway**

Push the completed commit chain to `main`. Poll the frontend deployment until it reaches a terminal state. Do not report success while status is BUILDING/DEPLOYING.

Expected: Railway frontend deployment `SUCCESS`; AI worker remains healthy.

- [ ] **Step 7: Inspect production logs**

Require explicit PASS for the V308 integration/startup contracts and successful Streamlit/Nginx startup. Confirm there is no `SyntaxError`, healthcheck failure, stale V307 visual rewrite, or obsolete cache gate.

- [ ] **Step 8: Visual acceptance**

Verify at minimum one phone viewport and one desktop viewport. Acceptance: stessa identità UI, stesso ordine e stessi componenti; desktop usa più spazio e dimensioni maggiori ma non introduce una seconda grafica. Se la struttura è corretta ma la scala necessita micro-regolazioni, modificare esclusivamente i token fluidi della UI master, non creare nuovi branch desktop.
