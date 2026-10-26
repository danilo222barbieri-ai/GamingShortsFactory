# V435 beta hardening — 2026-10-26 checkpoint

Feature freeze. No merge or deployment until the required blockers close.
Claim: `closed-beta-v435-hardening-current-home-notifica-4860a6`.
Baseline source: `a25435a6e9fc857ff93d47f850a2b7f21ebdb52c`.
Observed public release: `4c4e39241bd5d2cb0c7d4e723b8205aa7e50a557`;
composite health all true, Production UI Verify 40227921535 success.
PR193 was already merged as `111113a6c074d733395dd4d02070d9d4270bbfca`.

## Confirmed defects and narrow changes

- Two obsolete V429 tests reproduced RED. They required the intentionally removed
  Home shell and notification adapter. Updated tests protect the existing full
  viewport, original internal Game Bar reserve and single bounded notification owner.
  No Home CSS or positioning was changed.
- Actual completed upload could replace the Home document while Streamlit retained
  its old component receiver registration. `loaded=true` arrived before initialization;
  user `create_ai` messages then reached the parent but never triggered backend work.
  Refresh recovered the session. A fresh component key on source-readiness changes
  restores the existing Streamlit lifecycle. Ordinary reruns keep the same identity.
  No polling/state engine or forced browser refresh was added.
- Official PyPI stable Streamlit 1.66.1 declares `pillow>=9.2.0,<14`.
  Replaced the temporary preview artifact with the supported stable pin; Pillow stays13.
- Exact-runtime audit found filelock4.0.6 CVE-2026-112940, CVE-2026-112913,
  CVE-2026-112907; first fixed version4.2.1 pinned. No ignored vulnerabilities.
- Real E2E harness still expected the retired uploaded ring and FATTO→render behavior.
  It now follows uploader handoff, FATTO→Home→Crea Short and verifies exact export codecs.

## Recorded verification

- Ordinary full suite before final key simplification:358PASS,57SKIP,71subcases.
  Browser runtime cases are separately required; skips are not counted as coverage.
- Four actual WebKit iPhone upload→AI terminal cases passed35.78s; strengthened
  request-ID-matched backend terminal verification is running at this checkpoint.
- Earlier unchanged real visual/navigation/resume suite:29PASS429.065s.
  Final candidate gate must run again, including the four new upload regression cases.
- Syntax, Node contracts, eight security/UI contracts,36coordination tests passed.
- `pip-audit --strict --path` on metadata from85actual installed runtime distributions:
  no known vulnerabilities after updates. Offline resolver with requirements/constraints
  and `pip check` both pass. Final clean-image CI resolution/audit remains mandatory.
- Real local20s upload→AUTO results(1moment,2.3s)→selection→Editor preview/edit/save passed.
  Full current render/export/Hub/resume journey remains pending; do not call E2E green.
- Independent review: no actionable P1/P2 in final lifecycle-key fix, dependency/test changes.

## Isolated materialization measurements

Actual canonical low-memory launcher, boto3 HTTP download, media validation, fsync,
atomic ready marker and SHA256 verification. App container is limited to1GiB with
swap disabled. Local streaming S3-compatible origin; **not a production bucket**.
Source:41,189,118byte H.264/AAC MP4; all batches produced complete matching files.

| Concurrent completions | Active transfers | Duration(s) | CPU(s) | Container peak(MiB) | Probe RSS peak(MiB) |
|---:|---:|---:|---:|---:|---:|
|1|1|0.173|0.133|539.17|162.08|
|2|1|0.394|0.325|593.08|169.62|
|4|1|0.549|0.437|676.98|184.95|
|6|1|0.791|0.607|778.86|199.18|

No OOM, restart or partial/error files observed. Linux cache is included in cgroup
memory. Fast local transport timings do not predict Railway bucket throughput.
Additional HEVC/hvc1 MOV/AAC fixture batches completed; this does not establish
physical iPhone capture/browser behavior. Render concurrency and combined-load
acceptance remain unverified. Do not infer 6 simultaneous full users from this probe.

## Release status

CLOSED BETA remains NO-GO at this checkpoint: final complete candidate E2E,
render/mixed-load memory acceptance, remote CI/Production Gate, promotion and
post-deploy verification have not yet passed. No new deployment has been requested.

## Later checkpoint: notification interaction and full journeys

- AUTO375x667 and ACTION430x932 actual WebKit journeys pass first render/export,
  Hub/drafts/Shorts/Profile/social settings, preserved edit resume, refresh and Back,
  without critical runtime errors. All export codec assertions pass.
- An existing notification's empty actions container intercepted the Shorts tab.
  Passive notification regions now pass pointers through; real close/action and
  confirmation controls remain interactive. Appearance/placement unchanged.
  Browser regression reproduced RED, then16notification cases and4subcases PASS.
- Stale browser assertions for the retired header pill and its earlier TTL were
  corrected to the approved outside-header V428 surface, without restyling it.
- Pre-existing WebKit continue-on-error is removed. The gate is blocking again;
  a diagnostic-green run does not count as a valid release gate.
- Ordinary suite359PASS58SKIP71subcases. Strengthened WebKit4cases PASS37.05s,
  with request-ID-matched actual backend terminal responses.
- Two-render observed cgroup peak1023.91MiB,2ffmpeg processes. Cumulative OOM
  count2 existed when read but its initial value was not recorded, so attribution
  and OOM-free concurrency remain unverified. A repeat with before/after counters
  is required; Docker OOMKilled=false alone cannot exclude killed child processes.
- Second-edit render/export acceptance is now added to the real E2E harness and
  remains pending at this checkpoint. No release or beta readiness is claimed.

## Measured render memory blocker and admission correction — 2026-10-26

- Repeated mixed-load test confirms real OOM child deaths under1GiB; Docker
  OOMKilled=false was insufficient. Release stays held until an exact repeat passes.
- Existing process-local render semaphore now also uses a bounded cross-process
  POSIX slot on low-memory frontend. Capacity timeout is terminal, not restarted
  per encoder. Background quality inspection uses this same slot and rechecks the
  queued file fingerprint; quality checks remain enabled.
- Actual peak process attribution isolated the cinematic FFmpeg graph at862628KiB
  RSS by itself. Its direct /usr/bin invocation bypassed the wrapper's filter and
  codec budgets. Low-memory mode now bounds filter pools and every input decoder
  to1thread, and the encoder to1thread. Graph,CRF14,pixel format and effects stay.
  Other deployments retain encoder2threads. Regression reproduced RED;19targeted
  render/admission/recipe tests PASS. Independent review requested for final delta.
- Corrected second-render harness now polls resolved backend state rather than an
  asynchronous browser predicate. AUTO375 and ACTION430 both complete real second
  edit/render/download, changed export hash and exact codecs, without JS errors.
  Those runs still had OOM events and are NOT memory acceptance evidence.
- Full ordinary suite before cinematic thread correction:364PASS58SKIP71subcases.
  Exact final suite, four WebKit upload terminal cases, concurrent REACTION/BEST
  full journeys and1GiB/OOM measurements are running. Production Gate additionally
  enforces actual1GiB/no-swap and zero cgroup oom/oom_kill counters.
- Official prior head df0abc7:GSF CI40335014268 SUCCESS; blocking Gate40335014381
  failed on an immediate terminal-state assertion while source moments were
  already usable during analysis. Test now polls the same request's terminal
  result with bounded120s deadline; no product assertions or gate removed.
- No merge or deployment. Public remains the previous verified V435 release.
