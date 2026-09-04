import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';

export const sha256 = value => createHash('sha256').update(value).digest('hex');
export function sorted(value) {
  if (Array.isArray(value)) return value.map(sorted);
  if (value && typeof value === 'object') return Object.fromEntries(Object.keys(value).sort().map(key=>[key,sorted(value[key])]));
  return value;
}
function encode(value, pretty=false, depth=0) {
  if(typeof value==='number') {assert.ok(Number.isFinite(value),'Non-JSON numeric value');return Object.is(value,-0)?'-0':JSON.stringify(value);}
  if(value===null||typeof value==='string'||typeof value==='boolean')return JSON.stringify(value);
  assert.ok(value && typeof value==='object','Non-JSON value');
  const array=Array.isArray(value),keys=array?value.map((_,i)=>i):Object.keys(value).sort();
  const items=keys.map(key=>(array?'':JSON.stringify(key)+(pretty?': ':':'))+encode(value[key],pretty,depth+1));
  const open=array?'[':'{',close=array?']':'}';
  return !items.length?open+close:pretty?open+'\n'+items.map(item=>'  '.repeat(depth+1)+item).join(',\n')+'\n'+'  '.repeat(depth)+close:open+items.join(',')+close;
}
export const json = value => encode(value,true)+'\n';
export const line = value => encode(value);

// A lossless envelope, not a claim that unlike native types share one ontology.
// Array order and absent/null distinctions survive the inverse operation.
export function exportCatalog(catalog, dataset) {
  assert.ok(catalog && !Array.isArray(catalog) && typeof catalog==='object');
  const shape=[],records=[];
  for (const table of Object.keys(catalog).sort()) {
    const array=Array.isArray(catalog[table]);
    const values=array?catalog[table]:[catalog[table]];
    shape.push({table,kind:array?'array':'value',count:values.length});
    const seen=new Set();
    for (const [ordinal,payload] of values.entries()) {
      const nativeId=payload && typeof payload==='object' && typeof payload.id==='string'?payload.id:null;
      if(nativeId!==null){assert.ok(!seen.has(nativeId),`${table}: duplicate native id`);seen.add(nativeId);}
      records.push({contract:'native-catalog-exchange/1',dataset,table,ordinal,native_id:nativeId,payload});
    }
  }
  return {shape,records};
}
export function importCatalog(shape,records,dataset) {
  const output={},used=new Set();
  for(const item of shape){
    assert.ok(!Object.hasOwn(output,item.table),'Duplicate shape table');
    assert.ok(['array','value'].includes(item.kind));
    assert.ok(Number.isInteger(item.count)&&item.count>=0);
    if(item.kind==='value') assert.equal(item.count,1);
    const selected=records.filter(row=>row.table===item.table).sort((a,b)=>a.ordinal-b.ordinal);
    assert.equal(selected.length,item.count,`${item.table}: lost or additional records`);
    const nativeIds=new Set();
    for(const [ordinal,row] of selected.entries()){
      assert.equal(row.contract,'native-catalog-exchange/1');assert.equal(row.dataset,dataset);
      assert.equal(row.ordinal,ordinal,`${item.table}: duplicate/missing ordinal`);
      assert.equal(row.native_id,row.payload && typeof row.payload==='object' && typeof row.payload.id==='string'?row.payload.id:null);
      if(row.native_id!==null){assert.ok(!nativeIds.has(row.native_id),`${item.table}: duplicate native id`);nativeIds.add(row.native_id);}
      used.add(row);
    }
    Object.defineProperty(output,item.table,{value:item.kind==='array'?selected.map(row=>row.payload):selected[0].payload,enumerable:true});
  }
  assert.equal(used.size,records.length,'Unmapped table/record');
  return output;
}
