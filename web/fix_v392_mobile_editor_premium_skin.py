#!/usr/bin/env python3
from pathlib import Path
import sys

MARK='V392_MOBILE_EDITOR_PREMIUM_SKIN'

EDITOR_PATCH=r'''
<!-- V392_MOBILE_EDITOR_PREMIUM_SKIN -->
<style id="v392MobileEditorPremiumSkin">
@media(max-width:760px){
  /* V392 is visual-only: V389/V391 keep geometry and behavior ownership. */
  #ng27 .stage.r916,#ng27.expanded .stage.r916{
    border-color:rgba(84,190,231,.52)!important;
    background:linear-gradient(180deg,rgba(220,246,253,.96),rgba(248,253,255,.98))!important;
    box-shadow:0 14px 34px rgba(52,111,153,.13),0 0 0 4px rgba(255,255,255,.68),inset 0 1px 0 rgba(255,255,255,.90)!important;
  }
  #ng27 .v389UndoRedo #undoBtn,#ng27 .v389UndoRedo #redoBtn,#ng27 #zoomEditorBtn,#ng27 .v389RatioBtn,
  #ng27 .v389TrimBtn{
    border-color:rgba(100,168,216,.30)!important;
    background:linear-gradient(145deg,rgba(255,255,255,.94),rgba(225,244,252,.88))!important;
    color:#315d82!important;
    box-shadow:0 5px 14px rgba(56,104,143,.13),inset 0 1px 0 rgba(255,255,255,.92)!important;
    -webkit-backdrop-filter:blur(12px) saturate(1.12)!important;
    backdrop-filter:blur(12px) saturate(1.12)!important;
  }
  #ng27 .v389UndoRedo .ico,#ng27 #zoomEditorBtn .ico{color:#315d82!important}
  #ng27 .v389ToolDock .railBtn{
    border-color:rgba(104,171,216,.30)!important;
    background:linear-gradient(145deg,rgba(255,255,255,.92),rgba(220,242,251,.84))!important;
    color:#315d82!important;
    box-shadow:0 7px 17px rgba(53,105,145,.14),inset 0 1px 0 rgba(255,255,255,.92)!important;
    -webkit-backdrop-filter:blur(13px) saturate(1.12)!important;
    backdrop-filter:blur(13px) saturate(1.12)!important;
  }
  #ng27 .v389ToolDock .railBtn .ico,#ng27 .v389ToolDock .railBtn span{color:#315d82!important}
  #ng27 .v389ToolDock .railBtn.active{
    background:linear-gradient(145deg,rgba(111,211,239,.96),rgba(100,178,236,.94))!important;
    border-color:rgba(86,173,225,.42)!important;
    box-shadow:0 8px 20px rgba(54,143,205,.22),inset 0 1px 0 rgba(255,255,255,.74)!important;
  }
  #ng27 .v389ToolDock .railBtn.active .ico,#ng27 .v389ToolDock .railBtn.active span{color:#fff!important}

  /* Keep the existing functional trim/timeline, but remove the heavy grey slab. */
  #ng27 .timeline{
    border-color:rgba(104,173,217,.26)!important;
    background:linear-gradient(145deg,rgba(245,251,254,.82),rgba(218,238,248,.76))!important;
    color:#315d82!important;
    box-shadow:0 7px 18px rgba(49,99,136,.12),inset 0 1px 0 rgba(255,255,255,.84)!important;
    -webkit-backdrop-filter:blur(14px) saturate(1.10)!important;
    backdrop-filter:blur(14px) saturate(1.10)!important;
  }
  #ng27 .timeline .tlMeta,#ng27 .timeline .trimRow,#ng27 .timeline label,#ng27 .timeline span{color:#315d82!important;text-shadow:none!important}
  #ng27 .timeline .track{border-color:rgba(69,160,216,.40)!important;background:rgba(25,61,88,.70)!important;box-shadow:inset 0 1px 5px rgba(8,29,46,.16)!important}
  #ng27 .v389PlayerProgress{color:#315d82!important;text-shadow:none!important}
  #ng27 .v389ProgressTrack{background:rgba(55,107,145,.24)!important}
  #ng27 .v389ProgressFill{background:linear-gradient(90deg,#67d5ef,#3799ee)!important}
  #ng27 .v389PlaybackDock #playBtn{
    border-color:rgba(255,255,255,.90)!important;
    background:linear-gradient(145deg,#6ad4f4,#3b91ef)!important;
    box-shadow:0 9px 23px rgba(43,125,203,.25),0 0 0 3px rgba(255,255,255,.32)!important;
  }

  /* Same V391 actions/placement, premium GSF skin only. */
  #ng27 .v391EditorActions{margin-top:8px!important;gap:8px!important}
  #ng27 .v391EditorAction{border-color:rgba(111,174,218,.28)!important;box-shadow:0 8px 20px rgba(55,107,147,.11),inset 0 1px 0 rgba(255,255,255,.88)!important}
  #ng27 .v391EditorAction.save{background:linear-gradient(145deg,rgba(255,255,255,.96),rgba(236,248,253,.92))!important;color:#315d82!important}
  #ng27 .v391EditorAction.create{background:linear-gradient(135deg,#70d4f3 0%,#45a7f2 48%,#3b8fea 100%)!important;color:#fff!important;border-color:rgba(68,151,224,.32)!important}
}
</style>
'''

SHELL_PATCH=r'''
<style id="v392EditorParentPremium">@media(max-width:760px){#gsf-editor-overlay-v220 .v392EditorCloseGone{display:none!important}}</style>
<script id="v392EditorCloseCleanup">(()=>{const host=document.getElementById('gsf-editor-overlay-v220');if(!host)return;const norm=v=>String(v||'').trim().toLowerCase();const mark=()=>{host.querySelectorAll('button,[role="button"],a').forEach(el=>{const vals=[norm(el.textContent),norm(el.getAttribute('aria-label')),norm(el.getAttribute('title')),norm(el.className),norm(el.id)];const close=vals.some(v=>v==='×'||v==='✕'||v==='✖'||v==='x'||v==='close'||v==='chiudi'||v.includes('close')||v.includes('chiudi'));if(close)el.classList.add('v392EditorCloseGone')})};mark();try{new MutationObserver(mark).observe(host,{childList:true,subtree:true})}catch(_e){}})();</script>
'''

def patch_editor(text:str)->str:
    if MARK in text:return text
    for anchor in ('V389_MOBILE_EDITOR_BOUNDED_RESET','V391_MOBILE_EDITOR_TOP_ACTIONS','</body>'):
        if anchor not in text:raise RuntimeError('V392 Editor anchor missing: '+anchor)
    return text.replace('</body>',EDITOR_PATCH+'\n</body>',1)

def patch_shell(text:str)->str:
    if 'id="v392EditorParentPremium"' in text:return text
    anchor='<style id="gsf-v220-editor-shell">'
    if anchor not in text:raise RuntimeError('V392 parent Editor shell anchor missing')
    return text.replace(anchor,SHELL_PATCH+'\n'+anchor,1)

def main()->None:
    root=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path('/app')
    editor=root/'web'/'editor_2027_component'/'index.html';shell=root/'GamingShortsFactory_V293_RENDER_MEMORY_GUARD.py'
    if not editor.is_file() or not shell.is_file():raise SystemExit('V392 runtime files missing')
    eb=editor.read_text(encoding='utf-8');ea=patch_editor(eb);editor.write_text(ea,encoding='utf-8')
    sb=shell.read_text(encoding='utf-8');sa=patch_shell(sb);compile(sa,str(shell),'exec');shell.write_text(sa,encoding='utf-8')
    print('V392 mobile Editor premium skin + close removal applied editor_changed=',eb!=ea,'shell_changed=',sb!=sa,flush=True)

if __name__=='__main__':main()
