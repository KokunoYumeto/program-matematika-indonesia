"""Replay native metadata mapping and reject specific misadmissions."""
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
import sys
import zipfile

SPEC = importlib.util.spec_from_file_location('a00_native', Path(__file__).with_name('a00-native-ledger-v1.py'))
NATIVE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(NATIVE)
BASE = NATIVE.BASE


class NativeLedgerTests(unittest.TestCase):
    def setUp(self):
        self.lock = json.loads((BASE / 'input/source-lock.json').read_bytes())
        self.raw = {r['path']: (BASE / 'input' / r['path']).read_bytes() for r in self.lock['snapshots']}

    def test_current_native_metadata(self):
        result = NATIVE.normalize(self.raw, self.lock)
        self.assertEqual(len(result['modules']), 75)
        self.assertEqual(len(result['terms']), 56)
        self.assertEqual(len(result['corrections']), 75)
        self.assertEqual({r['module_id'] for r in result['source_map_discrepancies']}, {'m81272','m81243','m81244','m81340'})
        self.assertFalse(result['verification']['semantic_canon_review'])
        self.assertEqual(result['verification']['segment_level_choice_coverage'], 'not_established')

    def test_target_drift_rejected(self):
        self.lock['target_probe'][0]['sha256'] = '0' * 64
        with self.assertRaisesRegex(ValueError, 'Target probe'):
            NATIVE.normalize(self.raw, self.lock)

    def test_omitted_probe_rejected(self):
        self.lock['target_probe'].pop()
        with self.assertRaisesRegex(ValueError, 'projection'):
            NATIVE.normalize(self.raw, self.lock)

    def test_unknown_csv_repair_rejected(self):
        self.raw['source-map.csv'] = self.raw['source-map.csv'].replace(b'111105,e2846', b'111106,e2846')
        with self.assertRaisesRegex(ValueError, 'Unrecognized malformed'):
            NATIVE.normalize(self.raw, self.lock)

    def test_native_term_edit_rejected(self):
        rows = NATIVE.jsonl(self.raw['terms.jsonl'])
        next(r for r in rows if r.get('source_record_id'))['preferred_term'] += ' changed'
        self.raw['terms.jsonl'] = ('\n'.join(json.dumps(r) for r in rows)).encode()
        with self.assertRaisesRegex(ValueError, 'Choice changed'):
            NATIVE.normalize(self.raw, self.lock)

    def test_duplicate_artifact_rejected(self):
        line = self.raw['artifacts.jsonl'].splitlines()[0]
        self.raw['artifacts.jsonl'] += b'\n' + line
        with self.assertRaisesRegex(ValueError, 'Duplicate artifact'):
            NATIVE.normalize(self.raw, self.lock)

    def test_exact_metadata_replay_without_native_corpus(self):
        with tempfile.TemporaryDirectory(prefix='a00-ledger-test-') as temp:
            dest = Path(temp)
            shutil.copytree(BASE / 'input', dest / 'input')
            NATIVE.build(dest)
            for name in ['data/ledger.json', 'data/source.zip', 'views/ledger.html', 'views/ledger-en.html', 'manifest.json']:
                self.assertEqual((dest / name).read_bytes(), (BASE / name).read_bytes())
            (dest / 'input/terms.jsonl').write_bytes(b'[]')
            with self.assertRaisesRegex(ValueError, 'Snapshot identity'):
                NATIVE.build(dest)

    def test_path_escape_rejected(self):
        for path in ['../x', '/outside', 'C:/outside', 'foo/../../x']:
            with self.assertRaises(ValueError):
                NATIVE.checked_path(BASE, path)

    def test_source_zip_builds_without_workspace(self):
        with tempfile.TemporaryDirectory(prefix='a00-ledger-zip-') as temp:
            root = Path(temp)
            with zipfile.ZipFile(BASE / 'data/source.zip') as archive:
                self.assertIsNone(archive.testzip())
                for name in archive.namelist():
                    NATIVE.checked_path(root, name)
                archive.extractall(root)
            run = subprocess.run([sys.executable, '-B', str(root / 'scripts/a00-native-ledger-v1.py')],
                                 cwd=root, capture_output=True, text=True, timeout=20)
            self.assertEqual(run.returncode, 0, run.stderr)
            rebuilt = root / BASE.relative_to(NATIVE.ROOT)
            for name in ['data/ledger.json','data/source.zip','views/ledger.html','views/ledger-en.html','manifest.json']:
                self.assertEqual((BASE / name).read_bytes(), (rebuilt / name).read_bytes())

    def test_actual_search_handlers(self):
        result = subprocess.run(['node', str(Path(__file__).with_name('test-a00-native-ledger-ui-v1.mjs'))],
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_localized_reader_labels(self):
        result = NATIVE.normalize(self.raw, self.lock)
        for english, expected, excluded in [
            (False, ['Byte sumber (EN)', 'Byte terjemahan (ID)', 'CNXML (bahasa Inggris)', '<th>Bahasa Inggris</th>'],
             ['EN bytes', 'ID bytes', 'CNXML (English)']),
            (True, ['<th>Module</th>', 'Source bytes (EN)', 'Translation bytes (ID)', 'CNXML (English)'],
             ['<th>Modul</th>', 'Byte sumber (EN)']),
        ]:
            page = NATIVE.render(result, english).decode('utf-8')
            for label in expected:
                self.assertIn(label, page)
            for label in excluded:
                self.assertNotIn(label, page)


if __name__ == '__main__':
    unittest.main()
