// Read-only replay of two manually reviewed course occurrences and their witnesses.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile} from 'node:fs/promises';
import {dirname, resolve, relative, isAbsolute} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const args=process.argv.slice(2), roots=new Map();
assert.equal(args.length,6,'Use --b90-native PATH --b90-authority PATH --d30-native PATH');
for(let i=0;i<args.length;i+=2){assert.ok(['--b90-native','--b90-authority','--d30-native'].includes(args[i]));assert.ok(!roots.has(args[i].slice(2)));roots.set(args[i].slice(2),resolve(args[i+1]));}
const base='backend/course-capsule-v1/authority/terminology-policy-v1/witnesses/';
const packetBytes=await readFile(resolve(root,base+'course-conditional-probability-occurrences-v1.json'));
const packet=JSON.parse(packetBytes), hash=s=>createHash('sha256').update(s).digest('hex');
const lf=s=>s.replace(/\r\n/g,'\n'), rows=s=>s.trim().split('\n').map(JSON.parse);
const files=new Map(), witnesses=new Map();
for(const input of packet.inputs){const dir=roots.get(input.root);assert.ok(dir);const path=resolve(dir,input.path),rel=relative(dir,path);assert.ok(rel&&!rel.startsWith('..')&&!isAbsolute(rel));assert.ok(!files.has(input.id));files.set(input.id,lf(await readFile(path,'utf8')));}
for(const review of packet.reviews){assert.ok(/^(uad|ulm)-probability-v1\.json$/.test(review.canon.packet));witnesses.set(review.canon.packet,await readFile(resolve(root,base+review.canon.packet)));}
const single=(items,id)=>{const matches=items.filter(r=>r.id===id);assert.equal(matches.length,1,'Unique native segment required');return matches[0];};
const checkIdentity=(text,bytes,sha)=>{assert.equal(Buffer.byteLength(text),bytes);assert.equal(hash(text),sha);};
const displayMath=(s,re)=>[...s.matchAll(re)].map(m=>m[1]);
const plain=s=>s.replace(/<[^>]*>/g,'').replace(/\s+/g,' ').trim();
function verify(p){
  assert.equal(p.schema,'indonesian-course-terminology-occurrence-review/1');
  assert.equal(p.scope.reviewed_passage_pairs,2);assert.equal(p.scope.reviewed_term_occurrences,2);
  for(const key of ['full_occurrence_coverage','program_policy_resolved','all_nine_probability_concepts_resolved','production_translation_modified','national_preference_established','human_response_required'])assert.equal(p.scope[key],false);
  assert.equal(p.inputs.length,6);assert.equal(new Set(p.inputs.map(x=>x.id)).size,6);
  for(const input of p.inputs)checkIdentity(files.get(input.id),input.lf_bytes,input.lf_sha256);
  assert.deepEqual(p.reviews.map(r=>r.id),['B90-CONDITIONAL-DEFINITION-001','D30-CONDITIONAL-EVENT-001']);
  for(const r of p.reviews){
    const raw=witnesses.get(r.canon.packet);assert.equal(hash(raw),r.canon.sha256);
    const w=JSON.parse(raw),witness=w.passages.filter(x=>x.id===r.canon.passage_id);
    assert.equal(witness.length,1);assert.equal(witness[0].physical_page,r.canon.physical_page);
    assert.ok(witness[0].attested_forms.includes(r.retained_form));assert.equal(witness[0].concept_id,p.scope.concept_id);
    // UAD predates the typed evidence_class field; bind its exact definition.
    if(r.canon.packet==='uad-probability-v1.json')assert.equal(witness[0].id,'uad-29155-p14-def1.3');
    else assert.equal(witness[0].evidence_class,'same_sense_definition');
    assert.equal(r.decision,'retain_current_designation_for_this_occurrence');
    assert.ok(r.rationale&&r.context_read&&r.editorial_confidence.reason&&r.alternative.reason);
    const impact=w.impact_inventory.filter(x=>x.course_id===r.course_id&&x.record_id===r.term_id);
    assert.equal(impact.length,1);assert.equal(impact[0].current_designation,r.retained_form);
  }
  const b=p.reviews[0],native=rows(files.get('b90_records'));
  const en=single(native,b.source_segment_id),id=single(native,b.target_segment_id);
  assert.equal(en.parent_id,b.unit_id);assert.equal(id.parent_id,b.unit_id);assert.equal(id.provenance.source_segment_id,en.id);
  assert.equal(en.provenance.authority_archive_sha256,b.upstream_archive_sha256);
  const source=files.get('b90_source').split('\\exercises')[0],target=id.data.text;
  checkIdentity(source,en.data.bytes,en.content_sha256);checkIdentity(target,id.data.bytes,id.content_sha256);
  assert.equal(hash(source),b.source_segment_sha256);assert.equal(hash(target),b.target_segment_sha256);
  assert.equal(files.get('b90_target').split('\\exercises')[0],target,'Actual target file must bind to native segment');
  const snippets=[];
  for(const [text,span]of [[source,b.source_slice],[target,b.target_slice]]){assert.ok(Number.isInteger(span.start)&&Number.isInteger(span.end)&&span.start>=0&&span.end>span.start&&span.end<=text.length);const s=text.slice(span.start,span.end);checkIdentity(s,span.bytes,span.sha256);assert.equal(s.split(span.term_excerpt).length-1,1);assert.ok(text.slice(0,span.start).includes('$P(E) > 0$'),'Condition must precede definition');snippets.push(s);}
  assert.equal(b.source_slice.term_excerpt,'conditional probability');assert.equal(b.target_slice.term_excerpt,b.retained_form);
  const bm=snippets.map(s=>displayMath(s,/\$\$([\s\S]*?)\$\$/g));assert.equal(bm[0].length,1);assert.deepEqual(bm[0],bm[1]);assert.ok(bm[0][0].includes('P(F|E) = \\frac {P(F \\cap E)}{P(E)}'));
  const d=p.reviews[1],dr=single(rows(files.get('d30_segments')),d.aligned_segment_id);
  assert.equal(dr.parent_id,d.unit_id);assert.equal(dr.source_locator,d.source_locator);assert.equal(dr.source_target_relationship,'translates');
  const ds=dr.payload.source_text,dt=dr.payload.target_text;
  checkIdentity(ds,d.source_segment_bytes,d.source_segment_sha256);checkIdentity(dt,d.target_segment_bytes,d.target_segment_sha256);
  assert.equal(hash(ds),dr.source_sha256);assert.equal(hash(dt),dr.target_sha256);
  assert.ok(plain(files.get('d30_source')).includes(plain(ds)));assert.ok(plain(files.get('d30_target')).includes(plain(dt)));
  assert.equal(ds.split(d.source_term_excerpt).length-1,1);assert.equal(dt.split(d.target_term_excerpt).length-1,1);
  assert.equal(d.source_term_excerpt,'conditional probability');assert.equal(d.target_term_excerpt,d.retained_form);
  for(const s of [ds,dt])assert.ok(s.includes('\\P(A) \\gt 0'));
  const dm=[ds,dt].map(s=>displayMath(s,/\\\[([\s\S]*?)\\\]/g));assert.equal(dm[0].length,2);assert.deepEqual(dm[0],dm[1]);assert.ok(dm[0][0].includes('\\P(B \\mid A) = \\frac{\\P(A \\cap B)}{\\P(A)}'));
  assert.equal(p.findings.length,1);const f=p.findings[0];assert.equal(f.id,'D30-MATH-TEXT-ENGLISH-001');assert.equal(f.aligned_segment_id,d.aligned_segment_id);assert.equal(f.exact_text,'\\text{ for measurable }');assert.ok(dt.includes(f.exact_text));assert.equal(f.status,'confirmed_in_current_public_source_and_reader_not_corrected_by_this_review');assert.equal(f.public_observations.length,2);for(const o of f.public_observations){assert.equal(o.status,200);assert.ok(o.url.startsWith('https://'));assert.match(o.sha256,/^[0-9a-f]{64}$/);assert.ok(o.bytes>0);}
  return {native_segments:3,reviewed_passage_pairs:2,display_formulas_compared:3,untranslated_annotations:1};
}
const result=verify(packet);
const mutations=[p=>{p.scope.full_occurrence_coverage=true;},p=>{p.reviews[0].source_slice.start++;},p=>{p.reviews[0].target_slice.sha256='0'.repeat(64);},p=>{p.reviews[0].source_segment_id+='x';},p=>{p.reviews[0].canon.passage_id='ulm-23100-p38-rejected';},p=>{p.reviews[1].retained_form='peluang bersyarat';},p=>{p.reviews[1].unit_id+='x';},p=>{p.reviews[1].source_segment_sha256='0'.repeat(64);},p=>{p.findings[0].status='corrected';},p=>{p.findings[0].exact_text='invented';},p=>{p.inputs.push(p.inputs[0]);},p=>{p.scope.reviewed_term_occurrences=200;}];
for(const mutate of mutations){const changed=structuredClone(packet);mutate(changed);assert.throws(()=>verify(changed));}
console.log(JSON.stringify({status:'pass',packet_sha256:hash(packetBytes),...result,rejected_mutations:mutations.length,network_replayed:false,producer_files_modified:false,scope:'Exact source/target identity, native joins, retained designations, witness joins and formula replay; contextual editorial reasoning is recorded, not automatically certified.'}));
