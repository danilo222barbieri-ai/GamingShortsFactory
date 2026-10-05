import sys
from pathlib import Path

hub = Path(sys.argv[1])
app = Path(sys.argv[2])
text = hub.read_text(encoding="utf-8")
app_text = app.read_text(encoding="utf-8")

checks = {
    "profile overview CSS marker": "V287 PROFILE OVERVIEW" in text,
    "shorts overview card": 'data-profile-overview="shorts"' in text and 'id="profileOverviewShorts"' in text,
    "drafts overview card": 'data-profile-overview="drafts"' in text and 'id="profileOverviewDrafts"' in text,
    "plan overview card": 'data-profile-overview="subscription"' in text and 'id="profileOverviewPlan"' in text,
    "social overview card": 'data-profile-overview="social"' in text and 'id="profileOverviewSocial"' in text,
    "profile overview click routing": '$$("[data-profile-overview]").forEach' in text,
    "real shorts count binding": 'profileOverviewShorts' in text and 'u.shorts||0' in text,
    "real drafts count binding": 'profileOverviewDrafts' in text and 'u.drafts||0' in text,
    "real plan binding": 'profileOverviewPlan' in text and 'a.plan||"FREE"' in text,
    "real social binding": 'profileOverviewSocial' in text and 'connectedCount+"/5"' in text,
    "subscription quick action": 'Gestisci il tuo abbonamento' in text,
    "social quick action": 'Account collegati' in text,
    "Creator Hub iframe cache is V287": '/creator-hub-v156/?v=287' in app_text,
}
for name, ok in checks.items():
    print(("PASS" if ok else "FAIL") + ": " + name)
bad = [name for name, ok in checks.items() if not ok]
if bad:
    raise SystemExit("V287 profile overview regression failed: " + ", ".join(bad))
print("V287 profile overview: PASS")
