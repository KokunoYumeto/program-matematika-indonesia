"""Reproduce the complete D100 classical HTML reader twice from isolated inputs.

Executes the HTML branch of the exact pinned native builder. No TeX process,
producer write, publication, terminology endorsement or PDF replay is claimed.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
NATIVE_RECEIPT = 'build/reader-id-corr1/BUILD_RECEIPT.json'
BUILDER = 'scripts/build_classical_reader_versioned.py'
BUILDER_SHA = 'c2560d838e791d76ef9400aa6e4e6104a7936402160644a774df445b6c63988b'
LEGACY_SHA = 'c807668bdf688f1a189366f204ac9f699c9a85010f45bbaa9dad4dbcc8106042'
SUPPLEMENT = 'backend/course-capsule-v1/authority/d100-classical-runtime-supplement-v1.json'
EXPECTED_HTML = {'bytes': 23773577, 'sha256': 'ea23c11b6a710a058e9d782eea1a7e0f2971a1551606f6cd51fc45209e9f87b5'}

def require(condition, message):
    if not condition:
        raise ValueError(message)

def fact(path):
    sha, size = hashlib.sha256(), 0
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            sha.update(block)
            size += len(block)
    return {'bytes': size, 'sha256': sha.hexdigest()}

def exact_path(root, relative):
    raw = Path(relative)
    require(not raw.is_absolute() and '..' not in raw.parts and ':' not in relative,
            'Non-relative input path')
    result = (root / raw).resolve()
    require(result.is_relative_to(root), 'Input escapes exact root')
    return result

def copy_inputs(native, stage, rows):
    for row in rows:
        relative = row['path']
        source = exact_path(native, relative)
        expected = {k: row[k] for k in ('bytes', 'sha256')}
        require(fact(source) == expected, 'Native input identity drift: ' + relative)
        target = exact_path(stage, relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        require(fact(target) == expected and fact(source) == expected,
                'Source changed or copy differs: ' + relative)

def one_run(stage, rows, pandoc, label):
    require(fact(stage / BUILDER)['sha256'] == BUILDER_SHA, 'Native builder drift')
    require(fact(stage / 'scripts/build_reader.py')['sha256'] == LEGACY_SHA,
            'Native historical dependency drift')
    sys.path.insert(0, str(stage / 'scripts'))
    sys.modules.pop('build_reader', None)
    try:
        spec = importlib.util.spec_from_file_location('d100_classical_' + label, stage / BUILDER)
        native = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(native)
        require(native.LANE == stage, 'Builder is not isolated')
        sources, title, subtitle, _ = native.classical_scope(30)
        asset_plan = native.classical_asset_plan(sources)
        lawful_plan = native.classical_lawful_input_plan(asset_plan)
        require(len(sources) == 120, 'Native source order scope changed')
        require(len(lawful_plan['rights_ledgers']) == 30, 'Native rights closure changed')
        tool_version = native.tool_line(pandoc, '--version')
        require(tool_version == native.EXPECTED_PANDOC, 'Pandoc version differs from native build')
        rendered = stage / 'isolated-html'
        rendered.mkdir()
        output = rendered / 'index.html'
        resource_path = os.pathsep.join((str(rendered), str(native.SOURCE_DIR),
                                        str(native.ASSET_DIR), str(stage)))
        command = [pandoc,
            '--from=markdown+yaml_metadata_block+tex_math_dollars+fenced_divs+bracketed_spans',
            '--standalone', '--toc', '--metadata=lang:id-ID',
            '--metadata=title:' + title, '--metadata=subtitle:' + subtitle,
            '--metadata=author:Holger Brenner (karya sumber)',
            '--resource-path=' + resource_path, *(str(p) for p in sources),
            '--to=html5', '--mathml', '--embed-resources',
            '--css=' + str(native.CSS), '--output=' + str(output)]
        env = os.environ.copy()
        env['SOURCE_DATE_EPOCH'] = native.SOURCE_DATE_EPOCH
        result = subprocess.run(command, cwd=stage, env=env, capture_output=True,
                                timeout=180, creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
        (rendered / 'pandoc-html.log').write_bytes(result.stdout + result.stderr)
        require(result.returncode == 0, 'Isolated Pandoc HTML execution failed')
        require(not result.stdout and not result.stderr, 'Native zero-warning condition changed')
        native.add_html_landmarks(output)
        actual = fact(output)
        require(actual == EXPECTED_HTML, 'HTML differs from the exact native reader')
        for row in rows:
            require(fact(stage / row['path']) == {k: row[k] for k in ('bytes', 'sha256')},
                    'Isolated input was modified: ' + row['path'])
        return {'label': label, 'source_files': len(rows), 'ordered_source_files': len(sources),
                'html': actual, 'tool': tool_version, 'mathml': True,
                'native_landmarks_applied': True, 'input_bytes_unchanged': True}
    finally:
        sys.path.pop(0)
        sys.modules.pop('build_reader', None)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--native-root', type=Path, default=ROOT.parent / 'algebraic-geometry-bridge-id')
    parser.add_argument('--output-root', type=Path, required=True)
    args = parser.parse_args()
    native, output = args.native_root.resolve(), args.output_root.resolve()
    require(output.is_relative_to((ROOT / 'work').resolve()), 'Output must be in the exact integration work area')
    require(not output.exists(), 'Existing replay preserved; inspect it rather than overwrite')
    receipt_path = native / NATIVE_RECEIPT
    receipt = json.loads(receipt_path.read_bytes())
    require(receipt['status'] == 'PASS' and len(receipt['inputs']) == 323,
            'Native build receipt scope changed')
    expected = next(row for row in receipt['outputs'] if row['path'].endswith('/index.html'))
    require({k: expected[k] for k in EXPECTED_HTML} == EXPECTED_HTML, 'Native HTML authority changed')
    require(fact(native / expected['path']) == EXPECTED_HTML, 'Native HTML bytes changed')
    supplement = json.loads((ROOT / SUPPLEMENT).read_bytes())
    require(supplement['native_build_receipt'] == {'path': NATIVE_RECEIPT, **fact(receipt_path)},
            'Supplement targets a different native receipt')
    require(supplement['builder']['sha256'] == BUILDER_SHA and len(supplement['files']) == 6,
            'Supplement builder/scope changed')
    rows = receipt['inputs'] + supplement['files']
    require(len({r['path'] for r in rows}) == len(rows) == 329, 'Duplicate runtime source path')
    pandoc = shutil.which('pandoc')
    require(pandoc, 'Pandoc unavailable')
    output.mkdir(parents=True)
    report = {'schema': 'd100-isolated-classical-html-replay/1', 'state': 'in_progress',
              'course_id': 'D100', 'locale': 'id-ID', 'source_course_units': 30,
              'receipt': {'path': NATIVE_RECEIPT, **fact(receipt_path)}, 'runs': [],
              'runtime_supplement': {'path': SUPPLEMENT, **fact(ROOT / SUPPLEMENT)},
              'producer_writes': False, 'tex_launched': False, 'pdf_replayed': False,
              'semantic_canon_review': False, 'whole_backend_complete': False,
              'integration_provenance': 'OpenAI Codex gpt-6-astra, Ultra',
              'native_builder_provenance': receipt.get('model_provenance')}
    try:
        for label in ('a', 'b'):
            stage = output / label
            stage.mkdir()
            copy_inputs(native, stage, rows)
            report['runs'].append(one_run(stage, rows, pandoc, label))
            (output / 'REPLAY.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
        require(report['runs'][0]['html'] == report['runs'][1]['html'], 'Replay A/B differ')
        report.update(state='pass', byte_identical_to_native=True,
                      runtime_producer_sources_used=False,
                      next_scope='BGK and original companion native HTML/backend replay; PDF remains separately evidenced.')
    except Exception as error:
        report.update(state='failed', failure_type=type(error).__name__,
                      reason=str(error).replace(str(ROOT), '<integration>').replace(str(native), '<native>'))
        raise
    finally:
        (output / 'REPLAY.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    print(json.dumps({'state': report['state'], 'runs': len(report['runs']),
                      'source_course_units': 30, 'html_bytes': EXPECTED_HTML['bytes'], 'tex_launched': False}))

if __name__ == '__main__':
    main()
