import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtemp, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { dirname, join, resolve, sep } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const temporaryParent = resolve(tmpdir());
const replayRoot = await mkdtemp(join(temporaryParent, 'course-capsule-v1-'));
assert.ok(replayRoot.startsWith(temporaryParent + sep), 'Replay root escaped the system temp directory.');
const a = join(replayRoot, 'a');
const b = join(replayRoot, 'b');

const run = (script, args = []) => {
  const result = spawnSync(process.execPath, [resolve(project, 'scripts', script), ...args], {
    cwd: project,
    encoding: 'utf8',
    stdio: 'pipe',
  });
  if (result.stdout) process.stdout.write(result.stdout);
  if (result.stderr) process.stderr.write(result.stderr);
  assert.equal(result.status, 0, script + ' failed with exit code ' + result.status + '.');
};

try {
  run('build-course-capsules-v1.mjs', ['--output-root=' + a]);
  run('build-course-capsules-v1.mjs', ['--output-root=' + b]);
  run('validate-course-capsules-v1.mjs', ['--output-root=' + a, '--peer-output-root=' + b]);
  run('validate-course-capsules-v1.mjs', ['--output-root=' + b, '--peer-output-root=' + a]);
  run('build-course-capsules-v1.mjs');
  run('validate-course-capsules-v1.mjs', ['--peer-output-root=' + a]);
  console.log(JSON.stringify({ status: 'pass', deterministic_replay_builds: 2, canonical_build: 'validated' }, null, 2));
} finally {
  assert.ok(replayRoot.startsWith(temporaryParent + sep), 'Refusing unsafe replay cleanup.');
  await rm(replayRoot, { recursive: true, force: true });
}
