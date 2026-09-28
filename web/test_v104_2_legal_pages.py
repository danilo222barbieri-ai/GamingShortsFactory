from pathlib import Path
import sys

p=Path(sys.argv[1])
s=p.read_text(encoding='utf-8')

def need(ok,msg):
    if not ok:
        raise AssertionError(msg)
    print('PASS:',msg)

need('location = /privacy' in s,'public /privacy route exists')
need('location = /terms' in s,'public /terms route exists')
need('alias /app/web/legal/privacy.html;' in s,'privacy page served by nginx')
need('alias /app/web/legal/terms.html;' in s,'terms page served by nginx')

privacy=Path('/app/web/legal/privacy.html')
terms=Path('/app/web/legal/terms.html')
need(privacy.exists(),'privacy HTML exists')
need(terms.exists(),'terms HTML exists')
pt=privacy.read_text(encoding='utf-8')
tt=terms.read_text(encoding='utf-8')
need('Gaming Shorts Factory' in pt and 'Privacy Policy' in pt,'privacy content branded')
need('Gaming Shorts Factory' in tt and 'Termini di servizio' in tt,'terms content branded')
need('YouTube' in pt and 'TikTok' in pt and 'Instagram' in pt,'privacy describes social integrations')
need('28 settembre 2026' in pt and '28 settembre 2026' in tt,'legal pages have update date')

print('V104.2 legal pages: PASS')
