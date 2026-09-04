import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
const root=resolve(dirname(fileURLToPath(import.meta.url)),'..');
for(const [command,script] of [['node','build-b80-capability-v1.mjs'],['python','validate-b80-capability-v1.py'],['node','admit-b80-capability-v1.mjs']]){
  const result=spawnSync(command,[...(command==='python'?['-B']:[]),resolve(root,'scripts',script)],{cwd:root,encoding:'utf8'});
  if(result.stdout)process.stdout.write(result.stdout);if(result.stderr)process.stderr.write(result.stderr);
  assert.equal(result.status,0,script+' failed');
}
