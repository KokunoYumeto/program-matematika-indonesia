import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
const base=new URL('../backend/course-capsule-v1/adapters/a00-native-ledger-v1/views/',import.meta.url);
for(const name of ['ledger.html','ledger-en.html']){
  const html=readFileSync(new URL(name,base),'utf8');
  const rows=[...html.matchAll(/<tr data-search="([^"]*)">/g)].map(match=>({dataset:{search:match[1]},hidden:false}));
  assert.equal(rows.length,95);
  const input={value:'',addEventListener(event,handler){assert.equal(event,'input');this.handler=handler;}};
  const count={textContent:''};
  const document={getElementById(id){return id==='search'?input:count;},querySelectorAll(selector){assert.equal(selector,'[data-search]');return rows;}};
  const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];
  assert.equal(scripts.length,1);
  vm.runInNewContext(scripts[0][1],{document},{timeout:1000});
  assert.equal(count.textContent,'95 / 95');
  for(const query of ['m81272','bilangan','M81243','not-a-real-term']){
    input.value=query;input.handler();
    assert.equal(rows.filter(r=>!r.hidden).length,rows.filter(r=>r.dataset.search.toLowerCase().includes(query.toLowerCase())).length);
  }
  input.value='';input.handler();assert.equal(rows.filter(r=>!r.hidden).length,95);
  assert.match(html,/aria-live="polite"/);assert.match(html,/<label for="search">/);
}
console.log(JSON.stringify({status:'pass',locales:2,actual_search_handlers:true,rows_per_locale:95}));
