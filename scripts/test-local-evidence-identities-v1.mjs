import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdtemp, mkdir, writeFile, rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join, resolve, sep} from 'node:path';
import {validateLocalEvidenceIdentities} from './local-evidence-identities-v1.mjs';

const parent=resolve(tmpdir()),root=await mkdtemp(join(parent,'local-evidence-test-'));
assert.ok(root.startsWith(parent+sep));
try {
  await mkdir(join(root,'docs'));
  const body=Buffer.from('current evidence\n');
  await writeFile(join(root,'docs/fact.txt'),body);
  const fact={locator:'docs/fact.txt',bytes:body.length,sha256:createHash('sha256').update(body).digest('hex')};
  assert.deepEqual(await validateLocalEvidenceIdentities(root,{evidence:[fact],layers:{nested:{...fact,path:fact.locator}}}),{facts:2,unique_files:1});
  await assert.rejects(validateLocalEvidenceIdentities(root,{...fact,sha256:'0'.repeat(64)}),/Local evidence identity drift/);
  await assert.rejects(validateLocalEvidenceIdentities(root,{...fact,bytes:body.length+1}),/Local evidence identity drift/);
  await assert.rejects(validateLocalEvidenceIdentities(root,{...fact,locator:'docs/../fact.txt'}),/Unsafe local evidence path/);
  await assert.rejects(validateLocalEvidenceIdentities(root,{...fact,locator:'docs/missing.txt'}),/ENOENT/);
  await writeFile(join(root,'docs/fact.txt'),'changed evidence\n');
  await assert.rejects(validateLocalEvidenceIdentities(root,fact),/Local evidence identity drift/);
  assert.deepEqual(await validateLocalEvidenceIdentities(root,{...fact,locator:'https://example.org/fact.txt'}),{facts:0,unique_files:0});
  console.log(JSON.stringify({state:'pass',negative_cases:5,nested_path_and_locator_checked:true,remote_revalidation_claimed:false}));
} finally {
  assert.ok(root.startsWith(parent+sep));
  await rm(root,{recursive:true,force:true});
}
