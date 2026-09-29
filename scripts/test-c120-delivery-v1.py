"""Structural audit negatives; no network, producer edits or corpus copies."""
import importlib.util
import json
from pathlib import Path

MODULE = Path(__file__).with_name('audit-c120-delivery-v1.py')
spec = importlib.util.spec_from_file_location('c120_audit', MODULE)
audit = importlib.util.module_from_spec(spec)
spec.loader.exec_module(audit)
pinned = {'commit': 'a' * 40, 'tree': 'b' * 40}
manifest_identity = {'bytes': 2, 'sha256': 'c' * 64}
assert audit.deployed_seed(pinned, manifest_identity)['files'] == []
previous = {**pinned, 'state': 'incomplete', 'input_manifest': manifest_identity,
            'anonymous': True, 'ambient_credentials_disabled': True, 'files': []}
assert audit.deployed_seed(pinned, manifest_identity, previous) == previous
for change in [{'state': 'in_progress'}, {'commit': 'd' * 40},
               {'input_manifest': {'bytes': 3, 'sha256': 'c' * 64}}, {'anonymous': False}]:
    try:
        audit.deployed_seed(pinned, manifest_identity, {**previous, **change})
    except AssertionError:
        pass
    else:
        raise AssertionError('Unsafe prior audit was reused')
paths = audit.collect()
learning = json.loads((audit.ROOT / audit.MAP).read_bytes())
first = audit.analyze(paths, learning)
assert first['state'] == 'pass' and first['mathml_count'] == 6283
assert first == audit.analyze(paths, learning), 'Structural replay is not deterministic'
key = 'O005-LEGA-V101-CH03/index.html'
text = paths[key].read_text(encoding='utf-8')
cases = [
    ('language', lambda t: t.replace('lang="id-ID"', 'lang="en"', 1), 'language_or_landmark'),
    ('main', lambda t: t.replace('<main ', '<div ').replace('</main>', '</div>'), 'language_or_landmark'),
    ('duplicate', lambda t: t.replace('</main>', '<span id="isi"></span></main>'), 'duplicate_ids'),
    ('missing_asset', lambda t: t.replace('</main>', '<img src="assets/missing.png" alt="test"></main>'), 'missing_local_target'),
    ('fragment', lambda t: t.replace('</main>', '<a href="#missing">test</a></main>'), 'missing_fragment'),
    ('alt', lambda t: t.replace('</main>', '<img src="assets/missing.png"></main>'), 'missing_alt'),
    ('math_source', lambda t: t.replace('encoding="application/x-tex"', 'encoding="text/plain"', 1), 'math_source_annotation_missing'),
]
for name, change, expected in cases:
    changed = dict(paths)
    changed[key] = audit.BytesWitness(change(text).encode())
    findings = audit.analyze(changed, learning)
    assert findings['state'] == 'findings' and any(r['kind'] == expected for r in findings['findings']), name
changed = dict(paths)
changed.pop(key)
try:
    audit.analyze(changed, learning)
except AssertionError:
    pass
else:
    raise AssertionError('Missing native unit was admitted')
print(json.dumps({'state': 'pass', 'identical_structural_replays': 2, 'negative_cases': len(cases) + 1,
                  'fresh_without_predecessor': True, 'predecessor_negatives': 4,
                  'unit_count': first['unit_count'], 'links': first['local_links_checked']}))
