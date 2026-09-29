from pathlib import Path
p=Path("/app/GamingShortsFactory_V106_BETA_RC1.py")
lines=p.read_text(encoding="utf-8").splitlines()

def dump(label,a,b):
    print("V1062_BLOCK_"+label+"_START")
    print("\n".join(f"{j+1}: {lines[j]}" for j in range(a-1,min(len(lines),b))))
    print("V1062_BLOCK_"+label+"_END")

dump("MAIN_EDITOR",12440,12780)
dump("INLINE_EDITOR",13020,13280)

first_video=None
for i,line in enumerate(lines,1):
    if line.strip()=="if video:":
        first_video=i
        break
if first_video:
    dump("SOURCE_FLOW", first_video, first_video+420)

print("V1062_SOURCE_PLAYER_HITS_START")
for i,line in enumerate(lines,1):
    low=line.lower()
    if ("st.video(" in low or "render_gsf" in low or "lettore" in low or "video caricato" in low) and i < 12500:
        print(f"{i}: {line}")
print("V1062_SOURCE_PLAYER_HITS_END")
