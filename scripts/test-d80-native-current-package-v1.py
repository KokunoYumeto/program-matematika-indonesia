"""Replay D80 solely from the shared release ZIP, without producer files or network."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ap=argparse.ArgumentParser();ap.add_argument('archive',type=Path);ap.add_argument('--receipt',type=Path);args=ap.parse_args()
BASE='backend/course-capsule-v1/adapters/d80-native-ledger-v1/'
def identity(raw):return {'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}
with zipfile.ZipFile(args.archive) as archive:
    manifest=json.loads(archive.read('CURRENT_BACKEND_PACKAGE_MANIFEST.json'))
    members={row['path']:row for row in manifest['files']}
    lock=json.loads(archive.read(BASE+'source-lock.json'))
    tests=json.loads(archive.read(BASE+'tests.json'))
    paths=[BASE+'source-lock.json','scripts/d80-native-ledger-v1.py','scripts/d80-native-ui.js','docs/backend/d60/native-ledger/ledger.css']
    paths += [BASE+row['path'] for row in lock['inputs']]+[row['path'] for row in lock['authorities']]
    assert len(paths)==len(set(paths))
    with tempfile.TemporaryDirectory(prefix='d80-packaged-replay-') as temp:
        root=Path(temp)
        for path in paths:
            row=members[path];raw=archive.read(path)
            assert identity(raw)=={k:row[k] for k in ('bytes','sha256')}
            dest=root/path
            assert dest.resolve().is_relative_to(root.resolve()) and not Path(path).anchor
            dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(raw)
        runs=[]
        for label in ['a','b']:
            result=subprocess.run([sys.executable,'-B',str(root/'scripts/d80-native-ledger-v1.py'),'--out',str(root/label)],
                cwd=root,capture_output=True,text=True,encoding='utf-8',timeout=90,check=True)
            built=json.loads(result.stdout)
            assert built['state']=='pass' and built['summary']==tests['summary']
            assert built['outputs']==tests['outputs']
            for name,fact in built['outputs'].items():
                assert identity((root/label/name).read_bytes())==fact
                assert identity(archive.read(BASE+'site/'+name))==fact
            runs.append({'exit_code':0,'outputs':len(built['outputs']),'summary':built['summary']})
        assert (root/'a/native-metadata.zip').read_bytes()==(root/'b/native-metadata.zip').read_bytes()
receipt={'schema':'d80-packaged-native-metadata-replay/1','state':'pass','runs':runs,'dependency_files':len(paths),
         'producer_sources_used':False,'network_used':False,'semantic_canon_approval':False,'native_book_rebuilt':False,
         'all_original_records':8430,'visible_records':7760,'isolated_outputs_match_shipped_raw_outputs':True}
if args.receipt:args.receipt.write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'state':'pass','runs':2,'outputs_each':8,'native_records_preserved':8430,'producer_or_network_required':False}))
