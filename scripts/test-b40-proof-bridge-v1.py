"""Check sealed lesson identity, navigation, MathML and isolated source replay."""
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path, PurePosixPath
import subprocess
import sys
import tempfile
from urllib.parse import urlsplit
import zipfile

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'docs/en/readers/basis-projection-bridge/'
ORIGIN = 'https://kokunoyumeto.github.io/program-matematika-indonesia/'
class Page(HTMLParser):
    def __init__(self):
        super().__init__(); self.hrefs=[]; self.ids=[]; self.math=0; self.nav=0; self.language=None
    def handle_starttag(self, tag, attrs):
        values=dict(attrs)
        if tag=='a': self.hrefs.append(values.get('href',''))
        if 'id' in values: self.ids.append(values['id'])
        if tag=='html': self.language=values.get('lang')
        if tag=='math': self.math+=1
        if tag=='nav': self.nav+=1
        assert tag!='script', 'Reader must not depend on remote JavaScript'

def validate(root=ROOT):
    directory=root/PREFIX
    receipt=json.loads((directory/'READER_MANIFEST.json').read_bytes())
    expected={'from-bases-to-projections-r2.md','ADAPTATION_R2.json','HEFFERON-PROOFS.tex','HEFFERON-LICENSE.txt','HEFFERON-ACKNOWLEDGEMENTS.txt','SOURCE_BINDINGS.json','00-basis-projection.tex','01-editable-source.zip','index.html','README.md','BUILD_INPUTS.json'}
    assert len(receipt['files'])==len(expected)
    assert {r['path'] for r in receipt['files']}==expected
    for row in receipt['files']:
        value=(directory/row['path']).read_bytes()
        assert len(value)==row['bytes'] and hashlib.sha256(value).hexdigest()==row['sha256'], row['path']
    assert receipt['source_sha256']=='131f01c7611a96c60a0dfdaf08c7b17e0f1a864dd371968ecd858b19f4e49652'
    assert receipt['formula_count']==167
    assert receipt['html_mathml_source_tex_exact'] and receipt['direct_latex_formula_replay_exact']
    assert not receipt['whole_course_verified'] and not receipt['hermitian_dependency_closed'] and not receipt['independent_proof_review']
    raw=(directory/'index.html').read_bytes(); page=Page(); page.feed(raw.decode())
    assert page.language=='en' and page.math==167 and page.nav==2
    assert len(page.ids)==len(set(page.ids))
    assert 'extending-a-basis-and-choosing-a-complement' in page.ids
    assert 'the-exact-step-used-in-representation-theory' in page.ids
    for route in ['en/programme/#core-B40','en/programme/#advanced-RT-FIN','id/programme/#core-B40']:
        assert page.hrefs.count(ORIGIN+route)==2
    assert page.hrefs.index('00-basis-projection.tex')<page.hrefs.index('01-editable-source.zip')
    for link in page.hrefs:
        parsed=urlsplit(link)
        if not parsed.scheme and parsed.path:
            candidate=(directory/parsed.path).resolve()
            assert candidate.is_relative_to(directory.resolve()) and candidate.is_file(), link
    return {'state':'pass','files':[{'document':PREFIX+'index.html','bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}],'source_formula_count':167,'full_course_verified':False}

if __name__=='__main__':
    result=validate()
    if '--replay' in sys.argv:
        out=ROOT/'outputs'; out.mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix='b40-proof-bridge-replay-',dir=out) as temporary:
            target=Path(temporary).resolve(); assert target.is_relative_to(out.resolve())
            with zipfile.ZipFile(ROOT/PREFIX/'01-editable-source.zip') as archive:
                assert len(archive.infolist())==17 and sum(r.file_size for r in archive.infolist())<1024*1024
                for row in archive.infolist():
                    name=PurePosixPath(row.filename)
                    assert not name.is_absolute() and '..' not in name.parts and '\\' not in row.filename and ':' not in row.filename
                archive.extractall(target)
            subprocess.run([sys.executable,'-B',str(target/'scripts/build-b40-proof-bridge-v1.py')],cwd=target,check=True,capture_output=True,timeout=30)
            original=json.loads((ROOT/PREFIX/'READER_MANIFEST.json').read_bytes())
            for row in original['files']:
                assert (target/PREFIX/row['path']).read_bytes()==(ROOT/PREFIX/row['path']).read_bytes(), row['path']
            assert (target/PREFIX/'READER_MANIFEST.json').read_bytes()==(ROOT/PREFIX/'READER_MANIFEST.json').read_bytes()
            validate(target)
            damaged=target/PREFIX/'index.html'; damaged.write_bytes(damaged.read_bytes()+b'changed')
            try: validate(target)
            except AssertionError: pass
            else: raise AssertionError('Changed reader body was accepted')
        result.update(isolated_zip_replay='byte_identical',tampered_reader_rejected=True)
    print(json.dumps(result))
