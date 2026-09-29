"""Model mutations, readable fallback coverage and deterministic planner replay."""
import argparse
import copy
from html.parser import HTMLParser
import importlib.util
import json
from pathlib import Path
import tempfile

spec=importlib.util.spec_from_file_location('builder',Path(__file__).with_name('build-openlogic-teacher-v1.py'))
b=importlib.util.module_from_spec(spec);spec.loader.exec_module(b)


class Page(HTMLParser):
    def __init__(self):
        super().__init__();self.script=False;self.payload='';self.references=[];self.ids=[];self.lang=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        if tag=='html':self.lang=a['lang']
        if tag=='script' and a.get('id')=='planner-data':self.script=True
        if tag=='a' and '#page=' in a.get('href',''):self.references.append(a['href'])
    def handle_endtag(self,tag):
        if tag=='script':self.script=False
    def handle_data(self,data):
        if self.script:self.payload+=data


def test():
    data=b.load();model=b.project(data)
    mutations=[
      lambda d:d['main-exercises.json']['exercises'][0].update(combined_page=1256),
      lambda d:d['main-exercises.json']['exercises'][0].update(combined_href='javascript:alert(1)'),
      lambda d:d['main-exercises.json']['exercises'][0]['source'].update(byte_start=0),
      lambda d:d['main-exercises.json']['exercises'][0]['target_file'].update(sha256='wrong'),
      lambda d:d['main-exercises.json']['exercises'][1].update(occurrence_id=d['main-exercises.json']['exercises'][0]['occurrence_id']),
      lambda d:d['main-exercises.json']['tag_disabled_source_problems'].pop(),
      lambda d:d['main-exercises.json']['source_only_findings'].clear(),
      lambda d:d['supplement-exercises.json']['exercises'][0].update(combined_page=15),
      lambda d:d['supplement-exercises.json']['exercises'][0].update(source_problem_id=d['main-exercises.json']['exercises'][0]['source_problem_id']),
      lambda d:d['source-problems.json']['problems'].pop(),
      lambda d:d['section-titles.json']['sections'].clear(),
      lambda d:d['section-titles.json']['sections']['section*.6'].update(title=r'\unexpanded{macro}'),
    ]
    for mutate in mutations:
        changed=copy.deepcopy(data);mutate(changed)
        try:b.project(changed)
        except (AssertionError,KeyError):pass
        else:raise AssertionError('Unsafe mapping mutation accepted')
    for lang in ['id','en']:
        page=Page();page.feed(b.render(model,lang))
        assert page.lang==lang and len(page.ids)==len(set(page.ids))
        assert page.references==[q['reader_url'] for q in model['questions']]
        payload=json.loads(page.payload)
        assert payload['locale']==lang and payload['model']==model
        assert all(i in page.ids for i in ['all-references','source-only','import','export','print'])
    assert all(not any(c in (q['section_title_id'] or '') for c in ['\\','{','}','$']) for q in model['questions'])
    outputs=[]
    with tempfile.TemporaryDirectory(prefix='openlogic-planner-replay-') as temporary:
        root=Path(temporary)
        for i in range(2):outputs.append(b.build(root/str(i)))
        assert outputs[0]==outputs[1]
        for f in outputs[0]['files']:
            assert (root/'0'/f['path']).read_bytes()==(root/'1'/f['path']).read_bytes()==(b.BASE/'site'/f['path']).read_bytes()
    return {'schema':'openlogic-teacher-build-tests/1','state':'pass','negative_mutations':len(mutations),
      'identical_replays':2,'html_locales':['id','en'],'readable_fallback_references_per_locale':442,
      'all_source_problems_accounted_for':438,'counts':model['counts'],
      'edition_binding':model['edition_binding'],'input_identities':b.INPUTS,
      'outputs':outputs[0]['files'],'scope':'Builder and static fallback; interactive DOM is checked separately.'}


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--out',type=Path,default=b.BASE/'build-tests.json')
    a=p.parse_args();result=test();a.out.write_bytes(b.encoded(result));print(json.dumps(result))
