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
  ['backend/course-capsule-v1/adapters/c110-capability-v1/views/C110.html','docs/backend/c110/C110.html'],
  ['backend/course-capsule-v1/adapters/c110-capability-v1/views/C110-pengajar.html','docs/backend/c110/C110-pengajar.html'],
  ['backend/course-capsule-v1/adapters/c120-capability-v1/views/C120.html','docs/backend/c120/C120.html'],
  ['backend/course-capsule-v1/adapters/c120-capability-v1/views/C120-pengajar.html','docs/backend/c120/C120-pengajar.html'],
  ['backend/course-capsule-v1/adapters/c70-capability-v1/views/C70.html','docs/backend/c70/C70.html'],
  ['backend/course-capsule-v1/adapters/c70-capability-v1/views/C70-pengajar.html','docs/backend/c70/C70-pengajar.html'],
];

const rows=[];
for(const [source,target] of mappings){
  const payload=await readFile(resolve(root,source));
  const targetPath=resolve(root,target);
  await mkdir(dirname(targetPath),{recursive:true});
  await writeFile(targetPath,payload);
  const readback=await readFile(targetPath);
  assert.deepEqual(readback,payload,`${target}: staged view differs from adapter source.`);
  rows.push({source,target,bytes:payload.length,sha256:sha256(payload)});
}
assert.equal(rows.length,14);
console.log(JSON.stringify({status:'pass',mode:'raw-views-only',files:rows},null,2));
