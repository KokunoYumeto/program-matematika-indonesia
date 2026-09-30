import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFile, realpath} from 'node:fs/promises';
import {resolve, sep} from 'node:path';

// Check every current local identity, not just selected course-specific cases.
// Remote citations retain their recorded observation; this is not a new network audit.
export async function validateLocalEvidenceIdentities(root, value) {
  const base = await realpath(root), cache = new Map();
  let facts = 0;
  async function visit(item) {
    if (!item || typeof item !== 'object') return;
    if (!Array.isArray(item)) {
      const path = item.path ?? item.locator;
      if (typeof path === 'string' && /^(backend|docs|schemas|scripts)\//.test(path)
          && typeof item.sha256 === 'string' && Number.isInteger(item.bytes)) {
        assert.ok(!path.includes('\\') && !path.split('/').includes('..'), 'Unsafe local evidence path');
        const target = await realpath(resolve(base, path));
        assert.ok(target.startsWith(base + sep), 'Local evidence escaped package root');
        if (!cache.has(path)) {
          const bytes = await readFile(target);
          cache.set(path, {bytes: bytes.length, sha256: createHash('sha256').update(bytes).digest('hex')});
        }
        assert.deepEqual({bytes:item.bytes,sha256:item.sha256}, cache.get(path), `Local evidence identity drift: ${path}`);
        facts += 1;
      }
    }
    for (const child of Object.values(item)) await visit(child);
  }
  await visit(value);
  return {facts, unique_files:cache.size};
}
