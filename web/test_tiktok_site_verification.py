from pathlib import Path
import sys

nginx=Path(sys.argv[1] if len(sys.argv)>1 else '/app/web/nginx.conf.template').read_text(encoding='utf-8')
name='tiktokAvCxVH6S4w3BElUktwlT3dRIBn1ECcZv.txt'
expected='tiktok-developers-site-verification=AvCxVH6S4w3BElUktwlT3dRIBn1ECcZv'

assert f'location = /{name}' in nginx, 'TikTok verification route missing'
assert f'alias /app/web/{name};' in nginx, 'TikTok verification alias missing'

p=Path('/app/web')/name
assert p.exists(), 'TikTok verification file missing'
assert p.read_text(encoding='utf-8').strip()==expected, 'TikTok verification token mismatch'
print('TikTok site verification: PASS')
