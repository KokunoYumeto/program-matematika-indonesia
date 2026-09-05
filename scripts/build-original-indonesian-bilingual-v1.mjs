import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdir, readFile, writeFile} from 'node:fs/promises';
import {dirname, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const base = 'backend/course-capsule-v1/localizations/original-indonesian-bilingual-v1';
const sha256 = bytes => createHash('sha256').update(bytes).digest('hex');
const json = value => `${JSON.stringify(value, null, 2)}\n`;
const esc = value => String(value ?? '').replace(/[&<>"']/g, character => ({
  '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;',
}[character]));
const link = (href, label) => `<a href="${esc(href)}">${esc(label)}</a>`;
const readJson = async path => JSON.parse(await readFile(resolve(root, path), 'utf8'));
const fact = async path => {
  const bytes = await readFile(resolve(root, path));
  return {path, bytes: bytes.length, sha256: sha256(bytes)};
};
const parseJsonl = text => text.trim().split(/\r?\n/).filter(Boolean).map(line => JSON.parse(line));
const orderedIds = rows => rows.map(row => row.id);
const pick = (row, keys) => Object.fromEntries(keys.map(key => [key, row[key]]));
const sortedRelations = (rows, types) => rows.filter(row => types.includes(row.type))
  .map(row => `${row.from}\u0000${row.type}\u0000${row.to}`).sort();

export function validateB80Identity(indonesian, english) {
  assert.equal(indonesian.course.id, 'B80');
  assert.equal(english.course.id, 'B80');
  assert.equal(indonesian.language, 'id-ID');
  assert.equal(english.language, 'en');
  assert.deepEqual(
    pick(english.course, ['id', 'prerequisite', 'project_id', 'selected_unit_count']),
    pick(indonesian.course, ['id', 'prerequisite', 'project_id', 'selected_unit_count']),
  );
  for (const table of ['units', 'exercises', 'labs', 'prerequisite_routes', 'components', 'artifacts', 'environments', 'sources']) {
    assert.deepEqual(orderedIds(english[table]), orderedIds(indonesian[table]), `B80 ${table} identity drift`);
  }
  for (let index = 0; index < english.units.length; index += 1) {
    assert.deepEqual(
      pick(english.units[index], ['id', 'components', 'exercises', 'reader_path', 'sections', 'curriculum_status']),
      pick(indonesian.units[index], ['id', 'components', 'exercises', 'reader_path', 'sections', 'curriculum_status']),
    );
  }
  for (let index = 0; index < english.exercises.length; index += 1) {
    assert.deepEqual(
      pick(english.exercises[index], ['id', 'unit', 'kind', 'sequence', 'curriculum_status', 'source_path']),
      pick(indonesian.exercises[index], ['id', 'unit', 'kind', 'sequence', 'curriculum_status', 'source_path']),
    );
    for (const kind of ['hint', 'check', 'solution']) {
      assert.deepEqual(
        pick(english.exercises[index][kind], ['source_anchor', 'status']),
        pick(indonesian.exercises[index][kind], ['source_anchor', 'status']),
      );
    }
  }
  for (let index = 0; index < english.labs.length; index += 1) assert.deepEqual(
    pick(english.labs[index], ['id', 'unit', 'environment', 'artifact_ids', 'exercise_ids', 'kind', 'source_paths', 'status']),
    pick(indonesian.labs[index], ['id', 'unit', 'environment', 'artifact_ids', 'exercise_ids', 'kind', 'source_paths', 'status']),
  );
  for (let index = 0; index < english.prerequisite_routes.length; index += 1) assert.deepEqual(
    pick(english.prerequisite_routes[index], ['id', 'unit', 'prerequisite', 'required_for_b80', 'sections', 'exercises', 'status', 'gate_id']),
    pick(indonesian.prerequisite_routes[index], ['id', 'unit', 'prerequisite', 'required_for_b80', 'sections', 'exercises', 'status', 'gate_id']),
  );
  const structuralRelations = ['precedes', 'uses_component', 'implements', 'uses_environment', 'requires_prerequisite'];
  assert.deepEqual(sortedRelations(english.relations, structuralRelations), sortedRelations(indonesian.relations, structuralRelations));
  return {
    units: english.units.length,
    exercises: english.exercises.length,
    labs: english.labs.length,
    prerequisite_routes: english.prerequisite_routes.length,
    components: english.components.length,
    artifacts: english.artifacts.length,
    environments: english.environments.length,
    sources: english.sources.length,
  };
}

function b80Projection(indonesian, english, sourceLock, publication) {
  const counts = validateB80Identity(indonesian, english);
  assert.deepEqual(counts, {
    units: 14, exercises: 75, labs: 4, prerequisite_routes: 4,
    components: 46, artifacts: 27, environments: 2, sources: 6,
  });
  const pages = new Map(sourceLock.courses.B80.public_pages.map(row => [row.unit_id, row]));
  assert.equal(pages.size, 14);
  const units = new Map(english.units.map(row => [row.id, row]));
  const exercises = new Map(english.exercises.map(row => [row.id, row]));
  const previous = english.relations.filter(row => row.type === 'precedes');
  const anchor = (unitId, id) => {
    const page = pages.get(unitId);
    assert.ok(page, `Missing B80 English page ${unitId}`);
    assert.equal(page.anchors[id], 1, `Missing B80 English anchor ${unitId}#${id}`);
    return `${page.url}#${encodeURIComponent(id)}`;
  };
  const mappedUnits = english.units.map(unit => ({
    id: unit.id,
    title: unit.title,
    href: pages.get(unit.id).url,
    page: pick(pages.get(unit.id), ['path', 'url', 'bytes', 'sha256']),
    sections: unit.sections,
    objectives_href: unit.sections.some(id => id.endsWith('-objectives'))
      ? anchor(unit.id, unit.sections.find(id => id.endsWith('-objectives'))) : null,
    previous_units: previous.filter(row => row.to === unit.id).map(row => row.from),
    components: unit.components,
    exercises: unit.exercises.map(id => {
      const exercise = exercises.get(id);
      assert.ok(exercise);
      const supports = Object.fromEntries(['hint', 'check', 'solution'].map(kind => {
        const support = exercise[kind];
        const available = ['complete', 'executable'].includes(support.status);
        return [kind, {...support, href: available ? anchor(unit.id, support.source_anchor) : null}];
      }));
      return {
        id, unit_id: unit.id, title: exercise.title, kind: exercise.kind,
        sequence: exercise.sequence, curriculum_status: exercise.curriculum_status,
        href: anchor(unit.id, id), ...supports,
      };
    }),
  }));
  const routes = english.prerequisite_routes.map(route => ({
    ...route,
    required_for_course: route.required_for_b80,
    href: anchor(route.unit, route.sections[0]),
  }));
  const catalogPage = publication.pages.files.find(row => row.path === 'backend/catalog.json');
  const offline = publication.release.assets.find(row => row.name.includes('OFFLINE_READER'));
  const pdf = publication.release.assets.find(row => row.name.endsWith('.pdf'));
  assert.ok(catalogPage && offline && pdf);
  const learningMap = {
    schema: 'b80-learning-map-en/1', contract: 'course-learning-capability/1',
    course_id: 'B80', locale: 'en', native_dataset: 'family-09-mathematical-computing/B80',
    title: english.course.title,
    localization_of: {course_id: 'B80', locale: 'id-ID', shared_identity: true},
    source_catalog: pick(catalogPage, ['url', 'bytes', 'sha256']),
    public_release: {
      repository: sourceLock.courses.B80.repository, commit: sourceLock.courses.B80.commit,
      tree: sourceLock.courses.B80.tree, release_tag: sourceLock.courses.B80.release_tag,
      offline_reader: offline, pdf,
    },
    units: mappedUnits, prerequisite_routes: routes,
    labs: english.labs, environments: english.environments,
    artifacts: english.artifacts, sources: english.sources,
    limitations: [
      'This is an additive English projection of the same B80 course, units, exercises, laboratories, and prerequisite routes; it is not a duplicate backend.',
      'The map routes to the public English reader and does not execute Python or SageMath in this program website.',
      'Native experiment receipts are preserved as source evidence and are not rerun by this adapter.',
      'The navigation page works offline; linked lessons and course tools require their own download or network access.',
    ],
  };
  const educatorMap = {
    schema: 'b80-educator-map-en/1', contract: learningMap.contract, course_id: 'B80', locale: 'en',
    title: 'B80 educator map · Mathematical Computing and Reproducible Experiments',
    shared_identity: true,
    units: mappedUnits.map(unit => ({
      unit_id: unit.id, title: unit.title, reader_url: unit.href,
      objectives_url: unit.objectives_href, previous_unit_ids: unit.previous_units,
      exercises: unit.exercises.map(row => ({
        exercise_id: row.id, title: row.title, kind: row.kind, curriculum_status: row.curriculum_status,
        exercise_url: row.href, hint: row.hint, check: row.check, solution: row.solution,
      })),
    })),
    prerequisite_routes: routes,
    labs: english.labs,
    limitations: learningMap.limitations,
  };
  return {learningMap, educatorMap, counts};
}

const D120_ID_KEYS = ['id', 'assessment_id', 'rubric_id', 'criterion_id', 'credential_state_id', 'evaluator_id'];
export function localizeD120Projection(indonesianLearning, indonesianEducator, semanticRows, coreRows, accessRows, sourceLock, publication) {
  assert.equal(indonesianLearning.course_id, 'D120');
  assert.equal(indonesianEducator.course_id, 'D120');
  assert.equal(semanticRows.length, 581);
  assert.equal(coreRows.length, 147);
  assert.equal(accessRows.length, 529);
  const completeAccess = new Map();
  for (const row of accessRows) {
    assert.equal(row.locale, 'en');
    assert.ok(!completeAccess.has(row.subject_id), `Duplicate D120 access locator ${row.subject_id}`);
    completeAccess.set(row.subject_id, row);
  }
  const localized = new Map();
  for (const row of [...coreRows, ...semanticRows]) {
    assert.equal(row.locale, 'en');
    const key = `${row.subject_id}\u0000${row.field}`;
    if (localized.has(key)) assert.equal(localized.get(key), row.text, `Conflicting D120 localization ${key}`);
    localized.set(key, row.text);
  }
  let localizedFields = 0;
  const transform = value => {
    if (Array.isArray(value)) return value.map(transform);
    if (!value || typeof value !== 'object') return value;
    const output = {};
    for (const [key, child] of Object.entries(value)) output[key] = transform(child);
    if (value.localization) {
      const subjectId = D120_ID_KEYS.map(key => value[key]).find(item => typeof item === 'string' && item.startsWith('O017-'));
      assert.ok(subjectId, 'Localized D120 object lacks a stable semantic ID');
      output.localization = {};
      for (const field of Object.keys(value.localization)) {
        const text = localized.get(`${subjectId}\u0000${field}`);
        assert.ok(text, `Missing D120 English localization ${subjectId}/${field}`);
        output.localization[field] = text;
        localizedFields += 1;
      }
    }
    return output;
  };
  const learningMap = transform(indonesianLearning);
  const educatorMap = transform(indonesianEducator);
  assert.equal(localizedFields, 339);
  const core = (subject, field) => {
    const text = localized.get(`${subject}\u0000${field}`);
    assert.ok(text, `Missing D120 core localization ${subject}/${field}`);
    return text;
  };
  learningMap.locale = 'en';
  learningMap.title = core('O017-PROGRAM', 'title');
  learningMap.native_reader = sourceLock.courses.D120.public_pages.find(row => row.public_path === 'en/index.html').url;
  const portable = publication.assets.find(row => row.filename.endsWith('-reader-html.zip'));
  assert.ok(portable);
  learningMap.portable_reader = portable.url;
  learningMap.limitations = [
    'This English view is an additive localization of the same D120 semantic objects; it does not create a second course identity.',
    'The adapter projects identities, metadata, relations, and evidence while course bodies remain in the public native edition.',
    'All 54 supporting records are source guidance, not complete solutions.',
    'HTML fragments are access locators and are not promoted to semantic identities.',
    'No learner attempt, submission, result, external participation, or credential is claimed.',
  ];
  educatorMap.locale = 'en';
  educatorMap.limitations = learningMap.limitations;
  const publicPage = new Map(sourceLock.courses.D120.public_pages.map(row => [row.public_path, row]));
  const used = new Map(sourceLock.courses.D120.used_access_locators.map(row => [row.subject_id, row]));
  assert.equal(used.size, sourceLock.courses.D120.used_access_locators.length);
  for (const [subjectId, row] of used) {
    const original = completeAccess.get(subjectId);
    assert.ok(original, `D120 source lock names an unknown access locator ${subjectId}`);
    assert.deepEqual(
      pick(row, ['reader_path', 'fragment']),
      pick(original, ['reader_path', 'fragment']),
      `D120 source-lock locator drift ${subjectId}`,
    );
    assert.equal(row.public_path, original.reader_path.replace(/^build\/html\//, 'en/'));
    assert.equal(row.anchor_count, row.fragment ? 1 : 0);
  }
  const urlFor = subjectId => {
    const locator = used.get(subjectId);
    assert.ok(locator, `Missing D120 used locator ${subjectId}`);
    const page = publicPage.get(locator.public_path);
    assert.ok(page, `Missing D120 public page ${locator.public_path}`);
    return locator.fragment ? `${page.url}#${encodeURIComponent(locator.fragment)}` : page.url;
  };
  for (const unit of learningMap.units) {
    unit.title = core(unit.unit_id, 'title');
    const page = publicPage.get(used.get(unit.unit_id).public_path);
    unit.public_reader = pick(page, ['url', 'bytes', 'sha256']);
    for (const item of unit.practice) {
      item.exercise_url = urlFor(item.exercise_id);
      item.guidance_url = urlFor(item.guidance_id);
    }
  }
  const usedSubjects = new Set(learningMap.units.flatMap(unit => [
    unit.unit_id, ...unit.practice.flatMap(item => [item.exercise_id, item.guidance_id]),
  ]));
  assert.equal(usedSubjects.size, 117);
  assert.deepEqual([...used.keys()].sort(), [...usedSubjects].sort());
  return {learningMap, educatorMap, localizedFields, accessBindings: usedSubjects.size};
}

const STYLE = `:root{color-scheme:light;--ink:#173832;--muted:#506963;--paper:#f4f3ea;--card:#fff;--line:#c9d7d1;--accent:#086c63;--warm:#b96328}*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:17px/1.55 system-ui,-apple-system,Segoe UI,sans-serif}main{max-width:1120px;margin:auto;padding:28px 22px 60px}nav,.links{display:flex;gap:1rem;flex-wrap:wrap;margin-bottom:1.4rem}a{color:var(--accent);text-underline-offset:3px}h1{font-size:clamp(2rem,5vw,3.35rem);line-height:1.08;margin:.2rem 0 1rem}h2{margin-top:2.2rem}.lede{font-size:1.15rem;max-width:76ch}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(190px,1fr));gap:12px;margin:1.5rem 0}.card,details{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:16px}.metric{font-size:1.8rem;font-weight:750;display:block}.muted{color:var(--muted)}details{margin:.8rem 0}summary{cursor:pointer;font-weight:700}.pill{display:inline-block;border:1px solid var(--line);border-radius:999px;padding:.1rem .55rem;font-size:.85rem}.notice{border-left:6px solid var(--warm);background:#fff8ef;padding:1rem 1.2rem;border-radius:8px}.scroll{overflow:auto}table{width:100%;border-collapse:collapse;background:white}th,td{border-bottom:1px solid var(--line);padding:.7rem;text-align:left;vertical-align:top}a:focus-visible,summary:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid #d48624;outline-offset:3px}.filters{display:flex;gap:16px;flex-wrap:wrap;padding:20px 0;border-block:1px solid var(--line)}label{display:grid;gap:5px}input,select{font:inherit;padding:9px;max-width:100%}.exercise{border-top:1px solid var(--line);padding:17px 0}[hidden]{display:none!important}@media print{nav,.filters{display:none}body{background:white;font-size:10pt}main{max-width:none;padding:0}}`;
const shell = (course, title, body, counterpart) => `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="description" content="Verified English learner and educator projection for ${course}."><title>${esc(title)}</title><style>${STYLE}</style></head><body><main><nav>${link('../../en/', 'Mathematics Program')}${link('../index.html', 'Backend hub')}${link(counterpart.href, counterpart.label)}${link(`../${course.toLowerCase()}/${course}.html`, 'Bahasa Indonesia')}</nav><p class="muted">${course} · English · shared course identity</p><h1>${esc(title)}</h1>${body}</main></body></html>\n`;

function renderB80Learning(map) {
  const unitOptions = map.units.map(unit => `<option value="${esc(unit.id)}">${esc(unit.title)}</option>`).join('');
  const rows = map.units.flatMap(unit => unit.exercises.map(exercise => `<article class="exercise" data-unit="${esc(unit.id)}" data-kind="${esc(exercise.kind)}"><p class="muted">${esc(unit.title)} · ${esc(exercise.kind)}</p><h2>${link(exercise.href, exercise.title)}</h2><div class="links">${exercise.hint.href ? link(exercise.hint.href, 'Hint') : 'Hint unavailable'}${exercise.check.href ? link(exercise.check.href, 'Check') : 'Check unavailable'}${exercise.solution.href ? link(exercise.solution.href, 'Solution') : 'Solution unavailable'}</div></article>`)).join('');
  const body = `<p class="lede">One English route through the same 14 B80 units, 75 exercises, four laboratories, and four prerequisite routes used by the Indonesian course.</p><div class="grid"><div class="card"><span class="metric">14</span>units</div><div class="card"><span class="metric">75</span>exercises</div><div class="card"><span class="metric">4</span>laboratories</div><div class="card"><span class="metric">4</span>prerequisite routes</div></div><p>${link(map.public_release.offline_reader.url, 'Download the offline English reader')} · ${link(map.public_release.pdf.url, 'English PDF')} · ${link('learning-map.json', 'Open map data')}</p><div class="notice"><strong>Identity boundary:</strong> this is an English localization of B80, not a second course. Unit, exercise, laboratory, prerequisite, component, artifact, environment, and source IDs remain aligned with the Indonesian edition.</div><div class="filters"><label>Search exercises<input id="query" type="search" placeholder="Title or topic"></label><label>Unit<select id="unit"><option value="">All units</option>${unitOptions}</select></label><label>Kind<select id="kind"><option value="">All kinds</option><option value="core">Core</option><option value="mastery">Mastery</option></select></label></div><p id="count" role="status" aria-live="polite"></p><section>${rows}</section><script>const q=document.querySelector('#query'),u=document.querySelector('#unit'),k=document.querySelector('#kind'),rows=[...document.querySelectorAll('.exercise')];function update(){let n=0;for(const row of rows){const show=(!u.value||row.dataset.unit===u.value)&&(!k.value||row.dataset.kind===k.value)&&row.textContent.toLocaleLowerCase('en').includes(q.value.toLocaleLowerCase('en').trim());row.hidden=!show;if(show)n++}document.querySelector('#count').textContent=n+' of '+rows.length+' exercises shown.'}for(const control of [q,u,k])control.addEventListener('input',update);update();</script>`;
  return shell('B80', map.title, body, {href: 'B80-educator.html', label: 'Educator view'});
}

function renderB80Educator(map) {
  const rows = map.units.map(unit => `<tr><th scope="row">${link(unit.reader_url, unit.title)}</th><td>${unit.objectives_url ? link(unit.objectives_url, 'Learning objectives') : 'Not indexed'}</td><td>${unit.previous_unit_ids.map(id => `<code>${esc(id)}</code>`).join(', ') || 'Start'}</td><td>${unit.exercises.map(exercise => link(exercise.exercise_url, exercise.title)).join('<br>')}</td></tr>`).join('');
  const labs = map.labs.map(lab => `<li><code>${esc(lab.id)}</code> · ${esc(lab.kind)} · unit <code>${esc(lab.unit)}</code> · ${lab.exercise_ids.length} exercise(s)</li>`).join('');
  const body = `<p class="lede">A shared-identity planning surface for the English B80 reader: sequence, objectives, exercises with staged support, prerequisite routes, and laboratory bindings.</p><p>${link('educator-map.json', 'Open educator data')} · ${link('learning-map.json', 'Open learner data')}</p><div class="notice"><strong>Boundary:</strong> this page organizes verified source metadata. It is not an execution service, automated grader, or claim that the native experiment receipts were rerun centrally.</div><h2>Unit plan</h2><div class="scroll"><table><thead><tr><th>Unit</th><th>Objectives</th><th>Previous</th><th>Exercises</th></tr></thead><tbody>${rows}</tbody></table></div><h2>Laboratories</h2><ul>${labs}</ul><h2>Prerequisite routes</h2><ul>${map.prerequisite_routes.map(route => `<li>${link(route.href, route.title)} · prerequisite <code>${esc(route.prerequisite)}</code> · ${route.required_for_course ? 'core' : 'enrichment'}</li>`).join('')}</ul>`;
  return shell('B80', map.title, body, {href: 'B80.html', label: 'Learner view'});
}

function renderD120Learning(map) {
  const units = map.units.map(unit => `<details><summary>Unit ${unit.ordinal} · ${esc(unit.title)} <span class="pill">${unit.outcomes.length} outcomes · ${unit.practice.length} exercises</span></summary><p>${link(unit.public_reader.url, 'Open English unit')} · competency <code>${esc(unit.competency.id)}</code> · assessment <code>${esc(unit.assessment_id)}</code></p><h2>Outcomes</h2><ol>${unit.outcomes.map(row => `<li><code>${esc(row.id)}</code> — ${esc(row.localization.description)}</li>`).join('')}</ol><h2>Practice and source guidance</h2><ul>${unit.practice.map(row => `<li>${link(row.exercise_url, row.exercise_id)} · ${link(row.guidance_url, `guidance ${row.guidance_id}`)}</li>`).join('')}</ul></details>`).join('');
  const body = `<p class="lede">A nine-unit English route for research reading, argument reconstruction, exposition, provenance, reproducible computation, errata, review, and auditable contribution work.</p><div class="grid"><div class="card"><span class="metric">9</span>units</div><div class="card"><span class="metric">71</span>outcomes</div><div class="card"><span class="metric">54</span>exercise–guidance pairs</div><div class="card"><span class="metric">14</span>assessment designs</div></div><p>${link(map.native_reader, 'Open the complete English reader')} · ${link(map.portable_reader, 'Download the offline English reader')} · ${link('learning-map.json', 'Open map data')}</p><div class="notice"><strong>Truth boundary:</strong> the 54 companion records are source guidance, not complete solutions. The backend defines routes and templates; it does not claim learner submissions, results, external participation, or credentials.</div><h2>Learning sequence</h2>${units}`;
  return shell('D120', map.title, body, {href: 'D120-educator.html', label: 'Educator view'});
}

function renderD120Educator(map) {
  const assessments = map.assessments.map(assessment => `<details><summary>${esc(assessment.localization.label)} <span class="pill">${esc(assessment.kind)}</span></summary><p>${esc(assessment.localization.description)}</p><p><strong>Instructions:</strong> ${esc(assessment.localization.instructions)}</p><p><code>${esc(assessment.assessment_id)}</code> · ${assessment.outcome_ids.length} outcomes · ${assessment.evidence_spec_ids.length} evidence specifications</p><ol>${assessment.rubric.criteria.map(row => `<li><code>${esc(row.criterion_id)}</code> — ${esc(row.localization.criterion_text)}</li>`).join('')}</ol></details>`).join('');
  const body = `<p class="lede">English planning surface for 14 assessments, 14 rubrics, 79 criteria, six credential-state definitions, and five evaluator roles using the same semantic IDs as the Indonesian D120 course.</p><p>${link('educator-map.json', 'Open educator data')} · ${link('learning-map.json', 'Open learner data')}</p><div class="notice"><strong>Truth boundary:</strong> credential states are definitions, not achievement claims. External action is never inferred from a template, locator, or prepared artifact.</div><h2>Assessment designs</h2>${assessments}`;
  return shell('D120', 'D120 educator map · Traceable Mathematical Work', body, {href: 'D120.html', label: 'Learner view'});
}

export async function buildOriginalIndonesianBilingual() {
  const sourceLockPath = `${base}/source-lock.json`;
  const sourceLock = await readJson(sourceLockPath);
  assert.equal(sourceLock.schema, 'original-indonesian-bilingual-source-lock/1');
  assert.equal(sourceLock.status, 'verified_public_inputs');
  assert.deepEqual(sourceLock.policy, {
    additive_localization_only: true,
    central_course_identity_duplicated: false,
    native_ids_preserved: true,
    producer_files_changed: false,
    textbook_bodies_copied: false,
  });
  for (const expected of [...sourceLock.inputs, ...sourceLock.central_inputs]) assert.deepEqual(await fact(expected.path), expected);

  const b80Id = await readJson('backend/course-capsule-v1/adapters/b80-capability-v1/input/catalog.json');
  const b80En = await readJson(`${base}/input/b80/catalog.en.json`);
  const b80Publication = await readJson(`${base}/input/b80/github-publication.json`);
  assert.equal(b80Publication.status, 'public_verified');
  const b80 = b80Projection(b80Id, b80En, sourceLock, b80Publication);
  const b80CentralReadbackPath = 'backend/course-capsule-v1/adapters/b80-capability-v1/publication/GITHUB_SOURCE_AND_PAGES_READBACK_20260904.json';
  const b80CentralReadback = await readJson(b80CentralReadbackPath);
  assert.equal(b80CentralReadback.schema, 'b80-source-pages-readback/1');
  assert.equal(b80CentralReadback.state, 'pass');
  assert.equal(b80CentralReadback.anonymous, true);
  assert.equal(b80CentralReadback.credentials_used, false);
  assert.equal(b80CentralReadback.github_source_and_pages_verified, true);
  assert.equal(b80CentralReadback.overall_program_backend_complete, false);
  const b80Manifest = await readJson('backend/course-capsule-v1/adapters/b80-capability-v1/manifest.json');
  const readbackByPath = new Map(b80CentralReadback.files.map(row => [row.path, row]));
  for (const output of b80Manifest.outputs) {
    const publicRow = readbackByPath.get(output.path);
    assert.ok(publicRow, `B80 public receipt omitted ${output.path}`);
    assert.deepEqual(pick(publicRow, ['bytes', 'sha256']), pick(output, ['bytes', 'sha256']));
    assert.equal(publicRow.http_status, 200);
  }
  const b80PublicationState = {
    schema: 'b80-current-publication-state/1', course_id: 'B80',
    current_central_adapter_status: 'public_github_verified',
    current_english_source_edition_status: 'public_github_verified',
    central_adapter: {
      source_commit: b80CentralReadback.source_commit,
      readback: await fact(b80CentralReadbackPath),
      github_source_and_pages_verified: true,
      zenodo_preservation_verified: b80CentralReadback.zenodo_preservation_verified,
    },
    english_source_edition: {
      repository: sourceLock.courses.B80.repository,
      commit: sourceLock.courses.B80.commit,
      tree: sourceLock.courses.B80.tree,
      release_tag: sourceLock.courses.B80.release_tag,
      anonymous_publication_receipt: await fact(`${base}/input/b80/github-publication.json`),
    },
    status_interpretation: 'The older manifest and validation fields are historical pre-publication statements. This current record is derived from the later immutable anonymous public readback and does not rewrite that historical evidence.',
    current_english_shared_projection_status: 'locally_verified_pending_this_increment_publication',
    overall_program_backend_complete: false,
  };

  const d120IdLearning = await readJson('backend/course-capsule-v1/adapters/d120-capability-v1/data/learning-map.json');
  const d120IdEducator = await readJson('backend/course-capsule-v1/adapters/d120-capability-v1/data/educator-map.json');
  const d120Semantic = parseJsonl(await readFile(resolve(root, `${base}/input/d120/semantic-wrapper-v1.localizations.en.jsonl`), 'utf8'));
  const d120Core = parseJsonl(await readFile(resolve(root, `${base}/input/d120/core-localizations.en.jsonl`), 'utf8'));
  const d120Access = parseJsonl(await readFile(resolve(root, `${base}/input/d120/english-access-locators.jsonl`), 'utf8'));
  const d120Publication = await readJson(`${base}/input/d120/github-publication.json`);
  assert.equal(d120Publication.status, 'PASS');
  const d120 = localizeD120Projection(d120IdLearning, d120IdEducator, d120Semantic, d120Core, d120Access, sourceLock, d120Publication);

  const canonical = new Map([
    [`${base}/data/b80/learning-map.en.json`, json(b80.learningMap)],
    [`${base}/data/b80/educator-map.en.json`, json(b80.educatorMap)],
    [`${base}/data/b80/publication-state.json`, json(b80PublicationState)],
    [`${base}/data/d120/learning-map.en.json`, json(d120.learningMap)],
    [`${base}/data/d120/educator-map.en.json`, json(d120.educatorMap)],
    [`${base}/views/b80/B80.html`, renderB80Learning(b80.learningMap)],
    [`${base}/views/b80/B80-educator.html`, renderB80Educator(b80.educatorMap)],
    [`${base}/views/d120/D120.html`, renderD120Learning(d120.learningMap)],
    [`${base}/views/d120/D120-educator.html`, renderD120Educator(d120.educatorMap)],
  ]);
  const publicMappings = [
    [`${base}/views/b80/B80.html`, 'docs/backend/b80-en/B80.html'],
    [`${base}/views/b80/B80-educator.html`, 'docs/backend/b80-en/B80-educator.html'],
    [`${base}/data/b80/learning-map.en.json`, 'docs/backend/b80-en/learning-map.json'],
    [`${base}/data/b80/educator-map.en.json`, 'docs/backend/b80-en/educator-map.json'],
    [`${base}/data/b80/publication-state.json`, 'docs/backend/b80/publication-state.json'],
    [`${base}/data/b80/publication-state.json`, 'docs/backend/b80-en/publication-state.json'],
    [`${base}/views/d120/D120.html`, 'docs/backend/d120-en/D120.html'],
    [`${base}/views/d120/D120-educator.html`, 'docs/backend/d120-en/D120-educator.html'],
    [`${base}/data/d120/learning-map.en.json`, 'docs/backend/d120-en/learning-map.json'],
    [`${base}/data/d120/educator-map.en.json`, 'docs/backend/d120-en/educator-map.json'],
  ];
  for (const [path, contents] of canonical) {
    await mkdir(dirname(resolve(root, path)), {recursive: true});
    await writeFile(resolve(root, path), contents);
  }
  for (const [source, target] of publicMappings) {
    const contents = await readFile(resolve(root, source));
    await mkdir(dirname(resolve(root, target)), {recursive: true});
    await writeFile(resolve(root, target), contents);
  }
  const generatedFacts = await Promise.all([...canonical.keys(), ...publicMappings.map(row => row[1])].map(fact));
  const validation = {
    schema: 'original-indonesian-bilingual-validation/1', state: 'pass',
    policy: sourceLock.policy,
    source_lock: await fact(sourceLockPath),
    B80: {...b80.counts, stable_identity_parity: true, public_pages: 14, public_anchor_binding: true, central_adapter_public_github_verified: true, english_source_edition_public_github_verified: true},
    D120: {
      units: 9, exercises: 54, guidance_records: 54, learning_outcomes: 71,
      assessments: 14, criteria: 79, semantic_localizations_available: 581,
      core_localizations_available: 147, access_locators_available: 529,
      localized_fields_used: d120.localizedFields, learner_access_bindings_used: d120.accessBindings,
      stable_identity_parity: true,
    },
    outputs: generatedFacts,
    duplicate_course_identities_created: 0,
    producer_files_changed: false,
    textbook_bodies_copied: false,
  };
  const validationText = json(validation);
  await writeFile(resolve(root, `${base}/validation.json`), validationText);
  for (const course of ['b80', 'd120']) await writeFile(resolve(root, `docs/backend/${course}-en/validation.json`), validationText);
  const validationFacts = await Promise.all([
    `${base}/validation.json`, 'docs/backend/b80-en/validation.json', 'docs/backend/d120-en/validation.json',
  ].map(fact));
  const byPath = new Map([...generatedFacts, ...validationFacts].map(row => [row.path, row]));
  const tools = [
    ['B80', 'b80-exercise-map-en-v1', 'B80 · English learner and exercise map', 'practice_diagnostic_map', 'docs/backend/b80-en/B80.html', 'docs/backend/b80-en/learning-map.json', '14 units, 75 exercises, four laboratories, and four prerequisite routes with the native B80 identities preserved.'],
    ['B80', 'b80-educator-map-en-v1', 'B80 · English educator map', 'reference', 'docs/backend/b80-en/B80-educator.html', 'docs/backend/b80-en/educator-map.json', 'English unit planning for the same 14 B80 units, 75 exercises, four laboratories, and four prerequisite routes.'],
    ['D120', 'd120.open_learner_hub.en', 'D120 · Traceable Mathematical Work in English', 'course_reader', 'docs/backend/d120-en/D120.html', 'docs/backend/d120-en/learning-map.json', 'Nine units, 54 exercise–guidance pairs, and 71 learning outcomes localized against the native D120 semantic IDs.'],
    ['D120', 'd120.open_educator_hub.en', 'D120 · English educator map', 'reference', 'docs/backend/d120-en/D120-educator.html', 'docs/backend/d120-en/educator-map.json', 'Fourteen assessments, 14 rubrics, 79 criteria, and explicit non-claim boundaries in English over the same D120 IDs.'],
  ].map(([courseId, tool_id, label, action_kind, pagePath, resourcePath, scope]) => ({
    courseId, contentLanguage: 'en', labelLanguage: 'en', tool_id, label,
    href: pagePath.replace(/^docs\//, ''), action_kind, scope, state: 'verified', primary: false,
    machine_data_is_learner_destination: false,
    page: byPath.get(pagePath), resource: byPath.get(resourcePath),
    evidence: byPath.get(`docs/backend/${courseId.toLowerCase()}-en/validation.json`),
    limitations: courseId === 'B80' ? b80.learningMap.limitations : d120.learningMap.limitations,
  }));
  const manifest = {
    schema: 'original-indonesian-bilingual-manifest/1', state: 'verified',
    course_ids: ['B80', 'D120'], locales: ['id-ID', 'en'],
    policy: sourceLock.policy,
    inputs: [await fact(sourceLockPath), ...sourceLock.inputs, ...sourceLock.central_inputs],
    outputs: [...generatedFacts, ...validationFacts],
    tools,
    counts: {courses_localized: 2, english_learner_views: 2, english_educator_views: 2, interface_tools: 4},
  };
  await writeFile(resolve(root, `${base}/manifest.json`), json(manifest));
  console.log(JSON.stringify({state: 'pass', B80: b80.counts, D120: validation.D120, tools: tools.length}));
  return {manifest, validation};
}

if (resolve(process.argv[1] ?? '') === resolve(fileURLToPath(import.meta.url))) await buildOriginalIndonesianBilingual();
