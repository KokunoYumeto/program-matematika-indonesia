"""Adversarial intake tests. Optional --intake runs against an actual private packet."""
import argparse
import copy
import io
import json
import stat
import tempfile
import unittest
import warnings
import zipfile
from pathlib import Path

from lxml import html

import course_formats as f


class SafetyTests(unittest.TestCase):
    def test_canonical_paths(self):
        for value in ['output/book.tex', 'native/lesson-01.md', 'sumber/latihan α.tex']:
            self.assertEqual(f.safe_name(value), value)

    def test_unsafe_paths(self):
        for value in ['', '../x', 'x/../y', '/x', 'C:/x', 'x\\y', 'x//y', 'x/./y',
                      'x:stream', 'x\x00y', 'dir/NUL.txt', 'x/foo.', 'x/foo ']:
            with self.subTest(value=value), self.assertRaises(f.InvalidPackage):
                f.safe_name(value)

    def test_duplicate_json_keys(self):
        with self.assertRaises(f.InvalidPackage):
            f.decode(b'{"files":[],"files":[1]}')

    def test_confined_file_hash(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'test.txt').write_bytes(b'exact')
            record = {'path': 'test.txt', 'bytes': 5, 'sha256': f.digest(b'exact')}
            self.assertEqual(f.checked_file(root, record), root / 'test.txt')
            for change in [{'bytes': 4}, {'sha256': '0' * 64}, {'path': '../test.txt'}]:
                with self.assertRaises(f.InvalidPackage):
                    f.checked_file(root, dict(record, **change))

    def zip_with(self, names, symlink=False):
        stream = io.BytesIO()
        with warnings.catch_warnings(), zipfile.ZipFile(stream, 'w') as archive:
            warnings.simplefilter('ignore', UserWarning)
            for name in names:
                info = zipfile.ZipInfo(name)
                if symlink:
                    info.external_attr = (stat.S_IFLNK | 0o777) << 16
                archive.writestr(info, b'x')
        stream.seek(0)
        return zipfile.ZipFile(stream)

    def test_zip_duplicate_case_and_escape(self):
        for names in [['x', 'x'], ['x', 'X'], ['../x'], ['/x'], ['x:stream']]:
            with self.zip_with(names) as archive, self.assertRaises(f.InvalidPackage):
                f.archive_inventory(archive)

    def test_zip_symlink(self):
        with self.zip_with(['x'], symlink=True) as archive, self.assertRaises(f.InvalidPackage):
            f.archive_inventory(archive)

    def test_xml_external_entity(self):
        with self.assertRaises(f.InvalidPackage):
            f.xml(b'<!DOCTYPE x [<!ENTITY x SYSTEM "file:///secret">]><x>&x;</x>')

    def test_relative_epub_reference(self):
        self.assertEqual(f.local_reference('EPUB/text/one.xhtml', '../images/a.png'), ('EPUB/images/a.png', ''))
        self.assertEqual(f.local_reference('EPUB/text/one.xhtml', '#%CE%B1'), ('EPUB/text/one.xhtml', 'α'))
        self.assertIsNone(f.local_reference('EPUB/nav.xhtml', 'https://example.org/'))
        for href in ['javascript:alert(1)', 'file:///secret', '//example.org/a',
                     '../../../outside', '%2e%2e/%2e%2e/%2e%2e/outside', 'C:/x', '/x', 'a?b=c']:
            with self.subTest(href=href), self.assertRaises(f.InvalidPackage):
                f.local_reference('EPUB/text/one.xhtml', href)


class EpubTests(unittest.TestCase):
    def make(self, path, *, annotations=('x', 'y'), duplicate=False, language='en', broken=False, repeated_toc_math=False):
        opf = f'''<package xmlns="{f.NS['o']}" version="3.0"><metadata xmlns:dc="{f.NS['dc']}"><dc:language>{language}</dc:language></metadata><manifest><item id="nav" href="nav.xhtml" properties="nav"/><item id="ch1" href="text/ch1.xhtml"/></manifest><spine><itemref idref="ch1"/></spine></package>'''
        target = 'missing' if broken else 'U1'
        nav = f'''<html xmlns="{f.NS['h']}" xmlns:epub="http://www.idpf.org/2007/ops"><body><nav epub:type="toc"><a href="text/ch1.xhtml#{target}">Lesson</a></nav></body></html>'''
        math = ''.join(f'<math xmlns="{f.NS["m"]}"><semantics><mi>{a}</mi><annotation encoding="application/x-tex">{a}</annotation></semantics></math>' for a in annotations)
        body = f'<html xmlns="{f.NS["h"]}"><body><h1 id="U1">Lesson</h1>{math}' + ('<p id="U1">Again</p>' if duplicate else '') + '</body></html>'
        if repeated_toc_math:
            nav = nav.replace('</a>', math + '</a>')
            opf = opf.replace('<spine>', '<spine><itemref idref="nav"/>')
        with zipfile.ZipFile(path, 'w') as archive:
            archive.writestr('mimetype', b'application/epub+zip', compress_type=zipfile.ZIP_STORED)
            archive.writestr('META-INF/container.xml', f'<container xmlns="{f.NS["c"]}"><rootfiles><rootfile full-path="EPUB/content.opf"/></rootfiles></container>')
            archive.writestr('EPUB/content.opf', opf)
            archive.writestr('EPUB/nav.xhtml', nav)
            archive.writestr('EPUB/text/ch1.xhtml', body)

    def test_formula_order_not_just_multiset(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'test.epub'
            self.make(path)
            rows = [{'epub': {'member': 'EPUB/text/ch1.xhtml', 'fragment': 'U1'}}]
            ledger = [{'tex': s, 'tex_sha256': f.digest(s.encode())} for s in ('x', 'y')]
            checked = f.epub_evidence(path, rows, 'en', ledger)
            self.assertEqual(checked['formula_regions'], 2)
            with self.assertRaises(f.InvalidPackage):
                f.epub_evidence(path, rows, 'en', list(reversed(ledger)))

    def test_epub_language_navigation_and_fragments(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'test.epub'
            rows = [{'epub': {'member': 'EPUB/text/ch1.xhtml', 'fragment': 'U1'}}]
            for change in [{'duplicate': True}, {'language': 'id'}, {'broken': True}]:
                self.make(path, **change)
                with self.subTest(change=change), self.assertRaises(f.InvalidPackage):
                    f.epub_evidence(path, rows, 'en')

    def test_navigation_formula_occurrences_are_separate(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'test.epub'
            self.make(path, repeated_toc_math=True)
            rows = [{'epub': {'member': 'EPUB/text/ch1.xhtml', 'fragment': 'U1'}}]
            ledger = [{'tex': s, 'tex_sha256': f.digest(s.encode())} for s in ('x', 'y')]
            checked = f.epub_evidence(path, rows, 'en', ledger)
            self.assertEqual(checked['formula_regions'], 2)
            self.assertEqual(checked['navigation_formula_regions'], 2)


class ClosureTests(unittest.TestCase):
    def test_undeclared_and_changed_source_archive_payloads(self):
        source = b'Exact original source'
        tex = b'Complete cumulative source fixture'
        unit = {'id': 'U1', 'source': 'native/u1.md', 'bytes': len(source), 'source_sha256': f.digest(source)}
        source_record = {'path': unit['source'], 'bytes': len(source), 'sha256': f.digest(source)}
        tex_record = {'path': 'output/01-book.tex', 'bytes': len(tex), 'sha256': f.digest(tex)}
        manifest = f.json_bytes({'files': [source_record]})
        payloads = {'native/u1.md': source, 'output/01-book.tex': tex, 'SOURCE_MANIFEST.json': manifest}
        closure = f.json_bytes({'schema': 'course-editable-source-closure/1', 'files': [
            {'path': name, 'bytes': len(raw), 'sha256': f.digest(raw)} for name, raw in payloads.items()]})
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'source.zip'
            for change in ['none', 'extra', 'changed']:
                with zipfile.ZipFile(path, 'w') as archive:
                    for name, raw in payloads.items():
                        archive.writestr(name, b'wrong' if change == 'changed' and name == 'native/u1.md' else raw)
                    archive.writestr('PACKAGE_CONTENTS.json', closure)
                    if change == 'extra':
                        archive.writestr('undeclared.txt', b'extra')
                if change == 'none':
                    self.assertTrue(f.source_closure(path, manifest, [tex_record], [unit])['direct_tex_matches_source_zip'])
                else:
                    with self.subTest(change=change), self.assertRaises(f.InvalidPackage):
                        f.source_closure(path, manifest, [tex_record], [unit])


class ReaderTests(unittest.TestCase):
    def fixture(self):
        formats = [{'path': f'output/{i}.{ext}', 'bytes': 1, 'sha256': '0' * 64}
                   for i, ext in enumerate(['pdf', 'tex', 'zip', 'epub'])]
        report = {'files': formats, 'pdf': {'tagged': False}}
        manifest = {'title': '<script>bad</script>', 'content_language': 'en',
                    'coverage_note': 'Source status unchanged.', 'source_author': 'Original creator',
                    'conversion_author': 'Original conversion', 'export': {'rights_notice': 'Original licence'}}
        routes = [{'lesson_id': 'U1', 'title': 'Original title', 'pdf': {'page': 4},
                   'epub': {'member': 'EPUB/text/ch1.xhtml', 'fragment': 'U1'}}]
        return report, manifest, routes

    def test_languages_content_identity_and_escaping(self):
        for locale in ('en', 'id'):
            report, manifest, routes = self.fixture()
            markup = f.reader_html(report, manifest, routes, locale)
            tree = html.fromstring(markup)
            self.assertEqual(tree.get('lang'), locale)
            self.assertEqual(tree.xpath('//h1/@lang'), ['en'])
            self.assertEqual(tree.xpath('//h1/text()'), ['<script>bad</script>'])
            self.assertFalse(tree.xpath('//script'))
            self.assertEqual(len(tree.xpath('//div[@class="downloads"]/a')), 4)
            self.assertIn('index.id.html', tree.xpath('//nav/a/@href'))
            self.assertTrue(all(not h.startswith(('http:', 'https:')) for h in tree.xpath('//a/@href')))
            self.assertIn('Original creator', tree.text_content())
            self.assertIn('Original licence', tree.text_content())
            self.assertIn(f.COPY[locale]['separate'], tree.text_content())

    def test_output_cannot_overwrite_or_touch_intake(self):
        report, manifest, routes = self.fixture()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for destination in [root, root / 'output', root.parent]:
                with self.assertRaises(f.InvalidPackage):
                    f.assemble(root, destination, report, manifest, routes)


class ActualIntakeTests(unittest.TestCase):
    def test_actual_intake_and_negative_routes(self):
        if not INTAKE:
            self.skipTest('Supply --intake for private integration fixture')
        report, manifest, routes = f.validate(INTAKE)
        self.assertEqual(report['selected_documents'], len(routes))
        pdf = INTAKE / report['files'][0]['path']
        epub = INTAKE / report['files'][3]['path']
        changed = copy.deepcopy(routes)
        changed[0]['pdf']['page'] += 1
        with self.assertRaises(f.InvalidPackage):
            f.pdf_evidence(pdf, changed)
        changed = copy.deepcopy(routes)
        changed[0]['epub']['fragment'] = 'nonexistent'
        with self.assertRaises(f.InvalidPackage):
            f.epub_evidence(epub, changed, manifest['content_language'])
        with self.assertRaises(f.InvalidPackage):
            f.epub_evidence(epub, list(reversed(routes)), manifest['content_language'])
        bad_native = copy.deepcopy(routes[:1])
        bad_native[0]['pdf']['named_destination'] = 'missing-native-destination'
        with self.assertRaises(f.InvalidPackage):
            f.pdf_evidence(pdf, routes, bad_native)
        bad_native[0]['epub']['fragment'] = 'missing-native-fragment'
        with self.assertRaises(f.InvalidPackage):
            f.epub_evidence(epub, routes, manifest['content_language'], native_locations=bad_native)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--intake', type=Path)
    args, remaining = parser.parse_known_args()
    INTAKE = args.intake
    unittest.main(argv=[__file__, *remaining])
else:
    INTAKE = None
