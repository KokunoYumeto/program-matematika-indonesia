"""Small independent negative/isolation checks; never renders native readers."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('d100_test_runner', Path(__file__).with_name('replay-d100-native-html-v1.py'))
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class IsolationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='d100-runtime-test-')
        self.root = Path(self.temp.name).resolve()
        self.native = self.root / 'native'
        self.stage = self.root / 'stage'
        self.native.mkdir()
        self.stage.mkdir()

    def tearDown(self):
        self.temp.cleanup()

    def row(self):
        (self.native / 'input.txt').write_bytes(b'exact original source')
        return {'path': 'input.txt', **runner.fact(self.native / 'input.txt')}

    def test_exact_copy(self):
        row = self.row()
        runner.copy_inputs(self.native, self.stage, [row])
        self.assertEqual(runner.fact(self.stage / 'input.txt'), runner.fact(self.native / 'input.txt'))

    def test_changed_source_refused_before_copy(self):
        row = self.row()
        (self.native / 'input.txt').write_bytes(b'changed source')
        with self.assertRaisesRegex(ValueError, 'identity drift'):
            runner.copy_inputs(self.native, self.stage, [row])
        self.assertFalse((self.stage / 'input.txt').exists())

    def test_copy_corruption_refused(self):
        row = self.row()
        with patch.object(runner.common.shutil, 'copyfile', side_effect=lambda src, dst: dst.write_bytes(b'wrong')):
            with self.assertRaisesRegex(ValueError, 'copy differs'):
                runner.copy_inputs(self.native, self.stage, [row])

    def test_native_change_during_copy_refused(self):
        row = self.row()
        def corrupt_source(src, dst):
            dst.write_bytes(src.read_bytes())
            src.write_bytes(b'concurrent change')
        with patch.object(runner.common.shutil, 'copyfile', side_effect=corrupt_source):
            with self.assertRaisesRegex(ValueError, 'Source changed'):
                runner.copy_inputs(self.native, self.stage, [row])

    def test_paths_escape_refused(self):
        for relative in ('../outside', '/outside', 'C:/outside', 'source/../../outside', '\\outside', '//host/share'):
            with self.subTest(relative=relative), self.assertRaises(ValueError):
                runner.exact_path(self.stage, relative)

    def test_missing_source_refused(self):
        row = self.row()
        (self.native / 'input.txt').unlink()
        with self.assertRaises(FileNotFoundError):
            runner.copy_inputs(self.native, self.stage, [row])

    def test_output_outside_integration_refused(self):
        with self.assertRaisesRegex(ValueError, 'integration work area'):
            runner.replay('bgk', self.native, self.stage / 'not-owned')

    def test_existing_output_preserved(self):
        work = self.root / 'work'
        work.mkdir()
        (work / 'sentinel.txt').write_bytes(b'keep me')
        with patch.object(runner, 'ROOT', self.root):
            with self.assertRaisesRegex(ValueError, 'Existing replay'):
                runner.replay('bgk', self.native, work)
        self.assertEqual((work / 'sentinel.txt').read_bytes(), b'keep me')

    def test_tex_and_non_html_commands_never_launch(self):
        for command in (['lualatex', '--to=html5'], ['pandoc', '--to=pdf'],
                        ['pandoc', '--to=html5', '--pdf-engine=lualatex']):
            with self.subTest(command=command), patch.object(runner.subprocess, 'run') as launched:
                with self.assertRaises(ValueError):
                    runner.run_html(command, self.stage, '0')
                launched.assert_not_called()

    def test_warnings_fail(self):
        process = types.SimpleNamespace(returncode=0, stdout=b'', stderr=b'warning')
        with patch.object(runner.subprocess, 'run', return_value=process):
            with self.assertRaisesRegex(ValueError, 'zero-warning'):
                runner.run_html(['pandoc', '--to=html5'], self.stage, '0')
        self.assertEqual((self.stage / 'pandoc-html.log').read_bytes(), b'warning')

    def test_failed_process_fails(self):
        process = types.SimpleNamespace(returncode=1, stdout=b'', stderr=b'failure')
        with patch.object(runner.subprocess, 'run', return_value=process):
            with self.assertRaisesRegex(ValueError, 'build failed'):
                runner.run_html(['pandoc', '--to=html5'], self.stage, '0')

    def test_module_cache_restored(self):
        scripts = self.stage / 'scripts'
        scripts.mkdir()
        builder = scripts / 'build_bgk_reader_versioned.py'
        builder.write_text('from pathlib import Path\nLANE = Path(__file__).resolve().parents[1]\n', encoding='utf-8')
        config = {**runner.LANES['bgk'], 'builder_sha256': runner.fact(builder)['sha256']}
        sentinel = types.ModuleType('old_native_module')
        original_path = list(sys.path)
        with patch.dict(sys.modules, {'build_bgk_reader_versioned': sentinel}), patch.dict(runner.LANES, {'bgk': config}):
            with runner.isolated_builder(self.stage, 'bgk') as loaded:
                self.assertEqual(loaded.LANE, self.stage)
                self.assertIsNot(loaded, sentinel)
            self.assertIs(sys.modules['build_bgk_reader_versioned'], sentinel)
        self.assertEqual(sys.path, original_path)


if __name__ == '__main__':
    unittest.main()
