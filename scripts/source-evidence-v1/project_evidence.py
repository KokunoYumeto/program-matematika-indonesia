"""Build, check or query a portable projection from an explicit frozen input."""
import argparse,json,sys
from pathlib import Path
from source_use_projection import encoded,need,project,validate

def jsonlines(rows):
    return b''.join((json.dumps(row,ensure_ascii=False,sort_keys=True,separators=(',',':'))+'\n').encode() for row in rows)

def exports(value):
    return {'projection.json':encoded(value),'source-use-evidence.jsonl':jsonlines(value['source_uses'])}

def main():
    # Windows redirected stdout otherwise uses the active ANSI code page,
    # even though the contract and on-disk exports are UTF-8.
    sys.stdout.reconfigure(encoding='utf-8')
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('input',type=Path)
    parser.add_argument('--output',type=Path)
    parser.add_argument('--check',action='store_true')
    queries=parser.add_mutually_exclusive_group()
    queries.add_argument('--result',help='An existing native result or requirement ID, not a new tag')
    queries.add_argument('--source',help='A content fingerprint, optionally prefixed sha256:')
    args=parser.parse_args();bundle=json.loads(args.input.read_bytes());value=project(bundle)
    if args.result:
        rows=[r for r in value['source_uses'] if r['target']['id']==args.result or r['within_record']['id']==args.result]
        records=[r for r in value['records'] if r['id']==args.result]
        need(rows or records,'No such result in the selected evidence')
        print(json.dumps({'records':records,'source_uses':rows},ensure_ascii=False,indent=2));return
    if args.source:
        key='sha256:'+args.source.removeprefix('sha256:').lower()
        rows=[r for r in value['source_uses'] if r['source_binding']==key]
        matches=[a for a in value['artifact_bindings'] if a['binding_id']==key]
        need(matches,'No such source fingerprint in the selected evidence')
        print(json.dumps({'artifact_bindings':matches,'source_uses':rows},ensure_ascii=False,indent=2));return
    need(args.output is not None,'An explicit output directory is required for build/check')
    payloads=exports(value)
    if args.check:
        for name,raw in payloads.items():need((args.output/name).read_bytes()==raw,'Replay mismatch: '+name)
        validate(json.loads((args.output/'projection.json').read_bytes()),bundle)
    else:
        args.output.mkdir(parents=True,exist_ok=True)
        for name,raw in payloads.items():(args.output/name).write_bytes(raw)
    print(json.dumps({'state':'PASS','mode':'check' if args.check else 'build','counts':value['counts']}))

if __name__=='__main__':main()
