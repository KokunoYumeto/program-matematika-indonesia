import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {validateD80PrerequisiteRoute,renderD80PrerequisiteRoute} from './d80-prerequisite-route-v1.mjs';
const record=JSON.parse(await readFile(new URL('../backend/cross-programme-v1/d80-prerequisite-route-v1.json',import.meta.url)));
validateD80PrerequisiteRoute(record);
const evidenceBytes=await readFile(new URL('../'+record.reader_notice.evidence.path,import.meta.url));
assert.equal(evidenceBytes.length,record.reader_notice.evidence.bytes);
assert.equal(createHash('sha256').update(evidenceBytes).digest('hex'),record.reader_notice.evidence.sha256);
const evidence=JSON.parse(evidenceBytes);
assert.equal(evidence.state,'pass');assert.equal(evidence.anonymous,true);
assert.equal(evidence.producer_files_changed,false);assert.equal(evidence.producer_fix_complete,false);
assert.equal(evidence.pdf_physical_page,119);assert.equal(evidence.pdf_printed_page,109);
assert.equal(evidence.public_sources.html.sha256,record.provider.sha256);
assert.equal(evidence.public_sources.tex.sha256,record.readings[1].editable_source.sha256);
assert.equal(evidence.public_sources.pdf.sha256,record.reader_notice.pdf.sha256);
const bad=[
  r=>{r.independent_mathematical_admission=true;},
  r=>{r.whole_prerequisite_closure=true;},
  r=>{r.distinct_course_relationships=32;},
  r=>{r.consumer.course_complete=true;},
  r=>{r.provider.content_language='id';},
  r=>{r.consumer.content_language='id';},
  r=>{r.readings[0].url='javascript:alert(1)';},
  r=>{r.readings[1].anchor='missing';},
  r=>{r.readings.pop();},
  r=>{r.readings[1]=structuredClone(r.readings[0]);},
  r=>{r.provider.sha256='0'.repeat(64);},
  r=>{r.consumer.editable_source.sha256='0'.repeat(64);},
  r=>{r.readings[2].editable_source.bytes++;},
  r=>{r.verification.public_section_anchors=false;},
  r=>{r.provider.rights='CC0';},
  r=>{r.consumer.rights='CC0';},
  r=>{r.use_loci.pop();},
  r=>{r.use_loci[0].provider_labels.pop();},
  r=>{r.use_loci[1].consumer_locus='Entire course';},
  r=>{delete r.use_loci[0].conditions.id;},
  r=>{delete r.verification.mathematical_review.id;},
  r=>{delete r.change_policy.en;},
  r=>{delete r.reader_notice;},
  r=>{r.reader_notice.producer_fix_complete=true;},
  r=>{r.reader_notice.pdf.url=r.reader_notice.pdf.url.replace('119','239');},
  r=>{r.reader_notice.pdf.sha256='0'.repeat(64);},
  r=>{delete r.reader_notice.text.id;},
  r=>{r.reader_notice.evidence.bytes++;},
];
for(const mutate of bad){const copy=structuredClone(record);mutate(copy);assert.throws(()=>validateD80PrerequisiteRoute(copy));}
for(const locale of ['id','en'])for(const side of ['provider','consumer']){
  const html=renderD80PrerequisiteRoute(record,locale,side);
  assert.equal((html.match(/hreflang="en"/g)||[]).length,6);
  assert.ok(html.includes('data-d80-reader-notice'));
  assert.ok(html.includes(record.reader_notice.text[locale].replaceAll('&','&amp;')));
  assert.ok(html.includes(record.reader_notice.pdf.url));
  assert.ok(html.includes('Wen-Wei Li'));assert.ok(html.includes('CC BY 4.0'));
  assert.ok(html.includes(record.scope[locale]));
  assert.ok(html.includes(record.use_loci[0].conditions[locale]));
  assert.ok(html.includes(record.use_loci[1].comparison[locale]));
  assert.ok(html.includes('data-d80-use-notes'));
}
const injection=structuredClone(record);injection.readings[0].title.en='<script>alert(1)</script>';
assert.ok(!renderD80PrerequisiteRoute(injection,'en','provider').includes('<script>'));
console.log(JSON.stringify({state:'pass',negative_cases:bad.length,localized_render_cases:4,html_injection_rejected:true}));
