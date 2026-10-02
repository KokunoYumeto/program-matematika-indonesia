"""Check source identity, reader routes, formula transport and isolated replay."""
import hashlib, json, subprocess, sys, tempfile, zipfile
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parents[1]
PREFIX=Path('docs/en/readers/finite-hermitian-spaces')
SOURCE=Path('backend/cross-programme-v1/providers/finite-hermitian-r1')
class Reader(HTMLParser):
    def __init__(self): super().__init__(); self.ids=[]; self.links=[]; self.math=0; self.lang=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        assert tag!='script'
        if 'id' in a: self.ids.append(a['id'])
        if tag=='a': self.links.append(a.get('href',''))
        if tag=='math': self.math+=1
        if tag=='html': self.lang=a.get('lang')

def validate(root):
    directory=root/PREFIX
    manifest=json.loads((directory/'READER_MANIFEST.json').read_bytes())
    assert manifest['schema']=='finite-hermitian-reader/1'
    assert manifest['source_sha256']=='a8547e894bab4c4eb862086af6fc078519945e11aa9976ba823bde94cbef551c'
    assert manifest['formula_count']==144
    assert manifest['mathml_formula_identity'] and manifest['direct_latex_formula_identity']
    assert manifest['language']=='en' and manifest['licence']=='CC-BY-SA-4.0'
    assert manifest['independent_review'] is False and manifest['whole_course_verified'] is False
    expected={'finite-hermitian-spaces.md','SOURCE_REVIEW.json','index.html','00-finite-hermitian.tex','README.md','BUILD_INPUTS.json','01-editable-source.zip'}
    assert {r['path'] for r in manifest['files']}==expected and len(manifest['files'])==len(expected)
    for row in manifest['files']:
        raw=(directory/row['path']).read_bytes()
        assert len(raw)==row['bytes'] and hashlib.sha256(raw).hexdigest()==row['sha256'],row['path']
    proof=(root/SOURCE/'finite-hermitian-spaces.md').read_bytes()
    assert hashlib.sha256(proof).hexdigest()==manifest['source_sha256']
    assert proof==(directory/'finite-hermitian-spaces.md').read_bytes()
    page=Reader();page.feed((directory/'index.html').read_text(encoding='utf-8'))
    assert page.lang=='en' and page.math==144 and len(page.ids)==len(set(page.ids))
    for anchor in ['gramschmidt-with-the-coefficients-in-the-correct-order','orthogonal-projection-and-decomposition','the-two-uses-in-representation-theory','exercises-with-solutions']:
        assert anchor in page.ids,anchor
    assert page.links.index('00-finite-hermitian.tex')<page.links.index('01-editable-source.zip')
    for link in page.links:
        parsed=urlsplit(link)
        if parsed.scheme: continue
        if parsed.path.startswith('../'):
            assert link=='../basis-projection-bridge/#extending-a-basis-and-choosing-a-complement'
        elif parsed.path:
            assert '/' not in parsed.path and (directory/parsed.path).is_file(),link
        if not parsed.path and parsed.fragment: assert parsed.fragment in page.ids
    return manifest

if __name__=='__main__':
    manifest=validate(ROOT)
    with tempfile.TemporaryDirectory(prefix='hermitian-reader-') as temporary:
        target=Path(temporary).resolve()
        with zipfile.ZipFile(ROOT/PREFIX/'01-editable-source.zip') as archive:
            assert len(archive.infolist())==9 and sum(r.file_size for r in archive.infolist())<400000
            for row in archive.infolist():
                p=PurePosixPath(row.filename)
                assert not p.is_absolute() and '..' not in p.parts and ':' not in row.filename and '\\' not in row.filename
            archive.extractall(target)
        subprocess.run([sys.executable,'-B',str(target/'scripts/build-finite-hermitian-reader-v1.py')],check=True,capture_output=True,timeout=30,cwd=target)
        for name in [r['path'] for r in manifest['files']]+['READER_MANIFEST.json']:
            assert (ROOT/PREFIX/name).read_bytes()==(target/PREFIX/name).read_bytes(),name
        validate(target)
        damaged=target/PREFIX/'index.html';damaged.write_bytes(damaged.read_bytes()+b'changed')
        try: validate(target)
        except AssertionError: pass
        else: raise AssertionError('Changed reader accepted')
        review=target/SOURCE/'SOURCE_REVIEW.json';obj=json.loads(review.read_bytes());obj['lesson_sha256']='0'*64;review.write_text(json.dumps(obj),encoding='utf-8')
        result=subprocess.run([sys.executable,'-B',str(target/'scripts/build-finite-hermitian-reader-v1.py')],capture_output=True,timeout=30,cwd=target)
        assert result.returncode!=0,'Unreviewed changed proof accepted'
    print(json.dumps({'state':'pass','formulas':144,'source_replay':'byte-identical','tampered_reader_rejected':True,'wrong_proof_binding_rejected':True,'universal_math_proof_tested_by_code':False}))
