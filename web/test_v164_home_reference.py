from pathlib import Path
root=Path("/app")
home=(root/"web/home_v154_component/index.html").read_text(encoding="utf-8")
checks={
 "Approved reference override exists":"V164 APPROVED HOME REFERENCE" in home,
 "Home has six visible grid rows":"grid-template-rows:42% 32% 4% 9% 6% 3%" in home,
 "Uploader formats restored":"MP4 · MOV · AVI<br>MAX 4 GB" in home,
 "Uploader helper visible":".circle small{" in home and "display:block!important" in home,
 "Uploader has stronger blue mint rings":"rgba(102,205,247,.075)" in home and "rgba(89,232,197,.055)" in home,
 "Handwritten notes positioned like reference":"left:4.5%;top:20%" in home and "right:3.8%;top:25%" in home,
 "CTA cards are tall reference cards":"height:100%;min-height:0" in home and "border-radius:clamp(25px" in home,
 "AI card is blue":"#d9efff" in home and "#3e8bea" in home,
 "Editor card is mint":"#dcf8e9" in home and "#168f68" in home,
 "Short card is yellow":"#fff1b6" in home and "#dc8700" in home,
 "CTA arrow circles exist":".feature:after" in home and "margin-top:auto" in home,
}
bad=[k for k,v in checks.items() if not v]
for k,v in checks.items(): print(("PASS" if v else "FAIL")+": "+k)
if bad: raise SystemExit("V164 approved reference contract failed: "+", ".join(bad))
print("V164 approved Home reference: PASS")
