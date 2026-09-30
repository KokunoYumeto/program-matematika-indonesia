"""Test actual bilingual CLP term consumers and isolated editable-source replay."""
import argparse
import copy
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import urlsplit
import zipfile

spec=importlib.util.spec_from_file_location('view',Path(__file__).with_name('build-clp1-term-view-v1.py'))
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
SKIP_REPLAY='--skip-replay' in sys.argv
if SKIP_REPLAY:sys.argv.remove('--skip-replay')

class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=[];self.hrefs=[];self.cards=[];self.lang=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if 'href' in a:self.hrefs.append(a['href'])
        if tag=='html':self.lang=a.get('lang')
        if tag=='article':self.cards.append(a)

class ViewTests(unittest.TestCase):
    def test_all_terms_and_both_languages(self):
        data=b.load()
        for en in [False,True]:
            raw=b.render(data,en).decode();page=Page();page.feed(raw)
            self.assertEqual(page.lang,'en' if en else 'id')
            self.assertEqual(len(page.cards),24)
            self.assertEqual(len(page.ids),len(set(page.ids)))
            self.assertEqual(sum(c['data-corrected']=='true' for c in page.cards),3)
            for t in data['terms']:
                self.assertIn(t['id'],page.ids)
                self.assertIn(b.html.escape(t['source_term']),raw)
                self.assertIn(b.html.escape(t['target_term']),raw)
            for href in page.hrefs:
                if href.startswith('#'):self.assertIn(href[1:],page.ids)
            self.assertIn('occurrence-level coverage'.lower() if en else 'setiap kemunculan',raw.lower())
            self.assertIn('gpt-6-astra',raw);self.assertIn('CC BY-NC-SA 4.0',raw)
            self.assertNotIn('fetch(',raw);self.assertNotIn('localStorage',raw)
    def test_exact_public_input_copies(self):
        for f in (b.BASE/'input').iterdir():
            self.assertEqual(f.read_bytes(),(b.OUT/'clp1-terms-data'/f.name).read_bytes())
    def test_manifest_binds_every_expected_file(self):
        v=json.loads((b.OUT/'B20.terms.validation.json').read_bytes())
        expected={'B20.terms.html','B20.terms.en.html','B20.terms.json','clp1-terms-source-v1.zip'}|{'clp1-terms-data/'+f.name for f in (b.BASE/'input').iterdir()}
        self.assertEqual({r['path'] for r in v['files']},expected)
        self.assertEqual(len(v['files']),len(expected))
        for r in v['files']:
            raw=(b.OUT/r['path']).read_bytes()
            # Hosted HTML can contain a separately verified reversible program shell.
            if not r['path'].endswith('.html'):
                self.assertEqual(b.p.fact(raw),{k:r[k] for k in ['bytes','sha256']})
        self.assertFalse(v['semantic_canon_review']);self.assertFalse(v['book_modified'])
        self.assertEqual(v['source_projection'],b.p.fact((b.BASE/'projection.json').read_bytes()))
    def test_isolated_source_replay(self):
        if SKIP_REPLAY:self.skipTest('Nested replay')
        original=(b.OUT/'clp1-terms-source-v1.zip').read_bytes()
        with tempfile.TemporaryDirectory(prefix='clp-term-replay-') as folder:
            root=Path(folder)
            with zipfile.ZipFile(b.OUT/'clp1-terms-source-v1.zip') as z:
                self.assertIsNone(z.testzip());self.assertEqual(len(z.namelist()),len(set(z.namelist())))
                self.assertTrue(all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist()))
                z.extractall(root)
            for name in ['B20.terms.html','B20.terms.en.html']:
                path=root/'docs/backend/clp'/name;page=Page();page.feed(path.read_text(encoding='utf-8'))
                for href in page.hrefs:
                    if not href.startswith('#') and not urlsplit(href).scheme:
                        self.assertTrue((path.parent/href).is_file(),href)
            for script,args in [('build-clp1-term-view-v1.py',[]),('test-clp1-native-terminology-v1.py',[]),('test-clp1-term-view-v1.py',['--skip-replay'])]:
                r=subprocess.run([sys.executable,'-B',str(root/'scripts'/script),*args],cwd=root,capture_output=True,text=True,timeout=30)
                self.assertEqual(r.returncode,0,r.stderr)
            self.assertEqual(original,(root/'docs/backend/clp/clp1-terms-source-v1.zip').read_bytes())
            for name in ['B20.terms.html','B20.terms.en.html','B20.terms.json','B20.terms.validation.json']:
                if name.endswith('.html'):
                    en='.en.' in name;self.assertEqual((root/'docs/backend/clp'/name).read_bytes(),b.render(b.load(),en))
                else:self.assertEqual((root/'docs/backend/clp'/name).read_bytes(),(b.OUT/name).read_bytes())
            r=subprocess.run(['node',str(root/'scripts/test-clp1-term-ui-v1.mjs')],cwd=root,capture_output=True,text=True,timeout=10)
            self.assertEqual(r.returncode,0,r.stderr)

if __name__=='__main__':unittest.main()
