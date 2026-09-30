"""Independent negative probes for D50 production admission claims."""
import copy
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('admission', Path(__file__).with_name('admit-d50-production-v1.py'))
admit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(admit)
BASE = ROOT / 'backend/course-capsule-v1/adapters/d50-surface-v1/production'
audit = json.loads((BASE / 'native-production-audit.json').read_bytes())
native = json.loads((BASE / 'native-rebuild-receipt.json').read_bytes())


class Claims(unittest.TestCase):
    def reject(self, change, target='audit'):
        a, n = copy.deepcopy(audit), copy.deepcopy(native)
        change(a if target == 'audit' else n)
        with self.assertRaises((RuntimeError, KeyError)):
            admit.validate_audit(a, n)

    def test_current(self):
        admit.validate_audit(audit, native)

    def test_no_fresh_pdf_claim(self):
        self.reject(lambda a: a.update(fresh_pdf_build=True))

    def test_missing_fresh_replay(self):
        self.reject(lambda a: a.update(fresh_html_backend_replay=None))

    def test_missing_output(self):
        self.reject(lambda a: a['fresh_html_backend_replay']['outputs'].pop('backend_csv'))

    def test_output_drift(self):
        self.reject(lambda a: a['fresh_html_backend_replay']['outputs']['html_entry'].update(sha256='0' * 64))

    def test_failed_fresh_command(self):
        self.reject(lambda a: a['fresh_html_backend_replay']['commands'][0].update(exit_code=1))

    def test_duplicate_native_cycle(self):
        self.reject(lambda n: n['clean_rebuilds'][1].update(cycle=1), 'native')

    def test_wrong_source_package(self):
        self.reject(lambda n: n['source_zip'].update(sha256='0' * 64), 'native')

    def test_missing_native_pdf_build(self):
        self.reject(lambda n: n['clean_rebuilds'][0]['commands'].pop(4), 'native')

    def test_native_cycle_drift(self):
        self.reject(lambda n: n['clean_rebuilds'][1]['outputs']['pdf'].update(bytes=1), 'native')

    def test_central_receipt_and_reader_identity(self):
        for name in ['native-production-audit.json', 'native-rebuild-receipt.json']:
            record = next(x for x in json.loads((BASE / 'admission.json').read_bytes())['evidence']
                          if x['locator'].endswith('/' + name))
            self.assertEqual(admit.a.identity(BASE / name), admit.a.core(record))
        public = json.loads((BASE / 'current-reader-readback.json').read_bytes())
        self.assertTrue(public['anonymous'])
        self.assertEqual(admit.a.identity(ROOT / 'docs/backend/d50/reader/index.html'), admit.a.core(public))


if __name__ == '__main__':
    unittest.main()
