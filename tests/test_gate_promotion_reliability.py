"""Promotion races are tested against real temporary Git repositories."""
import os
import subprocess
import unittest
import test_gate_promotion_diff as existing


class PromotionReliability(existing.PromotionDiffTest):
    def runtime_commit(self):
        (self.work / 'app.py').write_text('version = 2\n')
        before = existing.git(self.work, 'rev-parse', 'HEAD')
        return before, self.commit('fix: tested runtime')

    def test_coordination_arriving_during_gate_does_not_drop_release(self):
        before, tested = self.runtime_commit()
        (self.work / '.gsf').mkdir()
        (self.work / '.gsf' / 'claims.json').write_text('{"new_owner":true}\n')
        self.commit('coord: another chat claimed files')
        self.run_step(before, tested)
        self.assertEqual(self.marker('frontend-deploy.txt'), tested)
        self.assertIn('new_owner', existing.git(self.work, 'show', 'origin/main:.gsf/claims.json'))

    def test_runtime_arriving_during_gate_is_never_promoted_untested(self):
        before, tested = self.runtime_commit()
        (self.work / 'app.py').write_text('version = 3\n')
        self.commit('fix: newer untested runtime')
        self.run_step(before, tested)
        self.assertEqual(self.marker('frontend-deploy.txt'), self.promoted)

    def test_coordination_deleted_file_is_preserved(self):
        (self.work / 'PROJECT_STATUS.md').write_text('old note\n')
        self.commit('coord: note')
        before, tested = self.runtime_commit()
        (self.work / 'PROJECT_STATUS.md').unlink()
        self.commit('coord: remove obsolete note')
        self.run_step(before, tested)
        self.assertEqual(self.marker('frontend-deploy.txt'), tested)
        result = subprocess.run(['git', 'cat-file', '-e', 'origin/main:PROJECT_STATUS.md'], cwd=self.work, capture_output=True)
        self.assertNotEqual(result.returncode, 0)

    def test_manual_marker_does_not_lose_runtime_before_test_only_push(self):
        (self.work / '.railway' / 'frontend-deploy.txt').write_text('deploy-app-icon-manual\n')
        self.commit('deploy: manual non-SHA marker')
        _, unpromoted = self.runtime_commit()
        (self.work / 'test_note.py').write_text('# gate diagnostic fix\n')
        tested = self.commit('test: repair gate after failed runtime gate')
        self.run_step(unpromoted, tested)
        self.assertEqual(self.marker('frontend-deploy.txt'), tested)
        self.assertEqual(self.marker('worker-deploy.txt'), self.promoted)

    def test_deleted_marker_recovers_last_promoted_commit(self):
        (self.work / '.railway' / 'frontend-deploy.txt').unlink()
        self.commit('deploy: marker deleted')
        _, unpromoted = self.runtime_commit()
        (self.work / 'test_note.py').write_text('# diagnostic fix\n')
        tested = self.commit('test: follow-up')
        self.run_step(unpromoted, tested)
        self.assertEqual(self.marker('frontend-deploy.txt'), tested)

    def test_no_marker_history_uses_empty_tree_not_previous_push(self):
        head = existing.git(self.work, 'rev-parse', 'HEAD')
        prefix = existing.promotion_script().split('\nfrontend_base=', 1)[0]
        out = subprocess.run(['bash', '-c', prefix + '\nbase_for .railway/never-existed.txt\n'],
            cwd=self.work, env=dict(os.environ, BEFORE_SHA=head, TESTED_SHA=head), capture_output=True, text=True)
        self.assertEqual(out.returncode, 0, out.stdout + out.stderr)
        self.assertEqual(out.stdout.strip().splitlines()[-1], '4b825dc642cb6eb9a060e54bf8d69288fbee4904')


if __name__ == '__main__':
    unittest.main()
