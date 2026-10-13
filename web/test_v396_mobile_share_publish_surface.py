#!/usr/bin/env python3
from pathlib import Path
import importlib.util
import sys

ROOT=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
FIX=ROOT/'web'/'fix_v396_mobile_share_publish_surface.py'
SHARE=ROOT/'web'/'share_v156_component'/'index.html'
CHAIN=ROOT/'web'/'fix_v373_creator_hub_spacing.py'

if not FIX.is_file():raise SystemExit('V396 implementation missing')
spec=importlib.util.spec_from_file_location('v396_mobile_share_publish_surface',FIX)
mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)

sample='''<!doctype html><html><body><main id="share" class="gsfFinalSurface">
<!-- V289 SHARE FINAL -->
<div data-card="youtube"><button data-platform="youtube">YT</button></div>
<div data-card="tiktok"><button data-platform="tiktok">TT</button></div>
<div data-card="instagram"><button data-platform="instagram">IG</button></div>
<div data-card="facebook"><button data-platform="facebook">FB</button></div>
<button class="downloadBtn">Scarica video</button>
</main></body></html>'''
out=mod.patch_share(sample)
required=(
 'V396_MOBILE_SHARE_PUBLISH_SURFACE','v396MobilePublishSurface','v396MuralText','Il tuo video è pronto',
 'PUBBLICA SU','Titolo','Descrizione','Hashtag','IMPOSTAZIONI',
 'id="v396Download"','id="v396Share"','id="v396Publish"','SCARICA','CONDIVIDI','PUBBLICA ORA',
 'navigator.share','navigator.canShare','GSF_SHARE_METADATA','data-v396-platform="youtube"','data-v396-platform="tiktok"',
 'data-v396-platform="instagram"','data-v396-platform="facebook"','#share.v396MobileMode>:not(#v396MobilePublishSurface)'
)
for token in required:
 if token not in out:raise AssertionError('V396 token missing: '+token)
patch=mod.PATCH
if patch.index('PUBBLICA SU')>patch.index('>Titolo<'):raise AssertionError('V396 publish destinations must be above metadata')
if 'SALVA BOZZA' in patch or 'CAMBIA SHORT' in patch:raise AssertionError('V396 mobile surface must not expose draft/change-short actions')
for label in ('SCARICA','CONDIVIDI','PUBBLICA ORA'):
 if patch.count(label)!=1:raise AssertionError('V396 must expose one distinct '+label+' button')
if mod.patch_share(out)!=out:raise AssertionError('V396 patch must be idempotent')

if SHARE.is_file():
 live=SHARE.read_text(encoding='utf-8')
 if 'V289 SHARE FINAL' in live and 'V396_MOBILE_SHARE_PUBLISH_SURFACE' in live:
  for token in ('v396MobilePublishSurface','v396MuralText','navigator.share','id="v396Publish"'):
   if token not in live:raise AssertionError('runtime V396 token missing: '+token)

if CHAIN.is_file():
 chain=CHAIN.read_text(encoding='utf-8')
 if 'fix_v396_mobile_share_publish_surface.py' in chain:
  if 'test_v396_mobile_share_publish_surface.py' not in chain:raise AssertionError('V396 test wiring missing')

print('V396 MOBILE SHARE PUBLISH SURFACE CONTRACT: PASS')
