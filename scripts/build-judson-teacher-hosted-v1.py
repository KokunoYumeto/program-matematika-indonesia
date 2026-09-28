"""Stage the verified reference planners beside existing Judson chapter tools."""
import importlib.util
import json
from pathlib import Path

spec=importlib.util.spec_from_file_location('judson',Path(__file__).with_name('build-judson-teacher-v1.py'))
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)


def main():
    tests=json.loads((b.BASE/'tests.json').read_bytes())
    package=json.loads((b.BASE/'source-package.json').read_bytes())
    built=json.loads((b.BASE/'site/teacher-build.json').read_bytes())
    assert tests['state']=='pass' and tests['input_identity']==built['input_identity']
    assert tests['native_checks']=={'all_native_exercises':913,'all_native_support_edges':329,'all_source_target_subtrees':1242,'source_archive_rehashed':True}
    assert package['offline_replay']==package['repacked_archive']=='byte_identical'
    outputs={}
    for f in built['files']:
        data=(b.BASE/'site'/f['path']).read_bytes()
        assert b.fact(data)=={k:f[k] for k in ['bytes','sha256']}
        outputs[f['path']]=data
    archive=(b.BASE/package['archive']).read_bytes()
    assert b.fact(archive)=={k:package[k] for k in ['bytes','sha256']}
    outputs[package['archive']]=archive
    report={'schema':'judson-teacher-hosted/1','state':'pass','course_counts':b.COUNTS,
      'interface_locales':['id','en'],'source_translation_created':False,'book_prose_copied':False,
      'precise_target_exercise_alignment':{'C30':True,'C40':True},
      'support_counts':{'supplied_hints':213,'empty_response_slots':116,'supplied_responses':0,'supplied_solutions':0},
      'primary_reader_counts':{'web':814,'sage':99},'verified_current_reader_anchors':913,
      'input_identity':built['input_identity'],'current_reader_identity':built['current_reader_identity'],
      'files':[{'path':n,**b.fact(data)} for n,data in sorted(outputs.items())],
      'public_deployment_verified':False}
    outputs['teacher-validation.json']=b.encoded(report)
    out=b.ROOT/'docs/backend/judson';out.mkdir(parents=True,exist_ok=True)
    for name,data in outputs.items():(out/name).write_bytes(data)
    print(json.dumps({'state':'staged','files':len(outputs),'course_counts':b.COUNTS}))


if __name__=='__main__':main()
