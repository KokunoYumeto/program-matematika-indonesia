"""Bounded streaming successor builder; no network or owner-tree writes."""
from pathlib import Path, PurePosixPath
import hashlib
import json
import posixpath
import subprocess
import zipfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent / 'd100-capability-v1-worktree'
OUT = HERE / 'central-a10-reader-20260908'
COMMIT = 'a593c3b32eea860c3f1a7d7009093cc4ca2c17d4'
BASE = '4cfcc7e106ce1e99bbd0a7260a297d878a793c5a'
OLD = HERE / 'central-v0.63.26-candidate/peta-belajar-multilingual-v0.63.26.zip'
DEST = OUT / 'peta-belajar-multilingual-v0.63.27.zip'
CHECKSUM = 'CHECKSUMS.sha256'
MARKER = 'SOURCE_COMMIT.txt'
ALIASES={f'docs/backend/{course}/data/claim-boundary.json':f'docs/backend/{course}/claim-boundary.json' for course in ('a20','a30','b90')}

def portable_script(names):
    # Only exact ZIP members may replace a canonical hosted link. External and
    # unbundled URLs retain their original destination, including publisher URLs.
    members=json.dumps(sorted(n for n in names if n.startswith('docs/')),separators=(',',':'))
    return ('''(function(){"use strict";
const members=new Set(MEMBERS);
const canonical=new URL("https://kokunoyumeto.github.io/program-matematika-indonesia/");
const root=new URL("./",document.currentScript.src);
function localTarget(raw){
 if(/^\\/(id|en)\\/(?:index\\.html)?(?:[?#].*)?$/.test(raw))raw=canonical.href+raw.slice(1);
 let u;try{u=new URL(raw,document.baseURI);}catch{return null;}
 if(u.origin!==canonical.origin||!u.pathname.startsWith(canonical.pathname))return null;
 let part=u.pathname.slice(canonical.pathname.length);
 if(part===""||part==="index.html")return new URL("START-HERE.html"+u.search+u.hash,root).href;
 if(/^(id|en)\\/(index\\.html)?$/.test(part))part=part.split("/")[0]+"/learning-map-paired.html";
 else if(part.endsWith("/"))part+="index.html";
 if(!members.has("docs/"+part))return null;
 return new URL("docs/"+part+u.search+u.hash,root).href;
}
function rewrite(a){const old=a.getAttribute("href");if(!old)return;const next=localTarget(old);if(next){a.dataset.onlineHref=old;a.setAttribute("href",next);}}
document.querySelectorAll("a[href]").forEach(rewrite);
new MutationObserver(function(changes){for(const change of changes)for(const node of change.addedNodes){if(node.nodeType!==1)continue;if(node.matches("a[href]"))rewrite(node);node.querySelectorAll("a[href]").forEach(rewrite);}}).observe(document.documentElement,{childList:true,subtree:true});
document.addEventListener("click",function(e){const a=e.target.closest&&e.target.closest("a[href]");if(a)rewrite(a);},true);
const banner=document.createElement("nav");banner.setAttribute("aria-label","Offline program navigation");
banner.style.cssText="font:1rem/1.5 system-ui,sans-serif;padding:1rem;border:1px solid #777;margin:1rem;background:#fff;color:#111";
for(const [label,path]of [["Program / Mulai","START-HERE.html"],["Bahasa Indonesia","docs/id/learning-map-paired.html"],["English","docs/en/learning-map-paired.html"]]){
 const a=document.createElement("a");a.textContent=label;a.href=new URL(path,root).href;a.style.marginRight="1rem";banner.append(a);
}
if(document.body){document.body.prepend(banner);document.body.append(banner.cloneNode(true));}
})();\n'''.replace('MEMBERS',members)).encode()

START=b'''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Mathematics program / Program matematika</title><style>body{font:1.1rem/1.6 system-ui,sans-serif;max-width:60rem;margin:auto;padding:2rem}a{color:#124ea1}li{margin:.7rem 0}</style><h1>Mathematics program / Program matematika</h1><p>Extract the entire ZIP before opening this page. / Ekstrak seluruh ZIP sebelum membuka halaman ini.</p><ul><li><a href="docs/id/learning-map-paired.html" lang="id">Mulai belajar dalam Bahasa Indonesia</a></li><li><a href="docs/en/learning-map-paired.html">Start learning in English</a></li><li><a href="docs/id-ID/courses/A10/reader/index.html">A10: Aljabar Dasar / Elementary Algebra - 82 Indonesian modules</a></li><li><a href="docs/id/learning-map-paired.html#course-B95">B95: introductory statistics / statistika pengantar</a></li><li><a href="docs/id/learning-map-paired.html#course-C140">C140: mathematical statistics / statistika matematika</a></li></ul><h2>Offline and online / Luring dan daring</h2><p>The paired learning maps and A10 reader open directly from these extracted files. Included central readers are linked locally. Original publishers, DOI downloads, and resources not contained in this ZIP still need internet access. A local copy does not imply every embedded third-party service works offline.</p><p lang="id">Peta belajar berpasangan dan pembaca A10 dapat dibuka langsung dari berkas hasil ekstraksi. Tautan pembaca pusat yang tersedia dalam ZIP diarahkan ke salinan lokal. Situs penerbit asli, unduhan DOI, dan sumber di luar ZIP tetap memerlukan internet.</p><p>Some interactive tools and the standard id/index.html and en/index.html pages use JavaScript modules. Serve this folder through a local HTTP server for those features; the paired maps above do not require one. Source and license notices remain in each course. Every reading page includes links back to the program.</p><p><a href="https://kokunoyumeto.github.io/program-matematika-indonesia/">Current online program</a> - <a href="https://doi.org/10.5281/zenodo.22059707">Preserved versions</a></p></html>'''

def digest(path, algorithm='sha256'):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, algorithm).hexdigest()

def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT)

def safe(name):
    return bool(name) and not name.startswith('/') and '\\' not in name and ':' not in name and '..' not in PurePosixPath(name).parts

def blob_reader():
    return subprocess.Popen(['git','cat-file','--batch'],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE)

def blob(pipe,name):
    pipe.stdin.write((COMMIT+':'+name+'\n').encode()); pipe.stdin.flush()
    header=pipe.stdout.readline().decode().rstrip()
    if header.endswith(' missing'):
        return None
    oid,kind,size=header.split(); assert kind=='blob'
    data=pipe.stdout.read(int(size)); assert len(data)==int(size) and pipe.stdout.read(1)==b'\n'
    assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==oid
    return data

def build(destination):
    changed=git('diff','--name-only','--diff-filter=ACMRT','-z',BASE,COMMIT,'--','docs','backend','scripts','package.json','.gitattributes','.openai','README.md').decode().split('\0')
    changed=set(filter(None,changed))
    with zipfile.ZipFile(OLD) as source:
        old_names=source.namelist(); assert len(old_names)==len(set(old_names))
        old_checks=dict((n,h) for h,n in (line.split('  ',1) for line in source.read(CHECKSUM).decode().splitlines()))
        assert set(old_checks)==set(old_names)-{CHECKSUM}
        names=sorted((set(old_names)|changed|set(ALIASES)|{'PORTABLE_NAVIGATION.js'})-{CHECKSUM})
        assert all(safe(n) for n in names)
        pipe=blob_reader(); rows={}; projections=[]; provenance={'inherited_unchanged':0,'refreshed':0,'added':0}
        try:
            with zipfile.ZipFile(destination,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9,allowZip64=True) as target:
                def add(name,data):
                    info=zipfile.ZipInfo(name,(2026,9,8,0,0,0)); info.create_system=3; info.external_attr=0o100644<<16
                    target.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=9)
                    rows[name]={'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}
                for number,name in enumerate(names):
                    prior=source.read(name) if name in old_checks else None
                    if prior is not None: assert hashlib.sha256(prior).hexdigest()==old_checks[name],name
                    if name==MARKER: data=(COMMIT+'\n').encode()
                    elif name=='START-HERE.html': data=START
                    elif name=='PORTABLE_NAVIGATION.js': data=portable_script(names)
                    else: data=blob(pipe,ALIASES.get(name,name))
                    if data is None: data=prior
                    assert data is not None,name
                    if prior==data: provenance['inherited_unchanged']+=1
                    elif prior is None: provenance['added']+=1
                    else: provenance['refreshed']+=1
                    if prior!=data and PurePosixPath(name).suffix.lower() in {'.html','.js','.json','.jsonl','.csv','.md','.py','.txt','.mjs'}:
                        assert b'c:/users/' not in data.lower() and b'c:\\users\\' not in data.lower(), 'Unsanitized profile path: '+name
                    if name.startswith('docs/') and name.endswith('.html'):
                        before=hashlib.sha256(data).hexdigest(); before_bytes=len(data)
                        rel=posixpath.relpath('PORTABLE_NAVIGATION.js',posixpath.dirname(name))
                        injection=('\n<script src="'+rel+'" data-portable-navigation="v0.63.27"></script>\n').encode()
                        at=data.lower().rfind(b'</body>')
                        data=data[:at]+injection+data[at:] if at>=0 else data+injection
                        projections.append({'path':name,'source_bytes':before_bytes,'source_sha256':before,'portable_bytes':len(data),'portable_sha256':hashlib.sha256(data).hexdigest(),'change':'one additive navigation script; source body unchanged'})
                    add(name,data)
                    if number%1000==0: print(json.dumps({'built':number,'total':len(names)}),flush=True)
                add('PORTABLE_PROJECTION.json',(json.dumps({'schema':'portable-navigation-projection/1','source_commit':COMMIT,'html':projections,'source_bound_aliases':ALIASES,'mathematical_content_changed':False,'external_links_preserved':True},indent=2)+'\n').encode())
                add(CHECKSUM,''.join(v['sha256']+'  '+n+'\n' for n,v in sorted(rows.items())).encode())
        finally:
            pipe.stdin.close(); pipe.stdout.close(); pipe.wait(timeout=30)
    with zipfile.ZipFile(destination) as archive:
        assert archive.testzip() is None
        assert len(archive.namelist())==len(rows) and len(set(archive.namelist()))==len(rows)
        for name,row in rows.items():
            data=archive.read(name); assert len(data)==row['bytes'] and hashlib.sha256(data).hexdigest()==row['sha256'],name
        assert archive.read(MARKER)==(COMMIT+'\n').encode()
        assert set(old_names)<=set(archive.namelist()),'Inherited member lost'
        for required in ('docs/id/learning-map-paired.html','docs/en/learning-map-paired.html','docs/id-ID/courses/A10/reader/index.html','backend/course-capsule-v1/adapters/b95-capability-v1/build/B95_THIN_CAPABILITY_METADATA_V1.zip','backend/course-capsule-v1/adapters/c140-capability-v1/build/C140_COMPLETE_THIN_CAPABILITY_METADATA_V1.zip'):
            assert required in rows,required
        a10=json.loads(archive.read('docs/id-ID/courses/A10/A10_READER_MIRROR_MANIFEST_V1.json'))
        assert a10['validation']['modules']==82
    return {'name':destination.name,'bytes':destination.stat().st_size,'sha256':digest(destination),'md5':digest(destination,'md5'),'entries':len(rows),'checksum_rows':len(rows)-1,'uncompressed_bytes':sum(r['bytes'] for r in rows.values()),'provenance':provenance,'source_commit':COMMIT,'status':'pass','inherited_member_count':len(old_names),'new_source_file_count':len(changed)}

if __name__=='__main__':
    assert digest(OLD)=='40dac0dd62a6e07603770dbfd8dc85068fae35df198ca11f1b5aeb462dbd17d5'
    assert git('rev-parse',COMMIT+'^{tree}').decode().strip()=='e4cbace025d312b1b3443a089beb258317ed50c2'
    assert not DEST.exists(),'Refuse to overwrite candidate'
    result=build(DEST)
    replay=OUT / 'navigator-v06327-replay.tmp.zip'
    assert not replay.exists()
    again=build(replay)
    assert (result['bytes'],result['sha256'])==(again['bytes'],again['sha256'])
    replay.unlink()  # Exact task-created temporary deterministic replay only.
    result['deterministic_builds']=2
    (OUT/'NAVIGATOR_V06327_LOCAL_RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result),flush=True)
