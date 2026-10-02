"""Bind six real isolated renders into the shared D100 production audit."""
import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('d100_replay_binding', ROOT / 'scripts/replay-d100-native-html-v1.py')
r = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)
DEST = ROOT / 'backend/course-capsule-v1/adapters/d100-native-production-v1'
EXPECTED = {'classical': r.common.EXPECTED_HTML, **{key: value['html'] for key, value in r.LANES.items()}}
COUNTS = {'classical': 329, 'bgk': 269, 'original': 170}


def bind(paths):
    pending, readers = {}, []
    for lane, directory in paths.items():
        directory = directory.resolve()
        r.require(directory.is_relative_to(ROOT / 'work'), 'Only integration-owned replay evidence is accepted')
        data = (directory / 'REPLAY.json').read_bytes()
        proof = json.loads(data)
        r.require(proof['state'] == 'pass' and proof['course_id'] == 'D100', 'Replay not passing D100')
        r.require(proof['locale'] == 'id-ID' and proof['producer_writes'] is False, 'Replay locale/write scope changed')
        r.require(proof['tex_launched'] is False and proof['pdf_replayed'] is False and
                  proof['whole_backend_complete'] is False, 'HTML-only evidence cannot be promoted')
        r.require(proof['byte_identical_to_native'] is True and proof['runtime_producer_sources_used'] is False,
                  'Replay was not isolated/native-identical')
        r.require([row['label'] for row in proof['runs']] == ['a', 'b'], 'Two distinct isolated runs required')
        for run in proof['runs']:
            r.require(run['html'] == EXPECTED[lane] and run['source_files'] == COUNTS[lane], 'Reader scope drift')
            r.require(run['input_bytes_unchanged'] is True, 'Input mutation')
            actual = r.fact(directory / run['label'] / 'isolated-html/index.html')
            r.require(actual == run['html'], 'Actual isolated output differs from receipt')
        supplement = proof['runtime_supplement']
        r.require(r.fact(r.exact_path(ROOT, supplement['path'])) == {k: supplement[k] for k in ('bytes', 'sha256')},
                  'Runtime supplement changed')
        r.require(b'Users\\' not in data and b'Users/' not in data, 'Private path in public replay receipt')
        name = lane + '-html-replay.json'
        pending[name] = data
        readers.append({'lane': lane, 'source_units': 0 if lane == 'original' else 30,
                        'companion_units': 32 if lane == 'original' else 0,
                        'inputs_per_run': COUNTS[lane], 'html': EXPECTED[lane],
                        'proof': {'path': name, **r.fact(directory / 'REPLAY.json')}})
    result = {'schema': 'd100-native-html-production-evidence/1', 'course_id': 'D100', 'locale': 'id-ID',
        'state': 'verified_html_only', 'readers': readers, 'isolated_builds': 6,
        'source_units': 60, 'companion_units': 32, 'runtime_dependencies_added': 28,
        'native_data_export_replayed': False, 'fresh_pdf_build': False,
        'semantic_canon_review': False, 'whole_backend_complete': False,
        'note_id': 'Tiga pembaca HTML Bahasa Indonesia dibangun ulang masing-masing dua kali dari masukan terisolasi; semua hasil identik dengan edisi asli. Cakupan: 60 unit sumber dan 32 unit pendamping, bukan 92 unit sumber. Sebanyak 28 dependensi yang hilang dari daftar historis diikat secara retrospektif. Ekspor data backend asli, produksi PDF, dan peninjauan semantik kanon tetap memerlukan bukti terpisah.',
        'note_en': 'All three Indonesian HTML readers were rebuilt twice from isolated inputs, byte-identical to their native editions: 60 source units plus 32 companion units, not 92 source units. Twenty-eight omitted runtime dependencies were bound retrospectively. Native data-export replay, PDF production and semantic canon review still require separate evidence.',
        'integration_provenance': 'OpenAI Codex gpt-6-astra, Ultra',
        'native_text_provenance': 'OpenAI Codex gpt-5.6-sol, Ultra (native production receipts; this audit did not translate the books).'}
    pending['HTML_REPLAY.json'] = (json.dumps(result, ensure_ascii=False, indent=2) + '\n').encode('utf-8')
    DEST.mkdir(parents=True, exist_ok=True)
    for name, data in pending.items():
        path = DEST / name
        r.require(not path.exists() or path.read_bytes() == data, 'Existing different admission evidence preserved')
        if not path.exists():
            path.write_bytes(data)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    for lane in EXPECTED:
        parser.add_argument('--' + lane, type=Path, required=True)
    args = parser.parse_args()
    result = bind({lane: getattr(args, lane) for lane in EXPECTED})
    print(json.dumps({'state': result['state'], 'isolated_builds': 6, 'source_units': 60,
                      'companion_units': 32, 'native_parity_promoted': False}))
