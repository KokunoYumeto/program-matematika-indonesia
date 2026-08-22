import { readFile, writeFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const outputPath = process.argv[2];
if (!outputPath) throw new Error('Pemakaian: node scripts/export-single-file-site.mjs <output.html>');

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const [sourceHtml, sourceCss, sourceCourses, sourceApp] = await Promise.all([
  readFile(resolve(root, 'docs/index.html'), 'utf8'),
  readFile(resolve(root, 'docs/styles.css'), 'utf8'),
  readFile(resolve(root, 'docs/courses.js'), 'utf8'),
  readFile(resolve(root, 'docs/app.js'), 'utf8')
]);

const coursesScript = sourceCourses.replace(/^export const /gm, 'const ');
const appScript = sourceApp.replace(/^import .*?;\r?\n/, '');
const executable = `${coursesScript}\n${appScript}`.replaceAll('</script>', '<\\/script>');

const standalone = sourceHtml
  .replace('  <link rel="stylesheet" href="styles.css">', `  <style>\n${sourceCss}\n  </style>`)
  .replace('  <script type="module" src="app.js"></script>\n', '')
  .replace('</body>', `  <script>\n${executable}\n  </script>\n</body>`);

if (/href="styles\.css"|src="app\.js"/.test(standalone)) {
  throw new Error('Ekspor mandiri masih memiliki dependensi lokal yang belum ditanamkan.');
}
if (!standalone.includes("const courses = [") || !standalone.includes('const program = Object.freeze({')) {
  throw new Error('Ekspor mandiri kehilangan katalog atau metadata program.');
}

await writeFile(outputPath, standalone, 'utf8');
