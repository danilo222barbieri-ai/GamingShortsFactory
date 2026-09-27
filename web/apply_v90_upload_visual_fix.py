from pathlib import Path

src=Path('/app/GamingShortsFactory_V89_DECOUPLED_UPLOAD_VISUAL.py')
out=Path('/app/GamingShortsFactory_V90_UPLOAD_VISUAL_FIX.py')
s=src.read_text(encoding='utf-8')

# V90 root fix: V89 accidentally escaped the f-string placeholders in the
# custom upload HTML. That produced literal class/text such as
# {_loaded_class}, {_icon}, {_label}; therefore the CSS class never matched.
repls = {
    'gsf-v89-upload-visual{{_loaded_class}}': 'gsf-v89-upload-visual{_loaded_class}',
    'aria-label="{{_label}}"': 'aria-label="{_label}"',
    '{{_icon}}': '{_icon}',
    '{{_label}}': '{_label}',
}
for old,new in repls.items():
    if old not in s:
        raise RuntimeError(f'V90 target not found: {old}')
    s=s.replace(old,new)

s=s.replace(
    'Gaming Shorts Factory · V89 Decoupled Upload Visual',
    'Gaming Shorts Factory · V90 Upload Visual Fix'
)

out.write_text(s,encoding='utf-8')
print(f'V90 patch applied: {out}')
