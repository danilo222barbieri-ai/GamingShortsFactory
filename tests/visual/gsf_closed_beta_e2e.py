"""Real mobile journey. No mocked requests, injected results or social posts.

Requires a running app with working AI/render services and --media gameplay.mp4.
Use GSF_BROWSER_PROXY for the managed proxy; preserve the browser's trusted CA
profile. Evidence excludes cookies, account data and signed media URLs.
"""
import argparse
import json
import os
import subprocess
import uuid
import time
from pathlib import Path
from urllib.parse import urlsplit

from playwright.sync_api import sync_playwright


def run(base, media, out, engine='chromium', ai_timeout=600, manual=False, ai_engine='auto', viewport=None):
    out.mkdir(parents=True, exist_ok=True)
    evidence = {'checks': {}, 'errors': [], 'base': base}

    def passed(name, details=True):
        evidence['checks'][name] = details
        print(name, json.dumps(details), flush=True)
        (out / 'evidence.json').write_text(json.dumps(evidence, indent=2))

    with sync_playwright() as p:
        options = {'headless': True}
        if engine == 'chromium':
            options.update(executable_path=os.environ.get('GSF_CHROMIUM', '/usr/bin/chromium'), args=['--no-sandbox'])
        if os.environ.get('GSF_BROWSER_PROXY'):
            options['proxy'] = {'server': os.environ['GSF_BROWSER_PROXY']}
        browser = getattr(p, engine).launch(**options)
        device = dict(p.devices['iPhone 13'])
        if viewport:
            width, height = map(int, viewport.split('x'))
            device['viewport'] = {'width': width, 'height': height}
        context = browser.new_context(**device, accept_downloads=True)
        if base.startswith('http://'):
            context.add_cookies([{'name':'gsf_sid','value':'beta'+uuid.uuid4().hex[:24],'url':base+'/'}])
        page = context.new_page()
        page.set_default_timeout(30000)
        page.on('pageerror', lambda error: evidence['errors'].append(str(error)))
        page.on('console', lambda message: evidence['errors'].append(message.text[:300]) if message.type == 'error' else None)
        page.on('response', lambda response: evidence['errors'].append(f'HTTP {response.status} {urlsplit(response.url).path}') if response.status >= 500 else None)
        try:
            page.goto(base, wait_until='domcontentloaded', timeout=60000)
            page.wait_for_function("()=>window.GSFNavigation?.snapshot().surfaces===5", timeout=60000)
            page.wait_for_function("()=>[...document.querySelectorAll('iframe')].some(f=>{try{return f.contentWindow.__GSF_V333_CTA_TOUCH===true}catch(_){return false}})", timeout=60000)
            home = next(f for f in page.frames if f.evaluate('()=>window.__GSF_V333_CTA_TOUCH===true'))
            passed('home')
            home.set_input_files('#pick', str(media))
            page.wait_for_function("()=>[...document.querySelectorAll('iframe')].some(f=>{try{return !!f.contentDocument.querySelector('#circle[data-gsf-uploader-idle=\"true\"]')}catch(_){return false}})", timeout=120000)
            page.wait_for_function("()=>document.querySelector('[data-testid=stApp]')?.getAttribute('data-test-script-state')==='notRunning'", timeout=60000)
            passed('upload')
            # Upload triggers a Streamlit rerun that can replace the Home iframe.
            # Resolve it for each action instead of retaining a detached Frame.
            home=page.frame_locator('iframe[title*="gsf_home_v154"]')
            context.storage_state(path='/tmp/gsf-beta-active-session.json')
            if manual:
                home.locator('.feature[data-action="editor"]').click()
                passed('manual_editor_entry')
            else:
                home.locator('.feature[data-action="ai"]').click()
                ai = page.frame_locator('#gsf-ai-overlay-v221 iframe')
                ai.locator('#createAi').wait_for()
                passed('ai_reachable')
                ai.locator(f'.eng[data-engine=\"{ai_engine}\"]').click()
                ai.locator('#createAi').click()
                started = time.monotonic()
                while not ai.locator('[data-view="moments"]').evaluate("e=>e.classList.contains('is-active')"):
                    if time.monotonic() - started > ai_timeout:
                        raise AssertionError('AI did not produce selectable moments within its deadline: ' + ai.locator('#aiStatus').inner_text())
                    if ai.locator('[data-view="engines"]').evaluate("e=>e.classList.contains('failed')"):
                        raise AssertionError('AI reported failure: ' + ai.locator('#aiStatus').inner_text())
                    page.wait_for_timeout(1000)
                count = ai.locator('.short').count()
                assert count > 0, 'No selectable moments'
                passed('ai_results', {'count': count, 'elapsed_seconds': round(time.monotonic()-started, 1)})
                ai.locator('.short').nth(min(1, count-1)).click()
                passed('moment_selection')
                ai.locator('#editMoment').click()
            editor = page.frame_locator('#gsf-editor-overlay-v220 iframe')
            editor.locator('#gameEditorApp').wait_for()
            page.wait_for_function("()=>document.querySelector('#gsf-editor-overlay-v220 iframe').contentDocument.querySelector('#gameplayVideo').readyState>=1", timeout=60000)
            passed('editor_video')
            editor.locator('#playButton').click()
            page.wait_for_function("()=>document.querySelector('#gsf-editor-overlay-v220 iframe').contentDocument.querySelector('#gameplayVideo').currentTime>0", timeout=15000)
            editor.locator('#playButton').click()
            passed('preview')
            editor.locator('#enterEditorButton').click()
            editor.locator('[data-tool="clip"]').click()
            before = editor.locator('#zoomRange').input_value()
            slider = editor.locator('#zoomRange')
            box = slider.bounding_box()
            assert box and box['width'] > 0, 'Zoom control must be visible'
            slider.click(position={'x':box['width'] * .25, 'y':box['height']/2})
            slider.evaluate("(e,before)=>new Promise((resolve,reject)=>{let n=0;const check=()=>{if(e.value!==before)return resolve();if(n++>50)return reject(new Error('Zoom did not change after a real pointer tap; value='+e.value));setTimeout(check,20)};check()})", before)
            editor.locator('#closeToolSheetButton').click()
            editor.locator('[data-tool="text"]').click()
            editor.locator('[data-caption-mode="Fixed"]').click()
            editor.locator('#captionTextInput').fill('GSF beta verification')
            editor.locator('#closeToolSheetButton').click()
            with page.expect_response('**/creator-hub/project/save-draft') as saved:
                editor.locator('#saveDraftButton').click()
            assert saved.value.ok and saved.value.json().get('ok'), 'Draft save failed'
            edited_state=editor.locator('#gameEditorApp').evaluate('()=>window.GSFGameEditor2026.getState()')
            passed('editor_edit_and_save')
            editor.locator('#continueButton').click()
            page.wait_for_function("()=>GSFNavigation.snapshot().target==='home'")
            passed('editor_done_returns_home')
            page.frame_locator('iframe[title*="gsf_home_v154"]').locator('.feature[data-action="short"]').click()
            share = page.frame_locator('#gsf-social-overlay-v159 iframe')
            share.locator('#crea413').wait_for(timeout=60000)
            passed('crea_short')
            deadline = time.monotonic() + 300
            while not share.locator('#preview').evaluate('v=>v.readyState>=1'):
                # Exercise the browser's cookie handling, including Secure
                # cookies on loopback; APIRequestContext can replace that jar.
                status = page.evaluate("()=>fetch('/job/status',{credentials:'same-origin'}).then(r=>r.json())")
                safe_status = {k:status.get(k) for k in ('render_status','render_progress','download_ready','render_error')}
                print('render_status', json.dumps(safe_status), flush=True)
                if status.get('render_status') in ('failed','error'):
                    raise AssertionError('Render failed: '+str(safe_status))
                if time.monotonic() > deadline:
                    raise AssertionError('Render deadline exceeded: '+str(safe_status)+'; UI: '+share.locator('#coreSub').inner_text())
                page.wait_for_timeout(5000)
            passed('render_completed')
            share.locator('[data-open="save"]').click()
            with page.expect_download() as download:
                share.locator('[data-share="download"]').click()
            exported=out/'beta-export.mp4'
            download.value.save_as(exported)
            probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_streams','-show_format','-of','json',str(exported)],text=True))
            video=next(stream for stream in probe['streams'] if stream['codec_type']=='video')
            assert (video['width'],video['height'])==(1080,1920), video
            assert video['codec_name']=='h264' and video['pix_fmt']=='yuv420p', video
            audio=next(stream for stream in probe['streams'] if stream['codec_type']=='audio')
            assert audio['codec_name']=='aac' and int(audio['sample_rate'])==48000 and audio['channels']==2, audio
            assert float(probe['format']['duration'])>0 and exported.stat().st_size>1024
            passed('export',{'width':video['width'],'height':video['height'],'duration':float(probe['format']['duration']),'bytes':exported.stat().st_size})
            with page.expect_response('**/drafts/save-current') as saved_current:
                share.locator('#draftBtn').click()
            assert saved_current.value.ok and saved_current.value.json().get('ok'), 'Crea Short save draft failed'
            passed('crea_short_save_draft')
            share.locator('#sheet-save [data-close]').click()
            page.screenshot(path=str(out / 'render-ready.png'))
            # Verify the persistent navigation after the entire render journey.
            for target in ('home', 'hub', 'projects', 'live', 'home'):
                page.locator(f'#gsf-global-gamebar [data-page="{target}"]').click()
                expected = 'hub' if target in ('projects', 'live') else target
                page.wait_for_function('target=>GSFNavigation.snapshot().target===target', arg=expected)
            passed('gamebar')
            page.locator('#gsf-global-gamebar [data-page="hub"]').click()
            hub=page.frame_locator('#gsf-creator-hub-live-v160 iframe')
            hub.locator('.view[data-view="dashboard"].active').wait_for()
            passed('creator_hub')
            hub.locator('.counter[data-open="drafts"]').click()
            hub.locator('.view[data-view="projects"].active [data-pane="drafts"].on').wait_for()
            hub.locator('.view.active .pcard.draft').first.wait_for(timeout=30000)
            assert hub.locator('.view.active .pcard.draft').count()>0, 'Saved draft missing in Creator Hub'
            passed('bozze')
            hub.locator('.view.active [data-pane="shorts"]').click()
            hub.locator('.view.active [data-pane="shorts"].on').wait_for()
            if base.startswith('https://'):
                hub.locator('.view.active .pcard.short').first.wait_for(timeout=30000)
            passed('i_miei_shorts')
            page.locator('#gsf-global-header .v343Account').click()
            hub.locator('.view[data-view="settings"].active').wait_for()
            assert hub.locator('.view.active .socialCard,.view.active .profileSocialRefRow').count()>0
            passed('profile_and_social_settings')
            page.locator('#gsf-global-gamebar [data-page="hub"]').click()
            hub.locator('.counter[data-open="drafts"]').click()
            hub.locator('.view.active .pcard.draft [data-act="resume"]').first.click()
            page.wait_for_function("()=>GSFNavigation.snapshot().target==='editor'&&document.querySelector('#gsf-editor-overlay-v220 iframe')?.__gsfEditorInitialized===true",timeout=60000)
            resumed=page.frame_locator('#gsf-editor-overlay-v220 iframe')
            page.wait_for_function("()=>document.querySelector('#gsf-editor-overlay-v220 iframe').contentWindow.GSFGameEditor2026?.getState().captionText==='GSF beta verification'",timeout=30000)
            resumed_state=resumed.locator('#gameEditorApp').evaluate('()=>window.GSFGameEditor2026.getState()')
            assert abs(float(resumed_state['zoom'])-float(edited_state['zoom']))<.01, 'Draft lost the framing edit'
            passed('draft_resume_preserves_edits')
            page.goto(base+'/?gsf_page=editor',wait_until='domcontentloaded')
            page.wait_for_function("()=>window.GSFNavigation?.snapshot().target==='editor'&&document.querySelector('#gsf-editor-overlay-v220 iframe')?.__gsfEditorInitialized===true",timeout=60000)
            page.reload(wait_until='domcontentloaded')
            page.wait_for_function("()=>window.GSFNavigation?.snapshot().target==='editor'&&document.querySelector('#gsf-editor-overlay-v220 iframe')?.__gsfEditorInitialized===true",timeout=60000)
            passed('editor_deep_link_and_refresh')
            page.locator('#gsf-global-gamebar [data-page="hub"]').click()
            page.wait_for_function("()=>GSFNavigation.snapshot().target==='hub'")
            page.go_back()
            page.wait_for_function("()=>GSFNavigation.snapshot().target==='editor'")
            passed('browser_back')
            assert not evidence['errors'], evidence['errors']
            passed('no_critical_runtime_errors')
        finally:
            (out / 'evidence.json').write_text(json.dumps(evidence, indent=2))
            page.screenshot(path=str(out / 'last-screen.png'))
            browser.close()
    return evidence


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--base', required=True)
    parser.add_argument('--media', type=Path, required=True)
    parser.add_argument('--out', type=Path, default=Path('/tmp/gsf-closed-beta'))
    parser.add_argument('--browser', default='chromium')
    parser.add_argument('--ai-timeout', type=int, default=600)
    parser.add_argument('--manual', action='store_true', help='Exercise the existing manual Home Editor path instead of AI selection')
    parser.add_argument('--ai-engine', choices=('auto','action','reaction','best'), default='auto')
    parser.add_argument('--viewport', choices=('375x667','390x844','393x852','430x932'))
    args = parser.parse_args()
    run(args.base.rstrip('/'), args.media, args.out, args.browser, args.ai_timeout, args.manual, args.ai_engine, args.viewport)
