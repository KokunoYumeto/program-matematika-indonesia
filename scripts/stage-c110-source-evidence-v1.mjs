import assert from 'node:assert/strict';
import {readFile,writeFile} from 'node:fs/promises';
const root=new URL('../',import.meta.url);
const intake='outputs/c110-source-format-112044378/';
const release=JSON.parse(await readFile(new URL(intake+'NATIVE_RELEASE_READBACK.json',root)));
const equivalence=JSON.parse(await readFile(new URL(intake+'assembled/C110_SOURCE_EQUIVALENCE.json',root)));
assert.equal(release.status,'published_and_anonymously_verified');
assert.equal(release.public_readback.length,8);
assert.equal(equivalence.native_and_assembled_pdf_byte_identical,true);
const evidence={schema:'central-supplemental-reader-evidence/1',status:release.status,
  course_id:'C110',content_language:'id',edition:'3.0-id.2-r1',
  scope:{whole_released_book:true,pages:387,not_new_translation:true,not_new_mathematical_review:true},
  release:release.release,equivalence,public_readback:release.public_readback,
  model_for_this_assembly:equivalence.model_for_this_assembly,
  dependency_policy:'The complete cumulative text uses the figures, bibliography and styles in the original same-edition source ZIP. Not dependency-free.',
  preserved_original_assets:release.original_assets_preserved};
await writeFile(new URL('docs/interface/evidence/c110-cumulative-source.json',root),JSON.stringify(evidence,null,2)+'\n');
console.log('C110 exact public source evidence staged; no native corpus copied.');
