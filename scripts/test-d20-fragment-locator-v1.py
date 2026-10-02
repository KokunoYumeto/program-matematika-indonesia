"""Adversarial checks of exact source/target fragment reconstruction."""
import hashlib
import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('d20_ledger', Path(__file__).with_name('d20-native-ledger-v1.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def record(text, first=1, last=1):
    return {'target_bytes': len(text), 'target_sha256': hashlib.sha256(text).hexdigest(),
            'target_line_start': first, 'target_line_end': last}


class FragmentTests(unittest.TestCase):
    def test_subline_fragment(self):
        result = module.locate_fragment(b'prefix exact suffix\n', record(b'exact'), 'target')
        self.assertEqual(result['state'], 'exact_fragment')
        self.assertEqual(len(result['matches']), 1)
        self.assertEqual(result['matches'][0]['raw_byte_start'], 7)
        self.assertEqual(result['matches'][0]['raw_byte_end'], 12)

    def test_utf8_byte_offsets(self):
        data = 'α ruang bernorma β\n'.encode()
        result = module.locate_fragment(data, record('ruang bernorma'.encode()), 'target')
        self.assertEqual(result['state'], 'exact_fragment')
        self.assertEqual(result['matches'][0]['byte_start'], 3)

    def test_multiline_and_newline_boundary(self):
        data = b'prefix\nabc\ndef\n'
        result = module.locate_fragment(data, record(b'abc\ndef\n', 2, 3), 'target')
        self.assertEqual(result['state'], 'exact_fragment')

    def test_universal_newline_read(self):
        result = module.locate_fragment(b'abc\r\ndef\r\n', record(b'abc\ndef', 1, 2), 'target')
        self.assertEqual(result['state'], 'exact_fragment')
        self.assertEqual(result['matches'][0]['view'], 'universal_newlines')

    def test_wrong_line_refused(self):
        result = module.locate_fragment(b'abc\ndef\n', record(b'abc', 2, 2), 'target')
        self.assertEqual(result['state'], 'fragment_not_found')

    def test_changed_fragment_not_certified(self):
        self.assertEqual(module.locate_fragment(b'abd', record(b'abc'), 'target')['state'], 'fragment_not_found')

    def test_repeated_hash_is_ambiguous(self):
        self.assertEqual(module.locate_fragment(b'abc abc', record(b'abc'), 'target')['state'], 'ambiguous_fragment')

    def test_equivalent_newline_views_not_double_counted(self):
        result = module.locate_fragment(b'abc\r\ndef', record(b'def', 2, 2), 'target')
        self.assertEqual(result['state'], 'exact_fragment')
        self.assertEqual(result['matches'][0]['raw_byte_start'], 5)
        self.assertEqual(result['matches'][0]['equivalent_views'], ['raw', 'universal_newlines'])

    def test_invalid_input_rejected(self):
        for bad in [dict(record(b'a'), target_bytes=-1), dict(record(b'a'), target_line_start=0),
                    dict(record(b'a'), target_sha256='missing')]:
            with self.assertRaises(ValueError):
                module.locate_fragment(b'abc', bad, 'target')


if __name__ == '__main__':
    unittest.main()
