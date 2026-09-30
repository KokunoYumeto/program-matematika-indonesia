"""Adversarial byte, ZIP-boundary and deterministic-package checks."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
import warnings
import zipfile

def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, Path(__file__).with_name(filename))
    value = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(value)
    return value

replay = module('replay', 'replay-d70-native-metadata-v1.py')
builder = module('builder', 'build-d70-native-replay-v1.py')

class ReplaySafety(unittest.TestCase):
    def test_deterministic_archive(self):
        with tempfile.TemporaryDirectory(prefix='d70-replay-test-') as directory:
            first, second = Path(directory) / 'first.zip', Path(directory) / 'second.zip'
            contents = {'data/example.json': b'{"native":true}\n', 'script.py': b'pass\n'}
            builder.write_bundle(first, contents)
            builder.write_bundle(second, contents)
            self.assertEqual(builder.audit.identity(first), builder.audit.identity(second))

    def check_rejection(self, names, message, cap=1024):
        with tempfile.TemporaryDirectory(prefix='d70-replay-test-') as directory:
            target = Path(directory) / 'bad.zip'
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', UserWarning)
                with zipfile.ZipFile(target, 'w') as archive:
                    for name, data in names:
                        archive.writestr(name, data)
            # ZipInfo also normalizes separators on Windows when *writing*.
            # Preserve a hostile wire name explicitly, not a normalized fixture.
            if any('\\' in name for name, _ in names):
                target.write_bytes(target.read_bytes().replace(b'path/outside', b'path\\outside'))
            with zipfile.ZipFile(target) as archive:
                with self.assertRaisesRegex(RuntimeError, message):
                    replay.checked_members(archive, cap)

    def test_unsafe_members(self):
        for name in ['../outside', '/absolute', 'C:/outside', 'path\\outside', 'path:stream', './alias']:
            with self.subTest(name=name):
                self.check_rejection([(name, b'x')], 'Unsafe')

    def test_duplicate_members(self):
        self.check_rejection([('same', b'x'), ('same', b'y')], 'Duplicate')

    def test_expanded_size(self):
        self.check_rejection([('large', b'x' * 1025)], 'expanded-size')

    def test_directory_members(self):
        self.check_rejection([('directory/', b'')], 'Unsafe|Non-file')

    def test_symlink_members(self):
        with tempfile.TemporaryDirectory(prefix='d70-replay-test-') as directory:
            target = Path(directory) / 'link.zip'
            with zipfile.ZipFile(target, 'w') as archive:
                info = zipfile.ZipInfo('link')
                info.create_system = 3
                info.external_attr = 0o120777 << 16
                archive.writestr(info, '../outside')
            with zipfile.ZipFile(target) as archive, self.assertRaisesRegex(RuntimeError, 'Non-file'):
                replay.checked_members(archive, 1024)

    def test_changed_dependency_rejected(self):
        report = {'extended_metadata_replay_pass': True, 'whole_native_parity_proven': False,
                  'explicit_external_dependencies': [{'path': 'authority/exact.json', 'bytes': 1, 'sha256': '0' * 64}] * 26}
        with tempfile.TemporaryDirectory(prefix='d70-replay-test-') as directory:
            source = Path(directory) / 'authority/exact.json'
            source.parent.mkdir()
            source.write_bytes(b'x')
            with self.assertRaisesRegex(RuntimeError, 'Frozen dependency changed'):
                builder.prepare(report, Path(directory), Path(directory))


if __name__ == '__main__':
    unittest.main()
