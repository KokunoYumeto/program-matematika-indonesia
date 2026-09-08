"""Read-only package closure and actual bundled URL-resolver checks."""
import argparse,hashlib,io,json,re,subprocess,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent
OUT=HERE/'central-a30-reader-20260908'
def sha(b):return hashlib.sha256(b).hexdigest()
def run():
    receipt=json.loads((OUT/'NAVIGATOR_V06328_LOCAL_RECEIPT.json').read_bytes())
    package=OUT/receipt['name']
    with package.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==receipt['sha256']
    with zipfile.ZipFile(package) as z:
        names=z.namelist();assert len(names)==len(set(names))==8206
        hashes={n:h for h,n in (line.split('  ',1) for line in z.read('CHECKSUMS.sha256').decode().splitlines())}
        assert set(hashes)==set(names)-{'CHECKSUMS.sha256'}
        for n,h in hashes.items():
            with z.open(n) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==h,n
        projections=json.loads(z.read('PORTABLE_PROJECTION.json'))['html'];assert len(projections)==439
        for row in projections:
            data=z.read(row['path']);assert sha(data)==row['portable_sha256']
            restored,count=re.subn(rb'\n<script src="[^"]+" data-portable-navigation="v0\.63\.28"></script>\n',b'',data)
            assert count==1 and len(restored)==row['source_bytes'] and sha(restored)==row['source_sha256'],row['path']
        nested=z.read('original-sources/A30-Precalculus-2e-original-English-reader-source-v1.zip')
        assert sha(nested)==receipt['source_package_sha256']
        with zipfile.ZipFile(io.BytesIO(nested)) as a:
            anames=a.namelist();assert len(anames)==2070==len(set(anames))
            ah={n:h for h,n in (line.split('  ',1) for line in a.read('CHECKSUMS.sha256').decode().splitlines())}
            assert set(ah)==set(anames)-{'CHECKSUMS.sha256'}
            for n,h in ah.items():
                b=a.read(n);assert sha(b)==h,n
                if n.endswith(('.py','.html','.md','.txt','.json','.jsonl','.css')):
                    assert not re.search(rb'(?i)c:[/\\]users[/\\]',b),'Private profile path: '+n
            for n in ('REPRODUCE.md','scripts/build_original_reader.py','scripts/verify_original_reader.py','vendor/build_reader_en.py','vendor/reader-id.css','source-rights/COMPONENT_RIGHTS.csv','source/SOURCE_CLOSURE_MANIFEST.csv','source/MODULE_ORDER.csv','source/collections/precalculus-2e.collection.xml'):
                assert n in anames,n
            assert len([n for n in anames if n.startswith('source/modules/') and n.endswith('index.cnxml')])==87
            assert len([n for n in anames if n.startswith('reader/media/')])==1873
            assert b'rebuild/00_control/' in a.read('REPRODUCE.md')
        script=z.read('PORTABLE_NAVIGATION.js').decode()
        prefix=script[:script.index('function rewrite')]+'globalThis.resolvePortable=localTarget;})();'
        program='''const vm=require('node:vm'), assert=require('node:assert/strict');let input='';process.stdin.setEncoding('utf8');process.stdin.on('data',x=>input+=x);process.stdin.on('end',()=>{const sandbox={URL,document:{currentScript:{src:'file:///offline/PORTABLE_NAVIGATION.js'},baseURI:'file:///offline/docs/en/courses/A30/reader/index.html'}};vm.createContext(sandbox);vm.runInContext(JSON.parse(input),sandbox);const r=sandbox.resolvePortable,b='https://kokunoyumeto.github.io/program-matematika-indonesia/';const cases=[[b,'file:///offline/START-HERE.html'],[b+'en/#course-A30','file:///offline/docs/en/learning-map-paired.html#course-A30'],['/id/','file:///offline/docs/id/learning-map-paired.html'],[b+'en/courses/A30/reader/','file:///offline/docs/en/courses/A30/reader/index.html'],[b+'en/courses/A30/reader/print.html','file:///offline/docs/en/courses/A30/reader/print.html'],[b+'id-ID/courses/A10/reader/','file:///offline/docs/id-ID/courses/A10/reader/index.html'],['https://openstax.org/books/precalculus-2e/pages/1-introduction-to-functions',null],[b+'unknown.html',null],['https://evil.invalid/program-matematika-indonesia/en/',null],['javascript:alert(1)',null],[b+'../secret',null]];for(const [x,y] of cases)assert.equal(r(x),y,x);console.log(JSON.stringify({passed:cases.length}));});'''
        test=subprocess.run(['node','-e',program],input=json.dumps(prefix),text=True,capture_output=True,check=True)
        count=json.loads(test.stdout)['passed']
    result={'schema':'portable-navigator-final-byte-QA/1','status':'pass','navigator':receipt['name'],'bytes':package.stat().st_size,'sha256':receipt['sha256'],'member_hashes':8205,'unique_members':8206,'reversible_html_projections':439,'nested_source_package_members':2070,'source_cnxml_modules':87,'source_assets':1873,'portable_url_resolver_cases':count,'private_profile_path_scan':'pass for nested source/reader code and text','browser_opened':False,'reproduction_ingredients':'present; exact layout and commands included; no new independent rebuild claimed'}
    (OUT/'NAVIGATOR_V06328_FINAL_BYTE_QA.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--artifacts',type=Path,default=OUT);a=p.parse_args();OUT=a.artifacts.resolve();run()
