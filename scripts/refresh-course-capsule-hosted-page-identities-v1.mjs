import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile, writeFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {sealB10} from './seal-b10-selection-public-v1.mjs';

const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
const overridePath='backend/course-capsule-v1/authority/integration-overrides-v1.json';
const overlayPath='backend/authority/central-course-surface-navigation-overlay-v1.json';
const receiptPath='backend/authority/course-capsule-hosted-page-identities-v1.json';
const programPagesPrefix='https://kokunoyumeto.github.io/program-matematika-indonesia/';
const sha256=bytes=>createHash('sha256').update(bytes).digest('hex');
const fact=(path,bytes)=>({path,bytes:bytes.length,sha256:sha256(bytes)});

const overrideBytes=await readFile(resolve(root,overridePath));
const overlayBytes=await readFile(resolve(root,overlayPath));
const overrides=JSON.parse(overrideBytes);
const overlay=JSON.parse(overlayBytes);
assert.equal(overlay.schema,'central-course-surface-navigation-overlay-v1');
assert.equal(overlay.status,'pass');
const overlayByPath=new Map(overlay.files.map(row=>[row.document,row]));

const changes=[];
const pagePaths=new Set();
const educatorPagePaths=new Set();
let toolCount=0;
let educatorFactCount=0;
for(const [courseId,tools] of Object.entries(overrides.learner_tools??{}).sort(([a],[b])=>a.localeCompare(b))){
  assert.ok(Array.isArray(tools)&&tools.length,`${courseId}: empty integration learner-tool set.`);
  for(const tool of tools){
    toolCount+=1;
    assert.equal(tool.page?.path,`docs/${tool.href}`,`${courseId}/${tool.tool_id}: page path differs from href.`);
    const row=overlayByPath.get(tool.page.path);
    assert.ok(row,`${courseId}/${tool.tool_id}: learner page is outside the final navigation overlay.`);
    assert.ok(row.course_ids.includes(courseId),`${courseId}/${tool.tool_id}: navigation overlay lacks course binding.`);
    const payload=await readFile(resolve(root,tool.page.path));
    const hosted=fact(tool.page.path,payload);
    assert.deepEqual(row.hosted_surface,hosted,`${courseId}/${tool.tool_id}: final hosted page differs from overlay receipt.`);
    assert.equal(row.source_body_replay_exact,true,`${courseId}/${tool.tool_id}: overlay is not reversible.`);
    changes.push({kind:'learner_tool_page',course_id:courseId,tool_id:tool.tool_id,before:tool.page,after:hosted});
    tool.page=hosted;
    pagePaths.add(hosted.path);
  }
}
// B95 and C140 are intentionally sourced from the dedicated learner-tool
// authority, so they must not also appear in integration-overrides.
// A10 adds one learner navigator and two educator views to the prior closure.
// C80 contributes one new planner page and one learner-tool binding.
assert.equal(toolCount,50,'Integration learner-tool closure changed.');
assert.equal(pagePaths.size,47,'Integration hosted-page closure changed.');
assert.ok(overrides.learner_tools.D20.some(tool=>tool.tool_id==='d20.native_ledger'
  && tool.page.path==='docs/backend/d20/native-ledger/ledger.html'),'D20 native ledger binding is missing.');
assert.ok(overrides.learner_tools.D80.some(tool=>tool.tool_id==='d80.native_ledger'
  && tool.page.path==='docs/backend/d80/native-ledger/ledger.html'),'D80 native ledger binding is missing.');
assert.ok(overrides.learner_tools.D60.some(tool=>tool.tool_id==='d60.native_ledger'
  && tool.page.path==='docs/backend/d60/native-ledger/ledger.html'),'D60 native ledger binding is missing.');
assert.ok(overrides.learner_tools.C130.some(tool=>tool.tool_id==='c130.native_ledger'
  && tool.page.path==='docs/backend/c130-native/ledger.html'),'C130 native ledger binding is missing.');
assert.ok(overrides.learner_tools.C130.some(tool=>tool.tool_id==='c130.assignment_planner'
  && tool.page.path==='docs/backend/c130-teacher/C130.teacher.html'),'C130 planner binding is missing.');
assert.ok(overrides.learner_tools.C80.some(tool=>tool.tool_id==='c80.openlogic_assignment_planner'
  && tool.page.path==='docs/backend/openlogic-teacher/C80.teacher.html'),'C80 planner binding is missing.');
for(const role of ['C30','C40'])assert.ok(pagePaths.has(`docs/backend/judson/${role}.teacher.html`));
for(const role of ['B20','B30','B50','B60'])assert.ok(pagePaths.has(`docs/backend/clp/${role}.teacher.html`));
assert.ok(pagePaths.has('docs/backend/d50/index.html'),'D50 hosted selector is missing.');
assert.ok(pagePaths.has('docs/backend/d110/index.html'),'D110 hosted selector is missing.');
assert.ok(overrides.learner_tools.A10.some(tool=>tool.tool_id==='a10.open_learner_hub'
  && tool.page.path==='docs/backend/a10/A10.html'),'A10 navigator binding is missing.');

const hostedPathForUrl=url=>{
  if(typeof url!=='string'||!url.startsWith(programPagesPrefix))return null;
  const parsed=new URL(url);
  let relative=parsed.pathname.slice('/program-matematika-indonesia/'.length);
  if(relative.endsWith('/'))relative+='index.html';
  return `docs/${decodeURIComponent(relative)}`;
};
const refreshEducatorFact=async(courseId,kind,owner,url)=>{
  const path=hostedPathForUrl(url);
  const row=path?overlayByPath.get(path):null;
  if(!row)return;
  assert.ok(row.course_ids.includes(courseId),`${courseId}/${kind}: navigation overlay lacks course binding.`);
  assert.equal(row.source_body_replay_exact,true,`${courseId}/${kind}: overlay is not reversible.`);
  const payload=await readFile(resolve(root,path));
  const hosted=fact(path,payload);
  assert.deepEqual(row.hosted_surface,hosted,`${courseId}/${kind}: final hosted educator page differs from overlay receipt.`);
  const before={bytes:owner.bytes,sha256:owner.sha256};
  owner.bytes=hosted.bytes;
  owner.sha256=hosted.sha256;
  changes.push({kind,course_id:courseId,path,before,after:{bytes:hosted.bytes,sha256:hosted.sha256}});
  educatorFactCount+=1;
  educatorPagePaths.add(path);
};
for(const [courseId,evidence] of Object.entries(overrides.educator_evidence??{}).sort(([a],[b])=>a.localeCompare(b))){
  await refreshEducatorFact(courseId,'educator_evidence',evidence,evidence.locator);
  for(const resource of evidence.resources??[]){
    await refreshEducatorFact(courseId,`educator_resource:${resource.id}`,resource,resource.url);
  }
}
// B95 and C140 each contribute educator evidence plus a hub resource over one
// central hosted page.
// C80 contributes primary educator evidence plus two localized resources.
// A00 exposes two localized native-ledger views without relabeling its book review.
// D70 adds two localized executable metadata-replay guides, without changing
// its full-native replay status or adding a duplicate learner destination.
assert.equal(educatorFactCount,109,'Integration educator hosted-fact closure changed.');
assert.equal(educatorPagePaths.size,69,'Integration educator hosted-page closure changed.');
for(const page of ['ledger.html','ledger-en.html'])assert.ok(educatorPagePaths.has(`docs/backend/d20/native-ledger/${page}`));
for(const page of ['ledger.html','ledger-en.html'])assert.ok(educatorPagePaths.has(`docs/backend/d80/native-ledger/${page}`));
for(const page of ['ledger.html','ledger-en.html'])assert.ok(educatorPagePaths.has(`docs/backend/d60/native-ledger/${page}`));
for(const suffix of ['', '.en'])assert.ok(educatorPagePaths.has(`docs/backend/d70-replay/index${suffix}.html`));
for(const suffix of ['', '.en'])assert.ok(educatorPagePaths.has(`docs/backend/c130-native/ledger${suffix}.html`));
for(const suffix of ['', '.en'])assert.ok(educatorPagePaths.has(`docs/backend/clp/B20.terms${suffix}.html`));
for(const page of ['ledger.html','ledger-en.html'])assert.ok(educatorPagePaths.has(`docs/backend/a00/${page}`));
for(const suffix of ['', '.en'])assert.ok(educatorPagePaths.has(`docs/backend/c130-teacher/C130.teacher${suffix}.html`));
for(const suffix of ['', '.en'])assert.ok(educatorPagePaths.has(`docs/backend/openlogic-teacher/C80.teacher${suffix}.html`));
for(const role of ['C30','C40'])for(const suffix of ['', '.en'])assert.ok(educatorPagePaths.has(`docs/backend/judson/${role}.teacher${suffix}.html`));
for(const role of ['B20','B30','B50','B60'])for(const suffix of ['', '.en'])assert.ok(educatorPagePaths.has(`docs/backend/clp/${role}.teacher${suffix}.html`));
for(const path of ['docs/backend/d50/teacher.html','docs/backend/d50/teacher.en.html'])assert.ok(educatorPagePaths.has(path));
for(const path of ['docs/backend/d110/teacher.html','docs/backend/d110/teacher.en.html'])assert.ok(educatorPagePaths.has(path));
for(const path of ['docs/backend/b10/B10-pengajar.html','docs/backend/b10/B10-pengajar-en.html'])assert.ok(educatorPagePaths.has(path));
for(const path of ['docs/backend/a00/A00-pengajar.html','docs/backend/a00/A00-pengajar-en.html'])
  assert.ok(educatorPagePaths.has(path),`${path}: A00 educator view is missing.`);
for(const path of ['docs/backend/a10/A10-pengajar.html','docs/backend/a10/A10-pengajar-en.html'])
  assert.ok(educatorPagePaths.has(path),`${path}: A10 educator view is missing.`);

const nextBytes=Buffer.from(JSON.stringify(overrides,null,2)+'\n');
await writeFile(resolve(root,overridePath),nextBytes);
const readback=await readFile(resolve(root,overridePath));
assert.deepEqual(readback,nextBytes,'Integration override write/readback changed bytes.');
const receipt={
  schema:'course-capsule-hosted-page-identities-v1',
  status:'pass',
  authority:{
    navigation_overlay:fact(overlayPath,overlayBytes),
    refresh_script:fact('scripts/refresh-course-capsule-hosted-page-identities-v1.mjs',await readFile(fileURLToPath(import.meta.url))),
  },
  scope:{
    tool_count:toolCount,
    unique_hosted_pages:pagePaths.size,
    educator_fact_count:educatorFactCount,
    unique_educator_hosted_pages:educatorPagePaths.size,
  },
  output:fact(overridePath,nextBytes),
  invariants:[
    'learner_tool_page_facts_and_centrally_hosted_educator_html_facts_are_refreshed',
    'non_html_resource_and_evidence_facts_remain_native_authority',
    'every_hosted_page_is_bound_by_the_reversible_navigation_overlay',
    'course_owner_binding_is_preserved',
  ],
  changes,
};
await writeFile(resolve(root,receiptPath),JSON.stringify(receipt,null,2)+'\n');
await sealB10();
console.log(JSON.stringify({status:'pass',output:receipt.output,scope:receipt.scope,receipt:fact(receiptPath,await readFile(resolve(root,receiptPath)))},null,2));
