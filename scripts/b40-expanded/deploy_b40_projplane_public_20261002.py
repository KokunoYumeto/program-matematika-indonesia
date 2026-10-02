"""Checked 31-to-32-section successor, preserving all unrelated public work."""
import argparse
import hashlib
import importlib.util
import json
from pathlib import Path
import re

LOG=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('expanded',LOG/'deploy_b40_expanded_public_20261002.py')
d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)
WORK=LOG.parent/'b40-projplane-public-20261002'
OLD=LOG.parent/'b40-chio-public-20261002'
d.WORK=WORK;d.prior.WORK=WORK
d.TAG='b40-original-en-2026.10.02-32-sections'
d.ASSET_ROOT='https://github.com/KokunoYumeto/program-matematika-indonesia/releases/download/'+d.TAG+'/'
d.LABEL='Original English — 32 sections through Projective Geometry (partial book)'
BACKEND='backend/b40-projplane-public-20261002/'
OLD_TAG='b40-original-en-2026.10.02-31-sections'
OLD_LABEL='Original English — 31 sections through Chiò’s Method (partial book)'
OLD_OFFLINE='Offline original English — 31 sections and complete editable source'
OFFLINE='Offline original English — 32 sections and complete editable source'
sha,jb,fact,save,get,api=d.sha,d.jb,d.fact,d.save,d.get,d.api


def blob_sha(raw):
    return hashlib.sha1(b'blob '+str(len(raw)).encode()+b'\0'+raw).hexdigest()


def reader_tree(commit):
    tree=json.loads(get(d.API+'/git/commits/'+commit))['tree']['sha']
    for part in d.PREFIX.rstrip('/').split('/'):
        rows=json.loads(get(d.API+'/git/trees/'+tree))['tree']
        row=next(x for x in rows if x['path']==part)
        assert row['type']=='tree'
        tree=row['sha']
    return tree


def stage():
    assert not (WORK/'PUBLICATION_RECEIPT.json').exists(), 'resume recorded publication'
    d.audit_package()
    latest=json.loads(get(d.API+'/commits/main'))
    parent,root_tree=latest['sha'],latest['commit']['tree']['sha']
    prior_tree=reader_tree(parent)
    listing=json.loads(get(d.API+'/git/trees/'+prior_tree+'?recursive=1'))
    assert not listing.get('truncated')
    blobs={r['path']:r['sha'] for r in listing['tree'] if r['type']=='blob'}
    old_manifest=d.json_read(OLD/'public/READER_MANIFEST.json')
    checked_old=0
    for row in old_manifest['public_files']:
        if row['path']=='COMPLETE_SOURCE.zip':continue
        raw=(OLD/'public'/row['path']).read_bytes()
        assert fact(raw)=={k:row[k] for k in ['bytes','sha256']}
        assert blobs.get(row['path'])==blob_sha(raw), 'Prior reader changed: '+row['path']
        checked_old+=1
    for name,local in [('READER_MANIFEST.json',OLD/'public/READER_MANIFEST.json'),('PUBLICATION_RECEIPT.json',OLD/'FINAL_PUBLIC_RECEIPT.json')]:
        assert blobs.get(name)==blob_sha(local.read_bytes()), 'Prior public evidence changed'
    entries,baselines={},[]
    def add(path,raw):
        assert path not in entries
        target=WORK/'publication-staging'/path
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        entries[path]=dict(path=path,local=target.relative_to(WORK).as_posix(),**fact(raw))
    def baseline(path):
        raw=get(d.RAW+'/'+parent+'/'+path)
        target=WORK/'public-baseline'/path
        target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
        baselines.append(dict(path=path,**fact(raw)))
        return raw
    manifest=d.json_read(WORK/'public/READER_MANIFEST.json')
    assert manifest['counts']['readers']==32
    for row in manifest['public_files']:
        raw=(WORK/'public'/row['path']).read_bytes()
        assert fact(raw)=={k:row[k] for k in ['bytes','sha256']}
        add(d.PREFIX+row['path'],raw)
    add(d.PREFIX+'READER_MANIFEST.json',(WORK/'public/READER_MANIFEST.json').read_bytes())
    index_fact=fact((WORK/'public/index.html').read_bytes())
    zip_fact=fact((WORK/'public/COMPLETE_SOURCE.zip').read_bytes())
    path='docs/interface/locales.js';original=baseline(path).decode()
    start=original.index('export const englishResources = {')
    match=re.search(r'  B40: \[.*?\n  \],',original[start:],re.S)
    assert match
    block=match.group()
    # The previous publisher serialized the offline em dash as a JSON escape.
    # Compare decoded label values, not their equivalent JavaScript spelling.
    old_labels=[]
    for line in block.splitlines():
        quoted=re.search(r'englishMirror\(("(?:\\.|[^"\\])*")',line)
        old_labels.append(json.loads(quoted.group(1)) if quoted else None)
    assert old_labels.count(OLD_LABEL)==1 and old_labels.count(OLD_OFFLINE)==1
    lines=block.splitlines()
    for i,line in enumerate(lines):
        if old_labels[i]==OLD_LABEL:
            lines[i]='    englishMirror('+json.dumps(d.LABEL,ensure_ascii=False)+", '"+d.URL+"', 'HTML', "+json.dumps(index_fact)+'),'
        elif old_labels[i]==OLD_OFFLINE:
            lines[i]='    englishMirror('+json.dumps(OFFLINE)+", '"+d.ASSET_ROOT+"COMPLETE_SOURCE.zip', 'HTML ZIP', "+json.dumps({**zip_fact,'offlineAfterDownload':True})+'),'
    replacement='\n'.join(lines)
    changed=original[:start+match.start()]+replacement+original[start+match.end():]
    assert changed.replace(replacement,block,1)==original
    add(path,changed.encode())
    for name in ['index.html','learning-map.html','learning-map-paired.html']:
        path='docs/en/'+name;original=baseline(path).decode()
        match=re.search(r'<article\b[^>]*id="course-B40".*?</article>',original,re.S);assert match
        block=match.group()
        assert block.count(OLD_LABEL)==1 and block.count(OLD_OFFLINE)==1 and block.count(OLD_TAG)==1
        replacement=block.replace(OLD_LABEL,d.LABEL).replace(OLD_OFFLINE,OFFLINE).replace(OLD_TAG,d.TAG)
        changed=original[:match.start()]+replacement+original[match.end():]
        assert changed.replace(replacement,block,1)==original
        add(path,changed.encode())
    for language in ['en','id']:
        path='docs/'+language+'/programme/index.html';original=baseline(path).decode()
        match=re.search(r'<section id="core-B40">.*?</section>',original,re.S);assert match
        block=match.group();link=re.search(r'<a data-b40-expanded="v1"[^>]*>[^<]*</a>',block);assert link
        old=link.group();assert '31' in old and d.URL in old
        label='Read original English — 32 sections through Projective Geometry (partial book)' if language=='en' else 'Baca teks asli berbahasa Inggris — 32 bagian (sebagian buku)'
        new='<a data-b40-expanded="v1" href="'+d.URL+'" hreflang="en">'+label+'</a>'
        replacement=block.replace(old,new,1)
        changed=original[:match.start()]+replacement+original[match.end():]
        assert changed.replace(replacement,block,1)==original
        add(path,changed.encode())
    path='docs/interface/learner-access-manifest.json';access=json.loads(baseline(path))
    other=jb({k:v for k,v in access['courses'].items() if k!='B40'});indonesian=jb(access['courses']['B40']['id'])
    english=access['courses']['B40']['en'];updated=0
    for row in english['program_hosted_reader']['resources']:
        if row['url']==d.URL:
            assert row['label']==OLD_LABEL
            row.update(label=d.LABEL,coverage='32 linked sections through Projective Geometry; not the whole book',**index_fact);updated+=1
    for row in english['offline_copies']:
        if OLD_TAG in row['url']:
            assert row['label']==OLD_OFFLINE
            row.update(label=OFFLINE,url=d.ASSET_ROOT+'COMPLETE_SOURCE.zip',coverage='32 linked sections through Projective Geometry; not the whole book',**zip_fact);updated+=1
    assert updated==2
    assert jb({k:v for k,v in access['courses'].items() if k!='B40'})==other
    assert jb(access['courses']['B40']['id'])==indonesian
    add(path,jb(access))
    for name in ['BUILD_RECEIPT.json','SOURCE_SEAL.json','BROWSER_QA.json','VISUAL_INSPECTION.json','PUBLIC_EXTRACTION_QA.json','PACKAGE_PRIVACY_CHECK.json','RUNTIME_PROVENANCE.json','EXPORT_SELECTION.json']:
        raw=(WORK/name).read_bytes()
        # EXPORT_SELECTION contains only task-relative authority, no private path.
        add(BACKEND+name,raw)
    for name in ['build_b40_expanded_public_20261002.py','seal_b40_expanded_public_20261002.py','test_b40_expanded_public_20261002.mjs','deploy_b40_expanded_public_20261002.py','deploy_b40_foundations_public_20261002.py',Path(__file__).name]:
        add('scripts/b40-expanded/'+name,(LOG/name).read_bytes())
    plan=dict(schema='b40-projplane-publication-plan/1',base_commit=parent,base_tree=root_tree,
        files=list(entries.values()),public_baselines=baselines,reader_baseline_tree=prior_tree,
        verified_previous_payload_files=checked_old,deleted_paths=[],force=False,
        preserved_prior_reader_prefix='docs/en/readers/hefferon-foundations/',
        previous_release_preserved=OLD_TAG,scope='32 selected sections, not full book',model='gpt-6-astra',effort='ultra')
    save(WORK/'PUBLICATION_PLAN.json',plan)
    print(json.dumps(dict(state='staged',base=parent,files=len(entries),previous_payloads_checked=checked_old,bytes=sum(r['bytes'] for r in entries.values()))),flush=True)
    return plan


original_refresh=d.refresh_parent
def refresh_parent(session,plan):
    head=api(session,'GET','/git/ref/heads/main')['object']['sha']
    assert reader_tree(head)==plan['reader_baseline_tree'], 'Reader changed concurrently; preserve and reconcile'
    return original_refresh(session,plan)
d.refresh_parent=refresh_parent


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--stage',action='store_true');p.add_argument('--publish',action='store_true')
    p.add_argument('--verify',action='store_true');p.add_argument('--pages',action='store_true')
    args=p.parse_args()
    plan=stage() if args.stage else d.json_read(WORK/'PUBLICATION_PLAN.json')
    if args.publish:d.publish(plan,None)
    if args.verify or args.pages:d.verify(plan,d.json_read(WORK/'PUBLICATION_RECEIPT.json'),args.pages)


if __name__=='__main__':main()
