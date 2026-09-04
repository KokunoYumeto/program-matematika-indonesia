import { courses as authorityCourses, topics } from '../courses.js';
import { materializeLiveCourses } from '../live-course-publications.js';
import { learnerDeliveryByCourseId } from '../learner-delivery.js';
import { learnerToolsByCourseId } from '../learner-tools.js';
import { interfaceCopy, topicCopy, englishCourseCopy, englishResources, siteOrigin } from './locales.js';
import { verifiedReaderActions } from './reader-actions.js';
import { finalEditions } from './final-editions.js';
import { capabilityTools } from './capability-tools.js';
import { supplementalReaders } from './supplemental-readers.js';
import { additionalOriginalSources } from './original-sources.js';

// Final links are a presentation overlay, not a replacement backend or corpus.
export const interfaceCourses = materializeLiveCourses(authorityCourses).map(course => {
  const edition = finalEditions.find(row => row.courseId === course.id);
  return edition ? {...course, state:'published', version:edition.version} : course;
});
// Reject any publication overlay that changes the authority graph.
for (const [position, course] of interfaceCourses.entries()) {
  const source = authorityCourses[position];
  if (course.id !== source.id || course.level !== source.level || course.topic !== source.topic
      || JSON.stringify(course.prerequisites) !== JSON.stringify(source.prerequisites)) {
    throw new Error('Publication projection changed the canonical graph: ' + source.id);
  }
}
export const interfaceTopics = topics;
export function escapeMarkup(value = '') {
  return String(value).replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;').replaceAll('"', '&quot;').replaceAll("'", '&#39;');
}
export function safeResourceUrl(value) {
  if (typeof value !== 'string' || !value || /[\u0000-\u0020]/.test(value)) throw new Error('Invalid resource URL');
  const url = new URL(value, siteOrigin);
  if (url.protocol !== 'https:') throw new Error('Only HTTPS learning resources are allowed');
  return url.href;
}
export function coursePresentation(course, locale) {
  if (locale === 'id') return { title: course.title, purpose: course.purpose, outcome: course.outcome, topic: course.topic };
  const copy = englishCourseCopy[course.id];
  if (!copy || !topicCopy[course.topic]) throw new Error('Missing English presentation: ' + course.id);
  return { title: copy[0], purpose: copy[1], outcome: copy[2], topic: topicCopy[course.topic] };
}
export function resourceBindings(course, locale) {
  const t = interfaceCopy[locale];
  const rows = [];
  const add = (label, href, contentLanguage, kind = 'link', extra = {}) => {
    if (href && !rows.some((row) => row.href === safeResourceUrl(href))) rows.push({ label, labelLanguage: locale, href: safeResourceUrl(href), contentLanguage, kind, ...extra });
  };
  for (const row of englishResources[course.id] ?? []) {
    const {label,href,contentLanguage,kind,...facts} = row;
    add(label, href, contentLanguage, kind, { ...facts, labelLanguage:'en', primary: locale === 'en' && rows.length === 0 });
  }
  const idPrefix = locale === 'en' ? 'Bahasa Indonesia — ' : '';
  const finalEdition = finalEditions.find(row => row.courseId === course.id);
  if (finalEdition) for (const row of finalEdition.resources) {
    const pages = row.pages ? ' — ' + row.pages + (locale === 'id' ? ' halaman' : ' pages') : '';
    add(idPrefix + row.labels[locale] + pages, row.href, 'id', row.kind,
      {editionResourceId:row.id, format:row.format, bytes:row.bytes, sha256:row.sha256,
        offlineAfterDownload:row.offlineAfterDownload, primary:locale === 'id' && row.primary});
  }
  const actions = verifiedReaderActions.filter((action) => action.courseId === course.id);
  const actionNames = locale === 'id'
    ? { textbook: 'Buku teks', problembook: 'Buku soal dan penyelesaian', combined_textbook_problembook: 'Buku gabungan teks dan soal' }
    : { textbook: 'Textbook', problembook: 'Problems and solutions', combined_textbook_problembook: 'Combined textbook and problems' };
  for (const action of actions) {
    const { label: sourceLabel, ...metadata } = action;
    add(idPrefix + actionNames[action.role] + ' — ' + action.pages + (locale === 'id' ? ' halaman' : ' pages'), action.href, 'id', action.role === 'problembook' ? 'companion' : 'reader',
      { ...metadata, labelLanguage: locale, primary: locale === 'id' && action.surfaceRole === 'default_primary' });
  }
  const primary = course.learner ?? course.reader ?? course.edition;
  if (!actions.length && !finalEdition) {
    add(idPrefix + t.open, primary, 'id', 'reader', { primary: locale === 'id' });
    if (course.edition !== primary) add(idPrefix + t.download, course.edition, 'id', 'edition');
    if (course.reader !== primary && course.reader !== course.edition) add(idPrefix + t.open, course.reader, 'id', 'reader');
  } else if (!finalEdition) {
    // The admitted whole-file reader actions supersede dated PDF overlay URLs.
    // Retain a distinct native HTML entry when one exists.
    for (const href of [course.learner, course.reader]) if (href && !/\.pdf$/i.test(new URL(safeResourceUrl(href)).pathname)) add(idPrefix + t.open, href, 'id', 'reader');
  }
  for (const tool of learnerToolsByCourseId[course.id] ?? []) {
    if (tool.state !== 'planned') add(tool.label, tool.href, 'id', 'tool', { labelLanguage: 'id' });
  }
  for (const tool of capabilityTools.filter(row=>row.courseId===course.id)) {
    add(tool.label, tool.href, tool.contentLanguage, 'tool', {labelLanguage:'id', capabilityToolId:tool.tool_id,
      bytes:tool.page.bytes, sha256:tool.page.sha256, primary:false, scope:tool.scope, limitations:tool.limitations,
      note:locale==='id' ? tool.scope+'. 72 latihan inti; 3 latihan menunggu prasyarat tambahan. '+tool.limitations.join(' ') : '14 units, 75 exercises (72 core; 3 need additional prerequisites), 4 labs. Indonesian material; no code execution or automatic grading. Linked lessons need a connection or a separate download.'});
  }
  const delivery = learnerDeliveryByCourseId[course.id];
  for (const row of supplementalReaders.filter(item => item.courseId === course.id)) {
    add(idPrefix + row.labels[locale], row.href, row.contentLanguage, row.kind, {
      supplementalReaderId: row.id, format: row.format, bytes: row.bytes, sha256: row.sha256,
      primary: false, offlineAfterDownload: row.offlineAfterDownload, note: row.notes[locale],
    });
  }
  for (const [field, name] of [['portable_html', 'HTML'], ['epub', 'EPUB']]) {
    const item = delivery?.[field];
    if (item?.status === 'verified') add(idPrefix + t.download + ' ' + name, item.url, 'id', field, { bytes: item.bytes });
  }
  for (const supplement of course.supplements ?? []) {
    if (finalEdition?.supersededSupplementIds.includes(supplement.id)) continue;
    if (actions.some((action) => action.href === supplement.url || action.sha256 === supplement.sha256)) continue;
    const machineArchive = supplement.resourceType === 'reference' && /(?:backend|sumber)/i.test(supplement.title) && !/HTML|pembaca|paket lengkap/i.test(supplement.title);
    add(supplement.title, supplement.url, 'id', machineArchive ? 'source-archive' : 'companion', { labelLanguage: 'id', supplementId: supplement.id, sha256: supplement.sha256 ?? null });
  }
  add(t.archive + (locale === 'en' ? ' — Indonesian edition' : ''), finalEdition?.archive ?? course.zenodo, 'id', 'archive');
  add(t.source + (locale === 'en' ? ' — Indonesian edition' : ''), finalEdition?.repository ?? course.repository, 'id', 'repository');
  // These indices are shared metadata, not an English translation of course prose.
  add(t.sharedBackend, 'backend/index.html', 'und', 'backend');
  for (const source of additionalOriginalSources[course.id] ?? []) {
    const existing = rows.find(row => row.href === safeResourceUrl(source.href));
    if (existing) Object.assign(existing, {origin:source.origin});
    else add(source.label, source.href, source.contentLanguage, 'HTML', {origin:source.origin, labelLanguage:source.contentLanguage, primary:false});
  }
  return rows;
}
export function isOriginalSource(row) {
  return ['upstream-original', 'program-original'].includes(row.origin);
}
export function contentLanguageName(code, locale) {
  if (code === 'und') return locale === 'id' ? 'metadata bersama' : 'shared metadata';
  if (code === 'id') return 'Bahasa Indonesia';
  if (code === 'en') return 'English';
  try { return new Intl.DisplayNames([locale], {type:'language'}).of(code) ?? code; }
  catch { return code; }
}
export function renderResourceLinks(course, locale) {
  const t = interfaceCopy[locale];
  const rows = resourceBindings(course, locale);
  const preferred = rows.filter((row) => row.contentLanguage === locale && !['repository', 'archive', 'source-archive'].includes(row.kind));
  const originals = rows.filter(row => isOriginalSource(row) && !preferred.includes(row));
  const other = rows.filter((row) => !preferred.includes(row) && !originals.includes(row));
  const link = (row) => '<a class="resource-link' + (row.primary ? ' primary' : '') + '" href="' + escapeMarkup(row.href)
    + '" data-content-language="' + row.contentLanguage + '" hreflang="' + row.contentLanguage
    + '"' + (row.actionId ? ' data-reader-action="' + escapeMarkup(row.actionId) + '"' : '')
    + (row.editionResourceId ? ' data-edition-resource="' + escapeMarkup(row.editionResourceId) + '"' : '')
    + (row.capabilityToolId ? ' data-capability-tool="' + escapeMarkup(row.capabilityToolId) + '"' : '')
    + (row.supplementalReaderId ? ' data-supplemental-reader="' + escapeMarkup(row.supplementalReaderId) + '"' : '')
    + (isOriginalSource(row) ? ' data-original-source="' + row.origin + '"' : '')
    + '>' + (isOriginalSource(row) ? '<strong>' + (locale === 'id' ? 'Sumber asli' : 'Original source') + '</strong>' : '')
    + '<span lang="' + row.labelLanguage + '">' + escapeMarkup(row.label) + '</span><small>' + escapeMarkup(row.format ?? (row.actionId ? 'PDF' : row.kind))
    + ' · <span lang="' + (['en','id'].includes(row.contentLanguage) ? row.contentLanguage : locale) + '">' + escapeMarkup(contentLanguageName(row.contentLanguage, locale)) + '</span>'
    + (row.offlineAfterDownload ? ' · ' + (locale === 'id' ? 'Luring setelah diunduh' : 'Offline after download') : '') + '</small></a>'
    + (row.note ? '<p class="footnote" lang="'+locale+'">'+escapeMarkup(row.note)+'</p>' : '');
  return (preferred.length ? preferred.map(link).join('') : '<p class="binding-note">' + escapeMarkup(t.noPrimary) + '</p>')
    + originals.map(link).join('')
    + (other.length ? '<details class="resource-details"><summary>' + escapeMarkup(locale === 'en' ? t.otherLanguage + ' / ' + t.sharedBackend : t.companion + ' / ' + t.source)
      + '</summary><div class="resource-list">' + other.map(link).join('') + '</div></details>' : '');
}
export function renderCourseCard(course, locale, evaluation = null) {
  const t = interfaceCopy[locale], c = coursePresentation(course, locale);
  const following = interfaceCourses.filter((row) => row.prerequisites.includes(course.id));
  const courseLink = (id) => {
    const row = interfaceCourses.find((item) => item.id === id);
    return '<a href="#course-' + id + '" data-course-link="' + id + '">' + id + ' — ' + escapeMarkup(coursePresentation(row, locale).title) + '</a>';
  };
  const statuses = { completed: t.completedByYou, eligible: t.ready, eligible_with_waiver: t.waiverReady, blocked: t.missing };
  const learner = evaluation ? '<div class="course-progress"><p>' + escapeMarkup(statuses[evaluation.status])
    + (evaluation.missingPrerequisiteIds.length ? ' · ' + evaluation.missingPrerequisiteIds.join(', ') : '')
    + '</p><label><input type="checkbox" data-completion="' + course.id + '"' + (evaluation.status === 'completed' ? ' checked' : '') + '> ' + t.done + '</label></div>' : '';
  return '<article class="course-card" id="course-' + course.id + '" data-course="' + course.id + '" tabindex="-1">'
    + '<div class="card-top"><span class="course-code">' + course.id + '</span><span>' + escapeMarkup(c.topic) + '</span></div>'
    + '<h3>' + escapeMarkup(c.title) + '</h3><p>' + escapeMarkup(c.purpose) + '</p>' + learner
    + '<div class="course-edges"><h4>' + t.prereqs + '</h4>' + (course.prerequisites.length ? course.prerequisites.map(courseLink).join('') : '<p>' + t.noPrereqs + '</p>')
    + '<h4>' + t.next + '</h4>' + (following.length ? following.map((row) => courseLink(row.id)).join('') : '<p>' + t.noNext + '</p>') + '</div>'
    + '<details><summary>' + t.details + '</summary><h4>' + t.outcome + '</h4><p>' + escapeMarkup(c.outcome) + '</p></details>'
    + '<div class="resource-list">' + renderResourceLinks(course, locale) + '</div></article>';
}
