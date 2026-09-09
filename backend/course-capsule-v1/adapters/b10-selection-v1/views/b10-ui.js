(() => {
 'use strict';
 const get=id=>document.getElementById(id),model=globalThis.B10Model,C=globalThis.B10Selection;
 const {locale,labels:L}=JSON.parse(get('b10-page-data').textContent),selected=new Set();let page=0,matches=[];
 const sections=()=>Array.from(document.querySelectorAll('input[name="section"]:checked'),x=>x.value);
 const filters=()=>({hint:get('hint').value,answer:get('answer').value,solution:get('solution').value,query:get('query').value});
 const node=(tag,text)=>{const e=document.createElement(tag);if(text)e.textContent=text;return e;};
 const link=(r,label)=>{const e=node('a',label);e.href=r.url;e.hreflang='en';return e;};
 function counts(){get('count').textContent=matches.length+' '+L.matches+' · '+selected.size+' '+L.chosen;for(const id of ['download-json','download-html'])get(id).disabled=selected.size===0;}
 function render(reset=false){
  matches=C.select(model,sections(),filters());const allowed=new Set(matches.map(e=>e.id));for(const id of selected)if(!allowed.has(id))selected.delete(id);
  if(reset)page=0;page=Math.min(page,Math.max(0,Math.ceil(matches.length/30)-1));get('results').replaceChildren();
  for(const e of matches.slice(page*30,(page+1)*30)){
   const li=node('li'),choice=node('input');choice.type='checkbox';choice.checked=selected.has(e.id);choice.value=e.id;choice.setAttribute('aria-label',L.exercises+' '+e.native_id);
   choice.addEventListener('change',()=>{choice.checked?selected.add(e.id):selected.delete(e.id);counts();});li.append(choice,' ',link(e.routes[0],e.native_id));
   if(e.route_granularity==='containing_source_unit')li.append(' — '+L.containing);
   const support=node('ul');for(const k of ['hint','answer','solution']){const item=node('li',L[k]+': ');if(!e.support[k].length)item.append(L.absent);
    for(const [i,r] of e.support[k].entries()){if(i)item.append('; ');item.append(link(r.routes[0],r.native_id));if(r.route_granularity==='containing_source_unit')item.append(' ('+L.containing+')');}support.append(item);}
   li.append(support);get('results').append(li);
  }
  if(!matches.length)get('results').append(node('li',L.empty));get('page').textContent=(page+1)+' / '+Math.max(1,Math.ceil(matches.length/30));
  get('previous').disabled=page===0;get('next').disabled=(page+1)*30>=matches.length;counts();
 }
 for(const el of document.querySelectorAll('input[name="section"]'))el.addEventListener('change',()=>render(true));
 for(const id of ['hint','answer','solution','query'])get(id).addEventListener('input',()=>render(true));
 get('select-all').addEventListener('click',()=>{for(const e of matches)selected.add(e.id);render();});
 get('clear').addEventListener('click',()=>{selected.clear();render();});
 get('previous').addEventListener('click',()=>{page--;render();});get('next').addEventListener('click',()=>{page++;render();});
 function download(type){try{const intent=Object.fromEntries(Object.keys(L.fields).map(k=>[k,get('intent-'+k).value]));const p=C.plan(model,sections(),[...selected],filters(),intent,locale);
  const payload=type==='json'?JSON.stringify(p,null,2)+'\n':C.renderPlan(p,L);const blob=new Blob([payload],{type:type==='json'?'application/json':'text/html;charset=utf-8'});
  const url=URL.createObjectURL(blob),a=node('a');a.href=url;a.download='B10-study-plan.'+type;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);get('error').textContent='';
 }catch{get('error').textContent=L.error;}}
 get('download-json').addEventListener('click',()=>download('json'));get('download-html').addEventListener('click',()=>download('html'));render();
})();
