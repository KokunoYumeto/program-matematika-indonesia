import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {createHash} from 'node:crypto';
import {collectDownloads,downloadFormat,renderDownloadPage} from './build-course-downloads-v1.mjs';
const base=new URL('../',import.meta.url);
const input=await readFile(new URL('docs/interface/learner-access-manifest.json',base));
const manifest=JSON.parse(input),model=collectDownloads(manifest);
assert.equal(model.courses.length,40);assert.equal(model.new_format_exports,false);
assert.deepEqual(model,collectDownloads(structuredClone(manifest)));
// D10's "PDF index" is a publisher HTML page, not a directly downloadable PDF.
assert.equal(model.counts.id.roles_by_format.pdf,38);assert.equal(model.counts.en.roles_by_format.pdf,15);
assert.equal(model.counts.id.roles_by_format.epub,3);assert.equal(model.counts.en.roles_by_format.epub,0);
assert.equal(model.counts.en.roles_by_format.tex,1);
assert.equal(model.counts.id.roles_by_format.tex,1);
const c110=model.courses.find(row=>row.course_id==='C110');
const c110id=c110.locales.id.downloads.map(d=>model.resources.find(r=>r.id===d.resource_id));
assert.deepEqual([...new Set(c110id.map(r=>r.format))],['pdf','tex','zip']);
assert.ok(c110id.find(r=>r.format==='tex').url.includes('/tea-time-numerical-analysis-id/releases/download/v3.0-id.2-r1/'));
assert.ok(!c110.locales.en.downloads.some(d=>model.resources.find(r=>r.id===d.resource_id).content_language==='id'));
const b40Source=model.courses.find(row=>row.course_id==='B40').locales.en.downloads.filter(binding=>model.resources.find(r=>r.id===binding.resource_id).format==='tex');
assert.equal(b40Source.length,1);assert.match(b40Source[0].label,/34 English sections/);
const resources=new Map(model.resources.map(r=>[r.id,r]));
assert.equal(resources.size,model.resources.length);
for(const course of model.courses)for(const locale of ['id','en']){
  const row=course.locales[locale];assert.equal(new Set(row.downloads.map(r=>r.resource_id)).size,row.downloads.length);
  for(const binding of row.downloads){const resource=resources.get(binding.resource_id);assert.ok(resource);assert.equal(resource.content_language,locale);}
}
for(const locale of ['id','en']){
  const page=await readFile(new URL(`docs/${locale}/downloads/index.html`,base),'utf8');
  const generated=renderDownloadPage(model,locale);
  if(page!==generated){
    const overlay=JSON.parse(await readFile(new URL('backend/authority/central-course-surface-navigation-overlay-v1.json',base)));
    const path=`docs/${locale}/downloads/index.html`,record=overlay.files.find(r=>r.document===path);
    const identity=text=>({path,bytes:Buffer.byteLength(text),sha256:createHash('sha256').update(text).digest('hex')});
    assert.ok(record,'Unregistered download-page transformation');assert.equal(record.source_body_replay_exact,true);
    assert.deepEqual(record.source_body,identity(generated));assert.deepEqual(record.hosted_surface,identity(page));
  }
  assert.equal((page.match(/data-course="/g)||[]).length,40);
  assert.match(page,new RegExp(`<html lang="${locale}">`));
  assert.doesNotMatch(page,/C:\\Users|Authorization:|access_token/i);
}
const saved=JSON.parse(await readFile(new URL('docs/interface/course-downloads-v1.json',base)));
const {source,...rest}=saved;assert.deepEqual(rest,model);
assert.deepEqual(source,{path:'interface/learner-access-manifest.json',bytes:input.length,sha256:createHash('sha256').update(input).digest('hex')});
const refused=[];
for(const [name,mutate] of [
  ['missing_course',m=>delete m.courses.A00],
  ['wrong_locale',m=>m.courses.A00.en.interface_locale='id'],
  ['wrong_course_route',m=>m.courses.A00.en.locale_route+='-wrong'],
  ['unsafe_url',m=>m.courses.A00.id.program_hosted_reader.resources[0].url='javascript:alert(1)'],
  ['credential_url',m=>m.courses.A00.id.program_hosted_reader.resources[0].url='https://user:secret@example.org/book.pdf'],
  ['conflicting_identity',m=>{const r={...m.courses.A00.id.program_hosted_reader.resources[1],bytes:1,sha256:'a'.repeat(64)};m.courses.A00.id.program_hosted_reader.resources[1]=r;m.courses.A00.id.alternatives.push({...r,bytes:2});}],
  ['invalid_file_identity',m=>m.courses.A00.id.program_hosted_reader.resources[1].sha256='not-a-hash'],
]){const m=structuredClone(manifest);mutate(m);assert.throws(()=>collectDownloads(m),undefined,name);refused.push(name);}
assert.equal(downloadFormat({url:'https://example.org/My%20Book.PDF?download=1'}),'pdf');
assert.equal(downloadFormat({url:'https://example.org/course',media_type:'HTML'}),null);
assert.equal(downloadFormat({url:'https://example.org/index.htm',media_type:'PDF index'}),null);
assert.equal(downloadFormat({url:'https://example.org/book.pdf.zip'}),'zip');
const polluted=structuredClone(model);polluted.courses[0].locales.en.title='<script>alert(1)</script>';
assert.ok(renderDownloadPage(polluted,'en').includes('&lt;script&gt;alert(1)&lt;/script&gt;'));
assert.throws(()=>renderDownloadPage(model,'xx'));
console.log(JSON.stringify({state:'pass',courses:40,locales:2,unique_files:model.resources.length,counts:model.counts,refused,actual_formats_not_interface_language:true,duplicate_downloads_removed:true,missing_not_declared_absent:true}));
