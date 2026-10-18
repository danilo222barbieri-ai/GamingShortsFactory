import os
import json
import unittest
from visual.gsf_navigation_stress import browser_page,navigate,force_fallback_fullscreen,assert_gamebar,metrics,tap

@unittest.skipUnless(os.environ.get('GSF_BASE_URL'),'requires running GSF_BASE_URL')
class MobileResumeStability(unittest.TestCase):
    def test_editor_cancels_incomplete_gesture_on_resume(self):
        with browser_page() as (page,errors,ctx):
            navigate(page,'editor')
            frame=force_fallback_fullscreen(page)
            frame.locator('#previewStage').dispatch_event('pointerdown',{'pointerId':77,'pointerType':'touch','clientX':130,'clientY':180,'bubbles':True})
            frame.locator('#previewStage').evaluate("e=>window.dispatchEvent(new PageTransitionEvent('pagehide',{persisted:true}))")
            frame.locator('#previewStage').evaluate("e=>window.dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true}))")
            self.assertFalse(frame.locator('#previewStage').evaluate("e=>e.classList.contains('is-gesturing')"))
            self.assertFalse(frame.locator('#gameEditorApp').evaluate("e=>e.classList.contains('is-expanded')"))
            assert_gamebar(page)
            self.assertFalse(errors,errors)

    def test_ten_resume_cycles_preserve_editor_and_navigation(self):
        with browser_page() as (page,errors,ctx):
            cdp=ctx.new_cdp_session(page) if os.environ.get('GSF_BROWSER','chromium')=='chromium' else None
            for target in ('hub','ai','editor','short','home'):navigate(page,target)
            baseline=metrics(page)
            for cycle in range(10):
                target=('editor','ai','short','home','hub')[cycle%5]
                navigate(page,target)
                if target=='editor':
                    frame=page.frame_locator('#gsf-editor-overlay-v220 iframe')
                    frame.locator('#gameEditorApp').wait_for()
                    frame.locator('#gameEditorApp').evaluate("()=>window.GSFGameEditor2026.commitEditorState({zoom:1.7})")
                # Backgrounding does not navigate away. Real pagehide/pageshow and BFCache
                # are covered by the dedicated history and gesture regressions.
                page.evaluate("()=>{Object.defineProperty(document,'hidden',{configurable:true,value:true});Object.defineProperty(document,'visibilityState',{configurable:true,value:'hidden'});document.dispatchEvent(new Event('visibilitychange'));window.dispatchEvent(new Event('blur'));}")
                if cdp:cdp.send('Page.setWebLifecycleState',{'state':'frozen'})
                seconds=float(os.environ['GSF_BACKGROUND_SECONDS']) if 'GSF_BACKGROUND_SECONDS' in os.environ else (3,30,60,3,3,3,3,3,3,3)[cycle]
                page.wait_for_timeout(seconds*1000)
                if cdp:cdp.send('Page.setWebLifecycleState',{'state':'active'})
                page.evaluate("()=>{delete document.hidden;delete document.visibilityState;window.dispatchEvent(new Event('focus'));document.dispatchEvent(new Event('visibilitychange'));}")
                if target=='editor':
                    self.assertAlmostEqual(frame.locator('#gameEditorApp').evaluate("()=>window.GSFGameEditor2026.getState().zoom"),1.7)
                    force_fallback_fullscreen(page)
                    tap(frame.locator('[data-tool="look"]'))
                    tap(frame.locator('#closeToolSheetButton'))
                    tap(frame.locator('#fullscreenButton'))
                    page.wait_for_function("()=>!document.documentElement.classList.contains('gsf-mobile-editor-fullscreen')")
                assert_gamebar(page)
                navigate(page,'home');navigate(page,'hub')
                print('RESUME',json.dumps({'cycle':cycle,'surface':target,'seconds':seconds,'cdp_freeze':bool(cdp),'simulated_visibility':True}),flush=True)
                self.assertFalse(errors,errors)

            end=metrics(page)
            print('RESUME RESOURCES',json.dumps({'before':baseline,'after':end}),flush=True)
            if 'listeners' in baseline:self.assertEqual(end['listeners'],baseline['listeners'])
            for kind in ('mutation','resize'):
                self.assertLessEqual(end['resources'][kind],baseline['resources'][kind])
            self.assertEqual(end['frames'],baseline['frames'])
            self.assertEqual(end['surfaces'],baseline['surfaces'])
            self.assertLessEqual(end['nodes'],baseline['nodes']+10)
            # Verify the actual Home component survived; Game Bar alone could
            # remain interactive while a disconnected Streamlit tree vanished.
            navigate(page,'home')
            point=page.evaluate("()=>{const f=[...document.querySelectorAll('iframe')].find(f=>{try{return f.contentWindow.__GSF_V333_CTA_TOUCH===true}catch(_){return false}});if(!f)throw new Error('Home component missing after resume');const r=f.getBoundingClientRect(),b=f.contentDocument.querySelector('.feature[data-action=ai]').getBoundingClientRect();return {x:r.x+(b.x+b.width/2)*r.width/f.clientWidth,y:r.y+(b.y+b.height/2)*r.height/f.clientHeight}}")
            page.mouse.click(point['x'],point['y'])
            page.wait_for_function("()=>window.GSFNavigation.snapshot().target==='ai'")
            assert_gamebar(page)
            self.assertFalse(errors,errors)

    def test_browser_history_restore_remains_interactive(self):
        with browser_page() as (page,errors,ctx):
            page.add_init_script("window.addEventListener('pageshow',e=>sessionStorage.setItem('gsf-test-restored',String(e.persisted)))")
            page.evaluate("window.addEventListener('pageshow',e=>sessionStorage.setItem('gsf-test-restored',String(e.persisted)))")
            navigate(page,'editor')
            frame=page.frame_locator('#gsf-editor-overlay-v220 iframe')
            frame.locator('#gameEditorApp').evaluate("()=>window.GSFGameEditor2026.commitEditorState({zoom:1.7})")
            if os.environ.get('GSF_TEST_MEDIA')=='1':
                page.wait_for_function("()=>document.querySelector('#gsf-editor-overlay-v220 iframe').contentDocument.querySelector('#gameplayVideo').readyState>=1")
            page.goto(os.environ['GSF_BASE_URL'].rstrip('/')+'/healthz',wait_until='load')
            # Use the native Back operation: a BFCache hit emits pageshow, not
            # another DOMContentLoaded, and may reuse the cached child target.
            page.evaluate('()=>history.back()')
            page.wait_for_function("()=>location.pathname==='/'&&!!window.GSFNavigation",timeout=120000)
            page.wait_for_selector('#gsf-global-gamebar',timeout=120000)
            page.wait_for_function("()=>window.GSFNavigation?.snapshot().surfaces===5",timeout=120000)
            restored=page.evaluate("sessionStorage.getItem('gsf-test-restored')")
            print('HISTORY RESTORE',json.dumps({'persisted':restored=='true','engine':os.environ.get('GSF_BROWSER','chromium')}),flush=True)
            print('RESTORED FRAME',page.evaluate("()=>{const f=document.querySelector('#gsf-editor-overlay-v220 iframe');return {src:f?.src,url:f?.contentWindow?.location.href,ready:f?.contentDocument?.readyState,hasEditor:!!f?.contentDocument?.querySelector('#gameEditorApp'),zoom:f?.contentWindow?.GSFGameEditor2026?.getState().zoom}}"),flush=True)
            if restored=='true':
                page.wait_for_function("()=>!!document.querySelector('#gsf-editor-overlay-v220 iframe')?.contentWindow?.GSFGameEditor2026")
                self.assertAlmostEqual(page.evaluate("()=>document.querySelector('#gsf-editor-overlay-v220 iframe').contentWindow.GSFGameEditor2026.getState().zoom"),1.7)
                # Probe actual pointer interaction inside the restored iframe,
                # independently of Playwright's cached frame-target mapping.
                page.evaluate("()=>{const w=document.querySelector('#gsf-editor-overlay-v220 iframe').contentWindow;w.document.querySelector('#gameEditorApp').requestFullscreen=()=>Promise.reject(new Error('fallback test'))}")
                for expanded in (True,False):
                    # A real pointer must wait for transient parent toasts as
                    # well as the restored child control to stop covering it.
                    point=page.wait_for_function("()=>{const f=document.querySelector('#gsf-editor-overlay-v220 iframe'),r=f.getBoundingClientRect(),d=f.contentDocument,b=d.querySelector('#fullscreenButton'),v=b.getBoundingClientRect(),cx=v.x+v.width/2,cy=v.y+v.height/2,x=r.x+cx*r.width/f.clientWidth,y=r.y+cy*r.height/f.clientHeight;return v.width>0&&v.height>0&&document.elementFromPoint(x,y)===f&&b.contains(d.elementFromPoint(cx,cy))?{x,y}:false}").json_value()
                    page.mouse.click(point['x'],point['y'])
                    page.wait_for_function("value=>document.documentElement.classList.contains('gsf-mobile-editor-fullscreen')===value",arg=expanded)
            for target in ('home','hub','editor','short','home'):navigate(page,target)
            page.wait_for_function("()=>document.querySelector('[data-testid=stApp]')?.getAttribute('data-test-connection-state')==='CONNECTED'",timeout=30000)
            assert_gamebar(page)
            self.assertFalse(errors,errors)
