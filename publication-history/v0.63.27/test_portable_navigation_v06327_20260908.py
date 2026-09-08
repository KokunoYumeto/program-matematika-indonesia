"""No browser: test the exact portable URL resolver in a Node VM."""
import importlib.util
import json
from pathlib import Path
import subprocess

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('builder',HERE/'prepare_navigator_v06327_20260908.py')
builder=importlib.util.module_from_spec(spec);spec.loader.exec_module(builder)
members=['docs/id/learning-map-paired.html','docs/en/learning-map-paired.html','docs/id-ID/courses/A10/reader/index.html','docs/backend/b95/index.html']
source=builder.portable_script(members).decode()
prefix=source[:source.index('function rewrite')]+ 'globalThis.resolvePortable=localTarget;})();'
program='''const vm=require('node:vm');const assert=require('node:assert/strict');
let input='';process.stdin.setEncoding('utf8');process.stdin.on('data',x=>input+=x);process.stdin.on('end',()=>{
 const src=JSON.parse(input);const sandbox={URL,document:{currentScript:{src:'file:///test/program/PORTABLE_NAVIGATION.js'},baseURI:'file:///test/program/docs/id/learning-map-paired.html'}};
 vm.createContext(sandbox);vm.runInContext(src,sandbox);const resolve=sandbox.resolvePortable;
 const base='https://kokunoyumeto.github.io/program-matematika-indonesia/';
 const cases=[
 [base+'id/','file:///test/program/docs/id/learning-map-paired.html'],
 [base+'en/index.html?course=A10#course-A10','file:///test/program/docs/en/learning-map-paired.html?course=A10#course-A10'],
 ['/en/?x=1#course-D30','file:///test/program/docs/en/learning-map-paired.html?x=1#course-D30'],
 ['/id/','file:///test/program/docs/id/learning-map-paired.html'],
 [base,'file:///test/program/START-HERE.html'],
 [base+'id-ID/courses/A10/reader/index.html#module-m82479','file:///test/program/docs/id-ID/courses/A10/reader/index.html#module-m82479'],
 [base+'backend/b95/','file:///test/program/docs/backend/b95/index.html'],
 [base+'missing.html',null],['https://openstax.org/details/books/elementary-algebra-2e',null],
 ['https://kokunoyumeto.github.io/program-matematika-indonesia-evil/id/',null],
 ['https://evil.invalid/program-matematika-indonesia/id/',null],['javascript:alert(1)',null],
 [base+'../secret',null],[base+'%2e%2e/secret',null],['file:///private/secret',null]
 ];for(const [raw,want]of cases)assert.equal(resolve(raw),want,raw);
 assert.ok(src.includes('members.has'));console.log(JSON.stringify({status:'pass',cases:cases.length}));
});'''
result=subprocess.run(['node','-e',program],input=json.dumps(prefix),text=True,capture_output=True,check=True)
receipt=json.loads(result.stdout)
receipt.update({'scope':'exact pure URL resolver; no browser; local and publisher link semantics','source_builder':'prepare_navigator_v06327_20260908.py'})
(HERE/'central-a10-reader-20260908/PORTABLE_NAVIGATION_TEST_RECEIPT.json').write_text(json.dumps(receipt,indent=2)+'\n',encoding='utf-8')
print(json.dumps(receipt))
