import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { interfaceCourses, renderCourseCard } from '../docs/interface/view.js';
import { supplementalReaders } from '../docs/interface/supplemental-readers.js';

const book = JSON.parse(readFileSync(new URL('../docs/human/the-science-of-computing/book.json', import.meta.url)));
test('the book exposes twenty-nine chapters in page order', () => {
  assert.equal(book.chapters.length, 29);
  let previous = 0;
  for (const [index, chapter] of book.chapters.entries()) {
    assert.equal(chapter.number, index + 1);
    assert(chapter.pdf_page > previous && chapter.pdf_page <= book.pages);
    previous = chapter.pdf_page;
  }
  assert.deepEqual(book.chapters.filter(c => c.html).map(c => c.number), [1, 2, 3, 4, 5]);
});
test('the English book is a C110 companion in both interface languages', () => {
  const course = interfaceCourses.find(item => item.id === 'C110');
  const rows = supplementalReaders.filter(item => item.id === 'C110:the-science-of-computing');
  assert.equal(rows.length, 1);
  assert.equal(rows[0].contentLanguage, 'en');
  for (const locale of ['en', 'id']) {
    assert(renderCourseCard(course, locale).includes(rows[0].hrefs[locale]));
  }
});
test('release assets are pinned by size and hash', () => {
  for (const [url, bytes, sha] of [[book.pdf, book.pdf_bytes, book.pdf_sha256], [book.source_zip, book.source_zip_bytes, book.source_zip_sha256]]) {
    assert.match(url, /^https:\/\/github\.com\/KokunoYumeto\/program-matematika-indonesia\/releases\/download\//);
    assert(bytes > 1000000);
    assert.match(sha, /^[0-9a-f]{64}$/);
  }
  assert.equal(book.licence, 'CC BY 4.0');
});
