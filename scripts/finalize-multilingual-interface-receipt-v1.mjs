import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile,writeFile} from 'node:fs/promises';
import {dirname,resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const receiptPath='docs/interface/build-receipt.json';
const overlayPath='backend/authority/central-course-surface-navigation-overlay-v1.json';
const sha256=bytes=>createHash('sha256').update(bytes).digest('hex');
const fact=(path,bytes)=>({path,bytes:bytes.length,sha256:sha256(bytes)});
const receipt=JSON.parse(await readFile(resolve(root,receiptPath),'utf8'));
const overlayBytes=await readFile(resolve(root,overlayPath));
const overlay=JSON.parse(overlayBytes);
assert.equal(receipt.schema,'multilingual-interface-build/v1');
assert.equal(overlay.status,'pass');
assert.equal(overlay.schema,'central-course-surface-navigation-overlay-v1');
assert.equal(receipt.outputs.length,receipt.locales.length*3+3,'Multilingual interface output closure changed.');
const generationOverlayInput=receipt.inputs.find(row=>row.path===overlayPath);
assert.ok(generationOverlayInput,'Generation overlay input is missing.');
receipt.generation_input_navigation_overlay=generationOverlayInput;
receipt.inputs=receipt.inputs.map(row=>row.path===overlayPath?fact(overlayPath,overlayBytes):row);
receipt.outputs=await Promise.all(receipt.outputs.map(async row=>{
  const bytes=await readFile(resolve(root,row.path));
  return fact(row.path,bytes);
}));
for(const path of [
  'docs/id/learning-map.html','docs/id/learning-map-paired.html',
  'docs/en/learning-map.html','docs/en/learning-map-paired.html',
]){
  const row=overlay.files.find(item=>item.document===path);
  assert.ok(row,`${path}: interface output is missing from navigation overlay.`);
  assert.deepEqual(receipt.outputs.find(item=>item.path===path),row.hosted_surface,`${path}: final receipt and overlay disagree.`);
}
receipt.final_presentation_navigation={
  status:'pass',
  overlay:fact(overlayPath,overlayBytes),
  finalizer:fact('scripts/finalize-multilingual-interface-receipt-v1.mjs',await readFile(fileURLToPath(import.meta.url))),
  output_identities_are_post_navigation:true,
};
const next=JSON.stringify(receipt,null,2)+'\n';
await writeFile(resolve(root,receiptPath),next);
console.log(JSON.stringify({status:'pass',receipt:fact(receiptPath,Buffer.from(next)),outputs:receipt.outputs},null,2));
