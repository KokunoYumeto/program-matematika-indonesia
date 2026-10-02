"""Failure-boundary tests for isolated native companion export replay."""
import importlib.util
import os
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('original_replay', Path(__file__).with_name('replay-d100-original-backend-v1.py'))
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)


class Boundaries(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='d100-export-test-')
        self.root = Path(self.temp.name).resolve()
        self.guard = replay.ReadOnlyNative(self.root)
        self.guard.enabled = True

    def tearDown(self):
        self.temp.cleanup()

    def test_source_read_is_hash_bound(self):
        source = self.root / 'source.txt'
        source.write_bytes(b'exact source')
        self.guard.observe('open', (str(source), 'r', os.O_RDONLY))
        self.assertEqual(self.guard.reads, {'source.txt': replay.fact(source)})

    def test_repeated_read_retains_first_identity(self):
        source = self.root / 'source.txt'
        source.write_bytes(b'first')
        self.guard.observe('open', (str(source), 'r', os.O_RDONLY))
        original = self.guard.reads['source.txt'].copy()
        source.write_bytes(b'changed')
        self.guard.observe('open', (str(source), 'r', os.O_RDONLY))
        self.assertEqual(self.guard.reads['source.txt'], original)
        self.assertNotEqual(replay.fact(source), original)

    def test_output_cannot_feed_rebuild(self):
        for folder in ('backend/original-bridge', 'backend/original-bridge-corr1'):
            with self.subTest(folder=folder), self.assertRaises(ValueError):
                self.guard.observe('open', (str(self.root / folder / 'records.jsonl'), 'r', 0))

    def test_outside_data_read_rejected(self):
        with self.assertRaises(ValueError):
            self.guard.observe('open', (str(self.root.parent / 'private-unbound.txt'), 'r', 0))

    def test_native_bytecode_not_used(self):
        with self.assertRaises(FileNotFoundError):
            self.guard.observe('open', (str(self.root / 'scripts/__pycache__/native.pyc'), 'r', 0))

    def test_write_modes_and_flags_rejected(self):
        for mode, flags in [('w', 0), ('a', 0), ('r+', 0), ('x', 0),
                            ('r', os.O_RDWR), ('r', os.O_CREAT), ('r', os.O_APPEND)]:
            with self.subTest(mode=mode, flags=flags), self.assertRaises(ValueError):
                self.guard.observe('open', (str(self.root / 'data'), mode, flags))

    def test_file_descriptors_not_unbound(self):
        with self.assertRaises(ValueError):
            self.guard.observe('open', (12, 'r', 0))

    def test_network_processes_and_mutations_rejected(self):
        for event in ('socket.connect', 'subprocess.Popen', 'os.system', 'os.remove',
                      'os.rename', 'os.mkdir', 'os.rmdir', 'os.symlink', 'os.link',
                      'os.truncate', 'os.utime'):
            with self.subTest(event=event), self.assertRaises(ValueError):
                self.guard.observe(event, ())

    def test_path_escape_rejected(self):
        for path in ('../outside', '/absolute', 'C:/absolute', 'a\\b', ''):
            with self.subTest(path=path), self.assertRaises(ValueError):
                replay.exact(self.root, path)

    def test_nested_relative_path_allowed(self):
        self.assertEqual(replay.exact(self.root, 'source/chapter.md'), self.root / 'source/chapter.md')

    def test_output_identity_includes_empty_streams(self):
        rows = replay.output_facts({'z.jsonl': b'content\n', 'empty.jsonl': b''})
        self.assertEqual([r['path'] for r in rows], ['empty.jsonl', 'z.jsonl'])
        self.assertEqual(rows[0]['bytes'], 0)
        self.assertEqual(rows[0]['sha256'], 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855')


if __name__ == '__main__':
    unittest.main()
