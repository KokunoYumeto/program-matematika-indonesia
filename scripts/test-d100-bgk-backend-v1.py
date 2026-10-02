"""Guard and strict-source/reader boundaries for BGK replay."""
import copy
import importlib.util
from pathlib import Path
import tempfile
import unittest

spec = importlib.util.spec_from_file_location('bgk_replay', Path(__file__).with_name('replay-d100-bgk-backend-v1.py'))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class Boundaries(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='d100-bgk-test-')
        self.root = Path(self.temp.name).resolve()
        self.allowed = m.BASE + '/records.jsonl'
        self.guard = m.BgkReadOnly(self.root, {self.allowed: {}})
        self.guard.enabled = True

    def tearDown(self):
        self.temp.cleanup()

    def test_current_output_and_unbound_history_forbidden(self):
        for path in (m.NAMESPACE + '/records.jsonl', m.BASE + '/unbound.jsonl',
                     'backend/original-bridge/records.jsonl'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                self.guard.observe('open', (str(self.root / path), 'r', 0))

    def test_explicit_history_read_is_recorded(self):
        target = self.root / self.allowed
        target.parent.mkdir(parents=True)
        target.write_bytes(b'historical fixture')
        self.guard.observe('open', (str(target), 'r', 0))
        self.assertEqual(self.guard.reads[self.allowed], m.fact(target))

    def test_writes_network_and_processes_forbidden(self):
        for event, args in [('open', (str(self.root / 'source.md'), 'w', 0)),
                            ('socket.connect', (None,)), ('subprocess.Popen', (None,))]:
            with self.subTest(event=event), self.assertRaises(ValueError):
                self.guard.observe(event, args)

    def test_exact_scope_required(self):
        manifest = {'through_unit': 30, 'record_count': 21690,
                    'historical_baseline': {'record_count': 21686, 'additive_stable_ids': [1, 2, 3, 4]},
                    'reader_binding': {'ready': True},
                    'validation': {'current_source_closure_and_unit_07_two_hop_exact': True,
                                   'current_reader_and_reader_qa_exact': True}}
        validation = {'record_count': 21690, 'schema_validated_records': 21690,
                      'source_projection': {'record_backed_source_file_count': 99,
                                            'current_source_file_count': 90},
                      'counts': {'segment': 7506, 'exercise': 495, 'solution': 25}}
        m.check_validation(manifest, validation)
        for group, field in [('counts', 'solution'), ('counts', 'exercise'),
                             ('source_projection', 'record_backed_source_file_count'),
                             ('source_projection', 'current_source_file_count')]:
            bad = copy.deepcopy(validation)
            bad[group][field] -= 1
            with self.subTest(field=field), self.assertRaises(ValueError):
                m.check_validation(manifest, bad)
        for group, field in [('reader_binding', 'ready'),
                             ('validation', 'current_source_closure_and_unit_07_two_hop_exact'),
                             ('validation', 'current_reader_and_reader_qa_exact')]:
            bad = copy.deepcopy(manifest)
            bad[group][field] = False
            with self.subTest(field=field), self.assertRaises(ValueError):
                m.check_validation(bad, validation)


if __name__ == '__main__':
    unittest.main()
