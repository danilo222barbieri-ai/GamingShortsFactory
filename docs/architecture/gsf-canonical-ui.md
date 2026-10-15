# GSF canonical UI pipeline

**Rule:** the files in this repository *are* the UI that production serves.
Nothing between `git push` and the browser may rewrite them.

```
canonical files in the repo  →  Docker build (copy 1:1)  →  immutable runtime  →  Railway
```

## Why (root cause, 2026-10-15)

Before this change the served UI was not in the repository:

- `app.py` was **never copied** into the image. The real app was a generated
  780 KB file built from a compressed V77 payload (`src_payload/`) through 94
  intermediate versions (`apply_v78` … `apply_v154`), then rewritten again.
- The component files under `web/*_component/index.html` were an old base.
  At build time `test_v269_creator_hub_recovery.py` (a "test") ran
  `materialize_runtime_patches.sh`, which extracted the V285–V373 migration
  chain from `start_web.sh` and replayed it: 22 writes on the Creator Hub,
  12 on Home, 10 on the Editor (V389–V396 nested inside other fixes), 22 on the
  app. V403/V410/V411 fixes then patched the result again.
- Patches matched anchors with `.replace()` and guarded on version markers, so
  editing a source file could make a later migration re-inject an older block,
  and some patches rewrote other patch scripts.
- Railway starts `sh /app/web/start_web.sh`; the repo copy of that script still
  contained the whole migration chain and was only swapped for the fast startup
  inside the image by the V269 hook.
- The deploy trigger list ignored `gsf_core/` and root `gsf_*.py` modules, so
  changes there could pass the gate and never reach Railway.

Result: "new in the repo, old online".

## How it works now

| Piece | What it does |
| --- | --- |
| `app.py` | The production Streamlit app (served as `/app/app.py`). |
| `web/*_component/index.html` | Home, Creator Hub, Editor, Crea con IA, Share/Crea Short — served as-is (nginx `alias`, `Cache-Control: no-store`). |
| `web/nginx.conf.template`, `web/direct_upload_server.py` | Edge + companion, including V410/V411 security, already folded in. |
| `Dockerfile` | Copies the canonical files, generates PWA icons, installs the single Streamlit `index.html` bridge (`install_adsense_bridge.py`, the only third-party file touched), writes and verifies the manifest. **No** payload, migration, materialization. |
| `web/start_web.sh` | Railway start command. Verifies the manifest, renders runtime config, launches services. Never transforms files. |
| `tools/gsf_ui_manifest.py` | One definition of the canonical file set (`app.py`, `web/**`, `gsf_core/**`, root `gsf_*.py`, `.streamlit/**`). `digest` (repo), `write`/`verify` (image), `compare` (repo vs image). |
| `/healthz` | Exposes `ui_digest` (and `release` = Railway commit) so CI can prove what is served. |

Historical `fix_v*.py` / `apply_v*.py` scripts remain in `web/` for the record
(the worker image still uses `apply_v78…v99`), but the frontend never runs them.
`web/materialize_runtime_patches.sh` is retired and exits 1 on purpose.

## Guards

- `tests/test_canonical_ui_pipeline.py` (gate + `GSF Canonical UI` workflow):
  fails if the Dockerfile or startup runs any legacy migration/payload, if the
  startup transforms files, if the manifest stops detecting a re-injected old
  UI, if approved surfaces lose their markers, or if Creator Hub session/CSRF
  security is weakened.
- Production Gate: the built image's manifest must equal the repo's; `/healthz`
  must report the repo digest; the four mobile pages served by the container
  must be byte-identical to the repo files; after the runtime smoke the running
  container must still verify (no runtime rewrite).
- `GSF Production UI Verify`: after promotion, waits until the production domain
  serves the repo digest, then byte-compares the served mobile pages and checks
  Home, `/creator-hub/state` (200 + CSRF token) and CSRF enforcement.

## Changing a mobile screen

1. Claim it (`tools/gsf_task.py start …`).
2. Edit the canonical file directly (e.g. `web/creator_hub_v156_component/index.html`).
   Do **not** add a `fix_vNNN.py` that patches it at build or startup.
3. Push → Production Gate → promotion → `GSF Production UI Verify` proves the
   same bytes are online.

If a change needs a transformation, make it once, commit the result, and keep
the script (if any) out of the build.
