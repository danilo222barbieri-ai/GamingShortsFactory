from pathlib import Path
import sys

p=Path(sys.argv[1])
s=p.read_text(encoding="utf-8")
checks={
    "two AI ads": 'key="v1055_ad_engine"' in s and 'key="v1055_ad_after_ai"' in s,
    "duration spacer": 'height:20px' in s and "Scegli la durata" in s,
    "no speech": "Nessuna traccia" in s and "Nessuna traccia parlata" not in s,
    "no regenerate": "RIGENERA TESTI" not in s,
    "connection gate": "_v1055_social_connected" in s,
    "publish gate": "if _v1055_social_connected and st.button(" in s,
    "examples": "Es. Halo Infinite" in s and "Es. #HaloInfinite #Gaming #Shorts" in s,
    "new composer": "v1055_social_composer_" in s,
    "version": "Gaming Shorts Factory · V105.5 Refinements" in s,
}
bad=[k for k,v in checks.items() if not v]
if bad:
    raise SystemExit("V105.5 contract failed: "+", ".join(bad))
compile(s,str(p),"exec")
print("V105.5 refinements contract: PASS")
