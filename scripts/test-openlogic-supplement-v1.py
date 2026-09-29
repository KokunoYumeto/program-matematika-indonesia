"""Exercise the supplement candidate boundaries without claiming admission."""
import copy
import importlib.util
from pathlib import Path

spec=importlib.util.spec_from_file_location('supplement',Path(__file__).with_name('map-openlogic-supplement-v1.py'))
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
raw=b'\\begin{prob}Buktikan bahwa himpunan tersebut mempunyai sifat berikut.\\end{prob}'
identity=mod.intake.identity(raw)
unit={'source_path':'content/example.tex','native_unit_id':'OLP-native',
      'source':{'sha256':'source-hash'},'target':identity}
problem={'id':'problem-1','source_path':unit['source_path'],
         'target':{'byte_start':0,'byte_end_exclusive':len(raw),'block':identity}}
coverage={'source_path':unit['source_path'],'source_sha256':'source-hash',
          'target_sha256':identity['sha256'],'pdf_start_page':'5','pdf_end_page':'6',
          'closure_id':'OLP-different-producer-index'}
destination={'destination':'prob*.4','component_page':4,'combined_page':1120,
             'heading_combined_page':1121,'printed_number':'1.2',
             '_text':'Soal 1.2 Buktikan bahwa himpunan tersebut mempunyai sifat berikut.'}
def run(p=problem,u=unit,c=coverage,ds=None,data=raw):
    return mod.candidates(p,u,c,[destination] if ds is None else ds,data)
row=run()
assert len(row['candidates'])==1
assert row['state']=='diagnostic_not_admitted'
assert row['native_unit_id']!=row['producer_closure_id']
assert row['file_combined_page_span']==[1121,1122]
assert row['candidates'][0]['longest_literal_word_run']==7
assert row['candidates'][0]['component_page']==4  # Heading, not anchor, is in span.
for page in [1120,1123,None]:
    altered={**destination,'heading_combined_page':page}
    assert run(ds=[altered])['candidates']==[]
assert len(run(ds=[destination,{**destination,'destination':'prob*.5'}])['candidates'])==2
# A tie remains two candidates; never guess one identity.
negative=0
for key,value in [('source_path','wrong'),('source_sha256','wrong'),
                  ('target_sha256','wrong'),('pdf_start_page','0'),('pdf_end_page','140')]:
    changed={**coverage,key:value}
    try:run(c=changed)
    except AssertionError:negative+=1
    else:raise AssertionError(('Invalid coverage accepted',key))
bad_problem=copy.deepcopy(problem);bad_problem['target']['block']['sha256']='wrong'
try:run(p=bad_problem)
except AssertionError:negative+=1
else:raise AssertionError('Block drift accepted')
try:run(p={**problem,'source_path':'wrong'})
except AssertionError:negative+=1
else:raise AssertionError('Wrong source join accepted')
print({'state':'pass','positive_cases':5,'negative_cases':negative})
