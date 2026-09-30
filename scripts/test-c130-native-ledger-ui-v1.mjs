import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const root=new URL('../backend/course-capsule-v1/adapters/c130-native-ledger-v1/',import.meta.url);
const script=readFileSync(new URL('ui/ledger.js',root),'utf8');
let checks=0;
for(const name of ['ledger.html','ledger.en.html']){
 const html=readFileSync(new URL('site/'+name,root),'utf8');
 const records=[...html.matchAll(/<article class="record" data-kind="([^"]+)" data-search="([^"]*)">/g)]
  .map(m=>({dataset:{kind:m[1],search:m[2]},hidden:false}));
 assert.equal(records.length,234);
 const query={value:'',addEventListener(e,f){assert.equal(e,'input');this.handler=f;}};
 const kind={value:'',addEventListener(e,f){assert.equal(e,'change');this.handler=f;}};
 const count={textContent:'',dataset:{label:'count'}};
 const document={getElementById(id){return {query,kind,count}[id]},querySelectorAll(s){assert.equal(s,'.record');return records}};
 vm.runInNewContext(script,{document},{timeout:1000});
 const visible=()=>records.filter(r=>!r.hidden).length;
 assert.equal(visible(),234);checks++;
 kind.value='term';kind.handler();assert.equal(visible(),140);checks++;
 kind.value='correction';kind.handler();assert.equal(visible(),94);checks++;
 kind.value='';query.value='term.additivity.id';query.handler();assert.equal(visible(),1);checks++;
 query.value='LINEARISASI NILAI MUTLAK';query.handler();assert.equal(visible(),1);checks++;
 query.value='CORR-CH10-MATRIX-AN-SIGNS';query.handler();assert.equal(visible(),1);checks++;
 kind.value='term';kind.handler();assert.equal(visible(),0);checks++;
 query.value='nonexistent-string-234';query.handler();assert.equal(visible(),0);checks++;
 kind.value='';query.value='';query.handler();assert.equal(visible(),234);checks++;
 assert.match(html,/aria-live="polite"/);
 assert.doesNotMatch(script,/fetch\(|localStorage|sessionStorage|XMLHttpRequest/);
}
console.log(JSON.stringify({state:'pass',locales:2,filter_checks:checks,offline_filtering:true}));
