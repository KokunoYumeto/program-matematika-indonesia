"""Package the full editable planner source and replay it in a clean directory."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import zipfile

spec=importlib.util.spec_from_file_location('builder',Path(__file__).with_name('build-openlogic-teacher-v1.py'))
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)
REL=Path('backend/course-capsule-v1/adapters/openlogic-teacher-v1')
SCRIPTS=['build-openlogic-teacher-v1.py','test-openlogic-teacher-build-v1.py',
         'test-openlogic-teacher-ui-v1.mjs','package-openlogic-teacher-v1.py']
FILES=['README.md','mapping-tests.json','ui/teacher.js','ui/teacher.css',*b.INPUTS]


def package(root):
    base=root/REL
    members={'scripts/'+name:(root/'scripts'/name).read_bytes() for name in SCRIPTS}
    members.update({(REL/name).as_posix():(base/name).read_bytes() for name in FILES})
    manifest={'schema':'openlogic-planner-source-members/1','files':[{'path':name,**b.fact(data)} for name,data in sorted(members.items())]}
    members['SOURCE-MANIFEST.json']=b.encoded(manifest)
    out=base/'openlogic-teacher-editable-source-v1.zip'
    with zipfile.ZipFile(out,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        for name,data in sorted(members.items()):
            info=zipfile.ZipInfo(name,(2026,9,28,0,0,0));info.compress_type=zipfile.ZIP_DEFLATED
            info.external_attr=0o644<<16;z.writestr(info,data,compresslevel=9)
    return out,manifest


def main():
    out,manifest=package(b.ROOT)
    expected=json.loads((b.BASE/'site/teacher-build.json').read_bytes())
    with tempfile.TemporaryDirectory(prefix='openlogic-source-replay-') as tmp:
        root=Path(tmp)
        with zipfile.ZipFile(out) as z:
            assert z.testzip() is None and len(z.namelist())==len(set(z.namelist()))
            assert all(not Path(n).is_absolute() and '..' not in Path(n).parts for n in z.namelist())
            for item in manifest['files']:assert b.fact(z.read(item['path']))=={k:item[k] for k in ['bytes','sha256']}
            z.extractall(root)
        subprocess.run([sys.executable,'-B',str(root/'scripts/build-openlogic-teacher-v1.py')],check=True,capture_output=True)
        actual=json.loads((root/REL/'site/teacher-build.json').read_bytes());assert actual==expected
        for item in expected['files']:assert (root/REL/'site'/item['path']).read_bytes()==(b.BASE/'site'/item['path']).read_bytes()
        subprocess.run([sys.executable,'-B',str(root/'scripts/test-openlogic-teacher-build-v1.py')],check=True,capture_output=True)
        replay,_=package(root);assert replay.read_bytes()==out.read_bytes()
    (b.BASE/'site'/out.name).write_bytes(out.read_bytes())
    receipt={'schema':'openlogic-teacher-source-package/1','archive':out.name,**b.fact(out.read_bytes()),
        'members':manifest['files'],'member_count':len(manifest['files'])+1,
        'offline_replay':'byte_identical','repacked_archive':'byte_identical',
        'reproduced_outputs':len(expected['files']),'book_bodies_bundled':False,
        'full_mapping_replay_requires_original_book_archives':True}
    (b.BASE/'source-package.json').write_bytes(b.encoded(receipt))
    print(json.dumps({k:v for k,v in receipt.items() if k!='members'}))


if __name__=='__main__':main()
