"""Record omitted D100 runtime reads from native read-only preflight branches."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('d100_replay', ROOT / 'scripts/replay-d100-native-html-v1.py')
replay = importlib.util.module_from_spec(spec)
spec.loader.exec_module(replay)


def discover(lane, native_root):
    native_root = native_root.resolve()
    config = replay.LANES[lane]
    receipt_path = native_root / config['receipt']
    replay.require(replay.fact(receipt_path)['sha256'] == config['receipt_sha256'], 'Receipt identity changed')
    receipt = json.loads(receipt_path.read_bytes())
    reads, enabled = set(), [True]

    def observe(event, args):
        if not enabled[0]:
            return
        if event == 'subprocess.Popen' or event.startswith(('os.remove', 'os.rename', 'os.mkdir')):
            raise ValueError('Read-only discovery forbids process/filesystem mutations')
        if event != 'open' or not isinstance(args[0], (str, bytes, os.PathLike)):
            return
        path = Path(os.fsdecode(args[0])).resolve()
        if not path.is_relative_to(native_root):
            return
        if path.suffix == '.pyc':
            raise FileNotFoundError('Use exact source, not an unbound native bytecode cache')
        mode, flags = args[1], args[2]
        replay.require(not (isinstance(mode, str) and any(c in mode for c in 'wax+'))
                       and not (isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT | os.O_TRUNC)),
                       'Native write forbidden during runtime discovery')
        if path.is_file():
            reads.add(path.relative_to(native_root).as_posix())

    sys.addaudithook(observe)
    try:
        with replay.isolated_builder(native_root, lane) as native:
            if lane == 'bgk':
                sources, *_ = native.complete_scope()
                native.validate_current_overlays(native.validate_source_closure())
                native.bgk_asset_plan(sources)
                for source in sources:
                    native.legacy.serialize_reader_math(source.read_text(encoding='utf-8'),
                                                       native.lane_relative(source), through=30)
            else:
                native.configure()
                native.review_gate()
                _, bgk_inputs, bgk, _ = native.verify_bgk()
                native.source_gate(bgk_inputs, bgk)
    finally:
        enabled[0] = False
    old = {r['path'] for r in receipt['inputs']}
    missing = sorted(reads - old)
    return {'schema': 'd100-native-runtime-supplement/1', 'course_id': 'D100', 'lane': lane,
        'finding': 'D100-RUNTIME-002' if lane == 'bgk' else 'D100-RUNTIME-003',
        'native_build_receipt': {'path': config['receipt'], **replay.fact(receipt_path)},
        'builder_sha256': config['builder_sha256'],
        'evidence_timing': 'retrospective_runtime_dependency_binding',
        'explanation_id': 'Daftar ini mengikat berkas yang dibaca pemeriksaan asli tetapi tidak tercantum dalam daftar masukan historis. Berkas asli dan bukti historis tidak diubah.',
        'scope': 'Observed native read-only source, correction-profile, rights and asset checks; followed by isolated HTML replay, not PDF or whole-backend closure.',
        'observed_native_reads': len(reads),
        'files': [{'path': relative, **replay.fact(native_root / relative)} for relative in missing],
        'producer_writes': False, 'processes_launched': False,
        'integration_provenance': 'OpenAI Codex gpt-6-astra, Ultra'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lane', choices=replay.LANES, required=True)
    parser.add_argument('--native-root', type=Path, default=ROOT.parent / 'algebraic-geometry-bridge-id')
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    replay.require(output.is_relative_to(ROOT / 'backend/course-capsule-v1/authority'), 'Exact integration authority output required')
    replay.require(not output.exists(), 'Preserve existing runtime supplement')
    result = discover(args.lane, args.native_root)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'lane': args.lane, 'observed_native_reads': result['observed_native_reads'],
                      'omitted_files': len(result['files']), 'omitted_bytes': sum(r['bytes'] for r in result['files'])}))
