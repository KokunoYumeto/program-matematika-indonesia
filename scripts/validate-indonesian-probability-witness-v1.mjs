// Read-only identity replay; contextual judgments remain explicitly recorded.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const packetPath='backend/course-capsule-v1/authority/terminology-policy-v1/witnesses/uad-probability-v1.json';
const args=process.argv.slice(2);
assert.equal(args.length,2,'Use --source-directory followed by the existing private source directory');
assert.equal(args[0],'--source-directory');
const sourceDirectory=resolve(args[1]);
const hash=data=>createHash('sha256').update(data).digest('hex');
const raw=await readFile(resolve(root,packetPath));
const packet=JSON.parse(raw);
const pdf=await readFile(resolve(sourceDirectory,packet.source.pdf_filename));
const extraction=await readFile(resolve(sourceDirectory,packet.source.extraction_filename));
const indices=new Map();
for(const item of packet.impact_inventory)indices.set(item.path,await readFile(resolve(root,item.path)));
function verify(record) {
  assert.equal(record.schema,'indonesian-contextual-terminology-witness/1');
  assert.equal(record.source.pdf_bytes,pdf.length);assert.equal(record.source.pdf_sha256,hash(pdf));
  assert.equal(record.source.extraction_bytes,extraction.length);assert.equal(record.source.extraction_sha256,hash(extraction));
  const pages=extraction.toString('utf8').split('\f');
  assert.equal(record.passages.length,3);assert.equal(new Set(record.passages.map(p=>p.id)).size,3);
  for(const p of record.passages){
    assert.ok(Number.isInteger(p.physical_page)&&p.physical_page>0&&p.physical_page<=pages.length);
    const text=pages[p.physical_page-1],bytes=Buffer.from(text,'utf8');
    assert.equal(p.page_text_bytes,bytes.length);assert.equal(p.page_text_sha256,hash(bytes));
    for(const form of p.attested_forms)assert.ok(text.includes(form),'Absent attested surface');
    assert.ok(p.context&&p.supports&&p.does_not_establish&&p.visual_comparison);
  }
  assert.equal(record.impact_inventory.length,2);
  for(const item of record.impact_inventory){
    const data=indices.get(item.path);assert.ok(data);assert.equal(hash(data),item.sha256);
    const rows=data.toString('utf8').trim().split(/\r?\n/).map(line=>JSON.parse(line));
    const selected=rows.filter(row=>row[item.id_field]===item.record_id);assert.equal(selected.length,1);
    assert.equal(selected[0][item.designation_field],item.current_designation);
  }
  for(const field of ['automatic_replacement_allowed','program_policy_resolved','full_occurrence_coverage'])
    assert.equal(record.decision[field],false,'Witness-only evidence cannot claim general resolution');
}
verify(packet);
const mutations=[
  r=>{r.passages[0].physical_page=13;},
  r=>{r.passages[0].page_text_sha256='0'.repeat(64);},
  r=>{r.passages[0].attested_forms=['unattested invented terminology'];},
  r=>{r.impact_inventory[0].current_designation='invented replacement';},
  r=>{r.decision.program_policy_resolved=true;},
  r=>{r.decision.full_occurrence_coverage=true;}
];
for(const mutate of mutations){const copy=structuredClone(packet);mutate(copy);assert.throws(()=>verify(copy));}
console.log(JSON.stringify({status:'pass',packet_sha256:hash(raw),source_pages:3,
  pinned_native_term_records:2,rejected_mutations:mutations.length,original_source_modified:false,
  production_translation_modified:false,automatic_resolution:false,
  scope:'source_and_page_identity_replay_plus_attested_forms_and_exact_native_term_records; not_independent_semantic_certification'}));
