"""Stage the verified C130 planner; preserve the frozen native C130 adapter."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT/'backend/course-capsule-v1/adapters/c130-teacher-v1'
def fact(raw):return {'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()}


def main():
    load=lambda name:json.loads((BASE/name).read_bytes())
    build=load('site/build-receipt.json');tests=load('validation.json');ui=load('ui-tests.json');browser=load('browser-checks.json')
    assert all(r['state']=='pass' for r in [tests,ui,browser])
    assert tests['build']==build and tests['mapping']==build['mapping']
    assert tests['source_mapping_replays']==2 and tests['offline_source_zip_replay'] is True
    assert ui['positive']==20 and ui['negative']==18 and tests['negative_cases']==28
    assert ui['script']==build['files']['teacher.js'] and ui['model']==build['files']['planner-model.json']
    assert browser['mapping_sha256']==build['mapping']['sha256']
    for name,value in browser['assets'].items():assert value==build['files'][name]['sha256']
    for path,value in build['source_members'].items():assert fact((ROOT/path).read_bytes())==value,path
    files={name:(BASE/'site'/name).read_bytes() for name in build['files']}
    for name,raw in files.items():assert fact(raw)==build['files'][name],name
    evidence={name:fact((BASE/name).read_bytes()) for name in ['validation.json','ui-tests.json','browser-checks.json']}
    report={'schema':'c130-teacher-hosted/1','state':'pass','course_id':'C130','counts':build['counts'],
        'precise_selected_exercise_and_activity_alignment':True,'all_native_solution_alignment':False,
        'source_only_legacy_exercises':4,'unmapped_other_solution_sources':0,
        'explicit_solution_heading_mappings':12,'ordered_composite_mappings':14,'adjacent_example_mappings':2,
        'mathematical_correctness_rechecked':False,'solver_results_reexecuted':False,'reader_language':'id',
        'interface_locales':['id','en'],'mapping':build['mapping'],'evidence':evidence,
        'files':{name:fact(raw) for name,raw in sorted(files.items())},'public_deployment_verified':False}
    out=ROOT/'docs/backend/c130-teacher';out.mkdir(parents=True,exist_ok=True)
    for name,raw in files.items():(out/name).write_bytes(raw)
    (out/'teacher-validation.json').write_text(json.dumps(report,ensure_ascii=False,sort_keys=True,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps({'state':'staged','role':'C130','files':len(files)+1,'selectable_items':227}))


if __name__=='__main__':main()
