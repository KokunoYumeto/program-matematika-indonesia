import { readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const outputPath = process.argv[2];
if (!outputPath) throw new Error('Pemakaian: node scripts/export-single-file-site.mjs <output.html>');

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const [sourceHtml, sourceCss, sourceCourses, sourceOverlay, sourceDelivery, sourceTools, sourceLearnerState, sourceApp] = await Promise.all([
  readFile(resolve(root, 'docs/index.html'), 'utf8'),
  readFile(resolve(root, 'docs/styles.css'), 'utf8'),
  readFile(resolve(root, 'docs/courses.js'), 'utf8'),
  readFile(resolve(root, 'docs/live-course-publications.js'), 'utf8'),
  readFile(resolve(root, 'docs/learner-delivery.js'), 'utf8'),
  readFile(resolve(root, 'docs/learner-tools.js'), 'utf8'),
  readFile(resolve(root, 'docs/learner-state.js'), 'utf8'),
  readFile(resolve(root, 'docs/app.js'), 'utf8')
]);

const coursesScript = sourceCourses
  .replace(/^export const courses =/m, 'const authorityCourses =')
  .replace(/^export const nextCourseIdsById =/m, 'const authorityNextCourseIdsById =')
  .replace(/^export const /gm, 'const ');
const overlayScript = sourceOverlay.replace(/^export (const|function) /gm, '$1 ');
const deliveryScript = sourceDelivery.replace(/^export (const|function) /gm, '$1 ');
const toolsScript = sourceTools
  .replace(/^export (const|function) /gm, '$1 ')
  .replaceAll('"href":"id-ID/courses/A00/latihan/index.html"', '"href":"https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/A00/latihan/index.html"');
const learnerStateScript = sourceLearnerState.replace(/^export (const|function) /gm, '$1 ');
const appScript = sourceApp.replace(/^import[\s\S]*?from ['"][^'"]+['"];\r?\n/gm, '');
if (/^\s*import\s/m.test(appScript)) {
  throw new Error('Ekspor mandiri masih memiliki import JavaScript yang belum dihapus.');
}
const executable = `${coursesScript}\n${overlayScript}\n${deliveryScript}\n${toolsScript}\n${learnerStateScript}\n${appScript}`
  .replaceAll('</script>', '<\\/script>');

const standalone = sourceHtml
  .replace('  <link rel="stylesheet" href="styles.css">', `  <style>\n${sourceCss}\n  </style>`)
  .replace('  <script type="module" src="app.js"></script>\n', '')
  .replace('href="peta-belajar-luring.html"', 'href="#katalog"')
  .replace('</body>', `  <script>\n${executable}\n  </script>\n</body>`);

if (/href="styles\.css"|src="app\.js"|from ['"]\.\/learner-delivery\.js['"]/.test(standalone)) {
  throw new Error('Ekspor mandiri masih memiliki dependensi lokal yang belum ditanamkan.');
}
if (!standalone.includes('const authorityCourses = Object.freeze([') || !standalone.includes('const program = Object.freeze({')) {
  throw new Error('Ekspor mandiri kehilangan katalog atau metadata program.');
}
if (!standalone.includes('const liveCoursePublications = Object.freeze({')
  || !standalone.includes('const learnerDeliveryByCourseId = Object.freeze(')
  || !standalone.includes('const learnerToolsByCourseId = Object.freeze(')
  || !standalone.includes('const courses = materializeLiveCourses(authorityCourses);')
  || !standalone.includes("const LEARNER_STATE_STORAGE_KEY = 'program-matematika-indonesia/learner-state/v1';")) {
  throw new Error('Ekspor mandiri kehilangan overlay publikasi langsung atau modul status pelajar.');
}
if ((standalone.match(/data-static-course-id=/g) ?? []).length !== 40) {
  throw new Error('Ekspor mandiri kehilangan fallback statis 40 mata kuliah.');
}
if (!standalone.includes('"href":"https://kokunoyumeto.github.io/program-matematika-indonesia/id-ID/courses/A00/latihan/index.html"')
  || standalone.includes('"href":"id-ID/courses/A00/latihan/index.html"')) {
  throw new Error('Ekspor mandiri harus menautkan alat A00 ke rute Pages absolut yang dapat dipakai.');
}

await writeFile(outputPath, standalone, 'utf8');
