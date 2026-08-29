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
const responseCache = new Map();

const wait = (milliseconds) => new Promise((resolvePromise) => setTimeout(resolvePromise, milliseconds));

async function fetchWithBoundedRetry(url) {
  let lastError;
  // Zenodo can return a Retry-After: 60 response while its anonymous
  // download limiter recovers.  Honor that bounded server instruction rather
  // than exhausting the retry budget early and reporting a false failure.
  for (let attempt = 0; attempt < 7; attempt += 1) {
    try {
      const response = await fetch(url, {
        method: 'GET',
        redirect: 'follow',
        signal: AbortSignal.timeout(30_000),
        headers: { 'user-agent': 'program-matematika-indonesia-link-check/1.1' },
      });
      const observed = { status: response.status, resolvedUrl: response.url };
      const retryable = response.status === 429 || response.status >= 500;
      const retryAfter = Number.parseInt(response.headers.get('retry-after') ?? '', 10);
      await response.body?.cancel();
      if (!retryable || attempt === 6) return observed;
      await wait(Number.isInteger(retryAfter) ? Math.min(retryAfter * 1000, 120_000) : Math.min(5000 * (2 ** attempt), 120_000));
    } catch (error) {
      lastError = error;
      if (attempt === 6) throw error;
      await wait(Math.min(5000 * (2 ** attempt), 120_000));
    }
  }
  throw lastError;
}

for (const link of links) {
  const observed = responseCache.get(link.url) ?? await fetchWithBoundedRetry(link.url);
  responseCache.set(link.url, observed);
  if (!(observed.status >= 200 && observed.status < 400) && allowPendingCentral && link.url.startsWith(centralPrefix)) {
    const relative = new URL(link.url).pathname.slice('/program-matematika-indonesia/'.length);
    const localPath = resolve(docsRoot, relative, relative.endsWith('/') ? 'index.html' : '');
    assert.ok(localPath.startsWith(`${docsRoot}${sep}`), `${link.course} ${link.field}: rute lokal keluar dari docs/.`);
    await access(localPath);
    results.push({ ...link, status: 'local-pending-publication', resolvedUrl: observed.resolvedUrl });
    continue;
  }
  assert.ok(observed.status >= 200 && observed.status < 400, `${link.course} ${link.field}: HTTP ${observed.status}`);
  results.push({ ...link, status: observed.status, resolvedUrl: observed.resolvedUrl });
}

console.log(JSON.stringify({ status: 'pass', checked: results.length, links: results }, null, 2));
