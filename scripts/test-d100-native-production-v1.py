"""Independent fixtures for the read-only D100 production preflight."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('d100_production', Path(__file__).with_name('audit-d100-native-production-v1.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)

class ProductionEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='d100-production-fixture-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.source = self.root / 'source.txt'
        self.source.write_text('source mathematics', encoding='utf-8')
        self.rendered = self.root / 'reader.html'
        self.rendered.write_text('<p>source mathematics</p>', encoding='utf-8')
        for relative in m.READERS.values():
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(json.dumps({'status': 'PASS',
                'inputs': [{'path': 'source.txt', **m.identity(self.source)}],
                'outputs': [{'path': 'reader.html', **m.identity(self.rendered)}]}), encoding='utf-8')

    def test_matching_receipts_are_not_a_new_build(self):
        report = m.audit(self.root)
        self.assertEqual(report['state'], 'identity_preflight_pass')
        self.assertEqual(report['input_references'], 3)
        self.assertEqual(report['output_references'], 3)
        self.assertEqual(report['unique_files_observed'], 2)
        self.assertFalse(report['native_build_executed'])
        self.assertFalse(report['whole_backend_complete'])
        self.assertFalse(report['semantic_canon_review'])

    def test_changed_source_is_reported_in_every_affected_reader(self):
        self.source.write_text('different mathematics', encoding='utf-8')
        report = m.audit(self.root)
        self.assertEqual(report['state'], 'identity_gaps')
        self.assertEqual(len(report['failures']), 3)
        self.assertEqual({r['state'] for r in report['failures']}, {'identity_drift'})

    def test_missing_output_is_not_success(self):
        self.rendered.unlink()
        report = m.audit(self.root)
        self.assertEqual(report['state'], 'identity_gaps')
        self.assertEqual(len(report['failures']), 3)
        self.assertEqual({r['state'] for r in report['failures']}, {'FileNotFoundError'})

    def test_paths_stay_inside_native_tree(self):
        for path in ['../outside', '/outside', 'C:/outside', 'C:outside']:
            with self.subTest(path=path), self.assertRaises(ValueError):
                m.inside(self.root, path)

    def test_failed_receipt_is_refused(self):
        target = self.root / next(iter(m.READERS.values()))
        receipt = json.loads(target.read_bytes())
        receipt['status'] = 'FAIL'
        target.write_text(json.dumps(receipt), encoding='utf-8')
        with self.assertRaises(ValueError):
            m.audit(self.root)

    def test_empty_scope_is_refused(self):
        target = self.root / next(iter(m.READERS.values()))
        receipt = json.loads(target.read_bytes())
        receipt['inputs'] = []
        target.write_text(json.dumps(receipt), encoding='utf-8')
        with self.assertRaises(ValueError):
            m.audit(self.root)

if __name__ == '__main__':
    unittest.main()
