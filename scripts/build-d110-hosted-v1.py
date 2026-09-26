"""Stage only the tested D110 consumer; preserve the existing course readers."""
import importlib.util
import json
from pathlib import Path

SCRIPT = Path(__file__).with_name('build-d110-surface-v1.py')
spec = importlib.util.spec_from_file_location('d110', SCRIPT)
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)


def main():
    tests = json.loads((b.BASE / 'tests.json').read_bytes())
    package = json.loads((b.BASE / 'source-package.json').read_bytes())
    assert tests['state'] == package['state'] == 'pass'
    assert tests['counts']['units'] == 2177
    out = b.ROOT / 'docs/backend/d110'
    out.mkdir(parents=True, exist_ok=True)
    outputs = {}
    for f in tests['outputs']:
        payload = (b.BASE / 'portable' / f['path']).read_bytes()
        assert (len(payload), b.sha(payload)) == (f['bytes'], f['sha256'])
        if f['path'] == 'validation.json':
            continue
        if f['path'].endswith('.html'):
            en = '.en.' in f['path']
            label = 'Editable selector source ZIP' if en else 'ZIP sumber pemilih yang dapat disunting'
            # The common reversible navigation overlay includes inline CSS.
            text = payload.decode().replace("style-src 'self';", "style-src 'self' 'unsafe-inline';")
            text = text.replace('</footer>', '<p><a href="d110-selector-editable-source-v1.zip" download>' + label + '</a></p></footer>')
            payload = text.encode()
        outputs[f['path']] = payload
    p = package['package']
    payload = (b.BASE / p['path']).read_bytes()
    assert (len(payload), b.sha(payload)) == (p['bytes'], p['sha256'])
    outputs[p['path']] = payload
    report = {'schema': 'd110-hosted-surface/1', 'state': 'pass', 'counts': tests['counts'],
              'files': [{'path': p, 'bytes': len(v), 'sha256': b.sha(v)} for p, v in outputs.items()],
              'new_translation': False, 'lean_execution': False, 'public_deployment_verified': False,
              'interface_locales': ['id', 'en'],
              'source_scope': 'complete selector source; linked book readers remain in their existing lineages',
              'integration_attribution': {'model': 'gpt-6-astra', 'effort': 'ultra', 'work': 'consumer code and mapping'}}
    outputs['validation.json'] = b.encoded(report)
    for name, payload in outputs.items():
        (out / name).write_bytes(payload)
    print(json.dumps({'state': 'staged', 'course': 'D110', 'files': len(outputs)}))


if __name__ == '__main__':
    main()
