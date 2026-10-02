"""Read-only source/output identity preflight for D100's three native readers.

This does not launch the native build, infer canon approval, or change coverage.
It identifies the exact existing production inputs for an isolated replay.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
READERS = {
    'classical': 'build/reader-id-corr1/BUILD_RECEIPT.json',
    'bgk': 'build/reader-bgk-id-corr1/BUILD_RECEIPT.json',
    'original': 'build/reader-original-bridge-id-corr1/BUILD_RECEIPT.json',
}

def inside(root, relative):
    raw = Path(relative)
    if raw.is_absolute() or '..' in raw.parts or ':' in relative:
        raise ValueError('Non-relative native input')
    result = (root / raw).resolve()
    if not result.is_relative_to(root):
        raise ValueError('Native input escapes the read-only root')
    return result

def identity(path):
    before = path.stat()
    digest, size = hashlib.sha256(), 0
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(block)
            size += len(block)
    after = path.stat()
    if (before.st_size, before.st_mtime_ns) != (after.st_size, after.st_mtime_ns):
        raise ValueError('Input changed during observation')
    return {'bytes': size, 'sha256': digest.hexdigest()}

def audit(native):
    native = native.resolve()
    report = {
        'schema': 'd100-native-production-preflight/1',
        'checked_at': datetime.now(timezone.utc).isoformat(),
        'course_id': 'D100', 'locale': 'id-ID', 'readers': [],
        'scope': 'Exact inputs and outputs named by the three native corrected-edition build receipts.',
        'producer_files_changed': False, 'native_build_executed': False,
        'semantic_canon_review': False, 'whole_backend_complete': False,
        'integration_provenance': 'OpenAI Codex gpt-6-astra, Ultra',
    }
    cache, failures = {}, []
    for lane, rel in READERS.items():
        path = inside(native, rel)
        receipt = json.loads(path.read_bytes())
        if receipt.get('status') != 'PASS':
            raise ValueError('Native reader has no passing receipt: ' + lane)
        result = {'lane': lane, 'receipt': {'path': rel, **identity(path)}, 'files': []}
        for kind in ('inputs', 'outputs'):
            rows = receipt[kind]
            if not rows:
                raise ValueError('Missing receipt file scope: ' + lane + ':' + kind)
            result[kind + '_count'] = len(rows)
            for row in rows:
                relative = row['path']
                expected = {k: row[k] for k in ('bytes', 'sha256')}
                try:
                    source = inside(native, relative)
                    # Re-read metadata to detect a changed file when a path repeats.
                    stamp = (source.stat().st_size, source.stat().st_mtime_ns)
                    key = (relative, stamp)
                    actual = cache.setdefault(key, identity(source)) if key not in cache else cache[key]
                    state = 'match' if actual == expected else 'identity_drift'
                except (OSError, ValueError) as error:
                    actual, state = None, type(error).__name__
                observation = {'kind': kind, 'path': relative, 'expected': expected,
                               'actual': actual, 'state': state}
                result['files'].append(observation)
                if state != 'match':
                    failures.append({'lane': lane, **observation})
        report['readers'].append(result)
    report.update(state='identity_preflight_pass' if not failures else 'identity_gaps',
                  unique_files_observed=len(cache), failures=failures,
                  input_references=sum(r['inputs_count'] for r in report['readers']),
                  output_references=sum(r['outputs_count'] for r in report['readers']))
    report['next_action'] = (
        'Inspect the exact native builders and their runtime/source closure, then replay in an isolated integration-owned tree. '
        'A matching stored receipt is not itself a new build or proof that all runtime dependencies are packaged.'
        if not failures else
        'Resolve the enumerated source/output identity differences against the native edition before constructing the isolated replay. '
        'Do not rewrite producer files or infer translation damage from a hash difference alone.')
    return report

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--native-root', type=Path, default=ROOT.parent / 'algebraic-geometry-bridge-id')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(ROOT.resolve()):
        raise ValueError('Report must stay in the integration checkout')
    report = audit(args.native_root)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({k: report[k] for k in ['state', 'unique_files_observed', 'input_references', 'output_references', 'native_build_executed']}))
    print(json.dumps({'failures': len(report['failures']), 'by_reader': [
        {'lane': r['lane'], 'inputs': r['inputs_count'], 'outputs': r['outputs_count']} for r in report['readers']]}))
