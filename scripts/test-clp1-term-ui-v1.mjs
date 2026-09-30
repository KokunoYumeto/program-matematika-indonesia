import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import vm from 'node:vm';
for(const name of ['B20.terms.html','B20.terms.en.html']){
 const html=readFileSync(new URL('../docs/backend/clp/'+name,import.meta.url),'utf8');
 const rows=[...html.matchAll(/<article id="[^"]+" data-search="([^"]*)" data-corrected="(true|false)">/g)].map(m=>({dataset:{search:m[1],corrected:m[2]},hidden:false}));
 assert.equal(rows.length,24);
 const input={value:'',addEventListener(e,f){assert.equal(e,'input');this.handler=f;}};
 const toggle={checked:false,addEventListener(e,f){assert.equal(e,'change');this.handler=f;}};
 const count={textContent:''};
 const document={getElementById(id){return {search:input,corrected:toggle,count}[id];},querySelectorAll(s){assert.equal(s,'[data-search]');return rows;}};
 const scripts=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)];assert.equal(scripts.length,1);
 vm.runInNewContext(scripts[0][1],{document},{timeout:1000});assert.equal(count.textContent,'24 / 24');
 for(const [q,n] of [['absolute maximum',1],['maksimum',2],['CEKUNG',2],['clp1.term.down',1],['no-such-term',0]]){
  input.value=q;input.handler();assert.equal(rows.filter(r=>!r.hidden).length,n);
 }
 input.value='';toggle.checked=true;toggle.handler();assert.equal(count.textContent,'3 / 24');
 input.value='down';input.handler();assert.equal(count.textContent,'1 / 24');
 toggle.checked=false;input.value='';input.handler();assert.equal(count.textContent,'24 / 24');
 assert.match(html,/aria-live="polite"/);assert.match(html,/<label for="search">/);
}
console.log(JSON.stringify({state:'pass',locales:2,search_cases:10,repair_filters:4,offline_runtime:true}));
