"""Independent streamed checksum, preserved-scope and actual URL-resolver verification."""
import hashlib,io,json,re,subprocess,zipfile
from pathlib import Path
HERE=Path(__file__).resolve().parent;OUT=HERE/'central-b10-reader-20260908/revision2'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    receipt=json.loads((OUT/'NAVIGATOR_V06329_LOCAL_RECEIPT.json').read_bytes());package=OUT/receipt['name']
    with package.open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==receipt['sha256']
    with zipfile.ZipFile(package) as z:
        names=z.namelist();assert len(names)==len(set(names))==receipt['entries']
        hashes={n:h for h,n in (line.split('  ',1) for line in z.read('CHECKSUMS.sha256').decode().splitlines())}
        assert set(hashes)==set(names)-{'CHECKSUMS.sha256'}
        for n,h in hashes.items():
            with z.open(n) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==h,n
        with zipfile.ZipFile(HERE/'central-a30-reader-20260908/peta-belajar-multilingual-v0.63.28.zip') as old:
            assert len(old.namelist())==8206 and set(old.namelist())<=set(names)
        assert z.read('SOURCE_COMMIT.txt').decode().strip()==receipt['source_commit']
        projections=json.loads(z.read('PORTABLE_PROJECTION.json'))['html'];assert len(projections)==996
        for row in projections:
            data=z.read(row['path']);assert sha(data)==row['portable_sha256']
            restored,count=re.subn(rb'\n<script src="[^"]+" data-portable-navigation="v0\.63\.29"></script>\n',b'',data)
            assert count==1 and len(restored)==row['source_bytes'] and sha(restored)==row['source_sha256'],row['path']
        nested=z.read('original-sources/B10-Discrete-Mathematics-original-English-reader-source-v2.zip')
        assert sha(nested)==receipt['source_package_sha256']
        with zipfile.ZipFile(io.BytesIO(nested)) as a:
            anames=a.namelist();assert len(anames)==3260==len(set(anames))
            ah={n:h for h,n in (line.split('  ',1) for line in a.read('CHECKSUMS.sha256').decode().splitlines())}
            assert set(ah)==set(anames)-{'CHECKSUMS.sha256'}
            for n,h in ah.items():assert sha(a.read(n))==h,n
            assert sum(n.startswith('source/') for n in anames)==939
            assert sum(n.startswith('reader/') for n in anames)==2271
            for n in ['scripts/bootstrap_frozen_tools.py','scripts/build_b10_original_html_20260908.py','scripts/normalize_b10_build_metadata_20260908.py','scripts/apply_frozen_program_shell.py','REPRODUCE.md']:
                assert n in anames
            for n in ['reader/_static/pretext/css/print-worksheet.css.map','reader/_static/pretext/css/theme.css.map']:
                value=json.loads(a.read(n));assert all(p.startswith('pretext-core://132ca234495d16ffbb8ad75fc06375f991000db4/css/') for p in value['sources'])
        for n in ['A10.html','A10-en.html','A10-pengajar.html','A10-pengajar-en.html']:assert 'docs/backend/a10/'+n in names
        assert sum(n.startswith('docs/en/courses/B10/reader/') and n.endswith('.html') for n in names)==553
        script=z.read('PORTABLE_NAVIGATION.js').decode();prefix=script[:script.index('function rewrite')]+'globalThis.resolvePortable=localTarget;})();'
        program="""const vm=require('node:vm'),assert=require('node:assert/strict');let input='';process.stdin.setEncoding('utf8');process.stdin.on('data',x=>input+=x);process.stdin.on('end',()=>{const sandbox={URL,document:{currentScript:{src:'file:///offline/PORTABLE_NAVIGATION.js'},baseURI:'file:///offline/docs/en/courses/B10/reader/index.html'}};vm.createContext(sandbox);vm.runInContext(JSON.parse(input),sandbox);const r=sandbox.resolvePortable,b='https://kokunoyumeto.github.io/program-matematika-indonesia/';const cases=[[b,'file:///offline/START-HERE.html'],[b+'en/#course-B10','file:///offline/docs/en/learning-map-paired.html#course-B10'],['/id/','file:///offline/docs/id/learning-map-paired.html'],[b+'en/courses/B10/reader/','file:///offline/docs/en/courses/B10/reader/index.html'],[b+'en/courses/A30/reader/','file:///offline/docs/en/courses/A30/reader/index.html'],[b+'backend/a10/A10-en.html','file:///offline/docs/backend/a10/A10-en.html'],['https://discrete.openmathbooks.org/dmoi4/',null],[b+'unknown.html',null],['https://evil.invalid/program-matematika-indonesia/en/',null],['javascript:alert(1)',null],[b+'../secret',null]];for(const [x,y] of cases)assert.equal(r(x),y,x);console.log(JSON.stringify({passed:cases.length}));});"""
        test=subprocess.run(['node','-e',program],input=json.dumps(prefix),text=True,capture_output=True,check=True)
        count=json.loads(test.stdout)['passed']
    replay=json.loads((HERE.parent/'reader_mirrors/levin-discrete-original-en-20260908/release/B10_DISTRIBUTED_PACKAGE_REPLAY_RECEIPT.json').read_bytes())
    assert replay['state']=='pass' and replay['package_sha256']==receipt['source_package_sha256'] and replay['exact_public_reader_bytes_reproduced']
    result={'schema':'portable-navigator-final-byte-QA/1','status':'pass','navigator':receipt['name'],'bytes':package.stat().st_size,'sha256':receipt['sha256'],
        'member_hashes':len(hashes),'unique_members':len(names),'preserved_predecessor_members':8206,'reversible_html_projections':996,
        'nested_source_package_members':3260,'source_files':939,'reader_files':2271,'source_commit':receipt['source_commit'],
        'portable_url_resolver_cases':count,'distributed_package_replay':'pass; exact reader bytes reproduced','browser_opened':False}
    (OUT/'NAVIGATOR_V06329_FINAL_BYTE_QA.json').write_bytes((json.dumps(result,indent=2)+'\n').encode());print(json.dumps(result),flush=True)
if __name__=='__main__':main()
