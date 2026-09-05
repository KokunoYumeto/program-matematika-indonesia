import { interfaceCourses, interfaceTopics, coursePresentation, resourceBindings, renderCourseCard, escapeMarkup } from './view.js';
import { interfaceCopy, localeMetadata, fillCopy } from './locales.js';
import { LEARNER_STATE_STORAGE_KEY, createEmptyLearnerState, loadLearnerState, saveLearnerState, clearLearnerState, normalizeLearnerState, serializeLearnerState, evaluateLearnerState, setCourseCompletion, setCourseClaim, setPrerequisiteWaiver } from '../learner-state.js';

const documentLanguageTag = String(document.documentElement.lang || '').toLowerCase();
const interfaceLocale = document.documentElement.dataset.interfaceLocale
  ?? Object.keys(localeMetadata).find((locale) => localeMetadata[locale].languageTag.toLowerCase() === documentLanguageTag);
if (!interfaceLocale || !interfaceCopy[interfaceLocale]) throw new Error('Unknown interface locale');
const ui = interfaceCopy[interfaceLocale];
const interfaceLanguageTag = localeMetadata[interfaceLocale].languageTag;
const $ = (selector) => document.querySelector(selector);
let storage = null;
try { storage = window.localStorage; } catch { /* Private browsing or file: restrictions. */ }
const loaded = loadLearnerState(storage, interfaceCourses);
let record = loaded.state, evaluated = evaluateLearnerState(interfaceCourses, record);
let unpersistedChanges = false;
let viewFragment = navigationFragment(location.hash);
const normalizeSearch = (value) => value.toLocaleLowerCase(interfaceLanguageTag).normalize('NFD').replace(/\p{M}/gu, '');

function navigationFragment(value) {
  return ['#top', '#katalog', '#progress', '#about'].includes(value) || interfaceCourses.some(course => value === '#course-' + course.id) ? value : '';
}
function viewUrl() {
  const url = new URL(location.href);
  url.search = ''; url.hash = viewFragment;
  // Navigation carries only view filters, never learner records or unknown URL data.
  for (const [key, value] of Object.entries(readFilters())) {
    if (value && value !== 'all') url.searchParams.set(key, value);
  }
  return url;
}
function updateLanguageLinks() {
  const view = viewUrl();
  document.querySelectorAll('[data-locale-link]').forEach((link) => {
    const url = new URL(link.getAttribute('data-locale-base'), location.href);
    url.search = view.search; url.hash = view.hash;
    link.href = url.href;
  });
}
function readFilters() {
  return { q: $('#search').value, topic: $('#topic').value, level: $('#level').value, show: $('#show').value };
}
function restoreFilters() {
  const params = new URLSearchParams(location.search);
  for (const [key, selector] of [['q', '#search'], ['topic', '#topic'], ['level', '#level'], ['show', '#show']]) {
    const control = $(selector), value = params.get(key) ?? (key === 'q' ? '' : 'all');
    control.value = value;
    if (key !== 'q' && !control.value) control.value = 'all';
  }
}
function storeFilters(preserveCourseFragment = false) {
  // A newly chosen filter is a new view, not an instruction to reopen an old card.
  if (!preserveCourseFragment && /^#course-/.test(viewFragment)) viewFragment = '';
  const url = viewUrl();
  try { history.replaceState(null, '', url); } catch { /* Offline file URLs may not support this. */ }
  updateLanguageLinks();
}
function filteredRows() {
  const filter = readFilters(), query = normalizeSearch(filter.q.trim());
  return interfaceCourses.filter((course) => {
    const c = coursePresentation(course, interfaceLocale), state = evaluated[course.id].status;
    if (filter.level !== 'all' && course.level !== filter.level) return false;
    if (filter.topic !== 'all' && String(interfaceTopics.indexOf(course.topic)) !== filter.topic) return false;
    if (filter.show === 'completed' && state !== 'completed') return false;
    if (filter.show === 'eligible' && !['eligible', 'eligible_with_waiver'].includes(state)) return false;
    if (filter.show === 'offline' && !resourceBindings(course, interfaceLocale).some((r) => r.accessRole === 'offline-copy' && r.contentLanguage.toLowerCase() === interfaceLanguageTag.toLowerCase())) return false;
    return !query || normalizeSearch([course.id, c.title, c.topic, c.purpose].join(' ')).includes(query);
  });
}
function renderInterface() {
  const activeCompletion = document.activeElement?.dataset?.completion;
  const expanded = [...document.querySelectorAll('.course-card details[open]')].map((detail) => {
    const card = detail.closest('.course-card');
    return { id: card.id, index: [...card.querySelectorAll('details')].indexOf(detail) };
  });
  const rows = filteredRows();
  $('#course-grid').innerHTML = rows.map((course) => renderCourseCard(course, interfaceLocale, evaluated[course.id])).join('');
  for (const item of expanded) {
    const detail = $('#' + item.id)?.querySelectorAll?.('details')?.[item.index];
    if (detail) detail.open = true;
  }
  if (activeCompletion) {
    const focusTarget = document.querySelector('[data-completion="' + activeCompletion + '"]') ?? $('#result-count');
    focusTarget.focus({ preventScroll: true });
  }
  $('#result-count').textContent = fillCopy(ui.result, { shown: rows.length, total: interfaceCourses.length });
  $('#empty-state').hidden = rows.length !== 0;
  const counts = Object.values(evaluated).reduce((all, row) => { all[row.status] = (all[row.status] ?? 0) + 1; return all; }, {});
  $('#progress-summary').textContent = fillCopy(ui.progressSummary, { done: counts.completed ?? 0, ready: (counts.eligible ?? 0) + (counts.eligible_with_waiver ?? 0), blocked: counts.blocked ?? 0 });
  const claims = [];
  for (const [field, kind] of [['placementClaims', 'placement'], ['equivalenceClaims', 'equivalence']]) {
    for (const claim of record[field]) claims.push('<li>' + escapeMarkup(ui[kind]) + ': ' + escapeMarkup(claim.courseId) + ' <button data-remove-claim="' + escapeMarkup(kind) + '" data-id="' + escapeMarkup(claim.courseId) + '">' + escapeMarkup(ui.remove) + '</button></li>');
  }
  for (const row of record.waivers) claims.push('<li>' + escapeMarkup(ui.waiver) + ': ' + escapeMarkup(row.targetCourseId) + ' ← ' + escapeMarkup(row.prerequisiteCourseId) + ' <button data-remove-waiver="' + escapeMarkup(row.targetCourseId) + '" data-prereq="' + escapeMarkup(row.prerequisiteCourseId) + '">' + escapeMarkup(ui.remove) + '</button></li>');
  $('#claims').innerHTML = claims.length ? '<ul>' + claims.join('') + '</ul>' : '<p>' + escapeMarkup(ui.noClaims) + '</p>';
}
function saveRecord(next) {
  const saved = saveLearnerState(storage, next, interfaceCourses);
  unpersistedChanges = !saved.persisted;
  record = saved.state; evaluated = evaluateLearnerState(interfaceCourses, record);
  $('#storage-message').textContent = saved.persisted ? ui.saved : ui.noStorage;
  renderInterface();
}
function restoreCourseFragment(focus = false) {
  const courseId = viewFragment.startsWith('#course-') ? viewFragment.slice('#course-'.length) : '';
  if (!courseId || !interfaceCourses.some((c) => c.id === courseId)) return;
  if (!$('#course-' + courseId)) {
    $('#search').value = ''; for (const selector of ['#topic', '#level', '#show']) $(selector).value = 'all';
    storeFilters(true); renderInterface();
  }
  requestAnimationFrame(() => {
    const card = $('#course-' + courseId);
    card?.scrollIntoView({ block: 'start' });
    if (focus) card?.focus({ preventScroll: true });
  });
}
function updateWaiverOptions() {
  const target = interfaceCourses.find((course) => course.id === $('#waiver-target').value);
  $('#waiver-prereq').innerHTML = target.prerequisites.map((id) => '<option value="' + id + '">' + id + '</option>').join('');
  $('#add-waiver').disabled = target.prerequisites.length === 0;
}
document.addEventListener('change', (event) => {
  if (event.target.matches('[data-completion]')) saveRecord(setCourseCompletion(record, interfaceCourses, event.target.dataset.completion, event.target.checked));
});
document.addEventListener('click', (event) => {
  const courseLink = event.target.closest('[data-course-link]');
  if (courseLink && !event.ctrlKey && !event.metaKey && !event.shiftKey && !event.altKey && event.button === 0) {
    event.preventDefault();
    viewFragment = '#course-' + courseLink.dataset.courseLink;
    const url = viewUrl();
    try { history.pushState(null, '', url); } catch { location.hash = url.hash; }
    restoreCourseFragment(true); updateLanguageLinks();
  }
  const remove = event.target.closest('[data-remove-claim]');
  if (remove) saveRecord(setCourseClaim(record, interfaceCourses, remove.dataset.removeClaim, remove.dataset.id, false));
  const waiver = event.target.closest('[data-remove-waiver]');
  if (waiver) saveRecord(setPrerequisiteWaiver(record, interfaceCourses, waiver.dataset.removeWaiver, waiver.dataset.prereq, false));
});
for (const selector of ['#topic', '#level', '#show']) $(selector).addEventListener('change', () => { storeFilters(); renderInterface(); });
$('#search').addEventListener('input', () => { storeFilters(); renderInterface(); });
$('#reset-filters').addEventListener('click', () => {
  $('#search').value = ''; for (const selector of ['#topic', '#level', '#show']) $(selector).value = 'all';
  storeFilters(); renderInterface();
});
for (const kind of ['placement', 'equivalence']) $('#add-' + kind).addEventListener('click', () => saveRecord(setCourseClaim(record, interfaceCourses, kind, $('#' + kind + '-course').value, true)));
$('#waiver-target').addEventListener('change', updateWaiverOptions);
$('#add-waiver').addEventListener('click', () => saveRecord(setPrerequisiteWaiver(record, interfaceCourses, $('#waiver-target').value, $('#waiver-prereq').value, true)));
$('#clear-progress').addEventListener('click', () => {
  if (!window.confirm(ui.resetConfirm)) return;
  clearLearnerState(storage); saveRecord(createEmptyLearnerState());
});
$('#export-progress').addEventListener('click', () => {
  const url = URL.createObjectURL(new Blob([serializeLearnerState(record, interfaceCourses)], { type: 'application/json' }));
  const link = document.createElement('a'); link.href = url; link.download = 'mathematics-progress.json'; link.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
});
$('#import-progress').addEventListener('change', async (event) => {
  const file = event.target.files?.[0]; if (!file) return;
  try {
    if (file.size > 1000000) throw new Error('Too large');
    const next = normalizeLearnerState(JSON.parse(await file.text()), interfaceCourses);
    saveRecord(next);
  } catch { $('#storage-message').textContent = ui.importError; }
  event.target.value = '';
});
window.addEventListener('hashchange', () => { viewFragment = navigationFragment(location.hash); restoreCourseFragment(true); updateLanguageLinks(); });
window.addEventListener('popstate', () => { viewFragment = navigationFragment(location.hash); restoreFilters(); renderInterface(); restoreCourseFragment(); updateLanguageLinks(); });
window.addEventListener('storage', (event) => {
  if (!storage || event.storageArea !== storage || (event.key !== null && event.key !== LEARNER_STATE_STORAGE_KEY)) return;
  // Failed writes leave an intentionally usable in-memory record. Another tab
  // must not silently discard that record; export remains available to save it.
  if (unpersistedChanges) return;
  const fresh = loadLearnerState(storage, interfaceCourses); record = fresh.state;
  evaluated = evaluateLearnerState(interfaceCourses, record); renderInterface();
});
$('#storage-message').textContent = loaded.status === 'unavailable' ? ui.noStorage : loaded.status === 'recovered_invalid' ? ui.recovered : ui.saved;
restoreFilters(); updateWaiverOptions(); renderInterface(); restoreCourseFragment(); updateLanguageLinks();
// Reveal controls only after initialization succeeds; the static catalog remains usable on failure.
document.documentElement.classList.add('js');
