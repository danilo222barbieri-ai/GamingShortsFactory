"""Promotion races are tested against real temporary Git repositories."""
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


if __name__ == '__main__':
    unittest.main()
