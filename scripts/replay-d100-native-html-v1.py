"""Rebuild D100 BGK/companion HTML twice from exact isolated native inputs.

The native HTML transformations and checks are used without running their PDF
branches. Existing native receipts, readers and producer sources stay read-only.
"""
import argparse
from contextlib import contextmanager
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('d100_html_common', ROOT / 'scripts/replay-d100-classical-html-v1.py')
common = importlib.util.module_from_spec(spec)
spec.loader.exec_module(common)
fact, require, exact_path, copy_inputs = common.fact, common.require, common.exact_path, common.copy_inputs
LANES = {
    'bgk': {
        'receipt': 'build/reader-bgk-id-corr1/BUILD_RECEIPT.json',
        'receipt_sha256': '5d8315031b51abf6da6b7e37d54fa8653a686efb4f839aceb2ce7a4449e5162d',
        'input_count': 267, 'unit_count': 30,
        'builder': 'build_bgk_reader_versioned',
        'builder_sha256': 'd6d09f73a3cc139e4de0ee837de1457c23caa24d42d188ee62ea1cbbc45fc321',
        'html': {'bytes': 6837686, 'sha256': '1805fb6325a12d0400999d5fab5bd4fe101174e088a7a2e54fa47ffb32ce243e'},
    },
    'original': {
        'receipt': 'build/reader-original-bridge-id-corr1/BUILD_RECEIPT.json',
        'receipt_sha256': 'd254c2dbf32f3fb08cf914f5a8b926c9ba43e85a20e479570cea997d3196389b',
        'input_count': 150, 'unit_count': 32,
        'builder': 'build_original_bridge_reader_corr1',
        'builder_sha256': 'c35da87c7416118fe1ace21e391d3d28975a5033ec84ff6b86aa9ae1044d7e05',
        'html': {'bytes': 1431866, 'sha256': 'e901f73948ad7637cf7dfb0212b43acb08157afacb719f25a942199673bf2233'},
    },
}


@contextmanager
def isolated_builder(stage, lane):
    path = stage / 'scripts' / (LANES[lane]['builder'] + '.py')
    require(fact(path)['sha256'] == LANES[lane]['builder_sha256'], 'Native builder identity changed')
    previous_path = list(sys.path)
    prior_modules = dict(sys.modules)
    local_names = {p.stem for p in (stage / 'scripts').glob('*.py')}
    for name in local_names:
        sys.modules.pop(name, None)
    sys.path.insert(0, str(stage / 'scripts'))
    try:
        spec = importlib.util.spec_from_file_location(LANES[lane]['builder'], path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        require(module.LANE == stage, 'Native builder escaped isolation')
        yield module
    finally:
        sys.path[:] = previous_path
        for name in local_names:
            sys.modules.pop(name, None)
            if name in prior_modules:
                sys.modules[name] = prior_modules[name]


def run_html(command, directory, epoch):
    require(Path(command[0]).name.lower() in {'pandoc', 'pandoc.exe'}, 'Only Pandoc HTML is allowed')
    require('--to=html5' in command and not any('--pdf' in part for part in command),
            'Only the native HTML branch is in this replay')
    env = os.environ.copy()
    env['SOURCE_DATE_EPOCH'] = epoch
    completed = subprocess.run(command, cwd=directory, env=env, capture_output=True,
        timeout=180, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    (directory / 'pandoc-html.log').write_bytes(completed.stdout + completed.stderr)
    require(completed.returncode == 0, 'Isolated HTML build failed; retained local log')
    require(not completed.stdout and not completed.stderr, 'Native zero-warning HTML condition failed')


def bgk_html(native, stage, pandoc):
    sources, title, subtitle, _ = native.complete_scope()
    closure = native.validate_source_closure()
    overlays = native.validate_current_overlays(closure)
    native.bgk_asset_plan(sources)
    require(len(sources) == 122 and len(overlays) == 6, 'BGK source/overlay scope changed')
    rendered = stage / 'isolated-html'
    rendered.mkdir()
    html_sources, math_records = [], []
    for source in sources:
        original = source.read_text(encoding='utf-8')
        text, records = native.legacy.serialize_reader_math(original, native.lane_relative(source), through=30)
        math_records.extend(records)
        if records:
            staged = rendered / ('html-' + source.name)
            require(not staged.exists(), 'Staged HTML name collision')
            staged.write_text(text, encoding='utf-8', newline='\n')
            html_sources.append(staged)
        else:
            html_sources.append(source)
    output = rendered / 'index.html'
    resources = os.pathsep.join(map(str, (rendered, native.SOURCE_DIR, native.SOURCE_ROOT, native.legacy.ASSET_DIR, stage)))
    run_html([pandoc,
        '--from=markdown+yaml_metadata_block+tex_math_dollars+fenced_divs+bracketed_spans',
        '--standalone', '--toc', '--metadata=lang:id-ID', '--metadata=title:' + title,
        '--metadata=subtitle:' + subtitle, '--metadata=author:Holger Brenner (karya sumber)',
        '--resource-path=' + resources, *map(str, html_sources), '--to=html5', '--mathml',
        '--embed-resources', '--css=' + str(native.legacy.CSS), '--output=' + str(output)],
        rendered, native.SOURCE_DATE_EPOCH)
    fragments = native.legacy.apply_html_fragment_compatibility(output, 30)
    native.legacy.add_html_landmarks(output)
    fragments = native.legacy.validate_final_html_fragment_compatibility(output, 30, fragments)
    return {'ordered_source_files': len(sources), 'math_serialization_records': len(math_records),
            'source_units': 30, 'current_overlays_checked': len(overlays),
            'fragment_compatibility': fragments, 'html': fact(output)}


def original_html(native, stage, pandoc):
    # Deliberately avoid preflight()/tools_gate(): those query TeX even for HTML.
    native.configure()
    reviews, dependencies = native.review_gate()
    bgk_fact, bgk_inputs, bgk_inventory, bgk_deps = native.verify_bgk()
    text, linked_sources, accounting = native.source_gate(bgk_inputs, bgk_inventory)
    require(len(native.ORDERED_NAMES) == 32, 'Original companion source order changed')
    rendered = stage / 'isolated-html'
    rendered.mkdir()
    markdown = rendered / 'reader.md'
    markdown.write_text(text, encoding='utf-8', newline='\n')
    shutil.copyfile(native.local(native.base.BGK_HTML), rendered / 'bgk-reader.html')
    output = rendered / 'index.html'
    run_html([pandoc, '--from=' + native.READ_FORMAT, '--standalone', '--toc', '--toc-depth=2',
        '--metadata=lang:id-ID', '--metadata=title:' + native.TITLE,
        '--metadata=subtitle:Bank penguasaan, soal integratif, dan latihan penutup',
        '--metadata=author:' + native.PROVENANCE, '--metadata=date:2026-08-31',
        '--metadata=toc-title:Daftar Isi', '--metadata=license:CC BY-SA 4.0', str(markdown),
        '--to=html5', '--mathml', '--embed-resources', '--css=' + str(native.local(native.base.CSS)),
        '--output=' + str(output)], rendered, native.EPOCH)
    html = native.base.landmarks(output.read_text(encoding='utf-8'))
    checks = native.base.check_html(html, {'accounting': accounting})
    output.write_text(html, encoding='utf-8', newline='\n')
    require(fact(rendered / 'bgk-reader.html') == {k: bgk_fact[k] for k in ('bytes', 'sha256')},
            'Bundled BGK reader identity changed')
    return {'ordered_source_files': 32, 'companion_units': 32, 'new_source_units': 0,
            'html': fact(output), 'html_checks': checks, 'existing_review_records_checked': len(reviews),
            'combined_markdown': fact(markdown), 'bundled_bgk': fact(rendered / 'bgk-reader.html')}


def replay(lane, native_root, output):
    native_root, output = native_root.resolve(), output.resolve()
    require(output.is_relative_to((ROOT / 'work').resolve()), 'Output must stay in integration work area')
    require(not output.exists(), 'Existing replay is preserved; choose a fresh output')
    config = LANES[lane]
    receipt_path = exact_path(native_root, config['receipt'])
    require(fact(receipt_path)['sha256'] == config['receipt_sha256'], 'Pinned native receipt changed')
    receipt = json.loads(receipt_path.read_bytes())
    rows = receipt['inputs']
    require(receipt['status'] == 'PASS' and len(rows) == config['input_count'], 'Native input scope changed')
    supplement_relative = ('backend/course-capsule-v1/authority/d100-bgk-runtime-supplement-v2.json'
                           if lane == 'bgk' else
                           'backend/course-capsule-v1/authority/d100-original-runtime-supplement-v1.json')
    supplement_path = ROOT / supplement_relative
    supplement = json.loads(supplement_path.read_bytes())
    require(supplement['lane'] == lane and supplement['native_build_receipt'] ==
            {'path': config['receipt'], **fact(receipt_path)}, 'Supplement targets a different reader')
    require(supplement['builder_sha256'] == config['builder_sha256'], 'Supplement builder changed')
    require(len(supplement['files']) == {'bgk': 2, 'original': 20}[lane], 'Supplement scope changed')
    rows = rows + supplement['files']
    require(len({r['path'] for r in rows}) == len(rows), 'Duplicate native input')
    expected_output = next(r for r in receipt['outputs'] if r['path'].endswith('/index.html'))
    require({k: expected_output[k] for k in ('bytes', 'sha256')} == config['html'], 'Native output authority changed')
    require(fact(exact_path(native_root, expected_output['path'])) == config['html'], 'Native reader identity changed')
    pandoc = shutil.which('pandoc')
    require(pandoc, 'Pandoc unavailable')
    output.mkdir(parents=True)
    report = {'schema': 'd100-isolated-native-html-replay/1', 'state': 'in_progress',
        'course_id': 'D100', 'locale': 'id-ID', 'lane': lane,
        'receipt': {'path': config['receipt'], **fact(receipt_path)}, 'runs': [],
        'runtime_supplement': {'path': supplement_relative, **fact(supplement_path)},
        'producer_writes': False, 'tex_launched': False, 'pdf_replayed': False,
        'new_semantic_canon_review': False, 'whole_backend_complete': False,
        'integration_provenance': 'OpenAI Codex gpt-6-astra, Ultra',
        'native_provenance': receipt.get('model_provenance')}
    try:
        for label in ('a', 'b'):
            stage = output / label
            stage.mkdir()
            copy_inputs(native_root, stage, rows)
            with isolated_builder(stage, lane) as native:
                version = subprocess.run([pandoc, '--version'], capture_output=True, text=True,
                    check=True, timeout=30, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0)).stdout.splitlines()[0]
                require(version == 'pandoc 3.9.0.2', 'Native Pandoc version changed')
                result = (bgk_html if lane == 'bgk' else original_html)(native, stage, pandoc)
            require(result['html'] == config['html'], 'Rebuilt HTML differs from exact native reader')
            for row in rows:
                require(fact(exact_path(stage, row['path'])) == {k: row[k] for k in ('bytes', 'sha256')},
                        'Isolated input changed: ' + row['path'])
            report['runs'].append({'label': label, 'source_files': len(rows), 'tool': version,
                'input_bytes_unchanged': True, **result})
            (output / 'REPLAY.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        require(report['runs'][0]['html'] == report['runs'][1]['html'], 'Two builds differ')
        report.update(state='pass', byte_identical_to_native=True, runtime_producer_sources_used=False)
    except Exception as error:
        report.update(state='failed', failure_type=type(error).__name__,
            reason=str(error).replace(str(ROOT), '<integration>').replace(str(native_root), '<native>'))
        raise
    finally:
        (output / 'REPLAY.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--lane', choices=LANES, required=True)
    parser.add_argument('--native-root', type=Path, default=ROOT.parent / 'algebraic-geometry-bridge-id')
    parser.add_argument('--output-root', type=Path, required=True)
    args = parser.parse_args()
    result = replay(args.lane, args.native_root, args.output_root)
    print(json.dumps({'state': result['state'], 'lane': args.lane, 'runs': len(result['runs']),
                      'html_bytes': result['runs'][0]['html']['bytes'], 'tex_launched': False}))
