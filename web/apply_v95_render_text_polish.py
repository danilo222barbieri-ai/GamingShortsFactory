from pathlib import Path
import re

src=Path('/app/GamingShortsFactory_V94_SHORT_QUALITY.py')
out=Path('/app/GamingShortsFactory_V95_RENDER_TEXT_POLISH.py')
s=src.read_text(encoding='utf-8')

def replace_once(old,new,label):
    global s
    if old not in s:
        raise RuntimeError(f'V95 patch target not found: {label}')
    s=s.replace(old,new,1)

# FFmpeg/libass in the slim Railway image does not reliably render colour emoji.
# Remove unsupported pictographs from burned-in hook text so users never get tofu boxes.
anchor='''def _gsf_write_render_ass(
'''
helper='''def _gsf_clean_burnin_text(value):
    text=str(value or "")
    # Emoji / pictographs + variation selectors. Keep punctuation and accented text.
    text=re.sub(r"[\\U0001F000-\\U0001FAFF\\u2600-\\u27BF]", "", text)
    text=text.replace("\\ufe0f","").replace("\\u200d","")
    text=re.sub(r"[ \\t]{2,}", " ", text)
    return text.strip()


def _gsf_write_render_ass(
'''
replace_once(anchor,helper,'burn-in text sanitizer')

replace_once(
'''    hook=str(hook_text or "").strip()
    if hook:
''',
'''    hook=_gsf_clean_burnin_text(hook_text)
    if hook:
''',
'hook sanitizer use')

# Make built-in hooks typography-safe by default too.
for old,new in [
    ('"CHE GOL! ⚽🔥"','"CHE GOL!"'),
    ('"ELIMINATO! 🎯"','"ELIMINATO!"'),
    ('"VITTORIA! 🏆"','"VITTORIA!"'),
    ('"CHE OCCASIONE! 😱"','"CHE OCCASIONE!"'),
    ('"MOMENTO GARA! 🏎️🔥"','"MOMENTO GARA!"'),
    ('"SBLOCCATO! ⭐"','"SBLOCCATO!"'),
    ('"ECCO IL MOMENTO! 💥"','"ECCO IL MOMENTO!"'),
    ('"CHE REAZIONE! 😱"','"CHE REAZIONE!"'),
    ('"AZIONE PURA! 🔥"','"AZIONE PURA!"'),
    ('"ECCO IL MOMENTO! 🎬"','"ECCO IL MOMENTO!"'),
]:
    s=s.replace(old,new)

s=s.replace(
    'Gaming Shorts Factory · V94 Short Quality',
    'Gaming Shorts Factory · V95 Render Text Polish'
)

out.write_text(s,encoding='utf-8')
print(f'V95 patch applied: {out}')
