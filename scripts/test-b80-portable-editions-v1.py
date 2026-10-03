"""Bounded native-source and EPUB regression checks; no network and no source execution."""
import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('b80_verifier', ROOT / 'scripts/verify-b80-portable-editions-v1.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
INPUT = ROOT / 'outputs/b80-formats-20261003'


class SourceTests(unittest.TestCase):
    def mutate_source(self, change):
        with zipfile.ZipFile(INPUT / 'en-source.zip') as original:
            payload = {name: original.read(name) for name in original.namelist()}
        change(payload)
        with tempfile.TemporaryDirectory(prefix='b80-source-test-') as temporary:
            path = Path(temporary) / 'mutated.zip'
            with zipfile.ZipFile(path, 'w') as archive:
                for name, raw in payload.items():
                    archive.writestr(name, raw)
            with self.assertRaises((AssertionError, ValueError, KeyError)):
                module.source_evidence(path)

    def test_both_native_sources(self):
        for language in ('en', 'id'):
            units, facts = module.source_evidence(INPUT / (language + '-source.zip'))
            self.assertEqual(len(units), 14)
            self.assertEqual(facts['exercises'], 75)
            self.assertFalse(facts['cumulative_latex_present'])

    def test_missing_unit(self):
        self.mutate_source(lambda files: files.pop('source/units/01-komputasi-bukti.qmd'))

    def test_altered_source(self):
        self.mutate_source(lambda files: files.update({'source/units/01-komputasi-bukti.qmd': b'Changed'}))

    def test_undeclared_payload(self):
        self.mutate_source(lambda files: files.update({'extra.txt': b'Undeclared'}))

    def test_duplicate_manifest_record(self):
        def change(files):
            manifest = json.loads(files['BUNDLE_MANIFEST.json'])
            manifest['files'].append(manifest['files'][0])
            files['BUNDLE_MANIFEST.json'] = json.dumps(manifest).encode()
        self.mutate_source(change)

    def test_path_escape(self):
        self.mutate_source(lambda files: files.update({'../escape.txt': b'Unsafe'}))

    def test_editions_resolve_native_and_chapter_anchors(self):
        for language in ('id', 'en'):
            report = module.inspect_edition(INPUT, language)
            self.assertEqual(report['epub']['document_routes_verified'], 14)
            self.assertEqual(report['epub']['native_locations_verified'], 14)
            self.assertEqual(report['epub']['formula_regions'], 272)
            self.assertTrue(all(row['source_anchor'] != row['epub']['fragment'] for row in report['routes']))

    def test_wrong_epub_language_rejected(self):
        with self.assertRaises(ValueError):
            module.epub_evidence(INPUT / 'en.epub', [], 'id')

    def test_wrong_epub_anchor_rejected(self):
        report = module.inspect_edition(INPUT, 'en')
        routes = report['routes']
        routes[0]['epub']['fragment'] = 'not-a-native-anchor'
        with self.assertRaises(ValueError):
            module.epub_evidence(INPUT / 'en.epub', routes, 'en')


if __name__ == '__main__':
    unittest.main()
