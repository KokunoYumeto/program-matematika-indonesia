import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { execFileSync } from 'node:child_process';
import { mkdir, readFile, writeFile } from 'node:fs/promises';
import { basename, dirname, resolve } from 'node:path';
import { homedir } from 'node:os';
import { fileURLToPath } from 'node:url';

// One bounded, read-only native intake. Subsequent builds use only frozen inputs.
const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const native = resolve(project, '../mathematical-computing-reproducible-experiments-id');
const target = resolve(project, 'backend/course-capsule-v1/adapters/b80-capability-v1/input');
const base = 'https://kokunoyumeto.github.io/mathematical-computing-reproducible-experiments-id/';
const repository = 'https://github.com/KokunoYumeto/mathematical-computing-reproducible-experiments-id';
const digest = bytes => createHash('sha256').update(bytes).digest('hex');
const fact = (path, bytes) => ({path, bytes:bytes.length, sha256:digest(bytes)});
const checkPublic = bytes => {
  const text = bytes.toString('utf8');
  const profile = basename(homedir()).replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  assert.ok(!new RegExp(`\\b${profile}\\b`, 'i').test(text), 'Private name in intake');
  assert.doesNotMatch(text, /[A-Za-z]:[\\/]+Users[\\/]|\bghp_[A-Za-z0-9]{20,}\b|\bgithub_pat_[A-Za-z0-9_]{20,}\b/);
};
async function get(url, limit=2000000) {
  const response = await fetch(url, {signal:AbortSignal.timeout(45000), headers:{'User-Agent':'course-capsule-evidence-intake'}});
  assert.equal(response.status, 200, `${url}: HTTP ${response.status}`);
  let size=0; const chunks=[];
  for await (const chunk of response.body) {
    size+=chunk.length; assert.ok(size<=limit, 'Unexpected response size'); chunks.push(chunk);
  }
  return Buffer.concat(chunks);
}
const catalogBytes = await readFile(resolve(native, 'backend/catalog.json'));
const schemaBytes = await readFile(resolve(native, 'backend/catalog.schema.json'));
checkPublic(catalogBytes); checkPublic(schemaBytes);
const catalog = JSON.parse(catalogBytes);
assert.equal(catalog.course.id, 'B80');
assert.equal(catalog.units.length, 14);
assert.equal(catalog.exercises.length, 75);
assert.deepEqual(await get(base+'backend/catalog.json'), catalogBytes, 'Public/native catalog divergence');
const commit = JSON.parse(await get('https://api.github.com/repos/KokunoYumeto/mathematical-computing-reproducible-experiments-id/commits/main')).sha;
assert.match(commit, /^[a-f0-9]{40}$/);
const pages=[];
for (const unit of catalog.units) {
  assert.match(unit.reader_path, /^source\/units\/[a-z0-9-]+\.qmd$/);
  const path=unit.reader_path.replace(/\.qmd$/, '.html');
  const bytes=await get(base+path);
  const parsed=JSON.parse(execFileSync('python', ['-B',resolve(project,'scripts/html-anchor-facts.py')],{input:bytes,maxBuffer:2000000}));
  const language=parsed.language;
  assert.ok(['id','id-ID'].includes(language), `${unit.id}: incorrect reader language`);
  const counts=parsed.anchor_counts;
  const expected=[...unit.sections, ...catalog.exercises.filter(row=>row.unit===unit.id).map(row=>row.id)];
  for (const id of expected) assert.equal(counts[id], 1, `${unit.id}: missing or ambiguous ${id}`);
  pages.push({...fact(path, bytes),unit_id:unit.id,url:base+path,language,anchor_counts:counts,
    mathml_elements:parsed.mathml_elements});
  console.log(JSON.stringify({unit:unit.id, public_anchors:expected.length, bytes:bytes.length}));
}
const receipt={schema:'b80-native-capability-intake/1',recorded_at:new Date().toISOString(),
  source:{repository,commit,catalog_url:base+'backend/catalog.json'},
  catalog:fact('catalog.json',catalogBytes),schema_file:fact('catalog.schema.json',schemaBytes),
  pages,credentials_used:false,reader_bodies_copied:false,
  scope:'Exact public catalog and reader anchors; this intake does not rerun native scientific experiments.'};
await mkdir(target,{recursive:true});
await writeFile(resolve(target,'catalog.json'),catalogBytes);
await writeFile(resolve(target,'catalog.schema.json'),schemaBytes);
await writeFile(resolve(target,'public-intake.json'),JSON.stringify(receipt,null,2)+'\n');
console.log(JSON.stringify({state:'pass',units:pages.length,catalog:receipt.catalog}));
