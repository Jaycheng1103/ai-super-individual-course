import argparse
import io
import json
from pathlib import Path
import sys
import tarfile
import tempfile
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import course
import connections


class SetupSafetyTests(unittest.TestCase):
    def test_rejects_course_as_workspace(self):
        with self.assertRaises(ValueError):
            course.workspace(str(course.ROOT), existing=False)
        with self.assertRaises(ValueError):
            course.workspace(str(course.ROOT / 'student'), existing=False)

    def test_refuses_existing_directory_without_modification(self):
        with tempfile.TemporaryDirectory() as d:
            target = Path(d) / 'existing'
            target.mkdir()
            (target / 'notes.md').write_text('my notes')
            with self.assertRaises(ValueError):
                course.init(argparse.Namespace(workspace=str(target), cache=None))
            self.assertEqual((target / 'notes.md').read_text(), 'my notes')

    def test_archive_traversal_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            archive = root / 'bad.tar.gz'
            with tarfile.open(archive, 'w:gz') as t:
                member = tarfile.TarInfo('package/../../escape')
                member.size = 1
                t.addfile(member, io.BytesIO(b'x'))
            out = root / 'out'; out.mkdir()
            with self.assertRaises(ValueError):
                course.safe_extract(archive, out)
            self.assertFalse((root / 'escape').exists())

    def test_archive_links_not_followed(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); archive = root / 'links.tar.gz'
            with tarfile.open(archive, 'w:gz') as t:
                m = tarfile.TarInfo('package/unsafe'); m.type = tarfile.SYMTYPE; m.linkname = '/tmp'; t.addfile(m)
            out = root / 'out'; out.mkdir()
            course.safe_extract(archive, out)
            self.assertFalse((out / 'unsafe').exists())

    def test_hash_mismatch_stops_before_extraction(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); cache = root / 'cache'; cache.mkdir()
            (cache / 'fake__source.tar.gz').write_bytes(b'not trusted')
            lock = root / 'sources.json'
            lock.write_text(json.dumps({'sources': {'demo': {'repo': 'fake/source', 'archive_sha256': '0' * 64}}}))
            with patch.object(course, 'LOCK', lock), self.assertRaises(ValueError):
                course.fetch('demo', root, cache)
            self.assertFalse((root / 'demo').exists())

    def test_conflicting_skill_preserves_all_existing_files(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); ws = root / 'workspace'; (ws / '.course').mkdir(parents=True)
            course.write_json(ws / '.course/progress.json', {'steps': {}})
            course.write_json(ws / '.course/installed.json', {})
            dst = ws / '.agents/skills/demo'; dst.mkdir(parents=True)
            (dst / 'SKILL.md').write_text('customized')
            src = root / 'source'; src.mkdir(); (src / 'SKILL.md').write_text('new version')
            info = {'skills': [{'name': 'demo', 'path': '.'}], 'commit': 'a' * 40}
            lock = root / 'lock.json'; lock.write_text(json.dumps({'sources': {'demo': info}}))
            with patch.object(course, 'LOCK', lock), patch.object(course, 'fetch', return_value=(src, info)):
                with self.assertRaises(ValueError):
                    course.install(argparse.Namespace(workspace=str(ws), component='demo', agent='codex', cache=None))
            self.assertEqual((dst / 'SKILL.md').read_text(), 'customized')

    def test_agent_reach_keeps_original_and_rejects_customized_overlay(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d); ws = self.start_workspace(root)
            course.write_json(ws / '.course/installed.json', {})
            source = root / 'source'; skill = source / 'agent_reach/skill'
            (skill / 'references').mkdir(parents=True)
            (skill / 'SKILL.md').write_text('upstream original')
            (skill / 'references/web.md').write_text('reference')
            (source / 'LICENSE').write_text('MIT fixture')
            info = json.loads(course.LOCK.read_text())['sources']['agent-reach']
            with patch.object(course, 'fetch', return_value=(source, info)):
                for agent, folder in course.AGENTS.items():
                    args = argparse.Namespace(workspace=str(ws), component='agent-reach', agent=agent, cache=None)
                    course.install(args)
                    course.install(args)
                    target = ws / folder / 'agent-reach'
                    self.assertEqual((target / 'SKILL.upstream.md').read_text(), 'upstream original')
                    self.assertEqual((target / 'references/web.md').read_text(), 'reference')
                    self.assertTrue((target / 'COURSE_SETUP.md').is_file())
                    self.assertIn('Tavily', (target / 'SKILL.md').read_text())
                    (target / 'SKILL.md').write_text('student customization')
                    with self.assertRaises(ValueError):
                        course.install(args)
                    self.assertEqual((target / 'SKILL.md').read_text(), 'student customization')
            self.assertEqual((skill / 'SKILL.md').read_text(), 'upstream original')
            vendor = ws / '.course/sources' / ('agent-reach-' + info['commit'][:12])
            self.assertEqual((vendor / 'LICENSE').read_text(), 'MIT fixture')

    def test_api_without_usage_permission_never_sends_request(self):
        with patch.object(connections, 'request_json') as send, self.assertRaises(ValueError):
            connections.check(Path('/not-used'), 'tavily', False)
        send.assert_not_called()

    def test_elevenlabs_without_upload_permission_never_sends_request(self):
        with tempfile.TemporaryDirectory() as d:
            ws = Path(d); (ws / '.course/secrets').mkdir(parents=True)
            (ws / '.course/secrets/elevenlabs.key').write_text('dummy-value')
            with patch.object(connections, 'request_json') as send, self.assertRaises(ValueError):
                connections.check(ws, 'elevenlabs', True, audio=None, allow_upload=False)
            send.assert_not_called()

    def test_mocked_tavily_records_sources_without_key(self):
        with tempfile.TemporaryDirectory() as d:
            ws = Path(d); (ws / '.course/secrets').mkdir(parents=True)
            (ws / '.course/secrets/tavily.key').write_text('dummy-private-value')
            with patch.object(connections, 'request_json', return_value={'results': [{'url': 'https://docs.tavily.com/'}]}):
                result = connections.check(ws, 'tavily', True)
            self.assertEqual(result['source_count'], 1)
            self.assertNotIn('dummy-private-value', (ws / '.course/checks/tavily.json').read_text())

    def start_workspace(self, root):
        ws = Path(root) / 'student'
        course.start(argparse.Namespace(workspace=str(ws)))
        return ws

    def status(self, ws):
        return course.progress(argparse.Namespace(workspace=str(ws), command='status'))

    def test_progress_can_resume_before_ais_install(self):
        with tempfile.TemporaryDirectory() as d:
            ws = self.start_workspace(d)
            out = course.progress(argparse.Namespace(workspace=str(ws), command='mark', step='environment', status='passed', evidence='test file read back'))
            self.assertEqual(out['next_step'], 'connectors')
            self.assertEqual(out['steps']['workspace']['status'], 'pending')
            self.assertFalse(out['core_complete'])

    def test_checkpoint_remembers_question_and_file_without_marking_passed(self):
        with tempfile.TemporaryDirectory() as d:
            ws = self.start_workspace(d)
            (ws / '.course/interview.md').write_text('confirmed answers')
            course.progress(argparse.Namespace(workspace=str(ws), command='checkpoint', step='background',
                current_action='answered identity', next_action='ask goal', question='question 3',
                blocker=None, artifact=['.course/interview.md']))
            result = self.status(ws)['steps']['background']
            self.assertEqual(result['status'], 'in_progress')
            self.assertEqual(result['next_question'], 'question 3')
            self.assertEqual(result['artifacts'], ['.course/interview.md'])
            course.progress(argparse.Namespace(workspace=str(ws), command='mark', step='background', status='passed', evidence='verified background'))
            self.assertEqual(self.status(ws)['steps']['background']['artifacts'], ['.course/interview.md'])

    def test_checkpoint_rejects_missing_or_external_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            ws = self.start_workspace(d)
            (Path(d) / 'outside.md').write_text('outside')
            for artifact in ['missing.md', '../outside.md']:
                with self.assertRaises(ValueError):
                    course.progress(argparse.Namespace(workspace=str(ws), command='checkpoint', step='environment',
                        current_action='checking', next_action='continue', question=None, blocker=None, artifact=[artifact]))
            self.assertEqual(self.status(ws)['steps']['environment']['status'], 'pending')

    def test_v1_progress_is_backed_up_and_requires_review_without_losing_evidence(self):
        with tempfile.TemporaryDirectory() as d:
            ws = Path(d)
            old = {'schema': 1, 'steps': {'00': {'status': 'passed', 'evidence': 'old evidence'},
                                       '02': {'status': 'passed', 'evidence': 'existing interview'}}}
            course.write_json(ws / '.course/progress.json', old)
            result = self.status(ws)
            self.assertEqual(result['steps']['background']['status'], 'needs_review')
            self.assertEqual(result['steps']['background']['evidence'], 'existing interview')
            self.assertEqual(result['steps']['content']['status'], 'pending')
            self.assertEqual(json.loads((ws / '.course/progress.v1.backup.json').read_text()), old)
            self.assertEqual(self.status(ws), result)

    def test_prepared_init_preserves_early_notes_and_progress(self):
        with tempfile.TemporaryDirectory() as d:
            ws = self.start_workspace(d)
            (ws / '.course/connections.md').write_text('calendar verified')
            course.progress(argparse.Namespace(workspace=str(ws), command='mark', step='environment', status='passed', evidence='environment verified'))
            def fake_fetch(source_id, temp, cache):
                src = temp / 'ais-os'; src.mkdir()
                for name in ('AGENTS.md', 'CLAUDE.md', 'aios-intake.md'):
                    (src / name).write_text('upstream template')
                return src, {'commit': 'a' * 40}
            with patch.object(course, 'fetch', side_effect=fake_fetch):
                course.init(argparse.Namespace(workspace=str(ws), cache=None))
            self.assertEqual((ws / '.course/connections.md').read_text(), 'calendar verified')
            self.assertEqual(self.status(ws)['steps']['environment']['status'], 'passed')
            self.assertTrue((ws / 'AGENTS.md').exists())
            with self.assertRaises(ValueError):
                course.init(argparse.Namespace(workspace=str(ws), cache=None))

    def test_prepared_init_refuses_unexpected_personal_files(self):
        with tempfile.TemporaryDirectory() as d:
            ws = self.start_workspace(d)
            (ws / 'notes.md').write_text('personal')
            with patch.object(course, 'fetch') as download, self.assertRaises(ValueError):
                course.init(argparse.Namespace(workspace=str(ws), cache=None))
            download.assert_not_called()
            self.assertEqual((ws / 'notes.md').read_text(), 'personal')

    def test_in_place_installs_into_existing_project_and_preserves_unrelated_files(self):
        with tempfile.TemporaryDirectory() as d:
            ws = Path(d) / 'student'; ws.mkdir()
            repo = ws / 'course-material'; repo.mkdir()
            (repo / 'README.md').write_text('course only')
            (ws / 'my-notes.txt').write_text('keep me')
            def fake_fetch(source_id, temp, cache):
                src = temp / 'ais-os'; src.mkdir()
                for name in ('AGENTS.md', 'CLAUDE.md', 'aios-intake.md'):
                    (src / name).write_text('upstream template')
                return src, {'commit': 'a' * 40}
            with patch.object(course, 'ROOT', repo), patch.object(course, 'fetch', side_effect=fake_fetch):
                course.init(argparse.Namespace(workspace=str(ws), cache=None, in_place=True))
                self.assertEqual(self.status(ws)['next_step'], 'environment')
            self.assertEqual((ws / 'my-notes.txt').read_text(), 'keep me')
            self.assertEqual((repo / 'README.md').read_text(), 'course only')
            self.assertTrue((ws / 'AGENTS.md').is_file())
            self.assertFalse((repo / '.course').exists())

    def test_in_place_conflict_prevents_all_installation_writes(self):
        with tempfile.TemporaryDirectory() as d:
            ws = Path(d) / 'student'; ws.mkdir()
            (ws / 'AGENTS.md').write_text('my rules')
            before = course.fingerprints(ws)
            def fake_fetch(source_id, temp, cache):
                src = temp / 'ais-os'; src.mkdir()
                for name in ('AGENTS.md', 'CLAUDE.md', 'aios-intake.md'):
                    (src / name).write_text('upstream template')
                return src, {'commit': 'a' * 40}
            with patch.object(course, 'fetch', side_effect=fake_fetch), self.assertRaises(ValueError):
                course.init(argparse.Namespace(workspace=str(ws), cache=None, in_place=True))
            self.assertEqual(course.fingerprints(ws), before)
            self.assertFalse((ws / '.course').exists())

    def test_in_place_still_rejects_course_repo_as_personal_workspace(self):
        with self.assertRaises(ValueError):
            course.init(argparse.Namespace(workspace=str(course.ROOT), cache=None, in_place=True))

    def test_unknown_progress_schema_is_preserved(self):
        with tempfile.TemporaryDirectory() as d:
            ws = self.start_workspace(d)
            path = ws / '.course/progress.json'
            data = json.loads(path.read_text())
            data['schema'] = 99
            course.write_json(path, data)
            before = path.read_bytes()
            with self.assertRaises(ValueError):
                self.status(ws)
            self.assertEqual(path.read_bytes(), before)

    def test_skipped_core_stage_is_not_full_completion(self):
        with tempfile.TemporaryDirectory() as d:
            ws = self.start_workspace(d)
            path = ws / '.course/progress.json'
            data = json.loads(path.read_text())
            for record in data['steps'].values():
                record['status'] = 'passed'
            data['steps']['connectors']['status'] = 'skipped'
            course.write_json(path, data)
            result = self.status(ws)
            self.assertIsNone(result['next_step'])
            self.assertFalse(result['core_complete'])
            self.assertEqual(result['not_passed'], ['connectors'])


if __name__ == '__main__':
    unittest.main()
