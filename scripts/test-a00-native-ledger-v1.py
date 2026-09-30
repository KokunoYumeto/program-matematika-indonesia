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
import copy
import xml.etree.ElementTree as ET

SPEC = importlib.util.spec_from_file_location('a00_native', Path(__file__).with_name('a00-native-ledger-v1.py'))
NATIVE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(NATIVE)
BASE = NATIVE.BASE


class NativeLedgerTests(unittest.TestCase):
    def setUp(self):
        self.lock = json.loads((BASE / 'input/source-lock.json').read_bytes())
        self.raw = {r['path']: (BASE / 'input' / r['path']).read_bytes() for r in self.lock['snapshots'] + ([self.lock['term_locations']] if self.lock.get('term_locations') else [])}

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

    def test_lexical_concordance_and_distinct_sum_choices(self):
        data = NATIVE.normalize(self.raw, self.lock)
        proof = data['term_locations']
        self.assertEqual(len(proof['modules']), 75)
        self.assertEqual(len(proof['choices']), 20)
        self.assertGreater(proof['summary']['choice_variant_matches'], 0)
        sums = [r for r in proof['choices'] if r['preferred_term'] == 'jumlah']
        self.assertEqual(len(sums), 2)
        self.assertNotEqual(sums[0]['choice_id'], sums[1]['choice_id'])
        self.assertEqual(sums[0]['matches'], sums[1]['matches'])
        self.assertFalse(proof['semantic_canon_review'])
        self.assertFalse(proof['scope_application_checked'])
        self.assertEqual(data['verification']['segment_level_choice_coverage'], 'not_established')

    def test_concordance_refuses_structural_and_semantic_drift(self):
        data = NATIVE.normalize(self.raw, self.lock)
        proof = data['term_locations']
        mutations = (
            lambda p: p['modules'].pop(),
            lambda p: p['modules'][0].update(sha256='0' * 64),
            lambda p: p['modules'][0].update(path='../outside.cnxml'),
            lambda p: p['choices'].pop(),
            lambda p: p['choices'][0].update(preferred_term='invented'),
            lambda p: p['choices'][0].update(match_count=-1),
            lambda p: p.update(semantic_canon_review=True),
            lambda p: p.update(scope_application_checked=True),
            lambda p: p['summary'].update(choice_variant_matches=0),
            lambda p: p['choices'][0]['matches'][0].update(xpath='/outside[1]'),
            lambda p: p['choices'][0]['matches'][0].update(excerpt='not the term'),
            lambda p: p['choices'][0]['matches'].append(copy.deepcopy(p['choices'][0]['matches'][0])),
        )
        for mutate in mutations:
            invalid = copy.deepcopy(proof)
            mutate(invalid)
            with self.assertRaises(ValueError):
                NATIVE.term_locations.validate(invalid, data)
        self.raw['term-locations.json'] += b' '
        with self.assertRaisesRegex(ValueError, 'Term proof identity'):
            NATIVE.normalize(self.raw, self.lock)

    def test_block_matching_does_not_duplicate_inline_terms_or_read_math(self):
        xml = '''<document xmlns="http://cnx.rice.edu/cnxml" xmlns:m="http://www.w3.org/1998/Math/MathML"><title>Excluded bilangan asli</title><content><section><title>Bilangan asli</title><para id="p1">Dua <term id="t1">bilangan asli</term> serta <m:math><m:mtext>bilangan asli</m:mtext></m:math>.</para><list><item id="i1"><para>bilangan asli</para></item></list></section></content></document>'''
        blocks, unwrapped = NATIVE.term_locations.text_blocks(ET.fromstring(xml))
        self.assertEqual(len(blocks), 3)
        self.assertEqual(sum(len(list(NATIVE.term_locations.pattern('bilangan asli').finditer(b['text']))) for b in blocks), 3)
        self.assertEqual([b['xml_id'] for b in blocks], [None, 'p1', 'i1'])
        self.assertEqual(unwrapped, [])
        self.assertEqual(NATIVE.term_locations.normalized('bilangan\n  asli'), 'bilangan asli')
        self.assertEqual(len(list(NATIVE.term_locations.pattern('digit').finditer('digital digit DIGIT'))), 2)

    def test_context_details_are_localized_and_escape_native_quotes(self):
        data = NATIVE.normalize(self.raw, self.lock)
        for english, label in [(False, 'kecocokan harfiah'), (True, 'literal matches')]:
            page = NATIVE.render(data, english).decode()
            self.assertEqual(page.count('class="term-locations"'), 20)
            self.assertIn(label, page)
            self.assertIn('native-ledger/term-locations.json', page)
            self.assertIn('gpt-6.1-sol, Ultra effort', page)
        altered = copy.deepcopy(data)
        altered['term_locations']['choices'][0]['matches'][0]['excerpt'] = '<img src=x onerror=alert(1)>'
        page = NATIVE.render(altered).decode()
        self.assertIn('&lt;img src=x onerror=alert(1)&gt;', page)
        self.assertNotIn('<img src=x onerror=alert(1)>', page)

    def test_table_cells_and_residual_text_have_separate_locations(self):
        xml = '''<document xmlns="http://cnx.rice.edu/cnxml"><content><note id="loose">bilangan asli</note><table><tgroup><tbody><row><entry>bilangan</entry><entry>asli</entry><entry>bilangan <emphasis>asli</emphasis></entry></row></tbody></tgroup></table></content></document>'''
        blocks, residual = NATIVE.term_locations.text_blocks(ET.fromstring(xml))
        self.assertEqual(len(blocks), 3)
        self.assertEqual(len(residual), 1)
        self.assertEqual(residual[0]['xml_id'], 'loose')
        self.assertTrue(residual[0]['xpath'].endswith('/text()[1]'))
        self.assertEqual(sum(len(list(NATIVE.term_locations.pattern('bilangan asli').finditer(b['text']))) for b in blocks + residual), 2)

    def test_changed_concordance_generator_is_not_relabelled_as_replayed(self):
        with tempfile.TemporaryDirectory(prefix='a00-generator-test-') as temp:
            dest = Path(temp)
            shutil.copytree(BASE / 'input', dest / 'input')
            lock = json.loads((dest / 'input/source-lock.json').read_bytes())
            lock['term_locations']['generator']['sha256'] = '0' * 64
            (dest / 'input/source-lock.json').write_bytes(NATIVE.packed(lock))
            with self.assertRaisesRegex(ValueError, 'generator identity'):
                NATIVE.build(dest)


if __name__ == '__main__':
    unittest.main()
