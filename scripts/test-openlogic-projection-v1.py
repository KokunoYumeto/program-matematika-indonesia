"""Position-preserving selective TeX tests; no general TeX execution claim."""
import importlib.util
from pathlib import Path

path=Path(__file__).with_name('map-openlogic-problems-v1.py')
spec=importlib.util.spec_from_file_location('projection',path)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

fixtures=[
    (r'\iftag{a}{YES}{NO}',{'a':True},['YES'],['NO']),
    (r'\iftag{a}{YES}{NO}',{'a':False},['NO'],['YES']),
    (r'\iftag{a,b}{YES}{NO}',{'a':False,'b':True},['YES'],['NO']),
    (r'\iftag{a}{\iftag{b}{INNER}{FALSE}}{OUTER}',{'a':True,'b':True},['INNER'],['FALSE','OUTER']),
    (r'\iftag{a}{\iftag{b}{INNER}{FALSE}}{OUTER}',{'a':False,'b':True},['OUTER'],['INNER','FALSE']),
    (r'\iftag{a}{DROP}\iftag{b}{YES}{NO}',{'a':False,'b':True},['YES'],['DROP','NO']),
    (r'\iftag{a}{DROP}\iftag{b}{YES}{NO}',{'a':False,'b':False},['NO'],['DROP','YES']),
    # With a=true the unbraced false argument is just the \iftag token;
    # its following groups are not arguments to the outer invocation.
    (r'\iftag{a}{KEEP}\iftag{b}{YES}{NO}',{'a':True,'b':False},['KEEP','YES','NO'],[]),
    (r'\tagprob[a]{b}BODY\tagendprob',{'a':True,'b':False},[],['BODY']),
    (r'\tagprob[a]{b}BODY\tagendprob',{'a':True,'b':True},['BODY'],[]),
]
for text,tags,kept,removed in fixtures:
    result=mod.project(text,tags)
    assert len(result)==len(text)
    assert all(a==b or b.isspace() for a,b in zip(text,result))
    for word in kept: assert word in result,(text,result,word)
    for word in removed: assert word not in result,(text,result,word)
for text in [r'\iftag{unknown}{x}{y}',r'\iftag{a}{x}',r'\tagprob{a}x']:
    try: mod.project(text,{'a':True})
    except ValueError: pass
    else: raise AssertionError(('Malformed input accepted',text))
print({'state':'pass','positive_fixtures':len(fixtures),'negative_fixtures':3})
