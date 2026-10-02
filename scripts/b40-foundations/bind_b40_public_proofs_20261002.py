"""Bind the already checked provider packet to exact published reader slices.

This is publication identity work, not a fresh proof audit or owner admission.
Historical provider/overlay bytes remain immutable. No native owner is edited.
"""
import copy
import hashlib
import json
from pathlib import Path

BASE=Path(__file__).resolve().parent.parent
WORK=BASE/'b40-foundations-public-20261002'
CORE=BASE/'d100-capability-v1-worktree'
PROVIDER=CORE/'backend/cross-programme-v1/provider-handoffs/B40-basis-extension-20261002/PROVIDER_HANDOFF.json'
ORIGIN='https://kokunoyumeto.github.io/program-matematika-indonesia/en/readers/hefferon-foundations/'
RAW='https://raw.githubusercontent.com/KokunoYumeto/program-matematika-indonesia/'

def sha(b):return hashlib.sha256(b).hexdigest()
def facts(b):return {'bytes':len(b),'sha256':sha(b)}
def dump(o):return (json.dumps(o,ensure_ascii=False,indent=2)+'\n').encode()

def bind(native,index,reader):
    matches=[u for u in index['units'] if u['unit_id']==native['native_unit_id']]
    assert len(matches)==1
    unit=matches[0]
    assert unit['source_fragments']==native['source_fragments']
    surface=unit['surface']
    assert surface['sha256']==native['rendered_fragment']['sha256']
    assert surface['bytes']==native['rendered_fragment']['bytes']
    fragment=reader[surface['byte_start']:surface['byte_end']]
    assert facts(fragment)=={k:surface[k] for k in ('bytes','sha256')}
    assert ('id="'+native['anchor']+'"').encode() in fragment
    return {'native_unit_id':unit['unit_id'],'anchor':native['anchor'],
            'source_fragments':unit['source_fragments'],'public_rendered_fragment':surface,
            'unchanged_from_checked_provider_fragment':True}

def main():
    receipt=json.loads((WORK/'PUBLICATION_RECEIPT.json').read_bytes())
    assert receipt['state']=='public_pages_and_sources_anonymously_verified'
    release=json.loads((WORK/'SOURCE_RELEASE_RECEIPT.json').read_bytes())
    assert release['state']=='public_all_assets_anonymously_verified'
    pb=PROVIDER.read_bytes();provider=json.loads(pb)
    assert sha(pb)=='bd2e67bee1e4e5f56315138bf1ad054a5e48882907686d1f46ee4cc92825d921'
    published={r['path']:r for r in receipt['anonymous_commit_readback']}
    pages={r['path']:r for r in receipt['pages_readback']}
    rows=[];negative=[]
    for result in provider['complete_proof_units']:
        bound={'id':result['id']}
        for kind in ('statement','proof'):
            native=result[kind];path=native['reader_path'].removeprefix('readers/')
            reader=(WORK/'public'/path).read_bytes()
            idxpath=Path(path).parent/'public-unit-index.json'
            ib=(WORK/'public'/idxpath).read_bytes();index=json.loads(ib)
            for rel,b in ((path,reader),(idxpath.as_posix(),ib)):
                for source in (published,pages):
                    row=source['docs/en/readers/hefferon-foundations/'+rel]
                    assert row['http']==200 and facts(b)=={k:row[k] for k in ('bytes','sha256')}
            bound[kind]={**bind(native,index,reader),'url':ORIGIN+path+'#'+native['anchor'],
                'reader':{'path':path,**facts(reader)},
                'unit_index':{'path':idxpath.as_posix(),**facts(ib)},
                'immutable_reader_url':RAW+receipt['commit']+'/docs/en/readers/hefferon-foundations/'+path+'#'+native['anchor']}
        rows.append(bound)
    native=provider['complete_proof_units'][-1]['proof']
    for label in ('source_hash','fragment_hash','anchor'):
        bad=copy.deepcopy(native)
        if label=='source_hash':bad['source_fragments'][0]['sha256']='0'*64
        elif label=='fragment_hash':bad['rendered_fragment']['sha256']='0'*64
        else:bad['anchor']='invented-result'
        try:bind(bad,index,reader)
        except AssertionError:negative.append(label)
        else:raise AssertionError('negative case accepted: '+label)
    out={'schema':'open-courses-public-proof-provider-binding/1','date':'2026-10-02',
         'provider_id':provider['id'],'course':'B40','language':'en',
         'description':'Exact public reading routes for the previously checked original-English basis-extension prerequisite chain. Source and rendered statement/proof identities are unchanged. This record establishes access, not downstream proof admission.',
         'description_id':'Tautan bacaan publik yang tepat untuk rangkaian prasyarat perluasan basis berbahasa Inggris yang telah diperiksa sebelumnya. Identitas sumber serta pernyataan dan bukti tidak berubah. Catatan ini membuktikan akses, bukan pengesahan penggunaan bukti oleh mata kuliah lain.',
         'provider_packet':facts(pb),'source_revision':provider['complete_proof_units'][0]['statement']['source_revision'],
         'public_commit':receipt['commit'],'public_tree':receipt['tree'],
         'result_pairs':rows,'conditions':provider['conditions'],'prerequisite_edges':provider['prerequisite_edges'],
         'editorial_dispositions':provider['editorial_dispositions'],'consumers':provider['consumers'],
         'reading_index':ORIGIN,'rights':provider['rights'],
         'source_release':{'url':release['url'],'assets':release['assets']},
         'states':{'published':True,'anonymous_source_and_reader_identity':'PASS','owner_admitted':False,'new_mathematical_admission':False,'entire_book_complete':False},
         'validation':{'statement_proof_pairs':len(rows),'bound_fragments':2*len(rows),'source_and_fragment_equality':'PASS','rejected_mutations':negative},
         'provenance':{'current_work':'Public-route binding and exact source/fragment verification','model':'gpt-6-astra','effort':'ultra','human_review_claimed':False,'historical_provider_unchanged':True}}
    assert all(not c['owner_admitted'] for c in out['consumers'])
    target=WORK/'PUBLIC_PROOF_BINDINGS.json'
    target.write_bytes(dump(out))
    print(json.dumps({'state':'PASS','artifact':target.name,**facts(target.read_bytes()),'pairs':len(rows),'negative_cases':negative}))

if __name__=='__main__':main()
