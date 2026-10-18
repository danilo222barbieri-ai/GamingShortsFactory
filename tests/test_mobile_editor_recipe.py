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
