import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class MobileEditorRecipe(unittest.TestCase):
    def setUp(self):
        path = ROOT/'web/mobile_editor_recipe.py'
        self.assertTrue(path.exists(), 'Mobile Editor autosave must reach the final renderer')
        spec = importlib.util.spec_from_file_location('mobile_recipe', path)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root/'media').mkdir()
        (self.root/'media/.direct_upload_ready.json').write_text(json.dumps({'upload_id':'uploadA'}))
        self.snapshot = {'source_key':'uploadA','context':{'clip_start':10,'clip_duration':15},
                         'state':{'inPoint':1,'outPoint':8,'zoom':1.5,'captionMode':'Fixed','captionText':'Beta'}}
        self.save()
        self.recipe = {'kind':'auto','source_path':'game.mp4','start':10,'duration':15}

    def save(self):
        (self.root/'editor_overlay_state.json').write_text(json.dumps(self.snapshot))

    def apply(self, recipe=None):
        return self.module.apply_saved_editor_recipe(
            recipe or self.recipe, self.root,
            lambda state, session: {'zoom':state['zoom'], 'subtitle_text':state['captionText']}, {})

    def test_saved_trim_zoom_and_caption_reach_final_recipe(self):
        result = self.apply()
        self.assertEqual((result['kind'],result['start'],result['duration']),('inline_editor',11,7))
        self.assertEqual(result['render_kwargs'],{'zoom':1.5,'subtitle_text':'Beta'})
        self.assertEqual(self.recipe['start'],10, 'Do not mutate the selected AI candidate')

    def test_applying_same_snapshot_twice_does_not_accumulate_trim(self):
        once = self.apply()
        self.assertEqual(self.apply(once),once)

    def test_old_upload_and_other_candidate_never_inherit_edits(self):
        self.snapshot['source_key']='oldUpload';self.save()
        self.assertEqual(self.apply(),self.recipe)
        self.snapshot['source_key']='uploadA';self.snapshot['context']['clip_start']=20;self.save()
        self.assertEqual(self.apply(),self.recipe)

    def test_empty_snapshot_preserves_existing_render_path(self):
        (self.root/'editor_overlay_state.json').unlink()
        self.assertEqual(self.apply(),self.recipe)


if __name__ == '__main__':
    unittest.main()

class FixedCaptionRender(unittest.TestCase):
    def test_manual_text_reaches_ass_without_transcription(self):
        import ast
        import shutil
        import time
        from unittest.mock import Mock
        tree=ast.parse((ROOT/'app.py').read_text())
        node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_gsf_render_core')
        class AssCaptured(Exception):
            pass
        writer=Mock(side_effect=AssCaptured)
        namespace={'time':time,'os':__import__('os'),'shutil':shutil,
                   '_gsf_normalize_final_fmt':lambda fmt:fmt,
                   '_gsf_session_mkdtemp':lambda prefix:tempfile.mkdtemp(prefix=prefix),
                   '_gsf_render_transcribe_words_lowmem':Mock(side_effect=AssertionError('Fixed caption must not request transcription')),
                   '_gsf_write_render_ass':writer}
        exec(compile(ast.Module(body=[node],type_ignores=[]),'app.py','exec'),namespace)
        with self.assertRaises(AssCaptured):
            namespace['_gsf_render_core']('source.mp4','output.mp4',0,5,
                subtitles_enabled=True,subtitle_mode='Manuale',subtitle_text='GSF beta verification')
        self.assertEqual(writer.call_args.kwargs['fallback_text'],'GSF beta verification')


class HomeEditorHandoff(unittest.TestCase):
    def apply_event(self, event):
        import ast
        from types import SimpleNamespace
        tree=ast.parse((ROOT/'app.py').read_text())
        node=next(n for n in ast.walk(tree) if isinstance(n,ast.If) and ast.unparse(n.test)=='isinstance(_gsf_v154_event, dict)')
        state={'modalita_gsf':'🚀 AUTO TOTALE'}
        namespace={'st':SimpleNamespace(session_state=state), '_gsf_v154_event':event,
                   '_gsf_v154_duration':15,'_gsf_v154_engine':'','video':object()}
        exec(compile(ast.Module(body=[node],type_ignores=[]),'app.py','exec'),namespace)
        return state

    def test_home_editor_cta_prepares_existing_manual_pipeline(self):
        state=self.apply_event({'event':'open_editor','engine':'manual','duration':15})
        self.assertEqual(state['modalita_gsf'],'✋ Manuale')

    def test_selected_ai_moment_keeps_its_existing_pipeline(self):
        state=self.apply_event({'event':'open_editor','engine':'auto','index':1,'start_time':10})
        self.assertEqual(state['modalita_gsf'],'🚀 AUTO TOTALE')


class QueuedRecipe(unittest.TestCase):
    def test_frozen_recipe_is_the_one_passed_to_final_render(self):
        import ast
        from types import SimpleNamespace
        tree=ast.parse((ROOT/'app.py').read_text())
        node=next(n for n in ast.walk(tree) if isinstance(n,ast.If)
                  and ast.unparse(n.test)=='_gsf_v107_pending'
                  and any(isinstance(child,ast.Name) and child.id=='_snap' for child in ast.walk(n)))
        frozen={'kind':'inline_editor','start':11,'duration':7,'render_kwargs':{'zoom':1.5}}
        state={'gsf_v107_render_recipe_snapshot':frozen}
        namespace={'st':SimpleNamespace(session_state=state),'_gsf_v107_pending':True,
                   '_final_recipe':{'kind':'auto','start':10,'duration':15}}
        exec(compile(ast.Module(body=[node],type_ignores=[]),'app.py','exec'),namespace)
        self.assertEqual(namespace['_final_recipe'],frozen)

class ReplacedGameplay(unittest.TestCase):
    def test_new_direct_upload_discards_previous_editor_source_and_recipe(self):
        import ast
        from types import SimpleNamespace
        from unittest.mock import Mock
        tree=ast.parse((ROOT/'app.py').read_text())
        node=next(n for n in tree.body if isinstance(n,ast.If) and ast.unparse(n.test)=='_gsf_direct_source is not None')
        with tempfile.TemporaryDirectory() as directory:
            root=Path(directory);source=root/'new.mp4';source.write_bytes(b'video')
            (root/'editor2027_current.txt').write_text(str(root/'old.mp4'))
            (root/'media').mkdir()
            (root/'media/gaming_short_finale_share.mp4').write_bytes(b'old export')
            (root/'render_job.json').write_text('{"status":"running"}')
            state={'gsf_source_path':str(root/'old.mp4'),'gsf_editor_source_path':str(root/'old.mp4'),
                   'gsf_final_recipe':{'source_path':'old.mp4'},'gsf_v107_render_recipe_snapshot':{'old':True}}
            reset=Mock(side_effect=lambda:state.pop('gsf_final_recipe',None))
            namespace={'st':SimpleNamespace(session_state=state),'_gsf_direct_source':source,
                       '_gsf_direct_name':'new.mp4','_GSFRecoveredUpload':lambda *args:object(),
                       '_gsf_v75_reset_engine_workflow':reset,'GSF_SESSION_ROOT':root}
            exec(compile(ast.Module(body=[node],type_ignores=[]),'app.py','exec'),namespace)
            self.assertNotIn('gsf_editor_source_path',state)
            self.assertNotIn('gsf_final_recipe',state)
            self.assertNotIn('gsf_v107_render_recipe_snapshot',state)
            self.assertFalse((root/'editor2027_current.txt').exists())
            self.assertFalse((root/'render_job.json').exists())
            self.assertFalse((root/'media/gaming_short_finale_share.mp4').exists())
            self.assertEqual(state['gsf_source_path'],str(source))
