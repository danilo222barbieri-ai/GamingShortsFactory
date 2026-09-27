from pathlib import Path

src=Path('/app/GamingShortsFactory_V90_UPLOAD_VISUAL_FIX.py')
out=Path('/app/GamingShortsFactory_V91_ROADMAP_POLISH.py')
s=src.read_text(encoding='utf-8')

old_css=r'''/* Real upload progress, but shown outside the invisible uploader as a tiny bar. */
.st-key-v73-upload-shell:has([role="progressbar"])::after,
.st-key-v73-upload-shell:has(progress)::after,
.st-key-v73-upload-shell:has([data-testid*="Progress"])::after{{
    content:"";
    display:block;
    width:154px;
    height:6px;
    margin:12px auto 0;
    border-radius:999px;
    background:#22C55E;
    box-shadow:0 0 0 1px rgba(34,197,94,.14);
}}
'''
new_css=r'''/* V91 — piccolo indicatore indipendente sotto il cerchio.
   Non mostra una percentuale inventata: appare solo mentre Streamlit espone
   il vero stato di upload e comunica chiaramente che il file sta salendo. */
.gsf-v91-upload-status{{
    display:none;
    width:154px;
    margin:10px auto 0;
    flex-direction:column;
    align-items:center;
    justify-content:center;
    gap:5px;
    color:#238A50;
    font-size:12px;
    font-weight:800;
    line-height:1;
    text-align:center;
}}
.st-key-v73-upload-shell:has([role="progressbar"]) .gsf-v91-upload-status,
.st-key-v73-upload-shell:has(progress) .gsf-v91-upload-status,
.st-key-v73-upload-shell:has([data-testid*="Progress"]) .gsf-v91-upload-status{{
    display:flex;
}}
.gsf-v91-upload-track{{
    position:relative;
    width:132px;
    height:5px;
    overflow:hidden;
    border-radius:999px;
    background:rgba(34,197,94,.18);
    box-shadow:inset 0 0 0 1px rgba(34,197,94,.08);
}}
.gsf-v91-upload-runner{{
    position:absolute;
    top:0;
    bottom:0;
    left:-42%;
    width:42%;
    border-radius:999px;
    background:#22C55E;
    animation:gsfV91UploadMove 1.0s ease-in-out infinite;
}}
@keyframes gsfV91UploadMove{{
    0%{{left:-42%;}}
    55%{{left:42%;}}
    100%{{left:100%;}}
}}
@media (prefers-reduced-motion: reduce){{
    .gsf-v91-upload-runner{{
        animation:none;
        left:29%;
    }}
}}
'''

if old_css not in s:
    raise RuntimeError('V91 progress CSS anchor not found')
s=s.replace(old_css,new_css,1)

old_html='''<div class="gsf-v89-upload-visual{_loaded_class}" role="status" aria-label="{_label}">
  <span class="gsf-v89-upload-icon">{_icon}</span>
  <span class="gsf-v89-upload-label">{_label}</span>
</div>
'''
new_html='''<div class="gsf-v89-upload-visual{_loaded_class}" role="status" aria-label="{_label}">
  <span class="gsf-v89-upload-icon">{_icon}</span>
  <span class="gsf-v89-upload-label">{_label}</span>
</div>
<div class="gsf-v91-upload-status" aria-live="polite">
  <span>Caricamento video…</span>
  <span class="gsf-v91-upload-track" aria-hidden="true">
    <span class="gsf-v91-upload-runner"></span>
  </span>
</div>
'''
if old_html not in s:
    raise RuntimeError('V91 upload HTML anchor not found')
s=s.replace(old_html,new_html,1)

s=s.replace(
    'Gaming Shorts Factory · V90 Upload Visual Fix',
    'Gaming Shorts Factory · V91 Roadmap Polish'
)

out.write_text(s,encoding='utf-8')
print(f'V91 patch applied: {out}')
