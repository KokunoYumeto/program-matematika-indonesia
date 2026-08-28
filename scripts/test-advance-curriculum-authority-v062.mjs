import assert from 'node:assert/strict';
import { spawn } from 'node:child_process';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const project = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const script = resolve(project, 'scripts/advance-curriculum-authority-v062.mjs');
const fixedArgs = [
  'seed',
  '--record-id', '22150264',
  '--source-commit', 'b4b38489fe90099fcdef98f832dc131bbb76b994',
  '--snapshot-date', '2026-08-28',
  '--record-count', '2479',
  '--dataset-count', '34',
  '--course-count', '40',
  '--reader-surfaces', '155',
  '--web-routes', '43',
  '--identity-crosswalks', '2122',
  '--publication-events', '67',
  '--qa-events', '17',
  '--dry-run',
];

function run(args) {
  return new Promise((accept, reject) => {
    const child = spawn(process.execPath, [script, ...args], {
      cwd: project,
      stdio: ['ignore', 'pipe', 'pipe'],
    });
    let stdout = '';
    let stderr = '';
    child.stdout.on('data', (chunk) => { stdout += chunk; });
    child.stderr.on('data', (chunk) => { stderr += chunk; });
    child.on('error', reject);
    child.on('close', (code) => accept({ code, stdout, stderr }));
  });
}

const first = await run(fixedArgs);
const second = await run(fixedArgs);
assert.equal(first.code, 0, first.stderr);
assert.equal(second.code, 0, second.stderr);
const firstResult = JSON.parse(first.stdout);
const secondResult = JSON.parse(second.stdout);
assert.deepEqual(secondResult, firstResult, 'Repeated v0.62 seed dry-runs differ.');
assert.deepEqual(firstResult, {
  mode: 'seed',
  dry_run: true,
  path: 'backend/authority/catalogs/program-matematika-indonesia-catalog-v0.62.0.json',
  bytes: 61557,
  sha256: 'bbd71bf40f9c9b36fbfa51ec61bbbdabaa0e9a52d004aa189bf7133bac77afd6',
});

const wrongRecord = [...fixedArgs];
wrongRecord[wrongRecord.indexOf('--record-id') + 1] = '22150265';
const rejected = await run(wrongRecord);
assert.notEqual(rejected.code, 0, 'A record ID outside the bound reservation was accepted.');
assert.match(rejected.stderr, /Expected values to be strictly equal|22150264/);

console.log(JSON.stringify({
  result: 'pass',
  deterministic_seed_runs: 2,
  bytes: firstResult.bytes,
  sha256: firstResult.sha256,
  wrong_record_id_rejected: true,
}, null, 2));
