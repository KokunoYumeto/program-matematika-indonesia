"""Exact-source additive navigator; no network and no native-owner writes."""
import argparse,hashlib,importlib.util,json,posixpath,re,subprocess,zipfile
from pathlib import Path,PurePosixPath

COMMIT='e0414b237c4d4837cd5e195e543ee1884a3b8ba5'
BASE='818dafebc973a6eff1330fcf6be86db8400192fd'
PREDECESSOR_SHA='4f134980866ec0bdbf70c9281b11bde9a8ccb2e3aa68d7dd4a383055f035860e'
PACKAGE_SHA='cd3b29543cf9bec2d621105398b227e9146a301948b979b7003d504d2594b3e2'
CHECKSUM='CHECKSUMS.sha256'
PROJECTION='PORTABLE_PROJECTION.json'
PACKAGE_NAME='original-sources/B10-Discrete-Mathematics-original-English-reader-source-v2.zip'
ALIASES={f'docs/backend/{c}/data/claim-boundary.json':f'docs/backend/{c}/claim-boundary.json' for c in ('a20','a30','b90')}
def digest(p,algorithm='sha256'):
    with p.open('rb') as f:return hashlib.file_digest(f,algorithm).hexdigest()
def jb(v):return (json.dumps(v,indent=2,sort_keys=True)+'\n').encode()
def run(repo,old,package,out,helper):
    assert digest(old)==PREDECESSOR_SHA and digest(package)==PACKAGE_SHA
    assert not out.exists(),'Refuse to overwrite candidate'
    spec=importlib.util.spec_from_file_location('v27_builder',helper);base=importlib.util.module_from_spec(spec);spec.loader.exec_module(base)
    def git(*args):return subprocess.check_output(['git','-c','gc.auto=0','-c','maintenance.auto=false',*args],cwd=repo)
    assert git('rev-parse',COMMIT+'^{tree}').decode().strip()=='8657e1e7243065eb6a0ba1d775183d7c4a22c57e'
    changed=set(filter(None,git('diff','--name-only','--diff-filter=ACMRT','-z',BASE,COMMIT,'--','docs','backend','scripts','package.json','.gitattributes','.openai','README.md').decode().split('\0')))
    with zipfile.ZipFile(old) as previous:
        old_names=previous.namelist();assert len(old_names)==8206==len(set(old_names))
        old_hashes={n:h for h,n in (line.split('  ',1) for line in previous.read(CHECKSUM).decode().splitlines())}
        assert set(old_hashes)==set(old_names)-{CHECKSUM}
        names=sorted((set(old_names)|changed|set(ALIASES)|{PACKAGE_NAME})-{CHECKSUM,PROJECTION})
        assert all(base.safe(n) for n in names)
        process=subprocess.Popen(['git','-c','gc.auto=0','-c','maintenance.auto=false','cat-file','--batch'],cwd=repo,stdin=subprocess.PIPE,stdout=subprocess.PIPE)
        def blob(name):
            process.stdin.write((COMMIT+':'+name+'\n').encode());process.stdin.flush()
            header=process.stdout.readline().decode().rstrip()
            if header.endswith(' missing'):return None
            oid,kind,size=header.split();assert kind=='blob';data=process.stdout.read(int(size));assert process.stdout.read(1)==b'\n'
            assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==oid
            return data
        rows={}; projections=[];new_count=0
        try:
            with zipfile.ZipFile(out,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6,allowZip64=True) as target:
                def add(name,data):
                    assert name not in rows,name
                    info=zipfile.ZipInfo(name,(2026,9,8,0,0,0));info.create_system=3;info.external_attr=0o100644<<16
                    target.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
                    rows[name]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
                for number,name in enumerate(names,1):
                    prior=previous.read(name) if name in old_hashes else None
                    if prior is not None:assert hashlib.sha256(prior).hexdigest()==old_hashes[name],name
                    if name=='SOURCE_COMMIT.txt':data=(COMMIT+'\n').encode()
                    elif name=='START-HERE.html':
                        assert prior is not None
                        data=prior.replace(b'</ul>',b'<li><a href="docs/en/courses/B10/reader/index.html">B10: Discrete Mathematics - original English, 768 exercises and 520 supplied solutions</a></li><li><a href="'+PACKAGE_NAME.encode()+b'">Discrete Mathematics standalone reader and original-source package</a></li><li><a href="docs/backend/a10/A10-en.html">A10: Elementary Algebra learning tools - English interface</a></li></ul>',1)
                    elif name=='PORTABLE_NAVIGATION.js':data=base.portable_script(names)
                    elif name==PACKAGE_NAME:data=package.read_bytes()
                    else:data=blob(ALIASES.get(name,name))
                    if data is None:data=prior
                    assert data is not None,name
                    if prior is None:new_count+=1
                    if prior!=data and PurePosixPath(name).suffix.lower() in {'.html','.js','.json','.jsonl','.csv','.md','.py','.txt','.mjs'}:
                        assert b'c:/users/' not in data.lower() and b'c:\\users\\' not in data.lower(),'Profile path: '+name
                    if name.startswith('docs/') and name.endswith('.html'):
                        data=re.sub(rb'\n<script src="[^"]+" data-portable-navigation="v0\.63\.\d+"></script>\n',b'',data)
                        original=data;rel=posixpath.relpath('PORTABLE_NAVIGATION.js',posixpath.dirname(name))
                        insertion=('\n<script src="'+rel+'" data-portable-navigation="v0.63.29"></script>\n').encode()
                        at=data.lower().rfind(b'</body>');data=data[:at]+insertion+data[at:] if at>=0 else data+insertion
                        assert data.count(b'data-portable-navigation="v0.63.29"')==1
                        projections.append({'path':name,'source_bytes':len(original),'source_sha256':hashlib.sha256(original).hexdigest(),'portable_bytes':len(data),'portable_sha256':hashlib.sha256(data).hexdigest(),'change':'one additive navigation script; mathematical body unchanged'})
                    add(name,data)
                    if number%1000==0:print(json.dumps({'built':number,'total':len(names)}),flush=True)
                add(PROJECTION,jb({'schema':'portable-navigation-projection/1','source_commit':COMMIT,'html':projections,'source_bound_aliases':ALIASES,'mathematical_content_changed':False,'external_links_preserved':True}))
                add(CHECKSUM,''.join(r['sha256']+'  '+n+'\n' for n,r in sorted(rows.items())).encode())
        finally:process.stdin.close();process.stdout.close();process.wait(timeout=30)
    with zipfile.ZipFile(out) as z:
        assert z.testzip() is None
        assert len(z.namelist())==len(set(z.namelist()))==len(rows)
        assert set(old_names)<=set(z.namelist())
        for n,r in rows.items():
            with z.open(n) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==r['sha256'],n
            assert z.getinfo(n).file_size==r['bytes']
        assert len([n for n in rows if n.startswith('docs/en/courses/B10/reader/') and n.endswith('.html')])==553
        assert all('docs/backend/a10/'+n in rows for n in ['A10.html','A10-en.html','A10-pengajar.html','A10-pengajar-en.html'])
        assert hashlib.sha256(z.read(PACKAGE_NAME)).hexdigest()==PACKAGE_SHA
    result={'schema':'additive-portable-navigator/1','status':'pass','name':out.name,'bytes':out.stat().st_size,'sha256':digest(out),'md5':digest(out,'md5'),'entries':len(rows),'checksum_rows':len(rows)-1,'source_commit':COMMIT,'predecessor_members_preserved':len(old_names),'new_members':new_count,'html_projections':len(projections),'source_package_sha256':PACKAGE_SHA,'verification':'CRC, every member size/SHA-256, unique safe paths, all predecessor names retained, exact source commit and offline reader closure'}
    out.with_name('NAVIGATOR_V06329_LOCAL_RECEIPT.json').write_bytes(jb(result));print(json.dumps(result),flush=True)
if __name__=='__main__':
    p=argparse.ArgumentParser()
    for flag in ('repo','predecessor','b10-package','output','v27-helper'):p.add_argument('--'+flag,required=True,type=Path)
    a=p.parse_args();run(a.repo.resolve(),a.predecessor.resolve(),a.b10_package.resolve(),a.output.resolve(),a.v27_helper.resolve())
