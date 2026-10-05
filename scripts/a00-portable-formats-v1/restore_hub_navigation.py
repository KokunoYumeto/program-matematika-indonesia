"""Restore existing navigation only on regenerated interface pages."""
import importlib.util
import json
import os
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'outputs/a00-portable-formats-v1'
LANGUAGE=os.environ.get('A00_HUB_LANGUAGE','id')
assert LANGUAGE in ('id','en')
if LANGUAGE=='en':OUT=ROOT/'outputs/a00-english-portable-formats-v1'
REFRESH='a00_english_format_link_refresh' if LANGUAGE=='en' else 'a00_format_link_refresh'
sys.path.insert(0,str(ROOT/'scripts'))
spec=importlib.util.spec_from_file_location('surface_nav',ROOT/'scripts/apply-central-course-surface-navigation-v1.py')
nav=importlib.util.module_from_spec(spec);spec.loader.exec_module(nav)
read=lambda p:json.loads(p.read_text(encoding='utf-8'))
baseline=read(OUT/'hub-parent/BASELINE.json')
overlay_path='backend/authority/central-course-surface-navigation-overlay-v1.json'
old_raw=(OUT/'hub-parent'/overlay_path).read_bytes()
overlay=read(OUT/'hub-parent'/overlay_path)
current_overlay=read(ROOT/overlay_path)
if current_overlay!=overlay:
    refresh=current_overlay.get(REFRESH,{})
    assert refresh.get('parent_overlay_sha256')==nav.sha256_bytes(old_raw),'Navigation changed concurrently'
    assert refresh['script']['path']=='scripts/a00-portable-formats-v1/restore_hub_navigation.py'
    assert set(refresh['documents']).issubset({r['path'] for r in baseline['files'] if r['path'].endswith('.html')})
    assert len(overlay['files'])==len(current_overlay['files'])
    for oldrow,newrow in zip(overlay['files'],current_overlay['files']):
        assert oldrow['document']==newrow['document']
        if oldrow['document'] not in refresh['documents']:assert oldrow==newrow,'Unrelated navigation change'
        else:
            assert {k:v for k,v in oldrow.items() if k not in ('source_body','hosted_surface')}=={k:v for k,v in newrow.items() if k not in ('source_body','hosted_surface')}
    reconstructed=json.loads(json.dumps(current_overlay))
    del reconstructed[REFRESH]
    reconstructed['files']=overlay['files']
    reconstructed['authority']['learner_access_manifest']=overlay['authority']['learner_access_manifest']
    assert reconstructed==overlay,'Unrelated navigation metadata changed'
contract=read(nav.CONTRACT_PATH)
program_targets=[(v['public_url'],k,v['navigation']['program_root']) for k,v in sorted(contract['interfaces'].items())]
updated=[]
for fact in baseline['files']:
    path=fact['path']
    if not path.endswith('.html'):continue
    payload=(ROOT/path).read_bytes()
    if payload==(OUT/'hub-parent'/path).read_bytes():continue
    row=next((r for r in overlay['files'] if r['document']==path),None)
    if row is None:
        assert nav.MARKER not in payload.decode('utf-8'),path
        continue
    assert row['role']=='generic' and row['course_ids']==[],path
    source,hosted=nav.inject_overlay(path,payload,[],program_targets,[],[],contract['interfaces'][row['locale']]['navigation'])
    (ROOT/path).write_bytes(hosted)
    row['source_body']=nav.fact(path,source)
    row['hosted_surface']=nav.fact(path,hosted)
    assert nav.strip_owned_overlay(hosted.decode('utf-8'),path).encode('utf-8')==source
    updated.append(path)
manifest_path='docs/interface/learner-access-manifest.json'
overlay['authority']['learner_access_manifest']=nav.fact(manifest_path,(ROOT/manifest_path).read_bytes())
overlay[REFRESH]={
    'parent_overlay_sha256':nav.sha256_bytes(old_raw),
    'script':nav.fact('scripts/a00-portable-formats-v1/restore_hub_navigation.py',Path(__file__).read_bytes()),
    'documents':updated,'other_navigation_rows_unchanged':True,
    'scope':'A00 format-link projection; course bodies and unrelated navigation unchanged.'}
(ROOT/overlay_path).write_text(json.dumps(overlay,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8',newline='\n')
print(json.dumps({'state':'pass','refreshed_documents':updated}))
