"""Deployed mobile bugfix audit. Uses fresh local Creator sessions, no social posts.

Run with --base URL --out evidence-directory. Set GSF_BROWSER_PROXY for public
network access. Browser state, cookies and signed media URLs are never exported.
"""
import argparse
import base64
import json
import os
from pathlib import Path
from playwright.sync_api import sync_playwright


def audit(base, out, engine='chromium'):
    out.mkdir(parents=True, exist_ok=True)
    results=[]
    with sync_playwright() as playwright:
        options={'headless':True}
        if engine=='chromium':options.update(executable_path=os.environ.get('GSF_CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox'])
        if os.environ.get('GSF_BROWSER_PROXY'):options['proxy']={'server':os.environ['GSF_BROWSER_PROXY']}
        browser=getattr(playwright,engine).launch(**options)
        try:
            for label,width,height in [('iphone-small',375,667),('iphone-standard',390,844),('iphone-large',430,932),('android-chrome',412,915)]:
                device=playwright.devices['Pixel 7' if label=='android-chrome' else 'iPhone 13']
                context=browser.new_context(**{**device,'viewport':{'width':width,'height':height}})
                page=context.new_page();errors=[];page.on('pageerror',lambda error:errors.append(str(error)))
                try:
                    page.goto(base,wait_until='domcontentloaded',timeout=60000)
                    page.wait_for_function('()=>GSFNavigation?.snapshot().surfaces===5',timeout=60000)
                    page.locator('#gsf-global-gamebar [data-page=hub]').click()
                    hub=page.frame_locator('#gsf-creator-hub-live-v160 iframe')
                    hub.locator('#hub').wait_for()
                    page.wait_for_function("()=>document.querySelector('#gsf-creator-hub-live-v160 iframe').contentWindow.GSFHubV415?.getState().csrf_token",timeout=30000)
                    page.wait_for_function("()=>document.querySelector('[data-testid=stApp]')?.getAttribute('data-test-script-state')==='notRunning'",timeout=60000)
                    views=[]
                    for extra_safe_area in (0,24):
                        if extra_safe_area:page.locator('#gsf-global-gamebar').evaluate("e=>e.style.setProperty('padding-bottom','24px','important')")
                        for view in ('dashboard','projects','live','settings'):
                            hub.locator('#hub').evaluate('(e,v)=>GSFHubV415.openView(v)',view)
                            hub.locator('#hub').evaluate('e=>new Promise(resolve=>requestAnimationFrame(()=>requestAnimationFrame(()=>{e.scrollTop=e.scrollHeight;resolve()})))');page.wait_for_timeout(120)
                            geometry=page.locator('#gsf-creator-hub-live-v160 iframe').evaluate("f=>{const r=f.getBoundingClientRect(),d=f.contentDocument,h=d.querySelector('#hub'),v=d.querySelector('.view.active'),bar=document.querySelector('#gsf-global-gamebar').getBoundingClientRect();h.scrollTop=h.scrollHeight;return {view:v.dataset.view,lastBottom:r.top+v.getBoundingClientRect().bottom,barTop:bar.top,scrollTop:h.scrollTop,scrollHeight:h.scrollHeight,clientHeight:h.clientHeight,paddingBottom:f.contentWindow.getComputedStyle(h).paddingBottom,frameTop:r.top,frameBottom:r.bottom,outerScroll:d.scrollingElement.scrollTop}}")
                            assert geometry['lastBottom']<=geometry['barTop']-8,(label,extra_safe_area,geometry)
                            assert geometry['outerScroll']==0,geometry
                            views.append({**geometry,'extra_safe_area':extra_safe_area})
                    page.locator('#gsf-global-gamebar').evaluate("e=>e.style.removeProperty('padding-bottom')")
                    page.locator('#gsf-global-header .v343Account').click()
                    hub.locator('#profileNameInput').wait_for()
                    assert not hub.locator('#accountBtn').is_visible(),'Guest Accedi row remains'
                    name='Beta '+label
                    hub.locator('#profileNameInput').fill(name)
                    with page.expect_response('**/creator-hub/profile') as saved:hub.locator('#saveProfileBtn').click()
                    assert saved.value.ok,saved.value.status
                    page.wait_for_function("name=>document.querySelector('#gsf-global-header .v343AccountName').textContent===name",arg=name)
                    image=page.evaluate("()=>{const c=document.createElement('canvas');c.width=1024;c.height=256;const x=c.getContext('2d');x.fillStyle='#27AEF3';x.fillRect(0,0,1024,256);return c.toDataURL('image/png').split(',')[1]}")
                    with page.expect_file_chooser() as chooser:hub.locator('#profileAvatar').click()
                    with page.expect_response('**/creator-hub/profile') as photo:
                        chooser.value.set_files({'name':'beta-profile.png','mimeType':'image/png','buffer':base64.b64decode(image)})
                    assert photo.value.ok,photo.value.status
                    page.wait_for_function("()=>{const i=document.querySelector('#gsf-global-header .v343Avatar img');return i&&i.complete&&i.naturalWidth>0}")
                    hub.locator('#profileAvatarImg').evaluate('e=>e.decode()')
                    dimensions=hub.locator('#profileAvatarImg').evaluate('e=>[e.naturalWidth,e.naturalHeight]')
                    assert max(dimensions)<=512,dimensions
                    page.reload(wait_until='domcontentloaded');page.wait_for_function('()=>GSFNavigation?.snapshot().surfaces===5')
                    page.locator('#gsf-global-header .v343Account').click()
                    hub.locator('#profileNameInput').wait_for()
                    page.wait_for_function("name=>document.querySelector('#gsf-creator-hub-live-v160 iframe').contentDocument.querySelector('#profileNameInput')?.value===name",arg=name)
                    assert hub.locator('#profileAvatar').evaluate("e=>e.classList.contains('has-photo')")
                    # Exercise actual persistent API + OFF CTA without sending a push.
                    preference=page.evaluate("async()=>{const s=await GSFPush.status();return fetch('/push/preferences',{method:'POST',headers:{'Content-Type':'application/json','X-GSF-CSRF':s.csrf_token},body:JSON.stringify({enabled:true,revision:Math.max(Date.now(),s.revision+1)})}).then(r=>r.json())}")
                    assert preference.get('enabled'),preference
                    hub.locator('#hub').evaluate("()=>GSFHubV415.loadState()")
                    hub.locator('#notifyBtn').filter(has_text='Disattiva').wait_for()
                    with page.expect_response('**/push/preferences') as off:hub.locator('#notifyBtn').click()
                    # The first response can be the status GET before the POST.
                    page.wait_for_function("async()=>!(await GSFPush.status()).enabled")
                    page.locator('#gsf-global-gamebar [data-page=home]').click()
                    page.wait_for_function("()=>GSFNavigation.snapshot().target==='home'")
                    assert page.evaluate('()=>document.scrollingElement.scrollTop')==0
                    page.locator('#gsf-global-gamebar [data-page=hub]').click()
                    hub.locator('#hub').evaluate("()=>{GSFHubV415.openView('dashboard');GSFAlive.emit('video.cleared');GSFAlive.refresh()}")
                    ring=[]
                    for scroll in (0,80,160,240):
                        hub.locator('#hub').evaluate('(e,n)=>e.scrollTop=n',scroll);page.wait_for_timeout(35)
                        point=hub.locator('#hub').evaluate("()=>{const t=document.querySelector('[data-alive-next~=upload]'),g=document.querySelector('#gsf-alive-guide'),r=g.getBoundingClientRect(),a=t.getBoundingClientRect();return {visible:getComputedStyle(g).display!=='none',offset:r.top-a.top+6}}")
                        if point['visible']:assert abs(point['offset'])<6,(label,point)
                        ring.append(point)
                    hub.locator('#hub').evaluate("()=>GSFAlive.say('Route lifecycle check')")
                    page.locator('#gsf-global-gamebar [data-page=home]').click()
                    page.locator('#gsf-global-gamebar [data-page=hub]').click()
                    assert not hub.locator('#gsf-alive-whisper').evaluate("e=>e.classList.contains('on')"),'Old voice returned'
                    assert not errors,errors
                    page.screenshot(path=str(out/(label+'.png')))
                    result={'device':label,'views':views,'profile_saved':True,'photo_dimensions':dimensions,'notifications_off_persistent':True,'ring':ring,'runtime_errors':errors}
                    results.append(result);print(json.dumps(result),flush=True)
                    (out/'evidence.json').write_text(json.dumps(results,indent=2))
                except Exception:
                    page.screenshot(path=str(out/(label+'-failure.png')))
                    raise
                finally:context.close()
        finally:browser.close()


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--base',required=True);parser.add_argument('--out',type=Path,required=True);parser.add_argument('--browser',default='chromium')
    args=parser.parse_args();audit(args.base.rstrip('/'),args.out,args.browser)
