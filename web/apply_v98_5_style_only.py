from pathlib import Path

src=Path('/app/GamingShortsFactory_V98_4_EDITOR_CLEANUP.py')
out=Path('/app/GamingShortsFactory_V98_5_STYLE_ONLY.py')
s=src.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise RuntimeError(f'V98.5 style-only target not found: {label}')
    s=s.replace(old,new,1)

# Main source preview: visual card only. Player dimensions remain untouched.
replace_once(
'''        .wrap{{width:100%;display:flex;justify-content:center;align-items:flex-start}}
''',
'''        .wrap{{width:fit-content;max-width:100%;margin:0 auto;
        display:flex;justify-content:center;align-items:flex-start;
        padding:12px;box-sizing:border-box;
        border:1px solid #D4E4EF;border-radius:24px;
        background:linear-gradient(180deg,#FFFFFF 0%,#F8FCFF 100%);
        box-shadow:0 12px 28px rgba(28,78,112,.09)}}
''',
'main preview visual card')

# Editor LIVE legacy preview: faux outer card via shadows only.
# This does not change frame_w/frame_h, the Streamlit columns, or player logic.
replace_once(
'''    .viewport{{position:relative;width:{frame_w}px;height:{frame_h}px;max-width:96vw;
      overflow:hidden;border-radius:18px;background:#000;box-shadow:0 14px 34px rgba(16,40,61,.14)}}
''',
'''    .viewport{{position:relative;width:{frame_w}px;height:{frame_h}px;max-width:96vw;
      margin:10px auto 12px auto;overflow:hidden;border-radius:20px;background:#000;
      box-shadow:0 0 0 9px #F8FCFF,0 0 0 10px #D4E4EF,
                 0 14px 34px rgba(16,40,61,.14)}}
''',
'editor live visual card')

s=s.replace(
    'Gaming Shorts Factory · V98.4 Editor Cleanup',
    'Gaming Shorts Factory · V98.5 Style Only'
)

out.write_text(s,encoding='utf-8')
print(f'V98.5 style-only patch applied: {out}')
