import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { interfaceCourses, renderCourseCard } from '../docs/interface/view.js';
import { supplementalReaders } from '../docs/interface/supplemental-readers.js';

const book = JSON.parse(readFileSync(new URL('../docs/human/open-data-structures/book.json', import.meta.url)));
test('the book exposes fourteen chapter and exercise routes', () => {
  assert.equal(book.chapters.length, 14);
  for (const [index, chapter] of book.chapters.entries()) {
    assert.equal(chapter.number, index + 1);
    assert(chapter.pdf_page > 0 && chapter.pdf_page <= book.pages);
    assert(chapter.exercise_pdf_page >= chapter.pdf_page && chapter.exercise_pdf_page <= book.pages);
  }
});
test('the English book retains the selected navigation language', () => {
  const course = interfaceCourses.find(item => item.id === 'B80');
  const row = supplementalReaders.filter(item => item.id === 'B80:open-data-structures');
  assert.equal(row.length, 1);
  assert.equal(row[0].contentLanguage, 'en');
  for (const locale of ['en', 'id']) {
    assert(renderCourseCard(course, locale).includes(row[0].hrefs[locale]));
  }
});
test('PDF, cumulative LaTeX and full source ZIP are available together', () => {
  const root = new URL('../docs/human/open-data-structures/', import.meta.url);
  assert(readFileSync(new URL(book.pdf, root)).subarray(0, 5).equals(Buffer.from('%PDF-')));
  const tex = readFileSync(new URL(book.latex, root), 'utf8');
  assert(!/\\include\{/.test(tex));
  assert.equal((tex.match(/\\begin\{Verbatim\}/g) || []).length, 159);
  assert(readFileSync(new URL(book.source_zip, root)).subarray(0, 2).equals(Buffer.from('PK')));
});
