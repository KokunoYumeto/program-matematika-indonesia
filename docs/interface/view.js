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
  if (locale === 'en') {
    const copy = englishCourseCopy[course.id];
    if (!copy || !topicCopy[course.topic]) throw new Error('Missing English presentation: ' + course.id);
    return { title: copy[0], purpose: copy[1], outcome: copy[2], topic: topicCopy[course.topic] };
  }
  throw new Error('Unsupported interface locale without a complete localized bundle: ' + locale);
}
export const learnerAccessRoles = Object.freeze([
  'hosted-reader', 'authoritative-original', 'offline-copy', 'companion', 'tool',
  'repository', 'preservation-record', 'source-package', 'backend',
]);
const learnerAccessRoleSet = new Set(learnerAccessRoles);
const isProgramOriginalCourse = (courseId) => (additionalOriginalSources[courseId] ?? []).some(row => row.origin === 'program-original');
export function resourceBindings(course, locale) {
  const t = interfaceCopy[locale];
  if (!t) throw new Error('Unsupported interface locale without a complete localized bundle: ' + locale);
  const rows = [];
  const add = (label, href, contentLanguage, kind = 'link', extra = {}) => {
    if (!href) return;
    const normalizedHref = safeResourceUrl(href);
    const candidate = { label, labelLanguage: locale, href: normalizedHref, contentLanguage, kind, ...extra };
    if (!learnerAccessRoleSet.has(candidate.accessRole)) throw new Error('Missing or invalid learner access role: ' + course.id + ' ' + normalizedHref);
    const existing = rows.find((row) => row.href === normalizedHref && row.accessRole === candidate.accessRole);
    if (existing) return;
    const sameUrl = rows.filter((row) => row.href === normalizedHref);
    if (sameUrl.length) {
      const roles = new Set([...sameUrl.map((row) => row.accessRole), candidate.accessRole]);
      const isProgramOriginalDualRole = candidate.origin === 'program-original'
        && roles.size === 2 && roles.has('hosted-reader') && roles.has('authoritative-original');
      if (!isProgramOriginalDualRole) throw new Error('One URL cannot have incompatible learner access roles: ' + course.id + ' ' + normalizedHref);
    }
    rows.push(candidate);
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
        offlineAfterDownload:row.offlineAfterDownload, primary:locale === 'id' && row.primary,
        accessRole:row.kind === 'portable_html' ? 'offline-copy' : row.kind === 'reader' ? 'hosted-reader' : 'companion',
        authorityRole:'program-edition', relationToSource:isProgramOriginalCourse(course.id) ? 'original-work' : 'translation-of'});
  }
  const actions = verifiedReaderActions.filter((action) => action.courseId === course.id);
  const actionNames = locale === 'id'
    ? { textbook: 'Buku teks', problembook: 'Buku soal dan penyelesaian', combined_textbook_problembook: 'Buku gabungan teks dan soal' }
    : { textbook: 'Textbook', problembook: 'Problems and solutions', combined_textbook_problembook: 'Combined textbook and problems' };
  for (const action of actions) {
    const { label: sourceLabel, ...metadata } = action;
    add(idPrefix + actionNames[action.role] + ' — ' + action.pages + (locale === 'id' ? ' halaman' : ' pages'), action.href, 'id', action.role === 'problembook' ? 'companion' : 'reader',
      { ...metadata, labelLanguage: locale, primary: locale === 'id' && action.surfaceRole === 'default_primary',
        accessRole:action.role === 'problembook' ? 'companion' : 'hosted-reader', authorityRole:'program-edition',
        relationToSource:isProgramOriginalCourse(course.id) ? 'original-work' : 'translation-of' });
  }
  const primary = course.learner ?? course.reader ?? course.edition;
  if (!actions.length && !finalEdition) {
    add(idPrefix + t.open, primary, 'id', 'reader', { primary: locale === 'id', accessRole:'hosted-reader', authorityRole:'program-edition', relationToSource:isProgramOriginalCourse(course.id) ? 'original-work' : 'translation-of' });
    if (course.edition !== primary) {
      const editionIsArchive = /\.zip$/i.test(new URL(safeResourceUrl(course.edition)).pathname);
      add(idPrefix + t.download, course.edition, 'id', 'edition', {accessRole:editionIsArchive ? 'offline-copy' : 'hosted-reader', authorityRole:'program-edition', relationToSource:editionIsArchive ? 'offline-copy-of' : isProgramOriginalCourse(course.id) ? 'original-work' : 'translation-of'});
    }
    if (course.reader !== primary && course.reader !== course.edition) add(idPrefix + t.open, course.reader, 'id', 'reader', {accessRole:'hosted-reader', authorityRole:'program-edition', relationToSource:isProgramOriginalCourse(course.id) ? 'original-work' : 'translation-of'});
  } else if (!finalEdition) {
    // The admitted whole-file reader actions supersede dated PDF overlay URLs.
    // Retain a distinct native HTML entry when one exists.
    for (const href of [course.learner, course.reader]) if (href && !/\.pdf$/i.test(new URL(safeResourceUrl(href)).pathname)) add(idPrefix + t.open, href, 'id', 'reader', {accessRole:'hosted-reader', authorityRole:'program-edition', relationToSource:isProgramOriginalCourse(course.id) ? 'original-work' : 'translation-of'});
  }
  for (const tool of learnerToolsByCourseId[course.id] ?? []) {
    if (tool.state !== 'planned') add(tool.label, tool.href, 'id', 'tool', { labelLanguage: 'id', accessRole:'tool', authorityRole:'program-edition', relationToSource:'supports' });
  }
  for (const tool of capabilityTools.filter(row=>row.courseId===course.id)) {
    const englishCapability = tool.contentLanguage === 'en';
    const note = englishCapability
      ? (locale === 'id'
          ? 'Kapabilitas berbahasa Inggris. Buka alat tertaut untuk cakupan, bukti, dan batas khusus sumbernya.'
          : tool.scope.replace(/[.\s]+$/u, '') + '. ' + tool.limitations.join(' '))
      : (locale === 'id'
          ? tool.scope.replace(/[.\s]+$/u, '') + '. ' + tool.limitations.join(' ')
          : 'Indonesian-language capability. Open the linked tool for its source-specific scope, evidence and limitations.');
    add(tool.label, tool.href, tool.contentLanguage, 'tool', {labelLanguage:englishCapability?'en':'id', capabilityToolId:tool.tool_id,
      bytes:tool.page.bytes, sha256:tool.page.sha256, primary:false, scope:tool.scope, limitations:tool.limitations,
      note, accessRole:'tool', authorityRole:'program-edition', relationToSource:'supports'});
  }
  const delivery = learnerDeliveryByCourseId[course.id];
  for (const row of supplementalReaders.filter(item => item.courseId === course.id)) {
    add(idPrefix + row.labels[locale], row.href, row.contentLanguage, row.kind, {
      supplementalReaderId: row.id, format: row.format, bytes: row.bytes, sha256: row.sha256,
      primary: false, offlineAfterDownload: row.offlineAfterDownload, note: row.notes[locale],
      accessRole:row.offlineAfterDownload ? 'offline-copy' : 'companion', authorityRole:'program-edition',
      relationToSource:row.offlineAfterDownload ? 'offline-copy-of' : 'companion-to',
    });
  }
  for (const [field, name] of [['portable_html', 'HTML'], ['epub', 'EPUB']]) {
    const item = delivery?.[field];
    if (item?.status === 'verified') add(idPrefix + t.download + ' ' + name, item.url, 'id', field, { bytes: item.bytes, accessRole:'offline-copy', authorityRole:'program-edition', relationToSource:'offline-copy-of' });
  }
  for (const supplement of course.supplements ?? []) {
    if (finalEdition?.supersededSupplementIds.includes(supplement.id)) continue;
    if (actions.some((action) => action.href === supplement.url || action.sha256 === supplement.sha256)) continue;
    if (rows.some(row => row.href === safeResourceUrl(supplement.url))) continue;
    const machineArchive = supplement.resourceType === 'reference' && /(?:backend|sumber)/i.test(supplement.title) && !/HTML|pembaca|paket lengkap/i.test(supplement.title);
    add(supplement.title, supplement.url, 'id', machineArchive ? 'source-archive' : 'companion', { labelLanguage: 'id', supplementId: supplement.id, sha256: supplement.sha256 ?? null,
      accessRole:machineArchive ? 'source-package' : 'companion', authorityRole:'program-edition', relationToSource:machineArchive ? 'supports' : 'companion-to' });
  }
  add(t.archive + (locale === 'en' ? ' — Indonesian edition' : ''), finalEdition?.archive ?? course.zenodo, 'id', 'archive', {accessRole:'preservation-record', authorityRole:'program-edition', relationToSource:'preserves'});
  add(t.source + (locale === 'en' ? ' — Indonesian edition' : ''), finalEdition?.repository ?? course.repository, 'id', 'repository', {accessRole:'repository', authorityRole:'program-edition', relationToSource:'supports'});
  // These indices are shared metadata, not an English translation of course prose.
  add(t.sharedBackend, 'backend/index.html', 'und', 'backend', {accessRole:'backend', authorityRole:'program-edition', relationToSource:'indexes'});
  for (const source of additionalOriginalSources[course.id] ?? []) {
    add(source.label, source.href, source.contentLanguage, 'HTML', {...source, labelLanguage:source.contentLanguage, primary:false});
  }
  return rows;
}
export function isOriginalSource(row) {
  return row.accessRole === 'authoritative-original' || ['upstream-original', 'program-original'].includes(row.origin);
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
  const hostedReaders = rows.filter((row) => row.contentLanguage === locale && row.accessRole === 'hosted-reader');
  const offlineCopies = rows.filter((row) => row.contentLanguage === locale && row.accessRole === 'offline-copy');
  const hosted = [...hostedReaders, ...offlineCopies];
  const originals = rows.filter(row => row.accessRole === 'authoritative-original');
  const preferred = rows.filter((row) => row.contentLanguage === locale && !hosted.includes(row) && !originals.includes(row)
    && !['repository', 'preservation-record', 'source-package', 'backend'].includes(row.accessRole));
  const other = rows.filter((row) => !hosted.includes(row) && !preferred.includes(row) && !originals.includes(row));
  const link = (row) => '<a class="resource-link' + (row.primary ? ' primary' : '') + '" href="' + escapeMarkup(row.href)
    + '" data-content-language="' + row.contentLanguage + '" hreflang="' + row.contentLanguage
    + '" data-access-role="' + escapeMarkup(row.accessRole)
    + '"' + (row.actionId ? ' data-reader-action="' + escapeMarkup(row.actionId) + '"' : '')
    + (row.editionResourceId ? ' data-edition-resource="' + escapeMarkup(row.editionResourceId) + '"' : '')
    + (row.capabilityToolId ? ' data-capability-tool="' + escapeMarkup(row.capabilityToolId) + '"' : '')
    + (row.supplementalReaderId ? ' data-supplemental-reader="' + escapeMarkup(row.supplementalReaderId) + '"' : '')
    + (isOriginalSource(row) ? ' data-original-source="' + row.origin + '"' : '')
    + '>'
    + '<span lang="' + row.labelLanguage + '">' + escapeMarkup(row.label) + '</span><small>' + escapeMarkup(row.format ?? (row.actionId ? 'PDF' : row.kind))
    + ' · <span lang="' + (['en','id'].includes(row.contentLanguage) ? row.contentLanguage : locale) + '">' + escapeMarkup(contentLanguageName(row.contentLanguage, locale)) + '</span>'
    + (row.offlineAfterDownload ? ' · ' + (locale === 'id' ? 'Luring setelah diunduh' : 'Offline after download') : '') + '</small></a>'
    + (row.note ? '<p class="footnote" lang="'+locale+'">'+escapeMarkup(row.note)+'</p>' : '');
  const group = (role, title, body) => '<section class="resource-group" data-access-group="' + role + '"><h4>' + escapeMarkup(title) + '</h4>' + body + '</section>';
  return group('hosted-reader', t.hostedReader, (hostedReaders.length ? '' : '<p class="binding-note">' + escapeMarkup(t.noHostedReader) + '</p>') + hosted.map(link).join(''))
    + group('authoritative-original', t.authoritativeOriginal, originals.length ? originals.map(link).join('') : '<p class="binding-note">' + escapeMarkup(t.noAuthoritativeOriginal) + '</p>')
    + preferred.map(link).join('')
    + (other.length ? '<details class="resource-details"><summary>' + escapeMarkup(locale === 'en' ? t.otherLanguage + ' / ' + t.sharedBackend : t.companion + ' / ' + t.source)
      + '</summary><div class="resource-list">' + other.map(link).join('') + '</div></details>' : '');
}
export function learnerAccessProjection(course, locale) {
  const rows = resourceBindings(course, locale);
  const normalize = (row) => ({
    access_role: row.accessRole, authority_role: row.authorityRole ?? 'unspecified',
    relation_to_source: row.relationToSource ?? 'unspecified', content_language: row.contentLanguage,
    media_type: row.format ?? (row.actionId ? 'PDF' : row.kind), url: row.href,
    label: row.label, label_language: row.labelLanguage, primary: Boolean(row.primary),
    offline_after_download: Boolean(row.offlineAfterDownload), bytes: row.bytes ?? null, sha256: row.sha256 ?? null,
  });
  const hosted = rows.filter(row => row.contentLanguage === locale && row.accessRole === 'hosted-reader').map(normalize);
  const originals = rows.filter(row => row.accessRole === 'authoritative-original').map(normalize);
  const offline = rows.filter(row => row.contentLanguage === locale && row.accessRole === 'offline-copy').map(normalize);
  return {
    course_id: course.id, interface_locale: locale, locale_route: siteOrigin + locale + '/#course-' + course.id,
    program_hosted_reader: {status: hosted.length ? 'available' : 'not-yet-hosted', resources: hosted},
    authoritative_original: {status: originals.length ? 'available' : 'unavailable', resources: originals},
    offline_copies: offline,
    alternatives: rows.filter(row => !hosted.some(item => item.url === row.href) && !originals.some(item => item.url === row.href) && !offline.some(item => item.url === row.href)).map(normalize),
  };
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
