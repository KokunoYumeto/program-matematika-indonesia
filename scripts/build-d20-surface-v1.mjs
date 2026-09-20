import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {dirname, resolve, basename} from 'node:path';
import {fileURLToPath} from 'node:url';

export const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
export const base = 'backend/course-capsule-v1/adapters/d20-surface-v1';
export const sha256 = b => createHash('sha256').update(b).digest('hex');
export const json = value => JSON.stringify(value, null, 2) + '\n';
const esc = value => String(value ?? '').replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('"','&quot;');

export async function loadInputs() {
  const bytes = await readFile(resolve(project, base, 'input/source-lock.json'));
  const lock = JSON.parse(bytes), tables = {}, raw = {};
  assert.equal(lock.schema, 'd20-consumer-input-lock/1');
  for (const fact of [...lock.inputs, lock.authority]) {
    assert.ok(fact.path.startsWith('backend/') && !fact.path.includes('..'));
    const b = await readFile(resolve(project, fact.path));
    assert.equal(b.length, fact.bytes, fact.path); assert.equal(sha256(b), fact.sha256, fact.path);
    if (fact.path.endsWith('.jsonl')) {
      const name = basename(fact.path, '.jsonl'); raw[name] = b.toString('utf8').trim().split('\n');
      tables[name] = raw[name].map(JSON.parse);
    }
  }
  return {lock, tables, raw, witness: JSON.parse(await readFile(resolve(project, base, 'input/reader-witness.json'))),
    lockIdentity: {path: `${base}/input/source-lock.json`, bytes: bytes.length, sha256: sha256(bytes)}};
}

export function projectMap({lock, tables: t, raw, witness, lockIdentity}) {
  assert.equal(lock.content_locale, 'id-ID'); assert.equal(witness.schema, 'd20-public-reader-witness/1');
  assert.equal(witness.origin, 'https://kokunoyumeto.github.io/functional-analysis-erdman-id/');
  const indexes = {};
  for (const [name, rows] of Object.entries(t)) {
    indexes[name] = new Map(rows.map(r => [r.id, r])); assert.equal(indexes[name].size, rows.length, `Duplicate ${name}`);
  }
  const pages = new Map(witness.pages.map(p => [p.path, p]));
  assert.equal(pages.size, witness.pages.length);
  const routes = new Map();
  for (const r of witness.routes) {
    assert.ok(pages.has(r.path));
    assert.ok(/^[\w/.-]+$/.test(r.path) && !r.path.includes('..'));
    assert.ok(/^[\w.:-]*$/.test(r.anchor));
    assert.equal(r.url, witness.origin + r.path + (r.anchor ? '#' + r.anchor : ''));
    const original = indexes[r.native_table].get(r.native_route_id); assert.ok(original);
    assert.equal(r.target_id, original.target_stable_id ?? original.id);
    const prefix = r.native_table === 'html_routes' ? 'output/html/' : 'output/html-companion/';
    assert.equal(r.path + (r.anchor ? '#' + r.anchor : ''), prefix + original.href);
    if (!routes.has(r.target_id)) routes.set(r.target_id, []);
    routes.get(r.target_id).push(r);
  }
  const routeFor = id => {
    const candidates = [...new Map((routes.get(id) ?? []).map(r => [r.url, r])).values()];
    assert.equal(candidates.length, 1, `Missing/ambiguous registered route: ${id}`);
    const r = candidates[0]; assert.equal(r.occurrences, 1, `Nonunique anchor: ${id}`);
    return {url: r.url, anchor: r.anchor, state: 'exact_unique_anchor', number: r.number,
      page: pages.get(r.path), native_route_id: r.native_route_id, native_route_table: r.native_table};
  };
  const core = t.units.filter(r => r.record_type === 'unit');
  const parents = new Map(t.semantic_units.map(r => [r.id, r.parent_id]));
  const coreIds = new Set(core.map(r => r.id));
  const rootOf = id => {
    const seen = new Set(); let node = id;
    while (!coreIds.has(node)) {assert.ok(!seen.has(node), 'Parent cycle'); seen.add(node); node = parents.get(node); assert.ok(node, `Unknown parent: ${id}`);}
    return node;
  };
  const conceptsByChapter = new Map();
  for (const r of t.concept_relations) {
    if (r.relation_type === 'prerequisite') {assert.ok(indexes.concepts.has(r.from_id) && indexes.concepts.has(r.to_id)); continue;}
    if (r.relation_type === 'prerequisite_course') {assert.equal(r.resolution,'external_curriculum_record'); continue;}
    assert.equal(r.relation_type, 'covers'); assert.ok(coreIds.has(r.from_id)); assert.ok(indexes.concepts.has(r.to_id));
    if (!conceptsByChapter.has(r.from_id)) conceptsByChapter.set(r.from_id, []);
    conceptsByChapter.get(r.from_id).push(r.to_id);
  }
  const units = [], add = (record, kind, group, parent, order) => {
    const route = routeFor(record.id), title = record.target_title ?? record.target_title_tex ?? record.title_tex ?? record.title ?? null;
    assert.ok(!record.locale || record.locale === 'id-ID');
    assert.ok(indexes.rights.has(record.rights_id));
    units.push({id: record.id, kind, group, parent_id: parent, order, title, title_en: record.source_title ?? record.source_title_tex ?? null,
      title_format: 'source_metadata_TeX_preserved', number: route.number, locale: 'id-ID',
      chapter_concept_ids: conceptsByChapter.get(group) ?? [], practice: kind === 'exer', route,
      rights_ids: [record.rights_id], source_record: record, support: [], support_state: 'not_recorded'});
  };
  for (const r of core) add(r, r.id.endsWith('PREFACE') ? 'preface' : 'chapter', r.id, null, r.order ?? r.source_order);
  for (const r of t.semantic_units) add(r, r.unit_kind, rootOf(r.id), r.parent_id, r.order_in_chapter);
  for (const r of t.o001_mastery) {assert.equal(r.production_state, 'complete'); assert.equal(r.admission_state, 'admitted'); add(r, 'original_solution', r.chapter_id, r.exercise_unit_id ?? r.result_unit_id, r.source_exercise_order ?? r.selection_order_in_chapter);}
  for (const r of t.bridge_units) {assert.equal(r.production_state, 'complete'); assert.equal(r.admission_state, 'admitted'); add(r, 'bridge_' + r.unit_kind, r.component_id, r.component_id, r.order_in_component);}
  const byId = new Map(units.map(u => [u.id,u])); assert.equal(byId.size, units.length);
  const supportRelations = [];
  for (const r of [...t.relations, ...t.companion_relations]) if (['hints','proves','solves','completes_source_proof'].includes(r.relation_type)) {
    assert.ok(byId.has(r.from_id) && byId.has(r.to_id), `Unknown support endpoint: ${r.id}`);
    const relation = {id: r.id, type: r.relation_type, from: r.from_id, to: r.to_id};
    byId.get(r.to_id).support.push(relation); supportRelations.push(relation);
    if (r.relation_type === 'completes_source_proof') byId.get(r.to_id).practice = true;
  }
  const overlayIds = new Set();
  for (const overlay of t.o001_status) {
    assert.ok(!overlayIds.has(overlay.base_support_id), 'Duplicate status overlay'); overlayIds.add(overlay.base_support_id);
    const index = t.exercise_support.findIndex(r => r.id === overlay.base_support_id); assert.ok(index >= 0);
    assert.equal(sha256(raw.exercise_support[index]), overlay.base_support_line_sha256, 'Stale base support');
    const original = t.exercise_support[index], solution = indexes.o001_mastery.get(overlay.solution_id);
    assert.ok(solution); assert.equal(solution.exercise_unit_id, original.exercise_unit_id);
    assert.equal(overlay.exercise_unit_id, original.exercise_unit_id);
    assert.equal(overlay.solution_id, original.original_solution_id);
    assert.equal(overlay.admission_state, 'admitted'); assert.equal(overlay.validation_state, 'integrated_pdf_html_passed');
    assert.equal(overlay.effective_original_solution_state, 'admitted_in_companion_readers');
    const u = byId.get(original.exercise_unit_id); assert.ok(u);
    assert.ok(u.support.some(r => r.from === solution.id && r.type === 'solves'));
    u.exercise_support = {base: original, overlay};
  }
  assert.equal(overlayIds.size, t.exercise_support.length, 'Missing exercise status overlay');
  for (const u of units) u.support_state = u.support.length ? 'exact_native_relations' : 'no_explicit_support_recorded';
  const coreOrder = new Map(core.map(r => [r.id,r.order ?? r.source_order]));
  units.sort((a,b) => (coreOrder.get(a.group) ?? 99) - (coreOrder.get(b.group) ?? 99) ||
    Number(a.kind !== 'chapter' && a.kind !== 'preface') - Number(b.kind !== 'chapter' && b.kind !== 'preface') || a.order-b.order || a.id.localeCompare(b.id,'en'));
  const prerequisites = t.companion_relations.filter(r => r.relation_type === 'requires_chapter');
  for (const r of prerequisites) {assert.ok(indexes.companion_components.has(r.from_id)); assert.ok(coreIds.has(r.to_id));}
  const counts = {units: units.length, chapters: core.filter(r => !r.id.endsWith('PREFACE')).length,
    semantic_units: t.semantic_units.length, exercises: t.exercise_support.length,
    original_solutions: t.o001_mastery.length, selected_reader_work: t.o001_mastery.filter(r => r.result_unit_id).length,
    bridge_units: t.bridge_units.length, support_relations: supportRelations.length, concepts: t.concepts.length,
    chapter_concept_links: t.concept_relations.filter(r=>r.relation_type==='covers').length,
    concept_prerequisites: t.concept_relations.filter(r=>r.relation_type==='prerequisite').length, bridge_prerequisites: prerequisites.length,
    practice_units: units.filter(u => u.practice).length, exact_routes: units.length};
  return {schema: 'native-study-map/1', course_id: 'D20', title: 'Analisis Fungsional', title_en: 'Functional Analysis', locale: 'id-ID',
    identity_namespace: 'functional-analysis-erdman-id/native', counts, units, support_relations: supportRelations,
    components: t.companion_components, concepts: t.concepts,
    chapter_concept_links: t.concept_relations.filter(r=>r.relation_type==='covers'),
    concept_prerequisites: t.concept_relations.filter(r=>r.relation_type==='prerequisite'),
    unresolved_external_course_relations: t.concept_relations.filter(r=>r.relation_type==='prerequisite_course'), component_prerequisites: prerequisites,
    historical_scope_records: t.units.filter(r => r.record_type !== 'unit'), rights: t.rights,
    source_witness: lockIdentity, inputs: lock.inputs, readers: witness.pages,
    limitations: ['Interface language is selectable; the linked readers are Indonesian, not a new English translation.',
      'Chapter concept coverage is native chapter-level metadata, not an assertion that every exercise teaches every listed concept.',
      'The native concept graph covers Chapter 1 only. Other chapters are not claimed concept-complete; the historical external COURSE-O007 reference is retained without guessing its current course binding.',
      'Completed companion status is a hash-bound overlay; historical queued states remain preserved, not silently overwritten.',
      'No recorded support relation means unknown support coverage. Source hints and separately authored solutions remain distinct.',
      'Plans preserve native IDs, source metadata, component rights and exact reader witnesses. They contain no complete textbook bodies.',
      'Teacher alignment here is unit and support selection, not a new syllabus, grading system, or full-course completion claim.',
      'This reproduces the shared tools, not the full native LaTeX build. No progress is transmitted or stored.']};
}

function render(map, lang, teacher) {
  const en = lang === 'en', t = (id,eng) => esc(en ? eng : id), suffix = en ? '.en' : '', page = teacher ? 'D20-pengajar' : 'D20';
  const title = t(teacher ? 'Analisis Fungsional · Rencana pengajaran' : 'Analisis Fungsional · Panduan belajar', teacher ? 'Functional Analysis · Teaching plan' : 'Functional Analysis · Study navigator');
  const chapters = map.units.filter(u => ['chapter','preface'].includes(u.kind));
  return `<!doctype html><html lang="${lang}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta http-equiv="Content-Security-Policy" content="default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'none'; object-src 'none'; base-uri 'none'"><title>D20 · ${title}</title><link rel="stylesheet" href="study-plan.css"><script defer src="data.js"></script><script defer src="study-plan.js"></script></head><body data-interface="${lang}" data-mode="${teacher?'teacher':'learner'}"><a class="skip" href="#main">${t('Langsung ke isi','Skip to content')}</a><nav aria-label="${t('Navigasi','Navigation')}"><a href="../../${lang}/#course-D20">${t('Program matematika','Mathematics program')}</a><a href="${teacher?'D20':'D20-pengajar'}${suffix}.html">${t(teacher?'Panduan belajar':'Panduan pengajar',teacher?'Study navigator':'Teaching plan')}</a><span class="language"><a href="${page}.html" lang="id">Bahasa Indonesia</a> / <a href="${page}.en.html" lang="en">English</a></span></nav><main id="main"><header><p class="eyebrow">D20 · ${t('Belajar dan mengajar','Study and teach')}</p><h1>${title}</h1><p>${t('Pilih unit bacaan dan latihan, buka bahan pendukung sesuai kebutuhan, lalu simpan rencana belajar atau mengajar.','Choose reading units and exercises, open support when needed, and save a study or teaching plan.')}</p><p class="notice">${t('Antarmuka tersedia dalam dua bahasa. Bacaan yang ditautkan berbahasa Indonesia. Ini bukan edisi bahasa Inggris baru.','The interface has two languages. Linked readings are Indonesian. This is not a new English edition.')}</p><div class="facts"><span>17 ${t('bab','chapters')}</span><span>52 ${t('latihan dengan solusi pendamping','exercises with companion solutions')}</span><span>10 ${t('hasil kerja-pembaca terpilih','selected reader-work results')}</span><span>13 ${t('unit jembatan','bridge units')}</span></div></header><section><h2>${t('Mulai membaca','Start reading')}</h2><details><summary>${t('Prakata dan 17 bab','Preface and 17 chapters')}</summary><ol>${chapters.map(u=>`<li><a href="${esc(u.route.url)}" lang="id">${esc(u.title)}</a></li>`).join('')}</ol></details><p><a href="https://kokunoyumeto.github.io/functional-analysis-erdman-id/output/html-companion/">${t('Solusi dan jembatan spektral-kompak','Solutions and compact-spectral bridge')}</a></p><p>${t('Prasyarat jembatan berdasarkan backend sumber','Bridge prerequisites recorded by the native backend')}: ${map.component_prerequisites.map(r=>{const u=map.units.find(u=>u.id===r.to_id);return `<a href="${esc(u.route.url)}">${esc(u.title)}</a>`;}).join(' · ')}</p></section><section id="workbench" hidden><h2>${t('Pilih bahan untuk rencana Anda','Choose material for your plan')}</h2><div class="filters"><label>${t('Cari judul atau ID','Search title or ID')}<input id="search" type="search"></label><label>${t('Jenis','Kind')}<select id="kind"><option value="">${t('Semua jenis','All kinds')}</option><option value="practice">${t('Latihan dan hasil terpilih','Exercises and selected results')}</option></select></label><label>${t('Kelompok bacaan','Reading group')}<select id="group"><option value="">${t('Semua kelompok','All groups')}</option></select></label><label>${t('Konsep tingkat bab','Chapter-level concept')}<select id="concept"><option value="">${t('Semua konsep','All concepts')}</option></select></label></div><p>${t('Filter konsep mengikuti kaitan tingkat bab; bukan pemetaan konsep untuk setiap latihan.','The concept filter uses chapter-level links, not exercise-level concept claims.')}</p><div class="toolbar"><button id="select-page">${t('Pilih halaman ini','Select this page')}</button><button id="clear">${t('Kosongkan pilihan','Clear selection')}</button><button id="export">${t('Unduh rencana JSON','Download plan JSON')}</button><button id="export-text">${t('Unduh rencana teks','Download text plan')}</button><span id="selection" role="status"></span></div><p id="results-status" role="status"></p><div id="unit-list"></div><div class="toolbar"><button id="previous">${t('Sebelumnya','Previous')}</button><button id="next">${t('Berikutnya','Next')}</button></div></section><noscript><p>${t('Daftar bacaan berfungsi tanpa JavaScript. Pencarian dan ekspor pilihan memerlukan JavaScript.','The reading lists work without JavaScript. Search and selection export need JavaScript.')}</p></noscript><section><h2>${t('Sumber dan batas cakupan','Sources and scope')}</h2><p>${t('52 solusi pendamping telah diterima. Catatan lama “queued” dipertahankan sebagai riwayat dan ditautkan ke overlay status yang sesuai. Solusi pendamping bukan karya Erdman.','The 52 companion solutions are admitted. Older “queued” records remain historical and are joined to their exact status overlays. Companion solutions are not authored by Erdman.')}</p><p>${t('Pilihan tetap berada di perangkat Anda. Rencana berisi metadata dan tautan, bukan buku lengkap untuk dibaca luring.','Selections stay on your device. Plans contain metadata and links, not a full offline book.')}</p><p><a href="learning-map.json">${t('Data yang dapat digunakan ulang','Reusable data')}</a> · <a href="validation.json">${t('Bukti pemeriksaan','Validation evidence')}</a> · <a href="https://github.com/KokunoYumeto/functional-analysis-erdman-id">${t('Sumber buku yang dapat diedit','Editable book source')}</a></p></section></main></body></html>\n`;
}

export async function build(out=resolve(project,'docs/backend/d20')) {
  const inputs=await loadInputs(), map=projectMap(inputs);
  const outputs={'learning-map.json':json(map),'data.js':'globalThis.COURSE_PLAN_DATA = '+JSON.stringify(map)+';\n'};
  for (const lang of ['id','en']) for (const teacher of [false,true]) outputs[(teacher?'D20-pengajar':'D20')+(lang==='en'?'.en':'')+'.html']=render(map,lang,teacher);
  outputs['study-plan.js']=await readFile(resolve(project,'scripts/study-plan-ui-v1.js'),'utf8');
  outputs['study-plan.css']=(await readFile(resolve(project,'scripts/d60-surface/d60.css'),'utf8'))+'\npre.metadata{white-space:pre-wrap}\n';
  const validation={schema:'d20-surface-validation/1',course_id:'D20',state:'pass',counts:map.counts,
    verification_scope:'Exact metadata, native support/status joins, and witnessed reading destinations; independent behavior and browser checks are separate.',
    inputs:[inputs.lockIdentity],body_content_copied:false,native_files_modified:false,
    outputs:Object.entries(outputs).map(([path,text])=>({path,bytes:Buffer.byteLength(text),sha256:sha256(text)})),limitations:map.limitations};
  outputs['validation.json']=json(validation); await mkdir(out,{recursive:true});
  for (const [name,text] of Object.entries(outputs)) await writeFile(resolve(out,name),text);
  return {map,validation};
}
if (process.argv[1] && resolve(process.argv[1])===fileURLToPath(import.meta.url)) console.log(json({state:'built',counts:(await build()).map.counts}));
