// Links to our removed Zenodo records (410 Gone since Nov 2026) in generated pages.
// A file link becomes the GitHub release copy listed in the successor records (same name; SHA-256 from the
// restored-release readback or the GitHub asset digest, equal to the former identity where that is recorded).
// Any other link to one of our records loses its anchor and keeps its text; a bare URL of such a record in
// page data becomes an empty string. Third-party records (ids below 21,000,000, e.g. The Turing Way) are untouched.
import { readFileSync } from 'node:fs';
import { resolve, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const load = (path) => JSON.parse(readFileSync(resolve(root, path), 'utf8'));
const fileSuccessors = new Map(load('backend/authority/removed-record-file-successors-20261119.json').successors
  .map((row) => [row.name, row.github_url]));
const urlSuccessors = new Map(load('backend/authority/removed-record-url-successors-20261119.json').successors
  .map((row) => [row.from, row.to]));
const OURS = 21_000_000;
const recordUrl = /https?:\/\/(?:www\.)?(?:zenodo\.org\/(?:api\/)?records?\/(\d+)(?:\/files\/([^"'\s<>?#]+)(?:\/content)?)?(?:\?download=1)?|doi\.org\/10\.5281\/zenodo\.(\d+))/g;

function successor(url, record, file) {
  if (Number(record) < OURS) return null;
  if (urlSuccessors.has(url)) return urlSuccessors.get(url);
  if (file) {
    const name = decodeURIComponent(file);
    if (fileSuccessors.has(name)) return fileSuccessors.get(name);
  }
  return '';
}

export function rehomeRemovedRecordLinks(input) {
  const text = Buffer.isBuffer(input) ? input.toString('utf8') : String(input);
  // 1. file links with a verified GitHub copy
  let out = text.replace(recordUrl, (url, record, file, doi) => {
    const next = successor(url, record ?? doi, file);
    return next ? next : url;
  });
  // 2. anchors that still point at one of our removed records: keep the text, drop the link
  out = out.replace(/<a\b[^>]*\bhref=(["'])(https?:\/\/(?:www\.)?(?:zenodo\.org\/(?:api\/)?records?\/(\d+)[^"']*|doi\.org\/10\.5281\/zenodo\.(\d+)[^"']*))\1[^>]*>([\s\S]*?)<\/a>/g,
    (anchor, quote, url, record, doi, inner) => (Number(record ?? doi) < OURS ? anchor : inner));
  // 3. remaining bare URLs of our removed records (page data, plain text)
  out = out.replace(recordUrl, (url, record, file, doi) => (Number(record ?? doi) < OURS ? url : ''));
  return Buffer.isBuffer(input) ? Buffer.from(out, 'utf8') : out;
}

export function countRemovedRecordLinks(input) {
  const text = Buffer.isBuffer(input) ? input.toString('utf8') : String(input);
  return [...text.matchAll(recordUrl)].filter((m) => Number(m[1] ?? m[3]) >= OURS).length;
}
