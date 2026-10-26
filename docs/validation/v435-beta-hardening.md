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
