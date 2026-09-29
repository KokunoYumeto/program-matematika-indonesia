"""Bounded source inventory replay and hostile parser/identity fixtures."""
import argparse
from copy import deepcopy
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('ol_intake',ROOT/'scripts/intake-openlogic-teacher-v1.py')
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)


def fixtures():
    cases=[
        (br'\begin{prob}x\end{prob}',1),
        (br'\begin{ex}not an exercise\end{ex}',0),
        (b'% \\begin{prob}x\\end{prob}\n',0),
        (br'\% \begin{prob}x\end{prob}',1),
        (b'\\\\% \\begin{prob}x\\end{prob}\n',0),
        (br'\verb|\begin{prob}fake\end{prob}|',0),
        (br'\verb*+\begin{prob}fake\end{prob}+',0),
        (br'\begin{verbatim}\begin{prob}fake\end{prob}\end{verbatim}',0),
        (br'\begin{probtag}{FOL}{x}x\end{probtag}',1),
        ('é\n\\begin{prob}α\\end{prob}'.encode(),1),
        (b'\xef\xbb\xbf\\begin{prob}x\\end{prob}',1),
        (b'\\begin{prob}\r\nx\r\n\\end{prob}',1),
    ]
    for raw,count in cases:
        result=b.blocks(raw);assert len(result)==count
        for row in result:
            segment=raw[row['byte_start']:row['byte_end_exclusive']]
            assert segment.startswith(('\\begin{'+row['environment']+'}').encode())
            assert segment.endswith(('\\end{'+row['environment']+'}').encode())
            assert b.identity(segment)==row['block']
    bad=[br'\begin{prob}unclosed',br'\end{prob}',br'\begin{prob}\end{probtag}',
         br'\begin{prob}\begin{prob}nested\end{prob}\end{prob}',br'\verb|unclosed',
         br'\begin{verbatim}unclosed',br'\begin{minted}unsupported\end{minted}']
    for raw in bad:
        try:b.blocks(raw)
        except ValueError:pass
        else:raise AssertionError(('Invalid syntax accepted',raw))
    try:b.materialized_source(b'x\n',b.identity(b'y\r\n'))
    except AssertionError:pass
    else:raise AssertionError('Source drift accepted')
    assert b.materialized_source(b'x\n',b.identity(b'x\r\n'))==(b'x\r\n','frozen_CRLF_materialization')
    return len(cases),len(bad)+1


def main():
    p=argparse.ArgumentParser();p.add_argument('--workspace',type=Path,required=True)
    p.add_argument('--report',type=Path,required=True);args=p.parse_args()
    positive,negative=fixtures()
    fresh=b.collect(args.workspace)
    retained=json.loads((b.OUT/'source-problems.json').read_bytes())
    assert fresh==retained
    assert fresh==b.collect(args.workspace),'Nondeterministic source replay'
    assert fresh['counts']=={'source_target_files':722,'source_problems':438,'source_problems_main':407,
                            'source_problems_supplement':31,'labelled_source_problems':11,'source_target_label_changes':1,
                            'byte_modes':{'frozen_CRLF_materialization':638,'exact_archive_bytes':84}}
    changes=[r for r in fresh['problems'] if not r['source_target_labels_identical']]
    assert len(changes)==1 and changes[0]['native_unit_id']=='OLP-0040'
    for key,value in [('id','bogus'),('native_unit_id','OLP-9999'),('reader_mapping_state','verified')]:
        changed=deepcopy(retained);changed['problems'][0][key]=value
        assert changed!=fresh;negative+=1
    report={'status':'pass','source_target_pairs_rehashed':722,'source_problems':438,
            'positive_parser_fixtures':positive,'negative_fixtures':negative,
            'two_replays_identical':True,'source_target_label_changes_preserved':1,
            'reader_mapping_claimed':False,'inventory':b.identity((b.OUT/'source-problems.json').read_bytes())}
    args.report.parent.mkdir(parents=True,exist_ok=True)
    args.report.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(report))


if __name__=='__main__':main()
