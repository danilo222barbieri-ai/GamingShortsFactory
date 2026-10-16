import os
import json
import unittest
from visual.gsf_navigation_stress import browser_page,navigate,force_fallback_fullscreen,assert_gamebar,metrics

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
                # Synthetic BFCache lifecycle plus real CDP renderer suspension where supported.
                page.evaluate("()=>{Object.defineProperty(document,'hidden',{configurable:true,value:true});Object.defineProperty(document,'visibilityState',{configurable:true,value:'hidden'});document.dispatchEvent(new Event('visibilitychange'));window.dispatchEvent(new Event('blur'));window.dispatchEvent(new PageTransitionEvent('pagehide',{persisted:true}));}")
                if cdp:cdp.send('Page.setWebLifecycleState',{'state':'frozen'})
                seconds=float(os.environ['GSF_BACKGROUND_SECONDS']) if 'GSF_BACKGROUND_SECONDS' in os.environ else (3,30,60,3,3,3,3,3,3,3)[cycle]
                page.wait_for_timeout(seconds*1000)
                if cdp:cdp.send('Page.setWebLifecycleState',{'state':'active'})
                page.evaluate("()=>{delete document.hidden;delete document.visibilityState;window.dispatchEvent(new PageTransitionEvent('pageshow',{persisted:true}));window.dispatchEvent(new Event('focus'));document.dispatchEvent(new Event('visibilitychange'));}")
                if target=='editor':
                    self.assertAlmostEqual(frame.locator('#gameEditorApp').evaluate("()=>window.GSFGameEditor2026.getState().zoom"),1.7)
                    force_fallback_fullscreen(page)
                    frame.locator('[data-tool="look"]').click()
                    frame.locator('#closeToolSheetButton').click()
                    frame.locator('#fullscreenButton').click()
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
            page.go_back(wait_until='domcontentloaded')
            page.wait_for_selector('#gsf-global-gamebar',timeout=120000)
            page.wait_for_function("()=>window.GSFNavigation?.snapshot().surfaces===5",timeout=120000)
            restored=page.evaluate("sessionStorage.getItem('gsf-test-restored')")
            print('HISTORY RESTORE',json.dumps({'persisted':restored=='true','engine':os.environ.get('GSF_BROWSER','chromium')}),flush=True)
            if restored=='true':
                self.assertAlmostEqual(page.frame_locator('#gsf-editor-overlay-v220 iframe').locator('#gameEditorApp').evaluate("()=>window.GSFGameEditor2026.getState().zoom"),1.7)
            for target in ('home','hub','editor','short','home'):navigate(page,target)
            assert_gamebar(page)
            self.assertFalse(errors,errors)
