"""Real-browser navigation/lifecycle assertions; GSF_BASE_URL selects running GSF.

Chromium uses GSF_CHROMIUM (system Chromium by default); GSF_BROWSER=webkit
uses Playwright WebKit. No request mocking or swallowed JS errors.
"""
import os
import base64
import uuid
import time
from contextlib import contextmanager

# A real, generated 2-second H.264 fixture. No provider or AI calls are needed.
MEDIA_FIXTURE=base64.b64decode('AAAAIGZ0eXBpc29tAAACAGlzb21pc28yYXZjMW1wNDEAAAQhbW9vdgAAAGxtdmhkAAAAAAAAAAAAAAAAAAAD6AAAB9AAAQAAAQAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAgAAA0x0cmFrAAAAXHRraGQAAAADAAAAAAAAAAAAAAABAAAAAAAAB9AAAAAAAAAAAAAAAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAABAAAAAAAAAAAAAAAAAABAAAAAAEAAAABAAAAAAAAkZWR0cwAAABxlbHN0AAAAAAAAAAEAAAfQAAAIAAABAAAAAALEbWRpYQAAACBtZGhkAAAAAAAAAAAAAAAAAAAoAAAAUABVxAAAAAAALWhkbHIAAAAAAAAAAHZpZGUAAAAAAAAAAAAAAABWaWRlb0hhbmRsZXIAAAACb21pbmYAAAAUdm1oZAAAAAEAAAAAAAAAAAAAACRkaW5mAAAAHGRyZWYAAAAAAAAAAQAAAAx1cmwgAAAAAQAAAi9zdGJsAAAAv3N0c2QAAAAAAAAAAQAAAK9hdmMxAAAAAAAAAAEAAAAAAAAAAAAAAAAAAAAAAEAAQABIAAAASAAAAAAAAAABFUxhdmM2MS4xOS4xMDEgbGlieDI2NAAAAAAAAAAAAAAAGP//AAAANWF2Y0MBZAAK/+EAGGdkAAqs2UQmwEQAAAMABAAAAwBQPEiWWAEABmjr48siwP34+AAAAAAQcGFzcAAAAAEAAAABAAAAFGJ0cnQAAAAAAAAPrAAAAAAAAAAYc3R0cwAAAAAAAAABAAAAFAAABAAAAAAUc3RzcwAAAAAAAAABAAAAAQAAAKhjdHRzAAAAAAAAABMAAAABAAAIAAAAAAEAABQAAAAAAQAACAAAAAABAAAAAAAAAAEAAAQAAAAAAQAAFAAAAAABAAAIAAAAAAEAAAAAAAAAAQAABAAAAAABAAAUAAAAAAEAAAgAAAAAAQAAAAAAAAABAAAEAAAAAAEAABQAAAAAAQAACAAAAAABAAAAAAAAAAEAAAQAAAAAAQAAEAAAAAACAAAEAAAAABxzdHNjAAAAAAAAAAEAAAABAAAAFAAAAAEAAABkc3RzegAAAAAAAAAAAAAAFAAAAt0AAAAOAAAADAAAAAwAAAAMAAAAFAAAAA4AAAAMAAAADAAAABQAAAAOAAAADAAAAAwAAAAUAAAADgAAAAwAAAAMAAAAFAAAAA4AAAAMAAAAFHN0Y28AAAAAAAAAAQAABFEAAABhdWR0YQAAAFltZXRhAAAAAAAAACFoZGxyAAAAAAAAAABtZGlyYXBwbAAAAAAAAAAAAAAAACxpbHN0AAAAJKl0b28AAAAcZGF0YQAAAAEAAAAATGF2ZjYxLjcuMTAzAAAACGZyZWUAAAPzbWRhdAAAAq4GBf//qtxF6b3m2Ui3lizYINkj7u94MjY0IC0gY29yZSAxNjQgcjMxMDggMzFlMTlmOSAtIEguMjY0L01QRUctNCBBVkMgY29kZWMgLSBDb3B5bGVmdCAyMDAzLTIwMjMgLSBodHRwOi8vd3d3LnZpZGVvbGFuLm9yZy94MjY0Lmh0bWwgLSBvcHRpb25zOiBjYWJhYz0xIHJlZj0zIGRlYmxvY2s9MTowOjAgYW5hbHlzZT0weDM6MHgxMTMgbWU9aGV4IHN1Ym1lPTcgcHN5PTEgcHN5X3JkPTEuMDA6MC4wMCBtaXhlZF9yZWY9MSBtZV9yYW5nZT0xNiBjaHJvbWFfbWU9MSB0cmVsbGlzPTEgOHg4ZGN0PTEgY3FtPTAgZGVhZHpvbmU9MjEsMTEgZmFzdF9wc2tpcD0xIGNocm9tYV9xcF9vZmZzZXQ9LTIgdGhyZWFkcz0yIGxvb2thaGVhZF90aHJlYWRzPTEgc2xpY2VkX3RocmVhZHM9MCBucj0wIGRlY2ltYXRlPTEgaW50ZXJsYWNlZD0wIGJsdXJheV9jb21wYXQ9MCBjb25zdHJhaW5lZF9pbnRyYT0wIGJmcmFtZXM9MyBiX3B5cmFtaWQ9MiBiX2FkYXB0PTEgYl9iaWFzPTAgZGlyZWN0PTEgd2VpZ2h0Yj0xIG9wZW5fZ29wPTAgd2VpZ2h0cD0yIGtleWludD0yNTAga2V5aW50X21pbj0xMCBzY2VuZWN1dD00MCBpbnRyYV9yZWZyZXNoPTAgcmNfbG9va2FoZWFkPTQwIHJjPWNyZiBtYnRyZWU9MSBjcmY9MjMuMCBxY29tcD0wLjYwIHFwbWluPTAgcXBtYXg9NjkgcXBzdGVwPTQgaXBfcmF0aW89MS40MCBhcT0xOjEuMDAAgAAAACdliIQAEf/+5+P8Cm2u/3E0oGO1rW13Ki6Nce2KM2pLx924Q9sRn8EAAAAKQZokbEEf/rUr7wAAAAhBnkJ4h38FvQAAAAgBnmF0Q38HfAAAAAgBnmNqQ38HfQAAABBBmmhJqEFomUwII//+tSvvAAAACkGehkURLDv/Bb0AAAAIAZ6ldEN/B30AAAAIAZ6nakN/B3wAAAAQQZqsSahBbJlMCCH//qpX3gAAAApBnspFFSw7/wW9AAAACAGe6XRDfwd8AAAACAGe62pDfwd8AAAAEEGa8EmoQWyZTAh///6pnTUAAAAKQZ8ORRUsO/8FvQAAAAgBny10Q38HfQAAAAgBny9qQ38HfAAAABBBmzNJqEFsmUwIb//+p4+IAAAACkGfUUUVLDf/B30AAAAIAZ9yakN/B3w=')

SURFACES = {'hub':'gsf-creator-hub-live-v160','editor':'gsf-editor-overlay-v220',
            'ai':'gsf-ai-overlay-v221','short':'gsf-social-overlay-v159',  # Crea Short = canonical page
            'social':'gsf-social-overlay-v159','account':'gsf-account-overlay-v223'}
SEQUENCES = [('home','hub','home','hub'),('home','ai','home','ai'),
             ('home','editor','home','editor'),('home','short','home','short'),
             ('hub','profile','hub','projects','hub'),('home','hub','editor','hub','home'),
             ('home','ai','editor','short','home')]

INSTRUMENT = r"""
(() => {
 let top;try {top=window.top;void top.document;} catch (_) {return;}
 const state=top.__gsfStability||(top.__gsfStability={mutation:0,resize:0,callbacks:0,callbackMs:0});
 for(const [name,key] of [['MutationObserver','mutation'],['ResizeObserver','resize']]) {
  const Native=window[name];if(!Native)continue;
  window[name]=class extends Native {
   constructor(callback){super((records,observer)=>{const t=performance.now();state.callbacks++;try{callback(records,observer);}finally{state.callbackMs+=performance.now()-t;}});this.counted=false;}
   observe(target,options){if(target.ownerDocument===top.document||target===top.document){if(!this.counted){state[key]++;this.counted=true;}}return super.observe(target,options);}
   disconnect(){if(this.counted){state[key]--;this.counted=false;}return super.disconnect();}
  };
 }
})();
"""

_MEDIA_SETUP_FAILURE=None

@contextmanager
def browser_page(mobile=True):
    global _MEDIA_SETUP_FAILURE
    from playwright.sync_api import sync_playwright
    # One broken media setup fails every later test at once instead of 2 minutes each.
    if _MEDIA_SETUP_FAILURE and os.environ.get('GSF_TEST_MEDIA')=='1':
        raise AssertionError('media setup already failed in this run: '+_MEDIA_SETUP_FAILURE)
    started=time.monotonic()
    with sync_playwright() as p:
        engine = os.environ.get('GSF_BROWSER','chromium')
        opts = {'headless':True}
        if engine=='chromium':
            opts.update(executable_path=os.environ.get('GSF_CHROMIUM','/usr/bin/chromium'),args=['--no-sandbox'],ignore_default_args=['--disable-back-forward-cache'])
        if os.environ.get('GSF_BROWSER_PROXY'):
            opts['proxy']={'server':os.environ['GSF_BROWSER_PROXY']}
            opts['env']={**os.environ,'HOME':'/tmp/gsf-browser-home'}
        browser = getattr(p,engine).launch(**opts)
        print("BROWSER LAUNCHED",engine,round(time.monotonic()-started,2),flush=True)
        ctx = browser.new_context(**(p.devices['iPhone 13'] if mobile else {'viewport':{'width':1440,'height':1000}}))
        ctx.add_init_script(INSTRUMENT)
        # The edge issues gsf_sid as a Secure cookie. Production is HTTPS; the gate talks to the
        # container over plain http://127.0.0.1, where WebKit drops Secure cookies, so every
        # request would get a fresh session (upload in one session, app in another). Give the
        # browser the same stable session id a real HTTPS visitor keeps.
        base=os.environ['GSF_BASE_URL'].rstrip('/')
        if base.startswith('http://'):
            ctx.add_cookies([{'name':'gsf_sid','value':'stability'+uuid.uuid4().hex[:20],'url':base+'/'}])
        if os.environ.get("GSF_DOM_DIAGNOSTICS"):
            from pathlib import Path
            ctx.add_init_script(Path(os.environ["GSF_DOM_DIAGNOSTICS"]).read_text())
        page = ctx.new_page()
        page.set_default_timeout(15000)
        # Headless WebKit on the Linux runner can stop issuing rendering updates
        # (requestAnimationFrame stalls in every frame while timers, visibility and
        # focus stay normal). Playwright's default 'raf' polling would then never
        # re-check a condition, so poll on a timer instead.
        native_wait=page.wait_for_function
        def wait_for_function(expression,arg=None,timeout=None,polling=100):
            return native_wait(expression,arg=arg,timeout=timeout,polling=polling)
        page.wait_for_function=wait_for_function
        errors=[]
        page.on('pageerror',lambda e:errors.append('pageerror: '+str(e)))
        def console_error(message):
            if message.type!='error':return
            errors.append('console: '+message.text+' '+str(message.location))
            if os.environ.get('GSF_DOM_DIAGNOSTICS'):print('BROWSER ERROR',message.text,flush=True)
        page.on('console',console_error)
        page.on('requestfailed',lambda r:errors.append('network: '+r.url+' '+str(r.failure)))
        page.on('response',lambda r:errors.append('http: '+str(r.status)+' '+r.url) if r.status>=400 else None)
        page.goto(os.environ['GSF_BASE_URL'],wait_until='domcontentloaded',timeout=120000)
        print('DOCUMENT READY',round(time.monotonic()-started,2),flush=True)
        page.wait_for_selector('#gsf-global-gamebar',timeout=120000)
        page.wait_for_function("()=>window.GSFNavigation?.snapshot().surfaces===5",timeout=120000)
        page.wait_for_function("()=>[...document.querySelectorAll('iframe')].some(f=>{try{return f.contentWindow.__GSF_V333_CTA_TOUCH===true}catch(_){return false}})",timeout=120000)
        page.wait_for_function("()=>document.querySelector('[data-testid=stApp]')?.getAttribute('data-test-script-state')==='notRunning'",timeout=120000)
        print("APP READY",round(time.monotonic()-started,2),flush=True)
        assert not errors,errors
        if os.environ.get('GSF_TEST_MEDIA')=='1':
            # Upload exactly like a user: choose the file in the Home uploader. The Home
            # then uploads it (bucket or chunked companion), marks itself loaded and
            # emits upload_complete so the app reruns and materializes the source.
            home=next(f for f in page.frames if f.evaluate("()=>{try{return window.__GSF_V333_CTA_TOUCH===true}catch(_){return false}}"))
            home.set_input_files('#pick',files=[{'name':'stability.mp4','mimeType':'video/mp4','buffer':MEDIA_FIXTURE}])
            # Upload completion triggers a real Streamlit rerun. Warm-up must
            # measure the loaded app, including its finite widget hotkeys.
            try:
                page.wait_for_function("()=>[...document.querySelectorAll('iframe')].some(f=>{try{return f.contentWindow.__GSF_V333_CTA_TOUCH===true&&!!f.contentDocument.querySelector('.rings.uploaded')}catch(_){return false}})",timeout=120000)
            except Exception as exc:
                # Make the setup failure diagnosable from the gate annotations.
                state=page.evaluate("""()=>{const app=document.querySelector('[data-testid=stApp]');const home=[...document.querySelectorAll('iframe')].find(f=>{try{return f.contentWindow.__GSF_V333_CTA_TOUCH===true}catch(_){return false}});let h={};try{const d=home.contentDocument;h={rings:d.querySelector('.rings')?.className,circle:d.querySelector('#circle')?.className,status:d.querySelector('#statusText')?.textContent,frameSrc:home.getAttribute('src')?.slice(0,80),parentIsTop:home.contentWindow.parent===window}}catch(e){h={err:String(e)}};return {script:app?.getAttribute('data-test-script-state'),exceptions:[...document.querySelectorAll('[data-testid=stException],.stException')].map(e=>e.innerText.slice(0,400)),alerts:[...document.querySelectorAll('[data-testid=stAlert]')].map(e=>e.innerText.slice(0,200)),home:h,frames:[...document.querySelectorAll('iframe')].map(f=>(f.title||'')+'|'+String(f.getAttribute('src')||'').slice(0,60))}}""")
                _MEDIA_SETUP_FAILURE=f"upload setup did not reach the loaded Home: {state} errors={errors[:8]}"
                raise AssertionError(_MEDIA_SETUP_FAILURE) from exc
            try:
                page.wait_for_function("()=>!!document.querySelector('.st-key-v81_new_video button')&&document.querySelector('[data-testid=stApp]')?.getAttribute('data-test-script-state')==='notRunning'",timeout=120000)
            except Exception as exc:
                state=page.evaluate("""()=>({script:document.querySelector('[data-testid=stApp]')?.getAttribute('data-test-script-state'),newVideo:!!document.querySelector('.st-key-v81_new_video'),keys:[...document.querySelectorAll('[class*=st-key-]')].map(e=>[...e.classList].find(c=>c.startsWith('st-key-'))).slice(0,60),buttons:[...document.querySelectorAll('button')].map(b=>(b.innerText||'').trim()).filter(Boolean).slice(0,40),exceptions:[...document.querySelectorAll('[data-testid=stException]')].map(e=>e.innerText.slice(0,500)),alerts:[...document.querySelectorAll('[data-testid=stAlert]')].map(e=>e.innerText.slice(0,200))})""")
                _MEDIA_SETUP_FAILURE=f"app did not settle on the loaded project after upload: {state} errors={errors[:8]}"
                raise AssertionError(_MEDIA_SETUP_FAILURE) from exc
        try:
            yield page,errors,ctx
        except BaseException:
            print('CAPTURED ERRORS',errors,flush=True)
            try:
                state=page.evaluate("""()=>{const ed=document.querySelector('#gsf-editor-overlay-v220 iframe');let edState={};try{const d=ed?.contentDocument,app=d?.getElementById('gameEditorApp');const look=d?.querySelector('[data-tool=look]');const r=look?.getBoundingClientRect();edState={cls:app?.className,look:r?[Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)]:null,lookVis:look?getComputedStyle(look).visibility:null,sheetOpen:app?.classList.contains('is-tool-open')}}catch(e){edState={err:String(e)}};const bar=document.getElementById('gsf-global-gamebar');const br=bar?.getBoundingClientRect();const so=document.querySelector('#gsf-social-overlay-v159 iframe');let share={};try{share={src:so?.getAttribute('src'),ready:so?.contentDocument?.readyState,crea:!!so?.contentDocument?.querySelector('#crea413')}}catch(e){share={err:String(e)}};return {nav:window.GSFNavigation?.snapshot(),html:document.documentElement.className,bar:br?[Math.round(br.x),Math.round(br.y),Math.round(br.width),Math.round(br.height),getComputedStyle(bar).display,getComputedStyle(bar).visibility]:null,editor:edState,share,render:window.__renderTriggered===true,toasts:[...document.querySelectorAll('.gsf-site-toast')].map(t=>t.innerText.slice(0,60)),tail:document.body.innerText.slice(-120)}}""")
                # Rendering health: Playwright's click stability and wait_for_function both
                # poll on requestAnimationFrame, so record whether frames still tick.
                try:state['frames']=page.evaluate("""()=>{const probe=w=>new Promise(res=>{let n=0;const t0=w.performance.now();let done=false;const finish=v=>{if(!done){done=true;res(v)}};const f=()=>{n++;if(w.performance.now()-t0<1000)w.requestAnimationFrame(f);else finish(n)};try{w.requestAnimationFrame(f)}catch(e){finish('err '+e)}setTimeout(()=>finish('stalled after '+n),1600)});const ed=document.querySelector('#gsf-editor-overlay-v220 iframe')?.contentWindow;const lag=new Promise(res=>{const t=performance.now();setTimeout(()=>res(Math.round(performance.now()-t)),0)});const anims=[...document.querySelectorAll('#gsf-global-gamebar button, #gsf-global-gamebar')].flatMap(b=>b.getAnimations?b.getAnimations({subtree:true}).map(a=>(a.animationName||a.transitionProperty||a.constructor.name)+':'+a.playState):[]);return Promise.all([probe(window),ed?probe(ed):Promise.resolve(null),lag]).then(([top,editor,timeoutLag])=>({top,editor,timeoutLag,visibility:document.visibilityState,hidden:document.hidden,focus:document.hasFocus(),fullscreen:!!document.fullscreenElement,anims:anims.slice(0,12)}))}""")
                except Exception as exc:state['frames']='probe failed: '+str(exc)[:200]
                # Experiment: does the stall follow the <video> elements? Describe them, then
                # pause them and re-probe, then detach their media and re-probe.
                try:state['videos']=page.evaluate("""async()=>{const wins=[window,...[...document.querySelectorAll('iframe')].map(f=>{try{void f.contentDocument;return f.contentWindow}catch(_){return null}}).filter(Boolean)];const vids=wins.flatMap(w=>[...w.document.querySelectorAll('video')].map(v=>({w,v})));const probe=()=>new Promise(res=>{let n=0;const t0=performance.now();let done=false;const fin=v=>{if(!done){done=true;res(v)}};const f=()=>{n++;if(performance.now()-t0<800)requestAnimationFrame(f);else fin(n)};requestAnimationFrame(f);setTimeout(()=>fin('stalled '+n),1200)});const list=vids.map(({w,v})=>[(w.location.pathname||'').slice(0,24),String(v.getAttribute('src')||'').slice(0,40),v.readyState,v.networkState,v.paused,Math.round(v.currentTime*10)/10,getComputedStyle(v).display]);vids.forEach(({v})=>{try{v.pause()}catch(_){}});const afterPause=await probe();vids.forEach(({v})=>{try{v.removeAttribute('src');v.load()}catch(_){}});const afterDetach=await probe();return {list,afterPause,afterDetach}}""")
                except Exception as exc:state['videos']='video probe failed: '+str(exc)[:200]
                print('FAILURE STATE',state,flush=True)
                print('::error title=GSF nav failure state::'+str(state).replace('%','%25').replace('\n','%0A')[:6000],flush=True)
            except Exception:pass
            raise
        finally:
            browser.close()

def navigate(page,target,ready=True):
    if target in ('home','hub','projects','live'):
        tap(page.locator(f'#gsf-global-gamebar [data-page="{target}"]'))
    elif target=='profile':
        tap(page.locator('#gsf-global-header .v343Account'))
    else:
        # The public protocol used by Home CTAs, AI results and Editor actions.
        page.evaluate("t=>window.postMessage({type:'GSF_SHELL_NAV',target:t},location.origin)",target)
    expected=SURFACES.get('hub' if target in ('profile','projects','live') else target)
    page.wait_for_function("id=>{const ids=['gsf-creator-hub-live-v160','gsf-editor-overlay-v220','gsf-ai-overlay-v221','gsf-short-overlay-v343','gsf-social-overlay-v159','gsf-account-overlay-v223'];return ids.every(k=>{const e=document.getElementById(k);return k===id?e?.classList.contains('is-open'):!e?.classList.contains('is-open')})}",arg=expected)
    if target in ('hub','profile','projects','live'):
        section={'hub':'dashboard','profile':'settings','projects':'projects','live':'live'}[target]
        # Read the actual same-origin view; cached iframe targets may not be
        # reattached in Playwright after a genuine BFCache pageshow.
        page.wait_for_function("section=>{const f=document.querySelector('#gsf-creator-hub-live-v160 iframe'),d=f?.contentDocument,e=d?.querySelector('.view[data-view=\"'+section+'\"].active');return !!e&&e.getBoundingClientRect().height>0&&f.contentWindow.getComputedStyle(e).visibility!=='hidden'}",arg=section)
    if target=='ai':
        page.wait_for_function("()=>{const d=document.querySelector('#gsf-ai-overlay-v221 iframe')?.contentDocument;return d?.readyState==='complete'&&!!d.querySelector('#ai404')}")
    if target=='editor' and ready:
        page.wait_for_function("()=>document.querySelector('#gsf-editor-overlay-v220 iframe')?.__gsfEditorInitialized===true")
        if os.environ.get('GSF_TEST_MEDIA')=='1':
            page.wait_for_function("()=>{const f=document.querySelector('#gsf-editor-overlay-v220 iframe'),videos=[...f.contentDocument.querySelectorAll('video')].filter(v=>v.getAttribute('src'));return videos.length>0&&videos.every(v=>v.readyState>=1)}")
    if target=='short':
        # "Crea Short" opens the canonical Crea Short page (/share-v156/), never the legacy V343 box.
        page.wait_for_function("()=>{const d=document.querySelector('#gsf-social-overlay-v159 iframe')?.contentDocument;return d?.readyState==='complete'&&!!d.querySelector('#crea413')}")
    assert_gamebar(page)

def tap(locator):
    """Click like a finger, without Playwright's rAF-based stability wait.

    The control must be visible and be the element actually hit at its centre
    (nothing covering it); then a real pointer click is sent at that point.
    """
    locator.wait_for(state='visible')
    hit=None
    for _ in range(50):
        hit=locator.evaluate("e=>{const r=e.getBoundingClientRect();if(!r.width||!r.height)return 'zero-size';const h=e.ownerDocument.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return e.contains(h)?'ok':(h?h.outerHTML.slice(0,120):'nothing')}")
        if hit=='ok':break
        time.sleep(.1)
    assert hit=='ok',f'control is covered or not hittable: {hit}'
    locator.click(force=True,no_wait_after=True)

def assert_gamebar(page):
    probes=page.locator('#gsf-global-gamebar button').evaluate_all("buttons=>buttons.map(b=>{const r=b.getBoundingClientRect();const hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return {page:b.dataset.page,hit:hit?.outerHTML.slice(0,150),ok:r.width>0&&r.height>0&&b.contains(hit)}})")
    assert len(probes)==4 and all(p['ok'] for p in probes),probes

def metrics(page):
    result=page.evaluate("()=>({nodes:document.querySelectorAll('*').length,frames:document.querySelectorAll('iframe').length,surfaces:document.querySelectorAll('#gsf-editor-overlay-v220,#gsf-ai-overlay-v221,#gsf-creator-hub-live-v160,#gsf-short-overlay-v343').length,epoch:window.GSFNavigation?.snapshot().epoch,resources:window.__gsfStability,heap:performance.memory?.usedJSHeapSize})")
    if page.context.browser.browser_type.name=='chromium':
        cdp=page.context.new_cdp_session(page)
        try:
            result['listeners']=cdp.send('Runtime.evaluate',{'expression':"Object.fromEntries(['window','document'].map(name=>[name,Object.fromEntries(Object.entries(getEventListeners(name==='window'?window:document)).map(([event,handlers])=>[event,handlers.length]))]))",'includeCommandLineAPI':True,'returnByValue':True})['result']['value']
        finally:
            cdp.detach()
    return result


def force_fallback_fullscreen(page):
    frame=page.frame_locator('#gsf-editor-overlay-v220 iframe')
    frame.locator('#gameEditorApp').wait_for()
    frame.locator('#gameEditorApp').evaluate("e=>e.requestFullscreen=()=>Promise.reject(new Error('Fullscreen unavailable on this device'))")
    tap(frame.locator('#fullscreenButton'))
    page.wait_for_function("()=>document.documentElement.classList.contains('gsf-mobile-editor-fullscreen')")
    return frame
