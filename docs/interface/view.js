import { courses as authorityCourses, topics } from '../courses.js';
import { materializeLiveCourses } from '../live-course-publications.js';
import { learnerDeliveryByCourseId } from '../learner-delivery.js';
import { learnerToolsByCourseId } from '../learner-tools.js';
import { interfaceCopy, topicCopy, englishCourseCopy, englishResources, siteOrigin } from './locales.js';
import { verifiedReaderActions } from './reader-actions.js';

export const interfaceCourses = materializeLiveCourses(authorityCourses);
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
  if (locale === 'en') for (const row of englishResources[course.id] ?? []) {
    add(row.label, row.href, row.contentLanguage, row.kind, { origin: row.origin, primary: rows.length === 0 });
  }
  const idPrefix = locale === 'en' ? 'Bahasa Indonesia — ' : '';
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
  if (!actions.length) {
    add(idPrefix + t.open, primary, 'id', 'reader', { primary: locale === 'id' });
    if (course.edition !== primary) add(idPrefix + t.download, course.edition, 'id', 'edition');
    if (course.reader !== primary && course.reader !== course.edition) add(idPrefix + t.open, course.reader, 'id', 'reader');
  } else {
    // The admitted whole-file reader actions supersede dated PDF overlay URLs.
    // Retain a distinct native HTML entry when one exists.
    for (const href of [course.learner, course.reader]) if (href && !/\.pdf$/i.test(new URL(safeResourceUrl(href)).pathname)) add(idPrefix + t.open, href, 'id', 'reader');
  }
  for (const tool of learnerToolsByCourseId[course.id] ?? []) {
    if (tool.state !== 'planned') add(tool.label, tool.href, 'id', 'tool', { labelLanguage: 'id' });
  }
  const delivery = learnerDeliveryByCourseId[course.id];
  for (const [field, name] of [['portable_html', 'HTML'], ['epub', 'EPUB']]) {
    const item = delivery?.[field];
    if (item?.status === 'verified') add(idPrefix + t.download + ' ' + name, item.url, 'id', field, { bytes: item.bytes });
  }
  for (const supplement of course.supplements ?? []) {
    if (actions.some((action) => action.href === supplement.url || action.sha256 === supplement.sha256)) continue;
    const machineArchive = supplement.resourceType === 'reference' && /(?:backend|sumber)/i.test(supplement.title) && !/HTML|pembaca|paket lengkap/i.test(supplement.title);
    add(supplement.title, supplement.url, 'id', machineArchive ? 'source-archive' : 'companion', { labelLanguage: 'id', supplementId: supplement.id, sha256: supplement.sha256 ?? null });
  }
  add(t.archive + (locale === 'en' ? ' — Indonesian edition' : ''), course.zenodo, 'id', 'archive');
  add(t.source + (locale === 'en' ? ' — Indonesian edition' : ''), course.repository, 'id', 'repository');
  // These indices are shared metadata, not an English translation of course prose.
  add(t.sharedBackend, 'backend/index.html', 'und', 'backend');
  return rows;
}
export function renderResourceLinks(course, locale) {
  const t = interfaceCopy[locale];
  const rows = resourceBindings(course, locale);
  const preferred = rows.filter((row) => row.contentLanguage === locale && !['repository', 'archive', 'source-archive'].includes(row.kind));
  const other = rows.filter((row) => !preferred.includes(row));
  const link = (row) => '<a class="resource-link' + (row.primary ? ' primary' : '') + '" href="' + escapeMarkup(row.href)
    + '" data-content-language="' + row.contentLanguage + '" hreflang="' + row.contentLanguage
    + '"' + (row.actionId ? ' data-reader-action="' + escapeMarkup(row.actionId) + '"' : '') + '><span lang="' + row.labelLanguage + '">' + escapeMarkup(row.label) + '</span><small>' + escapeMarkup(row.actionId ? 'PDF' : row.kind)
    + ' · <span lang="' + (row.contentLanguage === 'und' ? locale : row.contentLanguage) + '">' + (row.contentLanguage === 'id' ? 'Bahasa Indonesia' : row.contentLanguage === 'en' ? 'English' : locale === 'id' ? 'metadata bersama' : 'shared metadata') + '</span>'
    + (row.offlineAfterDownload ? ' · ' + (locale === 'id' ? 'Luring setelah diunduh' : 'Offline after download') : '') + '</small></a>';
  return (preferred.length ? preferred.map(link).join('') : '<p class="binding-note">' + escapeMarkup(t.noPrimary) + '</p>')
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
