"""Bounded Chinese-starter checks, including exact offline source replay."""
import argparse
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit
import zipfile

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT/'docs/zh'


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids, self.hrefs, self.kinds, self.lang = [], [], [], None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.append(a['id'])
        if 'href' in a:
            self.hrefs.append(a['href'])
        if 'data-resource-kind' in a:
            self.kinds.append(a['data-resource-kind'])
        if tag == 'html':
            self.lang = a.get('lang')
        assert tag not in ['script', 'iframe'], 'Starter must work without scripts or embedded tracking'
        assert not any(k.startswith('on') for k in a), 'No inline event handlers'


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--standalone', action='store_true')
    parser.add_argument('--skip-replay', action='store_true')
    args = parser.parse_args()
    data = json.loads((SITE/'catalog.json').read_bytes())
    assert data['schema'] == 'chinese-program-starter/1'
    assert data['complete_curriculum'] is False and data['canonical_role_admissions'] == []
    assert data['integration_provenance']['model'] == 'gpt-6-astra'
    assert data['integration_provenance']['effort'] == 'ultra'
    assert {r['id'] for r in data['resources']} == {'algebra-1', 'algebra-2', 'openlogic', 'algebra-trigonometry', 'calculus-1'}
    page = Page()
    text = (SITE/'index.html').read_text(encoding='utf-8')
    page.feed(text)
    assert page.lang == 'zh-Hans-CN'
    assert len(page.ids) == len(set(page.ids))
    assert page.kinds.count('released-translation') == 3 and page.kinds.count('chinese-original') == 2
    for href in page.hrefs:
        url = urlsplit(href)
        if url.scheme:
            assert url.scheme == 'https'
            assert url.hostname in {'kokunoyumeto.github.io','github.com','raw.githubusercontent.com','zenodo.org'}
        elif href.startswith('#'):
            assert href[1:] in page.ids
        elif href in ['../id/', '../en/']:
            if not args.standalone:
                assert (SITE/href/'index.html').is_file()
        else:
            target = SITE/href
            if target.is_dir():
                target /= 'index.html'
            assert target.is_file(), href
    assert '起步入口' in text and '课程衔接、章节对应和学习工具还将逐步补齐' in text
    assert '不是本项目的 AI 译文' in text
    for r in data['resources']:
        assert r['evidence'] and r['license'] in ['CC BY 4.0','CC BY-NC-SA 4.0']
        if r['kind'] == 'chinese-original':
            assert len(r['commit']) == 40 and r['commit'] in r['pdf']['url']
            assert r['commit'] in r['tex_master']['url'] and r['commit'] in r['source_tree']
        else:
            assert r['release_tag'] in r['pdf']['browser_download_url']
            assert r['editable_sources'] and r['pdf']['digest'].startswith('sha256:')
    receipt = json.loads((SITE/'build-receipt.json').read_bytes())
    for row in receipt['files']:
        body = (SITE/row['path']).read_bytes()
        assert len(body) == row['bytes'] and hashlib.sha256(body).hexdigest() == row['sha256']
    if not args.standalone:
        for locale in ['en','id']:
            for name in ['index.html','learning-map.html','learning-map-paired.html']:
                existing = (ROOT/'docs'/locale/name).read_text(encoding='utf-8')
                assert existing.count('data-chinese-starter="v1"') == 1
                assert '中文（起步版）' in existing
        assert 'data-chinese-starter="v1"' in (ROOT/'docs/index.html').read_text(encoding='utf-8')
        contract = json.loads((ROOT/'backend/authority/central-reader-navigation-v1.json').read_bytes())
        registered = [r for r in contract['generic_surfaces'] if r['document'] == 'docs/zh/index.html']
        assert registered == [{'document':'docs/zh/index.html','state':'additive-chinese-starter','navigation_required':False,'navigation_provider':'chinese-starter-v1'}]
        assert set(contract['interfaces']) == {'id','en'}
    if not args.skip_replay:
        with tempfile.TemporaryDirectory(prefix='chinese-starter-replay-') as tmp:
            root = Path(tmp)
            with zipfile.ZipFile(SITE/'chinese-starter-source-v1.zip') as z:
                assert z.testzip() is None
                assert z.namelist() == sorted(receipt['source_members'])
                assert all('..' not in Path(n).parts and not Path(n).is_absolute() for n in z.namelist())
                z.extractall(root)
            for script, options in [('build-chinese-starter-v1.py', []), ('test-chinese-starter-v1.py', ['--standalone','--skip-replay'])]:
                result = subprocess.run([sys.executable,'-B',str(root/'scripts'/script),*options],cwd=root,capture_output=True,text=True,timeout=30)
                assert result.returncode == 0, result.stderr
            for row in receipt['files']:
                assert (root/'docs/zh'/row['path']).read_bytes() == (SITE/row['path']).read_bytes()
            assert (root/'docs/zh/build-receipt.json').read_bytes() == (SITE/'build-receipt.json').read_bytes()
    print(json.dumps({'status':'pass','resources':5,'translated_books':3,'chinese_original_volumes':2,
                      'new_course_admissions':0,'source_replay':not args.skip_replay,'reciprocal_navigation':not args.standalone}))


if __name__ == '__main__':
    main()
