import assert from 'node:assert/strict';
import { access } from 'node:fs/promises';
import { dirname, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';
import { courses as authorityCourses } from '../docs/courses.js';
import { materializeLiveCourses } from '../docs/live-course-publications.js';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const docsRoot = resolve(root, 'docs');
const centralPrefix = 'https://kokunoyumeto.github.io/program-matematika-indonesia/';
const allowPendingCentral = process.env.ALLOW_PENDING_CENTRAL === '1';
const courses = materializeLiveCourses(authorityCourses);
const links = courses.flatMap((course) => {
  const primary = ['learner', 'reader', 'edition', 'zenodo', 'repository', 'release']
    .filter((field) => course[field])
    .map((field) => ({ course: course.id, field, url: course[field] }));
  const supplements = (course.supplements ?? [])
    .map(({ title, url }) => ({ course: course.id, field: `supplement:${title}`, url }));
  return [...primary, ...supplements];
});
const results = [];

for (const link of links) {
  const response = await fetch(link.url, {
    method: 'GET',
    redirect: 'follow',
    signal: AbortSignal.timeout(30_000),
    headers: { 'user-agent': 'program-matematika-indonesia-link-check/1.0' },
  });
  if (!(response.status >= 200 && response.status < 400) && allowPendingCentral && link.url.startsWith(centralPrefix)) {
    const relative = new URL(link.url).pathname.slice('/program-matematika-indonesia/'.length);
    const localPath = resolve(docsRoot, relative, relative.endsWith('/') ? 'index.html' : '');
    assert.ok(localPath.startsWith(`${docsRoot}${sep}`), `${link.course} ${link.field}: rute lokal keluar dari docs/.`);
    await access(localPath);
    await response.body?.cancel();
    results.push({ ...link, status: 'local-pending-publication', resolvedUrl: response.url });
    continue;
  }
  assert.ok(response.status >= 200 && response.status < 400, `${link.course} ${link.field}: HTTP ${response.status}`);
  await response.body?.cancel();
  results.push({ ...link, status: response.status, resolvedUrl: response.url });
}

console.log(JSON.stringify({ status: 'pass', checked: results.length, links: results }, null, 2));
