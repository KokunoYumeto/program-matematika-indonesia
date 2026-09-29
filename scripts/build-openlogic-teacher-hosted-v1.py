"""Stage verified OpenLogic planners without modifying the book or frozen adapter."""
import importlib.util
import json
from pathlib import Path

spec=importlib.util.spec_from_file_location('builder',Path(__file__).with_name('build-openlogic-teacher-v1.py'))
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)


def main():
    load=lambda name:json.loads((b.BASE/name).read_bytes())
    build=load('site/teacher-build.json');tests=load('build-tests.json')
    ui=load('ui-tests.json');browser=load('browser-checks.json');package=load('source-package.json')
    mapping=load('mapping-tests.json')
    assert all(r['state']=='pass' for r in [tests,ui,browser,mapping])
    assert build['edition_binding']==tests['edition_binding']==ui['edition_binding']==browser['edition_binding']
    assert tests['outputs']==build['files'] and tests['input_identities']==build['input_identities']==b.INPUTS
    assert tests['all_source_problems_accounted_for']==438 and tests['negative_mutations']==12
    assert ui['negative']==33 and ui['positive']==93
    assert browser['script_sha256']==ui['script']['sha256'] and browser['model_sha256']==ui['model']['sha256']
    assert package['offline_replay']==package['repacked_archive']=='byte_identical'
    files={}
    for f in build['files']:
        body=(b.BASE/'site'/f['path']).read_bytes()
        assert b.fact(body)=={k:f[k] for k in ['bytes','sha256']}
        files[f['path']]=body
    assert b.fact(files['teacher.js'])==ui['script'] and b.fact(files['C80.teacher.json'])==ui['model']
    archive=(b.BASE/package['archive']).read_bytes()
    assert b.fact(archive)=={k:package[k] for k in ['bytes','sha256']}
    files[package['archive']]=archive
    # Bind the actual reports, not merely their existence or names.
    evidence={name:b.fact((b.BASE/name).read_bytes()) for name in
              ['mapping-tests.json','build-tests.json','ui-tests.json','browser-checks.json','source-package.json']}
    report={'schema':'openlogic-teacher-hosted/1','state':'pass','course_id':'C80',
        'counts':build['counts'],'precise_rendered_exercise_alignment':True,
        'all_source_exercises_accounted_for':True,'solutions_audited':False,
        'input_identities':b.INPUTS,'edition_binding':build['edition_binding'],
        'interface_locales':['id','en'],'reader_language':'id',
        'book_prose_copied':False,'new_translation':False,'evidence':evidence,
        'files':[{'path':name,**b.fact(body)} for name,body in sorted(files.items())],
        'public_deployment_verified':False}
    files['teacher-validation.json']=b.encoded(report)
    out=b.ROOT/'docs/backend/openlogic-teacher';out.mkdir(parents=True,exist_ok=True)
    for name,body in files.items():(out/name).write_bytes(body)
    print(json.dumps({'state':'staged','files':len(files),'counts':report['counts']}))


if __name__=='__main__':main()
