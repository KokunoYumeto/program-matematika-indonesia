#!/usr/bin/env python3
"""Admit a validated original-English A30 reader into the existing program."""
import argparse,hashlib,importlib.util,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DEST=ROOT/'docs/en/courses/A30/reader'
def sha(b):return hashlib.sha256(b).hexdigest()
def fact(b):return {'bytes':len(b),'sha256':sha(b)}
def put(p,b):
    if p.exists() and p.read_bytes()==b:return
    p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
def run(mirror):
    receipt_bytes=(mirror/'LOCAL_VALIDATION_RECEIPT.json').read_bytes();receipt=json.loads(receipt_bytes)
    qa_bytes=(mirror/'INDEPENDENT_FINAL_BYTE_QA.json').read_bytes();qa=json.loads(qa_bytes)
    replay_bytes=(mirror/'DETERMINISTIC_REPLAY_RECEIPT.json').read_bytes();replay=json.loads(replay_bytes)
    assert qa['state']==replay['state']=='pass'
    assert qa['local_validation_receipt']==fact(receipt_bytes)
    assert replay['aggregate_sha256']==receipt['aggregate_sha256']
    assert qa['adapter']==replay['builder']==fact((mirror/'scripts/build_original_reader.py').read_bytes())
    assert receipt['modules']==87 and receipt['counts']['math']==26583 and qa['native_ids']==46359
    module=importlib.util.spec_from_file_location('navigation',ROOT/'scripts/apply-central-course-surface-navigation-v1.py')
    overlay=importlib.util.module_from_spec(module);module.loader.exec_module(overlay)
    for row in receipt['files']:
        relative=Path(row['path']);assert not relative.is_absolute() and '..' not in relative.parts
        b=(mirror/'output/html-en'/relative).read_bytes();assert fact(b)=={k:row[k] for k in ('bytes','sha256')}
        target=DEST/relative
        if target.is_file() and target.suffix=='.html':
            original=overlay.strip_owned_overlay(target.read_text(encoding='utf-8'),target.relative_to(ROOT).as_posix()).encode()
            if original==b:continue
        put(target,b)
    proof_root=ROOT/'docs/en/courses/A30/evidence'
    for name,b in [('LOCAL_VALIDATION_RECEIPT.json',receipt_bytes),('INDEPENDENT_FINAL_BYTE_QA.json',qa_bytes),('DETERMINISTIC_REPLAY_RECEIPT.json',replay_bytes)]:put(proof_root/name,b)
    admission={'schema':'central-original-reader-admission/1','course_id':'A30','language':'en','source_revision':receipt['source_revision'],
        'original':'https://openstax.org/books/precalculus-2e/pages/1-introduction-to-functions',
        'reader':'https://kokunoyumeto.github.io/program-matematika-indonesia/en/courses/A30/reader/',
        'native_source_unchanged':True,'translation_performed':False,'module_count':87,'native_ids':46359,'assets':1873,
        'local_validation':fact(receipt_bytes),'independent_qa':fact(qa_bytes),'replay':fact(replay_bytes),
        'source_projection_files':receipt['files'],'public_readback':'pending','owner_mutation':False,
        'navigation':'Existing central reversible overlay adds every registered locale/course return; original publisher and book contents links retained.'}
    put(ROOT/'docs/en/courses/A30/A30_ORIGINAL_ENGLISH_ADMISSION_V1.json',(json.dumps(admission,indent=2,sort_keys=True)+'\n').encode())
    print(json.dumps({'state':'staged','course_id':'A30','files':len(receipt['files']),'source_projection_bytes':sum(r['bytes'] for r in receipt['files'])}))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--mirror',required=True,type=Path);a=p.parse_args();run(a.mirror.resolve())
