"""Deterministic complete planner-source ZIP and clean offline replay."""
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[1]
REL=Path('backend/course-capsule-v1/adapters/judson-teacher-v1')
BASE=ROOT/REL
SCRIPTS=['intake-judson-teacher-v1.py','build-judson-teacher-v1.py','test-judson-teacher-v1.py',
         'test-judson-teacher-ui-v1.mjs','package-judson-teacher-v1.py','verify-judson-live-readers-v1.py']
FILES=['README.md','input/native-exercise-intake.json','input/source-lock.json','input/COPYING',
       'input/gfdl.xml','input/reader-access.json','ui/teacher.js','ui/teacher.css']


def identity(data): return {'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()}


def package(root):
    base=root/REL
    members={('scripts/'+n):(root/'scripts'/n).read_bytes() for n in SCRIPTS}
    members.update({(REL/n).as_posix():(base/n).read_bytes() for n in FILES})
    manifest={'schema':'judson-teacher-source-members/1','files':[{'path':n,**identity(data)} for n,data in sorted(members.items())]}
    members['SOURCE-MANIFEST.json']=(json.dumps(manifest,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode()
    output=base/'judson-teacher-editable-source-v1.zip'
    with zipfile.ZipFile(output,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(members.items()):
            item=zipfile.ZipInfo(name,(2026,9,28,0,0,0));item.compress_type=zipfile.ZIP_DEFLATED
            item.external_attr=0o644<<16;z.writestr(item,data,compresslevel=9)
    return output,manifest


def main():
    output,manifest=package(ROOT)
    expected=json.loads((BASE/'site/teacher-build.json').read_bytes())
    with tempfile.TemporaryDirectory(prefix='judson-source-replay-') as scratch:
        target=Path(scratch)
        with zipfile.ZipFile(output) as z:
            assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))
            assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist())
            for entry in manifest['files']: assert identity(z.read(entry['path']))=={k:entry[k] for k in ['bytes','sha256']}
            z.extractall(target)
        subprocess.run([sys.executable,str(target/'scripts/build-judson-teacher-v1.py')],check=True,capture_output=True)
        actual=json.loads((target/REL/'site/teacher-build.json').read_bytes());assert actual==expected
        for entry in expected['files']:
            assert (target/REL/'site'/entry['path']).read_bytes()==(BASE/'site'/entry['path']).read_bytes()
        other,_=package(target);assert output.read_bytes()==other.read_bytes()
    (BASE/'site'/output.name).write_bytes(output.read_bytes())
    receipt={'schema':'judson-teacher-source-package/1','archive':output.name,**identity(output.read_bytes()),
             'members':manifest['files'],'member_count':len(manifest['files'])+1,'offline_replay':'byte_identical',
             'repacked_archive':'byte_identical','reproduced_outputs':len(expected['files']),
             'whole_book_archives_bundled':False,'native_intake_replay_requires_original_archives':True}
    (BASE/'source-package.json').write_text(json.dumps(receipt,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in receipt.items() if k!='members'}))


if __name__=='__main__':main()
