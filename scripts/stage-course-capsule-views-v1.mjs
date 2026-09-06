import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const sha256=bytes=>createHash('sha256').update(bytes).digest('hex');
const mappings=[
  ['backend/course-capsule-v1/adapters/d80-capability-v1/views/D80.html','docs/backend/d80/D80.html'],
  ['backend/course-capsule-v1/adapters/d80-capability-v1/views/D80-pengajar.html','docs/backend/d80/D80-pengajar.html'],
  ['backend/course-capsule-v1/adapters/d100-capability-v1/views/D100.html','docs/backend/d100/D100.html'],
  ['backend/course-capsule-v1/adapters/d100-capability-v1/views/D100-pengajar.html','docs/backend/d100/D100-pengajar.html'],
  ['backend/course-capsule-v1/adapters/d10-capability-v1/views/D10.html','docs/backend/d10/D10.html'],
  ['backend/course-capsule-v1/adapters/d10-capability-v1/views/D10-pengajar.html','docs/backend/d10/D10-pengajar.html'],
  ['backend/course-capsule-v1/adapters/d120-capability-v1/views/D120.html','docs/backend/d120/D120.html'],
  ['backend/course-capsule-v1/adapters/d120-capability-v1/views/D120-pengajar.html','docs/backend/d120/D120-pengajar.html'],
  ['backend/course-capsule-v1/adapters/d90-capability-v1/views/D90.html','docs/backend/d90/D90.html'],
  ['backend/course-capsule-v1/adapters/d90-capability-v1/views/D90-pengajar.html','docs/backend/d90/D90-pengajar.html'],
  ['backend/course-capsule-v1/adapters/d30-capability-v1/views/D30.html','docs/backend/d30/D30.html'],
  ['backend/course-capsule-v1/adapters/d30-capability-v1/views/D30-pengajar.html','docs/backend/d30/D30-pengajar.html'],
  ['backend/course-capsule-v1/adapters/c60-capability-v1/views/C60.html','docs/backend/c60/C60.html'],
  ['backend/course-capsule-v1/adapters/c60-capability-v1/views/C60-pengajar.html','docs/backend/c60/C60-pengajar.html'],
  ['backend/course-capsule-v1/adapters/c110-capability-v1/views/C110.html','docs/backend/c110/C110.html'],
  ['backend/course-capsule-v1/adapters/c110-capability-v1/views/C110-pengajar.html','docs/backend/c110/C110-pengajar.html'],
  ['backend/course-capsule-v1/adapters/c120-capability-v1/views/C120.html','docs/backend/c120/C120.html'],
  ['backend/course-capsule-v1/adapters/c120-capability-v1/views/C120-pengajar.html','docs/backend/c120/C120-pengajar.html'],
  ['backend/course-capsule-v1/adapters/c70-capability-v1/views/C70.html','docs/backend/c70/C70.html'],
  ['backend/course-capsule-v1/adapters/c70-capability-v1/views/C70-pengajar.html','docs/backend/c70/C70-pengajar.html'],
  ['backend/course-capsule-v1/adapters/b40-capability-v1/views/B40.html','docs/backend/b40/B40.html'],
  ['backend/course-capsule-v1/adapters/b40-capability-v1/views/B40-pengajar.html','docs/backend/b40/B40-pengajar.html'],
  ['backend/course-capsule-v1/adapters/a20-capability-v1/views/A20.html','docs/backend/a20/A20.html'],
  ['backend/course-capsule-v1/adapters/a20-capability-v1/views/A20-pengajar.html','docs/backend/a20/A20-pengajar.html'],
];

const rows=[];
for(const [source,target] of mappings){
  const sourcePayload=await readFile(resolve(root,source));
  let payload=sourcePayload;
  let projection='byte-identical';
  if(target==='docs/backend/d90/D90-pengajar.html'){
    const original=sourcePayload.toString('utf8');
    assert.equal(original.split('../data/').length-1,4,`${source}: expected four adapter-relative governance links.`);
    const projected=original
      .replace('../data/rights-index.jsonl','data/rights-index.jsonl')
      .replace('../data/corrections-index.jsonl','data/corrections-index.jsonl')
      .replace('../data/terms-index.jsonl','data/terms-index.jsonl')
      .replace('../data/claim-boundary.json','claim-boundary.json');
    assert.equal(projected.includes('../data/'),false,`${target}: adapter-relative governance link survived projection.`);
    payload=Buffer.from(projected,'utf8');
    projection='public-directory-link-depth';
  }
  if(target==='docs/backend/a20/A20-pengajar.html'){
    const original=sourcePayload.toString('utf8');
    assert.equal(original.split('../data/').length-1,7,`${source}: expected seven adapter-relative governance links.`);
    const projected=original.replaceAll('../data/','data/');
    assert.equal(projected.includes('../data/'),false,`${target}: adapter-relative governance link survived projection.`);
    payload=Buffer.from(projected,'utf8');
    projection='public-directory-link-depth';
  }
  const targetPath=resolve(root,target);
  await mkdir(dirname(targetPath),{recursive:true});
  await writeFile(targetPath,payload);
  const readback=await readFile(targetPath);
  assert.deepEqual(readback,payload,`${target}: staged view differs from adapter source.`);
  rows.push({source,target,projection,source_bytes:sourcePayload.length,source_sha256:sha256(sourcePayload),bytes:payload.length,sha256:sha256(payload)});
}
assert.equal(rows.length,24);
console.log(JSON.stringify({status:'pass',mode:'source-bound-public-projections',files:rows},null,2));
