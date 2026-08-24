import assert from 'node:assert/strict';
import { courses } from '../docs/courses.js';

const links = courses.flatMap((course) => ['edition', 'zenodo', 'repository']
  .filter((field) => course[field])
  .map((field) => ({ course: course.id, field, url: course[field] })));
const results = [];

for (const link of links) {
  const response = await fetch(link.url, {
    method: 'GET',
    redirect: 'follow',
    signal: AbortSignal.timeout(30_000),
    headers: { 'user-agent': 'program-matematika-indonesia-link-check/1.0' },
  });
  assert.ok(response.status >= 200 && response.status < 400, `${link.course} ${link.field}: HTTP ${response.status}`);
  await response.body?.cancel();
  results.push({ ...link, status: response.status, resolvedUrl: response.url });
}

console.log(JSON.stringify({ status: 'pass', checked: results.length, links: results }, null, 2));
