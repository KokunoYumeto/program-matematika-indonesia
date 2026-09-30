import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {loadD100IndonesianEvidence,d100TranslationKeys,d100TranslationVerification,validateD100TranslationClaims} from './d100-indonesian-evidence-v1.mjs';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const {evidence}=await loadD100IndonesianEvidence(root);
const path=resolve(root,'backend/course-capsule-v1/authority/integration-overrides-v1.json');
const overrides=JSON.parse(await readFile(path,'utf8'));
const before=structuredClone(overrides);
for(const key of d100TranslationKeys)overrides.native_capabilities.D100[key]={
  status:'verified',locale:'id-ID',verification_scope:d100TranslationVerification.scope,evidence,
};
validateD100TranslationClaims(overrides.native_capabilities.D100,evidence);
const preserved=structuredClone(overrides);
for(const key of d100TranslationKeys)preserved.native_capabilities.D100[key]=before.native_capabilities.D100[key];
assert.deepEqual(preserved,before,'D100 locale admission must not change any other authority');
await writeFile(path,JSON.stringify(overrides,null,2)+'\n');
console.log(JSON.stringify({state:'pass',course:'D100',target_locale:'id-ID',changed_capabilities:d100TranslationKeys,
  semantic_canon_review:'not_established',other_authorities_unchanged:true}));
