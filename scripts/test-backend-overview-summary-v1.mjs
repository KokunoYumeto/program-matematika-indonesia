import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {coverageCounts, renderCoverageOverview} from './backend-overview-summary-v1.mjs';
const root = new URL('../', import.meta.url);
const model = JSON.parse(await readFile(new URL('backend/course-capsule-v1/generated/program-backend-coverage-v1.json', root)));
const template = await readFile(new URL('docs/backend/index.template.html', root), 'utf8');
const page = await readFile(new URL('docs/backend/index.html', root), 'utf8');
const counts = coverageCounts(model);
assert.equal(counts.roles, 40);
assert.equal(counts.locally_validated_adapter_roles, 40);
assert.equal(counts.native_capability_parity_verified_roles, 16);
const rendered = renderCoverageOverview(template, model);
assert.match(rendered, /40 dari 40 peran kurikulum mempunyai adapter/);
assert.match(rendered, /terverifikasi untuk 16 dari 40 peran/);
assert.doesNotMatch(rendered, /36 dari 40|Dua puluh sembilan dari 33|keadaan publik saat ini memuat 13/);
assert.equal(renderCoverageOverview(rendered, model), rendered, 'Rendering must be idempotent');
assert.equal(renderCoverageOverview(page, model), page, 'Published page differs from current coverage');
let refused = 0;
for (const mutate of [
  m => { m.summary.locally_validated_adapter_roles = 39; },
  m => { m.summary.native_capability_parity_verified_roles = 40; },
  m => { m.roles.push(m.roles[0]); },
  m => { m.roles[0].common_adapter.status = 'unknown'; },
]) {
  const changed = structuredClone(model); mutate(changed);
  assert.throws(() => renderCoverageOverview(template, changed)); refused++;
}
for (const altered of [template.replace('CURRENT-BACKEND-COVERAGE:START', 'missing'), template + '<!-- CURRENT-BACKEND-COVERAGE:END -->']) {
  assert.throws(() => renderCoverageOverview(altered, model)); refused++;
}
const next = structuredClone(model);
const row = next.roles.find(r => r.native_capability_parity_completion !== 'verified');
row.native_capability_parity_completion = 'verified';
next.summary.native_capability_parity_verified_roles++;
assert.match(renderCoverageOverview(template, next), /terverifikasi untuk 17 dari 40 peran/);
console.log(JSON.stringify({state:'pass', mutation_refusals:refused, successor_count_updates:true, idempotent:true}));
