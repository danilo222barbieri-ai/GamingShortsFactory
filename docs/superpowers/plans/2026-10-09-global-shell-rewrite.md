# V343 Single Global Shell Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the competing global chrome systems with one parent-owned V343 shell that keeps the header, Game Bar and footer visible and functional across Home, Editor, Hub, Progetti, Live, AI and Short without breaking the now-working Editor route.

**Architecture:** Retire the legacy chrome authorities at startup, preserve only their unrelated Home/Live/routing behavior, and install one executable parent-DOM bridge called `GSF_GLOBAL_SHELL_V343`. V343 creates exactly three global root nodes, owns one canonical `GSF_SHELL_NAV` listener, constrains overlays below the shell, and remounts itself with one idempotent observer when Streamlit replaces DOM nodes.

**Tech Stack:** Python 3.12 runtime patch scripts, Streamlit 1.49, `streamlit.components.v1.html`, vanilla JavaScript/CSS, Railway, nginx.

**Spec:** `docs/superpowers/specs/2026-10-09-global-shell-rewrite-design.md`

## Global Constraints

- The working Game Editor route must remain functional and lazy-load `/editor-live/` on demand.
- Exactly one global header, one global Game Bar and one global footer may exist in the parent document.
- Header copy is exactly `GAMING SHORTS FACTORY` and the signed-out account fallback is exactly `Accedi`.
- Global shell is visible on mobile and desktop; mobile must honor safe-area insets.
- Home remains fixed/non-scrolling; internal pages may keep their existing internal scrolling.
- V330/V332/V334/V341/V342 may remain in repository history but must not be active runtime chrome authorities.
- V328 may keep Home/Live layout work only; it must no longer create or control global footer/brand/navigation chrome.
- No page overlay may use a z-index above the V343 global shell.
- Do not redesign Home, Editor tools, AI engines, Creator Hub cards, upload/render or social-connect flows.

## Review Focus

- **Streamlit rerender:** if the parent DOM replaces shell nodes, V343 must remount exactly one copy of each root.
- **iPhone safe area:** footer and Game Bar must remain fully visible above the home indicator and must not cover Home CTAs.
- **Editor open/close:** opening Editor must not hide shell chrome; closing it must restore Home without duplicating shell nodes.
- **Account endpoint failure:** header must still render with `Accedi` and a fallback avatar when `/creator-hub/state` fails or returns partial data.
- **Legacy child chrome:** duplicate local brand/nav/footer must be hidden without hiding functional page-specific headings or controls.

---

### Task 1: Lock the final V343 runtime contract with a failing test

**Files:**
- Create: `web/test_v343_single_global_shell.py`
- Test: `web/test_v343_single_global_shell.py`

**Interfaces:**
- Consumes: generated `/app/GamingShortsFactory_V154_STRUCTURAL_HOME.py`, `web/start_web.sh`, Home component HTML.
- Produces: one executable contract test that later tasks must satisfy.

- [ ] **Step 1: Write the failing test**

Create assertions for the final generated/runtime contract:

```python
assert shell.count('id="gsf-global-header"') == 1
assert shell.count('id="gsf-global-gamebar"') == 1
assert shell.count('id="gsf-global-footer"') == 1
assert 'GSF_GLOBAL_SHELL_V343' in shell
assert 'GAMING SHORTS FACTORY' in shell
assert '>Accedi<' in shell
assert "target:'editor'" in shell
assert '/editor-live/' in shell
assert "target:'short'" in shell
assert '--gsf-shell-safe-bottom' in shell
assert 'keepGlobalShellMounted' in shell
```

Also assert that `start_web.sh` does **not** execute these legacy chrome authorities:

```python
for old in (
    'fix_v330_global_chrome.py',
    'fix_v332_global_frame_lock.py',
    'fix_v334_global_chrome_hard_lock.py',
    'fix_v340_shell_resilience.py',
):
    assert old not in start
```

Assert `fix_v341_global_shell_contract.py` is not chained indirectly by any startup-executed script, and assert final runtime source does not contain active root IDs from V328/V330/V334.

- [ ] **Step 2: Run the test and verify RED**

Run:

```bash
python web/test_v343_single_global_shell.py /app
```

Expected: FAIL because V343 does not exist yet and legacy shell authorities are still wired into startup.

- [ ] **Step 3: Commit the failing contract test**

```bash
git add web/test_v343_single_global_shell.py
git commit -m "test: define V343 single global shell contract"
```

---

### Task 2: Retire legacy chrome ownership without losing unrelated behavior

**Files:**
- Modify: `web/fix_v328_global_balance.py`
- Modify: `web/start_web.sh`
- Modify: `web/test_v328_global_balance.py`
- Test: `web/test_v343_single_global_shell.py`

**Interfaces:**
- Consumes: V328 Home balance, Live compact layout and Home Short fallback.
- Produces: V328 with no parent global footer/brand/nav observer; startup no longer invokes V330/V332/V334/V340 or their chrome-specific tests.

- [ ] **Step 1: Add focused assertions to the V328 test**

Assert V328 still patches Home/Live and Short fallback, but does not append any parent chrome block:

```python
assert 'v328HomeBalance' in home
assert 'v328LiveCompact' in hub
assert 'shellNav("short")' in home
assert 'gsf-v328-global-footer' not in shell
assert '__GSF_V328_GLOBAL_BALANCE' not in shell
```

- [ ] **Step 2: Run the V328 test and verify RED**

Run:

```bash
python web/test_v328_global_balance.py /app
```

Expected: FAIL on the legacy shell/footer assertions.

- [ ] **Step 3: Remove only V328 parent-shell emission**

In `web/fix_v328_global_balance.py`, keep `patch_home()` and `patch_hub()` behavior but stop appending `SHELL_BLOCK` to the generated app. Keep the Home Short fallback message so V343 can handle it canonically.

- [ ] **Step 4: Remove old chrome authorities from startup**

In `web/start_web.sh`, stop executing:

```text
fix_v330_global_chrome.py / test_v330_global_chrome.py
fix_v332_global_frame_lock.py / test_v332_global_frame_lock.py
fix_v334_global_chrome_hard_lock.py / test_v334_global_chrome_hard_lock.py
fix_v340_shell_resilience.py / test_v340_shell_resilience.py
```

Do not delete the historical files. Keep V331 primary actions routing and V333 touch handling until V343 proves equivalent behavior.

- [ ] **Step 5: Run focused tests**

Run:

```bash
python web/test_v328_global_balance.py /app
python web/test_v331_primary_actions_routing.py /app
python web/test_v333_home_cta_touch_fix.py /app
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add web/fix_v328_global_balance.py web/test_v328_global_balance.py web/start_web.sh
git commit -m "refactor: retire legacy global chrome authorities"
```

---

### Task 3: Implement the single executable V343 Global Shell

**Files:**
- Create: `web/fix_v343_single_global_shell.py`
- Modify: `web/start_web.sh`
- Modify: `web/home_v154_component/index.html` at runtime through V343 patch logic
- Test: `web/test_v343_single_global_shell.py`

**Interfaces:**
- Consumes: `GSF_SHELL_NAV` messages from Home/internal pages, `/creator-hub/state`, existing overlay IDs, `/editor-live/`.
- Produces: `_gsf_components_v343.html(...)`, `#gsf-global-header`, `#gsf-global-gamebar`, `#gsf-global-footer`, `keepGlobalShellMounted()`, one canonical shell router.

- [ ] **Step 1: Extend the V343 failing test for geometry and z-index**

Assert these exact public contracts exist:

```python
for token in (
    '--gsf-shell-header-h',
    '--gsf-shell-gamebar-h',
    '--gsf-shell-footer-h',
    '--gsf-shell-safe-bottom',
    '--gsf-shell-content-top',
    '--gsf-shell-content-bottom',
):
    assert token in shell

assert 'keepGlobalShellMounted' in shell
assert 'MutationObserver' in shell
assert 'display_name' in shell
assert 'nickname' in shell
assert "split('@')[0]" in shell
```

Add checks that known overlays use `--gsf-shell-content-top` and `--gsf-shell-content-bottom`, and that V343 shell z-index is greater than the known overlay z-index constant.

- [ ] **Step 2: Run V343 test and verify RED**

Run:

```bash
python web/test_v343_single_global_shell.py /app
```

Expected: FAIL because V343 script is not installed yet.

- [ ] **Step 3: Implement `fix_v343_single_global_shell.py`**

The script must expose one patch entry point:

```python
def main() -> None
```

It must append one executable Streamlit component bridge using:

```python
import streamlit.components.v1 as _gsf_components_v343
```

and `_gsf_components_v343.html(..., height=0)`.

The bridge creates exactly these parent nodes:

```text
#gsf-global-header
#gsf-global-gamebar
#gsf-global-footer
```

Required behavior inside the bridge:

- one `GSF_SHELL_NAV` listener;
- routes: `home`, `hub`, `projects`, `live`, `editor`, `short`, `close`;
- on-demand Editor surface builder that lazy-loads `/editor-live/`;
- working Short route preserved from V331;
- active Game Bar state update;
- account sync with fallback order from the spec;
- one observer/watchdog named `keepGlobalShellMounted`;
- child-frame duplicate chrome suppression limited to known local brand/nav/footer selectors;
- fixed content bounds applied to Editor, AI, Short, Hub, Social and Account surfaces;
- shell root z-index above all those surfaces;
- safe-area geometry on mobile and same ownership contract on desktop.

- [ ] **Step 4: Add Home geometry reservation without visible duplicate chrome**

V343 runtime patching may add/update one Home style block that reserves the final shell top/bottom space but never renders a second visible topbar, Game Bar or footer.

The Home must remain `100dvh` and non-scrolling; CTA cards must end above `--gsf-shell-content-bottom`.

- [ ] **Step 5: Wire V343 once in startup**

In `web/start_web.sh`, run:

```bash
python /app/web/fix_v343_single_global_shell.py /app
python /app/web/test_v343_single_global_shell.py /app
```

after V333 and before V335/V336 compatibility checks. Do not chain V343 through another versioned patch.

- [ ] **Step 6: Run V343 test**

Run:

```bash
python web/test_v343_single_global_shell.py /app
```

Expected: PASS.

- [ ] **Step 7: Commit**

```bash
git add web/fix_v343_single_global_shell.py web/test_v343_single_global_shell.py web/start_web.sh
git commit -m "feat: add single V343 global shell"
```

---

### Task 4: Make executable-bridge and runtime-recovery utilities understand the new architecture

**Files:**
- Modify: `web/fix_v336_executable_shell_bridge.py`
- Modify: `web/test_v336_executable_shell_bridge.py`
- Modify: `web/fix_v335_runtime_shell_recovery.py`
- Modify: `web/test_v335_runtime_shell_recovery.py`
- Test: `web/test_v343_single_global_shell.py`

**Interfaces:**
- Consumes: V331 legacy action bridge plus V343 direct executable bridge.
- Produces: compatibility tools that no longer require V330/V332/V334 markers.

- [ ] **Step 1: Update the V336 test first**

Change the required converted legacy bridge set from five historical shell bridges to only the still-required V331 bridge. Assert V343 is already executable through `_gsf_components_v343.html` and must not be rewritten by V336.

- [ ] **Step 2: Run V336 test and verify RED**

Run:

```bash
python web/test_v336_executable_shell_bridge.py /app
```

Expected: FAIL against the old five-bridge contract.

- [ ] **Step 3: Narrow `BRIDGES` in V336**

Set the V336 conversion contract to the remaining sanitized legacy JS bridge only:

```python
BRIDGES = {
    'V331': '__GSF_V331_PRIMARY_ACTIONS_ROUTING',
}
```

V343 must remain outside this converter because it emits executable component HTML directly.

- [ ] **Step 4: Update V335 integrity requirements**

Replace the V334-specific required marker with V343:

```python
required = [
    'V331_PRIMARY_ACTIONS_ROUTING',
    'GSF_GLOBAL_SHELL_V343',
    'GSF_SHELL_NAV',
    'gsf-editor-overlay-v220',
    'gsf-global-header',
    'gsf-global-gamebar',
    'gsf-global-footer',
]
```

Keep V335 limited to repairing unsupported `st.html(..., height=0)` calls; it must not mutate `_gsf_components_v343.html`.

- [ ] **Step 5: Run compatibility tests**

Run:

```bash
python web/test_v336_executable_shell_bridge.py /app
python web/test_v335_runtime_shell_recovery.py /app
python web/test_v343_single_global_shell.py /app
```

Expected: PASS.

- [ ] **Step 6: Commit**

```bash
git add web/fix_v336_executable_shell_bridge.py web/test_v336_executable_shell_bridge.py web/fix_v335_runtime_shell_recovery.py web/test_v335_runtime_shell_recovery.py
git commit -m "refactor: align shell compatibility tools with V343"
```

---

### Task 5: Regression verification for routing, shell persistence and generated runtime

**Files:**
- Modify only if a regression test exposes a real defect.
- Test: existing routing/editor/Home tests plus `web/test_v343_single_global_shell.py`.

**Interfaces:**
- Consumes: final V343 runtime app generated by the normal startup patch sequence.
- Produces: a branch that is safe to promote once live runtime evidence confirms visible chrome.

- [ ] **Step 1: Run the focused regression suite**

Run:

```bash
python web/test_v327_editor_open_bridge.py /app
python web/test_v331_primary_actions_routing.py /app
python web/test_v333_home_cta_touch_fix.py /app
python web/test_v335_runtime_shell_recovery.py /app
python web/test_v336_executable_shell_bridge.py /app
python web/test_v343_single_global_shell.py /app
python -m py_compile /app/GamingShortsFactory_V154_STRUCTURAL_HOME.py
```

Expected: all PASS.

- [ ] **Step 2: Verify no competing global chrome remains in final runtime source**

Search the generated runtime app for active legacy markers/IDs. Expected active global roots are only:

```text
gsf-global-header
gsf-global-gamebar
gsf-global-footer
```

Historical strings in comments/tests are acceptable; executable parent-DOM code for V328/V330/V332/V334/V341/V342 is not.

- [ ] **Step 3: Inspect branch diff**

Run:

```bash
git diff main...HEAD -- web/start_web.sh web/fix_v328_global_balance.py web/fix_v335_runtime_shell_recovery.py web/fix_v336_executable_shell_bridge.py web/fix_v343_single_global_shell.py web/test_v343_single_global_shell.py
```

Expected: one shell authority, preserved Editor/Short routes, no unrelated UI redesign.

- [ ] **Step 4: Commit any regression-only corrections**

```bash
git add <only files changed by a proven regression fix>
git commit -m "fix: close V343 shell regressions"
```

---

### Task 6: Promote once and verify the live site before declaring success

**Files:**
- No new production code unless live evidence finds a reproducible defect.

**Interfaces:**
- Consumes: reviewed V343 branch head.
- Produces: one production deployment with browser/runtime evidence.

- [ ] **Step 1: Promote one reviewed branch head to `main`**

Do not push intermediate speculative commits to `main`. Record the exact promoted commit SHA.

- [ ] **Step 2: Wait for Railway deployment SUCCESS**

Verify the frontend deployment corresponding to the promoted SHA reaches `SUCCESS`; inspect startup logs for V343 test PASS and no shell-related exceptions.

- [ ] **Step 3: Verify live HTTP/browser behavior**

Check these states on the production URL:

```text
Home      → header + logo/name + Game Bar + footer visible
Editor    → same shell visible while Editor is open
Hub       → same shell visible and Hub route active
Progetti  → same shell visible and Projects active
Live      → same shell visible and Live active
Short     → same shell visible
```

Also verify no duplicate `GAMING SHORTS FACTORY`, no duplicate Game Bar/footer, no Home CTA covered, and Editor still loads `/editor-live/`.

- [ ] **Step 4: Only then mark V343 complete**

A successful build or static test alone is not completion. Completion requires live shell visibility and working navigation on the deployed app.
