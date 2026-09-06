import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile, writeFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

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
assert.equal(toolCount,32,'Integration learner-tool closure changed.');
assert.equal(pagePaths.size,29,'Integration hosted-page closure changed.');

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
assert.equal(educatorFactCount,44,'Integration educator hosted-fact closure changed.');
assert.equal(educatorPagePaths.size,22,'Integration educator hosted-page closure changed.');

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
console.log(JSON.stringify({status:'pass',output:receipt.output,scope:receipt.scope,receipt:fact(receiptPath,await readFile(resolve(root,receiptPath)))},null,2));
