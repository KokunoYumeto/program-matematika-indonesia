"""Regression tests reject content loss while allowing documented AST presentation differences."""
import copy
import json
import hashlib
from pathlib import Path
import unittest
import zipfile

from build_b80 import (group_numeric_cells, inline_code_runs, semantic_signature,
                       text_tokens, print_document, pandoc, xml, NS)


def code(text):
    return {'t': 'Code', 'c': [['', [], []], text]}


class PreservationTests(unittest.TestCase):
    def test_code_bracket_wrappers_only(self):
        source = [code('values[1:3]')]
        target = [code('values'), {'t': 'Span', 'c': [['', [], []], [code('[')]]},
                  code('1:3'), code(']')]
        self.assertEqual(inline_code_runs(source), inline_code_runs(target))

    def test_code_whitespace_separates_runs(self):
        self.assertNotEqual(inline_code_runs([code('ab')]),
                            inline_code_runs([code('a'), {'t': 'Space'}, code('b')]))

    def test_code_mutation_is_detected(self):
        self.assertNotEqual(inline_code_runs([code('values[1:3]')]),
                            inline_code_runs([code('values[1:4]')]))

    def test_quotes_are_preserved(self):
        raw = [{'t': 'Str', 'c': '\u201cterm\u201d'}]
        quoted = [{'t': 'Quoted', 'c': [{'t': 'DoubleQuote'}, [{'t': 'Str', 'c': 'term'}]]}]
        self.assertEqual(text_tokens(raw), text_tokens(quoted))
        self.assertNotEqual(text_tokens(raw), text_tokens([{'t': 'Str', 'c': 'term'}]))

    def test_word_boundary_and_punctuation_loss_rejected(self):
        self.assertNotEqual(text_tokens([{'t': 'Str', 'c': 'not equal'}]),
                            text_tokens([{'t': 'Str', 'c': 'notequal'}]))
        self.assertNotEqual(text_tokens([{'t': 'Str', 'c': '1.0'}]),
                            text_tokens([{'t': 'Str', 'c': '10'}]))

    def test_numeric_cell_protection_is_scoped(self):
        original = b'outside 0 & 1 \\\\\n\\begin{longtable}{rr}\n0 & 1.0 \\\\\n\\end{longtable}\n'
        changed, count = group_numeric_cells(original)
        self.assertEqual(count, 2)
        self.assertIn(b'outside 0 & 1', changed)
        self.assertIn(b'\\mbox{0} & \\mbox{1.0}', changed)
        self.assertEqual(group_numeric_cells(changed), (changed, 0))

    def test_math_change_rejected(self):
        source = [{'t': 'Math', 'c': [{'t': 'InlineMath'}, 'x + 1']}]
        target = [{'t': 'Math', 'c': [{'t': 'InlineMath'}, 'x + 2']}]
        self.assertNotEqual(semantic_signature(source), semantic_signature(target))

    def test_codeblock_indent_rejected(self):
        source = [{'t': 'CodeBlock', 'c': [['', [], []], 'if x:\n    y()']}]
        target = copy.deepcopy(source)
        target[0]['c'][1] = 'if x:\ny()'
        self.assertNotEqual(semantic_signature(source)['code_blocks'],
                            semantic_signature(target)['code_blocks'])

    def test_link_change_rejected(self):
        source = [{'t': 'Link', 'c': [['', [], []], [{'t': 'Str', 'c': 'same'}], ['#one', '']]}]
        target = copy.deepcopy(source)
        target[0]['c'][2][0] = '#two'
        self.assertNotEqual(semantic_signature(source)['links'], semantic_signature(target)['links'])

    def test_inline_code_breaking_roundtrips_escape_characters(self):
        executable = Path.home() / 'AppData/Local/Pandoc/pandoc.exe'
        original = {'pandoc-api-version': [1, 23, 1, 1], 'meta': {}, 'blocks': [
            {'t': 'Para', 'c': [code('p(40)=41^2 and values[1:3] and path/to_file.py')]}]}
        transformed = print_document(original)
        tex = pandoc(executable, ['-f', 'json', '-t', 'latex'], json.dumps(transformed).encode())
        restored = json.loads(pandoc(executable, ['-f', 'latex', '-t', 'json'], tex))
        self.assertEqual(semantic_signature(original['blocks']), semantic_signature(restored['blocks']))

    def test_current_native_exports(self):
        root = Path(__file__).resolve().parents[2]
        for language in ('id', 'en'):
            with self.subTest(language=language):
                work = root / 'outputs/b80-format-repair-v1' / language
                receipt = json.loads((work / 'SOURCE_EXPORT_RECEIPT.json').read_text(encoding='utf-8'))
                self.assertTrue(all(receipt['semantic_roundtrip'].values()))
                self.assertEqual(receipt['tex_sha256'], hashlib.sha256((work / f'01-b80-{language}.tex').read_bytes()).hexdigest())
                corrected = work / f'03-b80-{language}.epub'
                self.assertEqual(receipt['epub_repair']['corrected_sha256'], hashlib.sha256(corrected.read_bytes()).hexdigest())
                with zipfile.ZipFile(corrected) as target, zipfile.ZipFile(root / 'outputs/b80-formats-20261003' / f'{language}.epub') as source:
                    opf = xml(target.read('EPUB/content.opf'))
                    uid = opf.xpath('./o:metadata/dc:identifier/text()', namespaces=NS)[0]
                    ncx = xml(target.read('EPUB/toc.ncx'))
                    self.assertEqual(uid, ncx.xpath('.//*[local-name()="meta"][@name="dtb:uid"]/@content')[0])
                    for name in source.namelist():
                        if name.startswith('EPUB/text/ch') and name != 'EPUB/text/ch007.xhtml':
                            self.assertEqual(source.read(name), target.read(name))


if __name__ == '__main__':
    unittest.main()
