"""Independent negative fixtures and deterministic source/PDF mapping replay."""
import argparse
import copy
import importlib.util
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/'scripts'/path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
supp=load('verify_supp','verify-openlogic-supplement-exercises-v1.py')
main_map=load('verify_main','verify-openlogic-main-exercises-v1.py')


def fixtures():
    choice={'id':'sample','number':'2.2','source_exact':['\\LeftR{\\lforall}'],
            'pdf_exact':['berakhir dengan ∀L.'],'rule':'formula_or_rule'}
    src=r'Periksa kasus D, berakhir dengan \LeftR{\lforall}.'
    ds=[{'destination':'prob*.146','component_page':36,'combined_page':1152,
         'heading_combined_page':1152,'printed_number':'2.2',
         '_text':'Soal 2.2. Periksa kasus D, berakhir dengan ∀L.\n'}]
    assert supp.verify_choice(choice,src,ds,ds)['component_page']==36
    cases=[]
    def fixture(c=choice,s=src,options=ds,rendered=ds):
        cases.append((copy.deepcopy(c),s,copy.deepcopy(options),copy.deepcopy(rendered)))
    fixture(c={**choice,'source_exact':[]})
    fixture(c={**choice,'pdf_exact':[]})
    fixture(c={**choice,'source_exact':['\\LeftR{\\lif}']})
    fixture(c={**choice,'pdf_exact':['berakhir dengan →L.']})
    fixture(c={**choice,'number':'2.1'})
    fixture(options=[])
    fixture(rendered=ds+ds)
    fixture(rendered=[{**ds[0],'_text':'berakhir dengan ∀L.\nSoal 2.2. Other text'}])
    other={**ds[0],'destination':'prob*.148','printed_number':'2.3',
           '_text':'Soal 2.3. Periksa kasus D, berakhir dengan ∀L.'}
    fixture(options=ds+[other],rendered=ds+[other])
    for c,s,options,rendered in cases:
        try:supp.verify_choice(c,s,options,rendered)
        except AssertionError:pass
        else:raise AssertionError(('Unsafe supplement association accepted',c))
    numbering=main_map.numbering
    aux=numbering.labels('\\newlabel{part:chap:sect:sec}{{2.4}{10}{Title}{section*.1}{}}\n')
    native={'problems':[{'id':'one','file_id_contexts':['part:chap:sect']},
                        {'id':'two','file_id_contexts':['part:chap:sect']}]}
    rows=[{'source_problem_id':'one','fol_context':True,'printed_number':'2.1','destination':'p1'},
          {'source_problem_id':'two','fol_context':True,'printed_number':'2.2','destination':'p2'}]
    assert numbering.check_numbering(native,{'comparisons':rows},aux)['errors']==[]
    wrong=copy.deepcopy(rows);wrong[1]['printed_number']='2.3'
    assert numbering.check_numbering(native,{'comparisons':wrong},aux)['errors']
    assert numbering.check_numbering(native,{'comparisons':list(reversed(rows))},aux)['errors']
    assert numbering.check_numbering(native,{'comparisons':rows},{})['errors']
    try:numbering.labels('\\newlabel{a}{{1}{2}}\\newlabel{a}{{1}{2}}')
    except AssertionError:pass
    else:raise AssertionError('Duplicate AUX labels accepted')
    return {'positive':2,'negative':len(cases)+4}


def main():
    p=argparse.ArgumentParser();p.add_argument('--workspace',type=Path,required=True)
    p.add_argument('--cache',type=Path,required=True);p.add_argument('--out',type=Path,required=True)
    a=p.parse_args();counts=fixtures();receipts={}
    for name,module in [('main',main_map),('supplement',supp)]:
        first=json.dumps(module.verify(a.workspace,a.cache),ensure_ascii=False,indent=2).encode()+b'\n'
        second=json.dumps(module.verify(a.workspace,a.cache),ensure_ascii=False,indent=2).encode()+b'\n'
        assert first==second,('Non-deterministic mapping',name)
        receipts[name]=supp.intake.identity(first)
    result={'schema':'openlogic-teacher-mapping-tests/1','state':'pass','fixtures':counts,
            'identical_replays':2,'main_printed_occurrences':411,'supplement_printed_occurrences':31,
            'distinct_rendered_source_problems':427,'retained_tag_disabled':10,'retained_unflushed':1,
            'maps':receipts,'scope':'Exercise identities only; no automatic claim that the teacher UI or full course integration is complete.'}
    a.out.parent.mkdir(parents=True,exist_ok=True)
    a.out.write_text(json.dumps(result,indent=2)+'\n',encoding='utf-8',newline='\n')
    print(json.dumps(result))


if __name__=='__main__':main()
