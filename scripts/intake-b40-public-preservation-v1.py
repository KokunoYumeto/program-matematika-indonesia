"""Verify and preserve the already public B40 packet without changing its bytes."""
import argparse
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import re
import shutil
import zipfile

ROOT=Path(__file__).resolve().parents[1]
BASE=Path('backend/b40-foundations-public-20261002/preservation')
FACT={'bytes':50268240,'sha256':'981dfe3f2b09659ecd6501d528355c1de73e71aa394221c7a038628e940dc5dc'}
NATIVE={'bytes':46936242,'sha256':'28c4d61ce0299af918d2937bd4bfb247bb161ac2702fae0bc4aa25e3f60c0d6e'}
URL='https://github.com/KokunoYumeto/program-matematika-indonesia/releases/download/b40-foundations-2026.10.02/PUBLIC_DEPENDENCY_INTEGRATION_SOURCE.zip'
TEXT={'.py','.js','.mjs','.cjs','.json','.jsonl','.html','.css','.tex','.txt','.md','.csv','.tsv','.bib'}
PATTERNS=[re.compile(p,re.I) for p in [rb'[A-Za-z]:[\\/]+Users[\\/]+[A-Za-z0-9._-]+[\\/]+',
    rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})',
    rb'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----']]

def identity(stream):
    h=hashlib.sha256();n=0
    while block:=stream.read(1024*1024):h.update(block);n+=len(block)
    return {'bytes':n,'sha256':h.hexdigest()}

def safe(name):
    p=PurePosixPath(name)
    if p.is_absolute() or '..' in p.parts or '\\' in name or ':' in name:
        raise ValueError('Unsafe archive path')

def scan(archive,depth=0):
    assert depth<4,'Unexpected nested archive depth'
    names=archive.namelist();assert len(names)==len(set(names))
    text_files=0;nested=0
    for item in archive.infolist():
        safe(item.filename)
        assert item.file_size<192*1024*1024,'Unexpected large individual member'
        if item.is_dir():continue
        suffix=PurePosixPath(item.filename).suffix.lower()
        if suffix in TEXT:
            text_files+=1;tail=b''
            with archive.open(item) as stream:
                while block:=stream.read(1024*1024):
                    value=tail+block
                    if any(p.search(value) for p in PATTERNS):
                        raise ValueError('Private-data-shaped content in archive member: '+item.filename)
                    tail=value[-256:]
        elif suffix=='.zip':
            with archive.open(item) as stream:raw=stream.read()
            with zipfile.ZipFile(io.BytesIO(raw)) as child:
                c=scan(child,depth+1);text_files+=c['text_files'];nested+=1+c['nested_archives']
    assert archive.testzip() is None
    return {'text_files':text_files,'nested_archives':nested,'members':len(names)}

def verify(path):
    with path.open('rb') as stream:assert identity(stream)==FACT,'Public packet identity mismatch'
    with zipfile.ZipFile(path) as z:
        inventory=json.loads(z.read('PRESERVATION_INVENTORY.json'))
        expected={r['path']:r for r in inventory['files']}
        assert len(z.namelist())==65 and set(z.namelist())==set(expected)|{'PRESERVATION_INVENTORY.json'}
        for name,row in expected.items():
            with z.open(name) as stream:assert identity(stream)=={k:row[k] for k in ('bytes','sha256')}
        with z.open('preservation/B40_COMPLETE_SOURCE.zip') as stream:assert identity(stream)==NATIVE
        checked=scan(z)
    return {'schema':'b40-public-preservation-intake/1','state':'pass','public_url':URL,
        'packet':{'path':(BASE/path.name).as_posix(),**FACT},'public_members_verified':64,
        'nested_source_archive':NATIVE,'archive_checks':checked,'native_source_bytes_changed':False,
        'full_native_book_build_claimed':False,'scope':'Exact public six-section foundation reader, editable sources and dependency adapter; not the complete forty-book corpus.',
        'integration_provenance':'OpenAI Codex gpt-6-astra, Ultra'}

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);ap.add_argument('--intake',action='store_true');args=ap.parse_args()
    result=verify(args.archive)
    if args.intake:
        dest=ROOT/BASE/args.archive.name;dest.parent.mkdir(parents=True,exist_ok=True)
        if dest.exists():assert dest.read_bytes()==args.archive.read_bytes(),'Refusing to replace preservation packet'
        else:shutil.copyfile(args.archive,dest)
        assert verify(dest)==result
        (dest.parent/'INTAKE_RECEIPT.json').write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(result))
