from pathlib import Path
p=Path('/app/GamingShortsFactory_V104_5_YOUTUBE_SOCIAL.py')
s=p.read_text(encoding='utf-8')
lines=s.splitlines()
print("GSF_SOCIAL_UI_BLOCK_BEGIN")
for i in range(13255,13325):
    if i-1 < len(lines):
        print(f"{i}: {lines[i-1]}")
print("GSF_SOCIAL_UI_BLOCK_END")
