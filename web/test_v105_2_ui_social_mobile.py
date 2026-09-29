from pathlib import Path
import sys

p=Path(sys.argv[1])
s=p.read_text(encoding="utf-8")
checks={
    "no speech message": 'Nessuna traccia parlata',
    "ad before final": 'aria-label="Spazio pubblicitario">Pubblicità</aside>',
    "social editable title": 'social_title_',
    "social editable description": 'social_description_',
    "social editable hashtags": 'social_hashtags_',
    "social publish confirmation": 'social_publish_confirm_',
    "pack override": 'pack_override=_edited_pack',
    "native mobile share": 'SALVA / CONDIVIDI SU MOBILE',
    "web share api": 'navigator.share',
    "final label": 'Gaming Shorts Factory · V105.2 UI Social Mobile',
}
missing=[name for name,needle in checks.items() if needle not in s]
if missing:
    raise SystemExit("V105.2 contract failed: "+", ".join(missing))
compile(s,str(p),"exec")
print("V105.2 UI/social/mobile contract: PASS")
