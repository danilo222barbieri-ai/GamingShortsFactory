from pathlib import Path
p=Path("/app/GamingShortsFactory_V106_BETA_RC1.py")
lines=p.read_text(encoding="utf-8").splitlines()

def dump(label,a,b):
    print("V1062_BLOCK_"+label+"_START")
    print("\n".join(f"{j+1}: {lines[j]}" for j in range(a-1,min(len(lines),b))))
    print("V1062_BLOCK_"+label+"_END")

dump("AI_CHOICE_FLOW",13150,13480)
dump("INLINE_EDITOR",12920,13220)
dump("UPLOAD_FLOW",11920,12280)
