"""Classical registry boundaries and claim limits, alongside common guard tests."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('classical_replay', Path(__file__).with_name('replay-d100-classical-backend-v1.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class Boundaries(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='d100-classical-test-')
        self.root = Path(self.temp.name).resolve()
        self.guard = m.ClassicalReadOnly(self.root)
        self.guard.enabled = True

    def tearDown(self):
        self.temp.cleanup()

    def test_current_outputs_cannot_feed_replay(self):
        with self.assertRaises(ValueError):
            self.guard.observe('open', (str(self.root / m.NAMESPACE / 'records.jsonl'), 'r', 0))

    def test_historical_registry_is_explicitly_allowed(self):
        for relative in m.REGISTRY:
            target = self.root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(b'registry fixture')
            self.guard.observe('open', (str(target), 'r', 0))
            self.assertIn(relative, self.guard.reads)

    def test_unrelated_backend_rejected(self):
        for relative in ('backend/units-01-30/unbound.jsonl', 'backend/original-bridge/records.jsonl',
                         'backend/bgk-units-01-30-corr1/records.jsonl'):
            with self.subTest(path=relative), self.assertRaises(ValueError):
                self.guard.observe('open', (str(self.root / relative), 'r', 0))

    def test_native_scope_overclaims_rejected(self):
        manifest = {'through_unit': 30, 'record_count': 23869}
        validation = {'record_count': 23869, 'json_schema_validated_records': 23869,
                      'baseline_stable_ids_preserved': 22752, 'added_stable_id_count': 1117,
                      'source_projection': {'source_file_count': 120, 'segment_record_count': 8056},
                      'ledger_projection': {'terminology_record_count': 276, 'correction_record_count': 159}}
        m.check_validation(manifest, validation)
        for key in ('json_schema_validated_records', 'baseline_stable_ids_preserved', 'added_stable_id_count'):
            bad = copy.deepcopy(validation)
            bad[key] -= 1
            with self.subTest(key=key), self.assertRaises(ValueError):
                m.check_validation(manifest, bad)
        for group, key in [('source_projection', 'source_file_count'), ('source_projection', 'segment_record_count'),
                           ('ledger_projection', 'terminology_record_count'), ('ledger_projection', 'correction_record_count')]:
            bad = copy.deepcopy(validation)
            bad[group][key] -= 1
            with self.subTest(key=key), self.assertRaises(ValueError):
                m.check_validation(manifest, bad)


if __name__ == '__main__':
    unittest.main()
