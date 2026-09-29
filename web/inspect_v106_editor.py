from pathlib import Path
p=Path("/app/GamingShortsFactory_V105_7_ADSENSE_READY.py")
lines=p.read_text(encoding="utf-8").splitlines()

for label,a,b in [
    ("LEGACY_PLAYER",11780,11930),
    ("MAIN_EDITOR",12270,12580),
    ("INLINE_EDITOR",13020,13240),
    ("RENDER_RECIPE",11600,11720),
]:
    print(f"V106_RANGE_{label}_START")
    for j in range(a-1,min(len(lines),b)):
        print(f"{j+1}: {lines[j]}")
    print(f"V106_RANGE_{label}_END")
