"""Package exact B10 reader/source/runtime with portable reproduction tooling."""
from pathlib import Path,PurePosixPath
import csv,hashlib,json,re,zipfile
LOG=Path(__file__).resolve().parent
ROOT=LOG.parent/'d100-capability-v1-worktree'
WORK=LOG.parent/'reader_mirrors/levin-discrete-original-en-20260908'
RELEASE=WORK/'release'
NAME='B10-Discrete-Mathematics-original-English-reader-source-v2.zip'
TOOLS=['build_b10_original_html','render_b10_static_solution_disclosures','localize_b10_original_reader',
    'audit_b10_original_html','repair_b10_generated_permalinks','insert_b10_static_solutions',
    'index_b10_original_reader','normalize_b10_build_metadata','adapt_b10_fragment_navigation','validate_b10_final_reader']
def sha(b):return hashlib.sha256(b).hexdigest()
def jb(v):return (json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode()
def safe(name):return not PurePosixPath(name).is_absolute() and '..' not in PurePosixPath(name).parts and '\\' not in name

BOOTSTRAP=r'''"""Expand only hash-verified packaged tools; install CSS deps separately."""
from pathlib import Path,PurePosixPath
import hashlib,json,tarfile,zipfile
ROOT=Path(__file__).resolve().parent.parent
def safe(name):return not PurePosixPath(name).is_absolute() and '..' not in PurePosixPath(name).parts and '\\' not in name
def put(root,name,b):
    assert safe(name);p=root/name;assert p.resolve().is_relative_to(root.resolve())
    p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
def main():
    # Verify the entire distributed archive's extracted file set before tool extraction.
    for line in (ROOT/'CHECKSUMS.sha256').read_text().splitlines():
        expected,name=line.split('  ',1);assert safe(name)
        with (ROOT/name).open('rb') as f:assert hashlib.file_digest(f,'sha256').hexdigest()==expected,name
    wheel=ROOT/'tooling/wheels/pretext-2.27.0-py3-none-any.whl'
    with zipfile.ZipFile(wheel) as z:
        for i in z.infolist():
            if not i.is_dir():put(ROOT/'tooling/pretext227',i.filename,z.read(i))
    cache=ROOT/'tooling/pretext-cache'
    with zipfile.ZipFile(ROOT/'tooling/pretext227/pretext/resources/core.zip') as z:
        for i in z.infolist():
            if not i.is_dir():put(cache/'core',i.filename.split('/',1)[1],z.read(i))
    for name in ['rs_services.xml','dist-8.2.5.tgz']:
        put(cache/'rs_cache',name,(ROOT/'tooling/runestone825'/name).read_bytes())
    for name in ['mathjax-3.2.2','prismjs-1.26.0','lunr-2.3.9']:
        folder=ROOT/'tooling/npm'/name
        with tarfile.open(folder/(name+'.tgz')) as t:
            for i in t.getmembers():
                if i.isdir():continue
                assert i.isfile() and safe(i.name)
                put(folder,i.name,t.extractfile(i).read())
    print('Frozen tools expanded. Install the pinned Python and CSS dependencies described in REPRODUCE.md.')
if __name__=='__main__':main()
'''

SHELL=r'''"""Apply the frozen, reversible program shell to the reproduced reader."""
from pathlib import Path
import hashlib,json,re
ROOT=Path(__file__).resolve().parent.parent
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    shells=json.loads((ROOT/'reproduction/NAVIGATION_SHELLS.json').read_bytes())
    source=ROOT/'output-complete/reader';dest=ROOT/'reproduced-reader'
    facts=json.loads((ROOT/'reproduction/READER_FILES.json').read_bytes())
    for row in facts:
        rel=row['path'];data=(source/rel).read_bytes()
        if rel in shells:
            shell=shells[rel];assert sha(data)==shell['source_sha256'],rel
            text=data.decode();a=list(re.finditer(r'<body\b[^>]*>',text,re.I));b=list(re.finditer(r'</body>',text,re.I))
            assert len(a)==len(b)==1
            text=text[:a[0].end()]+'\n'+shell['top']+text[a[0].end():b[0].start()]+shell['bottom']+'\n'+text[b[0].start():]
            data=text.encode()
        assert len(data)==row['bytes'] and sha(data)==row['sha256'],rel
        p=dest/rel;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
    print('Exact distributed reader reproduced:',len(facts),'files')
if __name__=='__main__':main()
'''

REPRO=r'''# Reproducing this original-English reader

The archive includes the full 939-file fourth-edition source tree, its immutable
source archive and manifests, the verified HTML reader, pinned renderer/runtime
distributions, production scripts, and the frozen central navigation shell.
No translation or new solutions were authored for this mirror.

Recorded build environment: Windows, Python 3.13.9, lxml 6.1.1, Node 22.17.0,
PreTeXt 2.27.0 and core 132ca234495d16ffbb8ad75fc06375f991000db4.
For exact byte reproduction use these versions. The reader remains platform-independent.

1. Extract the complete archive into its own directory. Run all commands there.
2. Install lxml 6.1.1 in the chosen Python environment if absent.
3. Run `python -B scripts/bootstrap_frozen_tools.py`. It verifies every distributed
   checksum before extracting the bundled tools and does not install a TeX system.
4. Run `npm ci --ignore-scripts --prefix tooling/pretext-cache/core/script/cssbuilder`.
   This is the dependency-acquisition step; it needs network access unless npm has
   the exact lockfile-bound dependencies cached. It is separate from rendering.
5. Run the pipeline below. Every source hash is checked before the HTML build;
   the build uses committed figures and committed WeBWorK representations. It
   does not fetch new questions, generate TeX, or call a remote scoring service.

```text
python -B scripts/build_b10_original_html_20260908.py --complete
python -B scripts/build_b10_original_html_20260908.py --complete --replay
python -B scripts/localize_b10_original_reader_20260908.py
python -B scripts/audit_b10_original_html_20260908.py --localized --complete
python -B scripts/repair_b10_generated_permalinks_20260908.py
python -B scripts/render_b10_static_solution_disclosures_20260908.py
python -B scripts/insert_b10_static_solutions_20260908.py
python -B scripts/index_b10_original_reader_20260908.py
python -B scripts/normalize_b10_build_metadata_20260908.py
python -B scripts/adapt_b10_fragment_navigation_20260908.py
python -B scripts/audit_b10_original_html_20260908.py --localized --complete
```

Replay the same presentation operations for the second build by appending
`--replay` to localization, audit, permalink repair, solution insertion, indexing,
normalization, and fragment adaptation, in that order. Do not rerender the static
solutions after insertion; both runs intentionally consume the same hash-bound
67-solution static projection. Then run:

```text
python -B scripts/validate_b10_final_reader_20260908.py
python -B scripts/apply_frozen_program_shell.py
```

The first command compares the independently rendered/presented outputs. The
second replays the exact navigation shell and verifies all 2,271 distributed
reader files against `reproduction/READER_FILES.json`.

Normalized build metadata is the generated index banner/timestamp, the internal
generated-assets directory spelling, and frozen-core-relative source names in
two CSS debug maps. Map mappings and embedded Sass source content are preserved.
Math, prose, source IDs,
solutions, and widgets are not normalized away. Portable script copies change
only the work/cache locations and Node executable lookup; exact transformations
and original/current script hashes are in `reproduction/SCRIPT_PROVENANCE.json`.

## Reading locally

Open `reader/index.html`, or for popup excerpts and local search use
`python -m http.server 8000 --directory reader` and visit `http://localhost:8000/`.
The local server needs no internet connection. The book text, diagrams, math
runtime, and source-provided readable solutions are included. SageCell, GeoGebra,
live external checking, original websites, and online program links still need
internet access. Browser execution of every interactive service is not claimed.
'''

def main():
    RELEASE.mkdir(exist_ok=True);out=RELEASE/NAME;assert not out.exists(),'Immutable release package already exists'
    final=json.loads((WORK/'output-complete/B10_FINAL_LOCAL_VALIDATION.json').read_bytes());assert final['state']=='pass'
    public=json.loads((LOG/'central-b10-reader-20260908/B10_PUBLIC_BYTE_READBACK.json').read_bytes());assert public['state']=='pass'
    public_files={r['path']:r for r in public['files']}
    delta=json.loads((LOG/'central-b10-reader-20260908/B10_PORTABILITY_DELTA_PUBLIC_READBACK.json').read_bytes())
    assert delta['state']=='pass' and delta['verified_files']==5
    public_files.update({r['path']:r for r in delta['files']})
    entries={};shells={};reader_rows=[]
    def add(name,data):
        assert safe(name) and name not in entries,name;entries[name]=data
    for row in final['files']:
        rel=row['path'];p=ROOT/'docs/en/courses/B10/reader'/rel;logical=p.relative_to(ROOT).as_posix()
        b=p.read_bytes();assert len(b)==public_files[logical]['bytes'] and sha(b)==public_files[logical]['sha256']
        add('reader/'+rel,p);reader_rows.append({'path':rel,'bytes':len(b),'sha256':sha(b)})
        if p.suffix=='.html':
            text=b.decode();top=re.findall(r'<nav\b(?=[^>]*data-central-surface-navigation="v1")(?=[^>]*data-placement="top")[^>]*>.*?</nav>',text,re.S)
            bottom=re.findall(r'<nav\b(?=[^>]*data-central-surface-navigation="v1")(?=[^>]*data-placement="bottom")[^>]*>.*?</nav>',text,re.S)
            assert len(top)==len(bottom)==1
            shells[rel]={'top':top[0],'bottom':bottom[0],'source_sha256':row['sha256']}
    for row in csv.DictReader((WORK/'source-intake/SOURCE_TREE_MANIFEST.csv').open(encoding='utf-8')):
        p=WORK/'source'/row['relative_path'];assert sha(p.read_bytes())==row['sha256'];add('source/'+row['relative_path'],p)
    for name in ['SOURCE_TREE_MANIFEST.csv','SOURCE_CLOSURE_MANIFEST.csv','B10_SOURCE_FREEZE_RECEIPT.json','discrete-book-82336dc87d77c3f18d2cdbc8ec1e74eb3ba38799.zip']:
        add('source-intake/'+name,WORK/'source-intake'/name)
    add('tooling/wheels/pretext-2.27.0-py3-none-any.whl',WORK/'tooling/wheels/pretext-2.27.0-py3-none-any.whl')
    for name in ['rs_services.xml','dist-8.2.5.tgz']:add('tooling/runestone825/'+name,WORK/'tooling/runestone825'/name)
    for name in ['mathjax-3.2.2','prismjs-1.26.0','lunr-2.3.9']:
        for file in [name+'.tgz','registry-metadata.json']:add('tooling/npm/'+name+'/'+file,WORK/'tooling/npm'/name/file)
    for p in (WORK/'tooling/reader-support').iterdir():
        if p.is_file():add('tooling/reader-support/'+p.name,p)
    add('tooling/B10_RUNTIME_INTAKE_RECEIPT.json',WORK/'tooling/B10_RUNTIME_INTAKE_RECEIPT.json')
    for p in sorted((WORK/'output-complete').glob('*.json')):add('evidence/'+p.name,p)
    for name in ['B10_PUBLIC_BYTE_READBACK.json','B10_ONLINE_RECEIPT_FINALIZATION.json','B10_PORTABILITY_DELTA_PUBLIC_READBACK.json']:add('evidence/'+name,LOG/'central-b10-reader-20260908'/name)
    changes=[]
    for prefix in TOOLS:
        name=prefix+'_20260908.py';original=(LOG/name).read_bytes();text=original.decode()
        text,count=re.subn(r'^WORK\s*=.*$',"WORK=Path(__file__).resolve().parent.parent",text,flags=re.M);assert count==1,name
        text=re.sub(r'^SHARED\s*=.*$',"SHARED=WORK/'tooling/pretext-cache'",text,flags=re.M)
        text=re.sub(r"core.set_ptx_path\(r'[^']+'\)","core.set_ptx_path(str(WORK/'tooling/pretext-cache/core'))",text)
        text=text.replace("[r'C:\\Program Files\\nodejs\\node.exe']","[shutil.which('node') or 'node']")
        data=text.encode();assert not re.search(rb'(?i)c:[/\\]users[/\\]',data);compile(text,name,'exec')
        add('scripts/'+name,data);changes.append({'path':'scripts/'+name,'original_sha256':sha(original),'portable_sha256':sha(data),
            'changes':['Package-root WORK location','Package-local PreTeXt cache where used','Node from PATH where used']})
    add('scripts/bootstrap_frozen_tools.py',BOOTSTRAP.encode());add('scripts/apply_frozen_program_shell.py',SHELL.encode())
    add('reproduction/SCRIPT_PROVENANCE.json',jb(changes));add('reproduction/NAVIGATION_SHELLS.json',jb(shells))
    add('reproduction/READER_FILES.json',jb(reader_rows));add('REPRODUCE.md',REPRO.encode())
    add('README.md',('''# Discrete Mathematics: An Open Introduction — original English

Oscar Levin, fourth edition. Start with `reader/index.html`.
Seven chapters, 36 sections, 768 selected exercises and 520 supplied solutions.
This unofficial program mirror keeps the original English content and adds
program-return navigation, local dependencies and directly readable solutions
alongside the source's interactive exercises. No translation was performed.

Original author: https://discrete.openmathbooks.org/dmoi4/
Program: https://kokunoyumeto.github.io/program-matematika-indonesia/en/
Book source: https://github.com/oscarlevin/discrete-book/tree/82336dc87d77c3f18d2cdbc8ec1e74eb3ba38799

The active fourth-edition book license is CC BY-NC-SA 4.0:
https://creativecommons.org/licenses/by-nc-sa/4.0/ . Preserve all source credits
and component notices. Stale BY-SA notices in the original tree are preserved
as historical evidence, not used to weaken the active fourth-edition terms.
Software/runtime components retain their own licenses. No author endorsement
is implied. This archive does not include remote computation/scoring servers.

See REPRODUCE.md for build and offline-reading details, CHECKSUMS.sha256 for
the complete payload, evidence/ for source/reader verification, and the
reader/metadata/ JSON and CSV source-unit routes. Those routes are not a claim
that every native backend capability has been integrated globally.

Codex, on instructions of the user.
''').encode())
    rows={};upstream_path_exceptions=[]
    for name,item in sorted(entries.items()):
        if not name.endswith(('.html','.json','.jsonl','.md','.py','.txt','.csv','.css','.js','.mjs','.map')) or name.startswith('source/'):continue
        data=item.read_bytes() if isinstance(item,Path) else item
        if re.search(rb'(?i)[a-z]:[/\\]+users[/\\]+',data):
            assert name=='reader/runtime/mathjax/es5/input/mml/extensions/mml3.sef.json',name
            original=WORK/'tooling/npm/mathjax-3.2.2/package/es5/input/mml/extensions/mml3.sef.json'
            assert data==original.read_bytes()
            profiles=re.findall(rb'(?i)[a-z]:[/\\]+users[/\\]+([^/\\]+)',data)
            assert all(p.decode().lower()!=Path.home().name.lower() for p in profiles)
            upstream_path_exceptions.append({'path':name,'sha256':sha(data),'policy':'Unchanged pinned MathJax compiled XSLT artifact contains upstream developer build locations, not task/user locations; preserved to avoid changing runtime semantics.'})
    with zipfile.ZipFile(out,'x',compression=zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for name,item in sorted(entries.items()):
            data=item.read_bytes() if isinstance(item,Path) else item
            if name.endswith(('.html','.json','.jsonl','.md','.py','.txt','.csv','.css','.js','.mjs','.map')) and not name.startswith('source/'):
                assert not re.search(rb'(?i)[a-z]:[/\\]+users[/\\]+',data) or any(x['path']==name for x in upstream_path_exceptions),name
            info=zipfile.ZipInfo(name,(2026,9,8,0,0,0));info.create_system=3;info.external_attr=0o100644<<16
            z.writestr(info,data,compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
            rows[name]={'bytes':len(data),'sha256':sha(data)}
        checksum=''.join(r['sha256']+'  '+n+'\n' for n,r in sorted(rows.items())).encode()
        info=zipfile.ZipInfo('CHECKSUMS.sha256',(2026,9,8,0,0,0));info.create_system=3;info.external_attr=0o100644<<16
        z.writestr(info,checksum,compress_type=zipfile.ZIP_DEFLATED,compresslevel=6)
    with zipfile.ZipFile(out) as z:
        assert len(z.namelist())==len(set(z.namelist()))==len(rows)+1 and z.testzip() is None
        for name,row in rows.items():
            with z.open(name) as f:assert hashlib.file_digest(f,'sha256').hexdigest()==row['sha256'],name
            assert z.getinfo(name).file_size==row['bytes']
        for name in ['scripts/bootstrap_frozen_tools.py','scripts/apply_frozen_program_shell.py']:compile(z.read(name),name,'exec')
    with out.open('rb') as f:digest=hashlib.file_digest(f,'sha256').hexdigest()
    receipt={'schema':'b10-original-reader-source-package/1','state':'pass','name':NAME,'bytes':out.stat().st_size,'sha256':digest,
        'entries':len(rows)+1,'checksum_rows':len(rows),'source_files':939,'reader_files':2271,'source_commit':final['source_commit'],
        'reader_commit':delta['commit'],'source_body_replay':'pass before packaging',
        'portable_script_copies_compile':True,'packaged_rebuild_execution':'not yet replayed in an isolated extraction',
        'all_zip_members_hash_and_crc_verified':True,'private_profile_path_scan':'pass including CSS maps; exact upstream software exception recorded separately',
        'upstream_software_path_exceptions':upstream_path_exceptions,
        'native_capability_parity_claim':False}
    (RELEASE/'B10_SOURCE_PACKAGE_V2_RECEIPT.json').write_bytes(jb(receipt));print(json.dumps(receipt),flush=True)
if __name__=='__main__':main()
